#!/usr/bin/env python3
"""
Script simple para ver qué agendas cambiaron después de una modificación.
Compara el backup más reciente con el archivo actual.
"""

import pandas as pd
import os
import glob
from datetime import datetime

def main():
    # Cambiar al directorio de datos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datos_dir = os.path.join(script_dir, '..', 'datos', 'csv_procesado')
    os.chdir(datos_dir)
    
    # Buscar último backup
    archivos_backup = glob.glob('agendas_consolidadas_backup_*.xlsx')
    if not archivos_backup:
        print("❌ No se encontraron archivos de backup")
        return
    
    archivos_backup.sort(reverse=True)
    archivo_backup = archivos_backup[0]
    archivo_actual = 'agendas_consolidadas.xlsx'
    
    if not os.path.exists(archivo_actual):
        print("❌ No se encontró agendas_consolidadas.xlsx")
        return
    
    print(f"🔍 Comparando:")
    print(f"   Backup: {archivo_backup}")
    print(f"   Actual: {archivo_actual}")
    print()
    
    try:
        df_antes = pd.read_excel(archivo_backup)
        df_despues = pd.read_excel(archivo_actual)
    except Exception as e:
        print(f"❌ Error cargando archivos: {e}")
        return
    
    print(f"📊 Registros antes: {len(df_antes)}")
    print(f"📊 Registros después: {len(df_despues)}")
    print()
    
    def normalizar_valor(valor):
        """Normaliza valores nan, NaN, None a string vacío para comparación consistente"""
        if pd.isna(valor) or valor is None or str(valor).lower() == 'nan':
            return ''
        return str(valor).strip()
    
    # Crear diccionarios de agendas para comparar
    agendas_antes = {}
    for _, row in df_antes.iterrows():
        key = row['nombre_original_agenda']
        agendas_antes[key] = {
            'doctor': normalizar_valor(row.get('doctor', '')),
            'area': normalizar_valor(row.get('area', '')),
            'tipo_turno': normalizar_valor(row.get('tipo_turno', ''))
        }
    
    agendas_despues = {}
    for _, row in df_despues.iterrows():
        key = row['nombre_original_agenda']
        agendas_despues[key] = {
            'doctor': normalizar_valor(row.get('doctor', '')),
            'area': normalizar_valor(row.get('area', '')),
            'tipo_turno': normalizar_valor(row.get('tipo_turno', ''))
        }
    
    # Buscar cambios
    cambios_encontrados = []
    for agenda in agendas_antes:
        if agenda in agendas_despues:
            antes = agendas_antes[agenda]
            despues = agendas_despues[agenda]
            
            cambios_agenda = []
            # Solo reportar cambios que no sean de vacío a vacío o variaciones de nan
            if antes['doctor'] != despues['doctor']:
                # Filtrar cambios triviales (nan ↔ '')
                if not (antes['doctor'] == '' and despues['doctor'] == ''):
                    cambios_agenda.append(f"Doctor: '{antes['doctor']}' → '{despues['doctor']}'")
            if antes['area'] != despues['area']:
                if not (antes['area'] == '' and despues['area'] == ''):
                    cambios_agenda.append(f"Área: '{antes['area']}' → '{despues['area']}'")
            if antes['tipo_turno'] != despues['tipo_turno']:
                if not (antes['tipo_turno'] == '' and despues['tipo_turno'] == ''):
                    cambios_agenda.append(f"Tipo: '{antes['tipo_turno']}' → '{despues['tipo_turno']}'")
            
            if cambios_agenda:
                cambios_encontrados.append({
                    'agenda': agenda,
                    'cambios': cambios_agenda
                })
    
    # Mostrar resultados
    if cambios_encontrados:
        print(f"🔄 Se encontraron {len(cambios_encontrados)} agendas con cambios:")
        print()
        
        # Resumen por tipo de cambio
        cambios_doctor = sum(1 for c in cambios_encontrados if any('Doctor:' in cambio for cambio in c['cambios']))
        cambios_area = sum(1 for c in cambios_encontrados if any('Área:' in cambio for cambio in c['cambios']))
        cambios_tipo = sum(1 for c in cambios_encontrados if any('Tipo:' in cambio for cambio in c['cambios']))
        
        print("📊 Resumen de cambios:")
        print(f"   • Doctor: {cambios_doctor} agendas")
        print(f"   • Área: {cambios_area} agendas") 
        print(f"   • Tipo de turno: {cambios_tipo} agendas")
        print()
        
        for i, cambio in enumerate(cambios_encontrados[:15]):  # Mostrar máximo 15
            print(f"{i+1}. {cambio['agenda']}")
            for detalle in cambio['cambios']:
                print(f"   └─ {detalle}")
            print()
        
        if len(cambios_encontrados) > 15:
            print(f"   ... y {len(cambios_encontrados) - 15} más")
    else:
        print("✅ No se detectaron cambios en las agendas")

if __name__ == "__main__":
    main()
