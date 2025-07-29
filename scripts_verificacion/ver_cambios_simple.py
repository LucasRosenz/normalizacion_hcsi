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
    
    # Crear diccionarios de agendas para comparar - TODOS LOS CAMPOS (excepto agenda_id y nombre_original_agenda)
    agendas_antes = {}
    for _, row in df_antes.iterrows():
        key = row['nombre_original_agenda']
        agendas_antes[key] = {
            'doctor': normalizar_valor(row.get('doctor', '')),
            'area': normalizar_valor(row.get('area', '')),
            'tipo_turno': normalizar_valor(row.get('tipo_turno', '')),
            'dia': normalizar_valor(row.get('dia', '')),
            'hora_inicio': normalizar_valor(row.get('hora_inicio', '')),
            'hora_fin': normalizar_valor(row.get('hora_fin', '')),
            'efector': normalizar_valor(row.get('efector', '')),
            'ventanilla': normalizar_valor(row.get('ventanilla', ''))
        }
    
    agendas_despues = {}
    for _, row in df_despues.iterrows():
        key = row['nombre_original_agenda']
        agendas_despues[key] = {
            'doctor': normalizar_valor(row.get('doctor', '')),
            'area': normalizar_valor(row.get('area', '')),
            'tipo_turno': normalizar_valor(row.get('tipo_turno', '')),
            'dia': normalizar_valor(row.get('dia', '')),
            'hora_inicio': normalizar_valor(row.get('hora_inicio', '')),
            'hora_fin': normalizar_valor(row.get('hora_fin', '')),
            'efector': normalizar_valor(row.get('efector', '')),
            'ventanilla': normalizar_valor(row.get('ventanilla', ''))
        }
    
    # Buscar cambios en TODOS LOS CAMPOS
    cambios_encontrados = []
    for agenda in agendas_antes:
        if agenda in agendas_despues:
            antes = agendas_antes[agenda]
            despues = agendas_despues[agenda]
            
            cambios_agenda = []
            # Comparar todos los campos (excepto agenda_id y nombre_original_agenda)
            campos_a_comparar = [
                ('doctor', 'Doctor'),
                ('area', 'Área'),
                ('tipo_turno', 'Tipo de turno'),
                ('dia', 'Día'),
                ('hora_inicio', 'Hora inicio'),
                ('hora_fin', 'Hora fin'),
                ('efector', 'Efector'),
                ('ventanilla', 'Ventanilla')
            ]
            
            for campo_key, campo_nombre in campos_a_comparar:
                if antes[campo_key] != despues[campo_key]:
                    # Filtrar cambios triviales (nan ↔ '' o '' ↔ '')
                    if not (antes[campo_key] == '' and despues[campo_key] == ''):
                        cambios_agenda.append(f"{campo_nombre}: '{antes[campo_key]}' → '{despues[campo_key]}'")
            
            if cambios_agenda:
                cambios_encontrados.append({
                    'agenda': agenda,
                    'cambios': cambios_agenda
                })
    
    # Generar reporte en archivo txt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_reporte = f"reporte_cambios_{timestamp}.txt"
    
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write("REPORTE DE CAMBIOS EN AGENDAS\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Archivo backup: {archivo_backup}\n")
        f.write(f"Archivo actual: {archivo_actual}\n\n")
        f.write(f"Registros antes: {len(df_antes)}\n")
        f.write(f"Registros después: {len(df_despues)}\n\n")
        
        if cambios_encontrados:
            f.write(f"RESUMEN: Se encontraron {len(cambios_encontrados)} agendas con cambios\n\n")
            
            # Resumen por tipo de cambio - TODOS LOS CAMPOS
            cambios_doctor = sum(1 for c in cambios_encontrados if any('Doctor:' in cambio for cambio in c['cambios']))
            cambios_area = sum(1 for c in cambios_encontrados if any('Área:' in cambio for cambio in c['cambios']))
            cambios_tipo = sum(1 for c in cambios_encontrados if any('Tipo de turno:' in cambio for cambio in c['cambios']))
            cambios_dia = sum(1 for c in cambios_encontrados if any('Día:' in cambio for cambio in c['cambios']))
            cambios_hora_inicio = sum(1 for c in cambios_encontrados if any('Hora inicio:' in cambio for cambio in c['cambios']))
            cambios_hora_fin = sum(1 for c in cambios_encontrados if any('Hora fin:' in cambio for cambio in c['cambios']))
            cambios_efector = sum(1 for c in cambios_encontrados if any('Efector:' in cambio for cambio in c['cambios']))
            cambios_ventanilla = sum(1 for c in cambios_encontrados if any('Ventanilla:' in cambio for cambio in c['cambios']))
            
            f.write("TIPOS DE CAMBIOS:\n")
            f.write(f"• Doctor: {cambios_doctor} agendas\n")
            f.write(f"• Área: {cambios_area} agendas\n") 
            f.write(f"• Tipo de turno: {cambios_tipo} agendas\n")
            f.write(f"• Día: {cambios_dia} agendas\n")
            f.write(f"• Hora inicio: {cambios_hora_inicio} agendas\n")
            f.write(f"• Hora fin: {cambios_hora_fin} agendas\n")
            f.write(f"• Efector: {cambios_efector} agendas\n")
            f.write(f"• Ventanilla: {cambios_ventanilla} agendas\n\n")
            
            f.write("DETALLE DE CAMBIOS:\n")
            f.write("-" * 30 + "\n\n")
            
            for i, cambio in enumerate(cambios_encontrados):
                f.write(f"{i+1}. {cambio['agenda']}\n")
                for detalle in cambio['cambios']:
                    f.write(f"   └─ {detalle}\n")
                f.write("\n")
        else:
            f.write("RESULTADO: No se detectaron cambios en las agendas\n")
    
    print(f"📄 Reporte generado: {archivo_reporte}")
    if cambios_encontrados:
        print(f"🔄 Se encontraron {len(cambios_encontrados)} agendas con cambios")
    else:
        print("✅ No se detectaron cambios en las agendas")

if __name__ == "__main__":
    main()
