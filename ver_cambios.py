#!/usr/bin/env python3
"""
Script simple para ver qué agendas cambiaron después de una modificación.
Compara el backup más reciente con el archivo actual.
"""

import pandas as pd
import os
import glob
from datetime import datetime

def encontrar_ultimo_backup():
    os.chdir('datos/csv_procesado')
    """Encuentra el backup más reciente"""
    archivos_backup = glob.glob('agendas_consolidadas_backup_*.xlsx')
    if not archivos_backup:
        print("❌ No se encontraron archivos de backup")
        return None
    
    # Ordenar por fecha en el nombre del archivo
    archivos_backup.sort(reverse=True)
    return archivos_backup[0]

def comparar_cambios():
    os.chdir('datos/csv_procesado')

    """Compara el archivo actual con el último backup"""
    
    # Buscar archivos
    archivo_actual = 'agendas_consolidadas.xlsx'
    archivo_backup = encontrar_ultimo_backup()
    
    if not archivo_backup:
        return
    
    if not os.path.exists(archivo_actual):
        print("❌ No se encontró agendas_consolidadas.xlsx")
        return
    
    print(f"🔍 Comparando:")
    print(f"   Backup: {archivo_backup}")
    print(f"   Actual: {archivo_actual}")
    print()
    
    # Cargar archivos
    try:
        os.chdir('datos/csv_procesado')

        df_antes = pd.read_excel(archivo_backup)
        df_despues = pd.read_excel(archivo_actual)
    except Exception as e:
        print(f"❌ Error cargando archivos: {e}")
        return
    
    print(f"📊 Registros antes: {len(df_antes)}")
    print(f"📊 Registros después: {len(df_despues)}")
    print()
    
    # Crear diccionarios de agendas para comparar
    agendas_antes = {}
    agendas_despues = {}
    
    # Agrupar por nombre de agenda y crear "firma" de cada agenda
    for _, row in df_antes.iterrows():
        agenda = row['nombre_original_agenda']
        if agenda not in agendas_antes:
            agendas_antes[agenda] = {
                'doctor': set(),
                'area': set(), 
                'tipo_turno': set(),
                'ventanilla': set(),
                'efector': row['efector']
            }
        agendas_antes[agenda]['doctor'].add(str(row['doctor']))
        agendas_antes[agenda]['area'].add(str(row['area']))
        agendas_antes[agenda]['tipo_turno'].add(str(row['tipo_turno']))
        agendas_antes[agenda]['ventanilla'].add(str(row['ventanilla']))
    
    for _, row in df_despues.iterrows():
        agenda = row['nombre_original_agenda']
        if agenda not in agendas_despues:
            agendas_despues[agenda] = {
                'doctor': set(),
                'area': set(),
                'tipo_turno': set(), 
                'ventanilla': set(),
                'efector': row['efector']
            }
        agendas_despues[agenda]['doctor'].add(str(row['doctor']))
        agendas_despues[agenda]['area'].add(str(row['area']))
        agendas_despues[agenda]['tipo_turno'].add(str(row['tipo_turno']))
        agendas_despues[agenda]['ventanilla'].add(str(row['ventanilla']))
    
    # Encontrar cambios
    agendas_cambiadas = []
    
    agendas_comunes = set(agendas_antes.keys()) & set(agendas_despues.keys())
    
    for agenda in agendas_comunes:
        antes = agendas_antes[agenda]
        despues = agendas_despues[agenda]
        
        cambios = []
        
        # Comparar cada campo
        if antes['doctor'] != despues['doctor']:
            cambios.append(f"doctor: {list(antes['doctor'])} → {list(despues['doctor'])}")
        
        if antes['area'] != despues['area']:
            cambios.append(f"area: {list(antes['area'])} → {list(despues['area'])}")
            
        if antes['tipo_turno'] != despues['tipo_turno']:
            cambios.append(f"tipo_turno: {list(antes['tipo_turno'])} → {list(despues['tipo_turno'])}")
            
        if antes['ventanilla'] != despues['ventanilla']:
            cambios.append(f"ventanilla: {list(antes['ventanilla'])} → {list(despues['ventanilla'])}")
        
        if cambios:
            agendas_cambiadas.append({
                'agenda': agenda,
                'efector': despues['efector'],
                'cambios': cambios
            })
    
    # Mostrar resultados
    if agendas_cambiadas:
        print(f"🔄 Se encontraron {len(agendas_cambiadas)} agendas con cambios:")
        print()
        
        for i, item in enumerate(agendas_cambiadas, 1):
            print(f"{i}. 📄 {item['agenda']}")
            print(f"   🏥 {item['efector']}")
            for cambio in item['cambios']:
                print(f"   🔄 {cambio}")
            print()
    else:
        print("✅ No se encontraron cambios en las agendas")
    
    # Agendas nuevas y eliminadas
    nuevas = set(agendas_despues.keys()) - set(agendas_antes.keys())
    eliminadas = set(agendas_antes.keys()) - set(agendas_despues.keys())
    
    if nuevas:
        print(f"➕ Agendas nuevas: {len(nuevas)}")
        for agenda in list(nuevas)[:5]:
            efector = agendas_despues[agenda]['efector']
            print(f"   • {agenda} ({efector})")
        if len(nuevas) > 5:
            print(f"   ... y {len(nuevas) - 5} más")
        print()
    
    if eliminadas:
        print(f"➖ Agendas eliminadas: {len(eliminadas)}")
        for agenda in list(eliminadas)[:5]:
            efector = agendas_antes[agenda]['efector']
            print(f"   • {agenda} ({efector})")
        if len(eliminadas) > 5:
            print(f"   ... y {len(eliminadas) - 5} más")

if __name__ == "__main__":
    print("🔍 Verificando cambios en agendas...")
    print()
    comparar_cambios()
