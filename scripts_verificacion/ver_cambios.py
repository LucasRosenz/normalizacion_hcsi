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
    directorio_procesado = os.path.join(script_dir, '..', 'datos', 'csv_procesado')
    directorio_backup = os.path.join(script_dir, '..', 'datos', 'backup')
    
    # Buscar último backup en la carpeta backup
    archivos_backup = glob.glob(os.path.join(directorio_backup, 'agendas_consolidadas_backup_*.xlsx'))
    if not archivos_backup:
        print("❌ No se encontraron archivos de backup en datos/backup/")
        return
    
    archivos_backup.sort(reverse=True)
    archivo_backup = archivos_backup[0]
    archivo_actual = os.path.join(directorio_procesado, 'agendas_consolidadas.xlsx')
    
    if not os.path.exists(archivo_actual):
        print("❌ No se encontró agendas_consolidadas.xlsx")
        return
    
    print(f"🔍 Comparando:")
    print(f"   Backup: {os.path.basename(archivo_backup)}")
    print(f"   Actual: agendas_consolidadas.xlsx")
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
    
    # Crear diccionarios de registros para comparar FILA POR FILA - TODOS LOS CAMPOS
    # Usar índice de fila como clave única para garantizar comparación fila por fila
    registros_antes = {}
    for idx, row in df_antes.iterrows():
        # Usar siempre el índice de fila para identificar cada fila única
        key = f'fila_{idx}'
        registros_antes[key] = {
            'nombre_original_agenda': normalizar_valor(row.get('nombre_original_agenda', '')),
            'doctor': normalizar_valor(row.get('doctor', '')),
            'area': normalizar_valor(row.get('area', '')),
            'tipo_turno': normalizar_valor(row.get('tipo_turno', '')),
            'dia': normalizar_valor(row.get('dia', '')),
            'hora_inicio': normalizar_valor(row.get('hora_inicio', '')),
            'hora_fin': normalizar_valor(row.get('hora_fin', '')),
            'efector': normalizar_valor(row.get('efector', '')),
            'ventanilla': normalizar_valor(row.get('ventanilla', ''))
        }
    
    registros_despues = {}
    for idx, row in df_despues.iterrows():
        # Usar siempre el índice de fila para identificar cada fila única
        key = f'fila_{idx}'
        registros_despues[key] = {
            'nombre_original_agenda': normalizar_valor(row.get('nombre_original_agenda', '')),
            'doctor': normalizar_valor(row.get('doctor', '')),
            'area': normalizar_valor(row.get('area', '')),
            'tipo_turno': normalizar_valor(row.get('tipo_turno', '')),
            'dia': normalizar_valor(row.get('dia', '')),
            'hora_inicio': normalizar_valor(row.get('hora_inicio', '')),
            'hora_fin': normalizar_valor(row.get('hora_fin', '')),
            'efector': normalizar_valor(row.get('efector', '')),
            'ventanilla': normalizar_valor(row.get('ventanilla', ''))
        }
    
    # Buscar cambios en TODOS LOS CAMPOS comparando fila por fila
    cambios_encontrados = []
    for fila_key in registros_antes:
        if fila_key in registros_despues:
            antes = registros_antes[fila_key]
            despues = registros_despues[fila_key]
            
            cambios_fila = []
            # Comparar todos los campos incluyendo nombre_original_agenda
            campos_a_comparar = [
                ('nombre_original_agenda', 'Nombre agenda'),
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
                        cambios_fila.append(f"{campo_nombre}: '{antes[campo_key]}' → '{despues[campo_key]}'")
            
            if cambios_fila:
                cambios_encontrados.append({
                    'fila': fila_key,
                    'agenda': despues['nombre_original_agenda'],  # Mostrar el nombre de la agenda
                    'cambios': cambios_fila
                })
    
    # Generar reporte en archivo txt en la carpeta backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_reporte = os.path.join(directorio_backup, f"reporte_cambios_{timestamp}.txt")
    
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write("REPORTE DE CAMBIOS EN AGENDAS\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Archivo backup: {os.path.basename(archivo_backup)}\n")
        f.write(f"Archivo actual: agendas_consolidadas.xlsx\n\n")
        f.write(f"Registros antes: {len(df_antes)}\n")
        f.write(f"Registros después: {len(df_despues)}\n\n")
        
        if cambios_encontrados:
            f.write(f"RESUMEN: Se encontraron {len(cambios_encontrados)} filas con cambios\n\n")
            
            # Resumen por tipo de cambio - TODOS LOS CAMPOS incluye ahora nombre_original_agenda
            cambios_nombre = sum(1 for c in cambios_encontrados if any('Nombre agenda:' in cambio for cambio in c['cambios']))
            cambios_doctor = sum(1 for c in cambios_encontrados if any('Doctor:' in cambio for cambio in c['cambios']))
            cambios_area = sum(1 for c in cambios_encontrados if any('Área:' in cambio for cambio in c['cambios']))
            cambios_tipo = sum(1 for c in cambios_encontrados if any('Tipo de turno:' in cambio for cambio in c['cambios']))
            cambios_dia = sum(1 for c in cambios_encontrados if any('Día:' in cambio for cambio in c['cambios']))
            cambios_hora_inicio = sum(1 for c in cambios_encontrados if any('Hora inicio:' in cambio for cambio in c['cambios']))
            cambios_hora_fin = sum(1 for c in cambios_encontrados if any('Hora fin:' in cambio for cambio in c['cambios']))
            cambios_efector = sum(1 for c in cambios_encontrados if any('Efector:' in cambio for cambio in c['cambios']))
            cambios_ventanilla = sum(1 for c in cambios_encontrados if any('Ventanilla:' in cambio for cambio in c['cambios']))
            
            f.write("TIPOS DE CAMBIOS:\n")
            f.write(f"• Nombre agenda: {cambios_nombre} filas\n")
            f.write(f"• Doctor: {cambios_doctor} filas\n")
            f.write(f"• Área: {cambios_area} filas\n") 
            f.write(f"• Tipo de turno: {cambios_tipo} filas\n")
            f.write(f"• Día: {cambios_dia} filas\n")
            f.write(f"• Hora inicio: {cambios_hora_inicio} filas\n")
            f.write(f"• Hora fin: {cambios_hora_fin} filas\n")
            f.write(f"• Efector: {cambios_efector} filas\n")
            f.write(f"• Ventanilla: {cambios_ventanilla} filas\n\n")
            
            f.write("DETALLE DE CAMBIOS:\n")
            f.write("-" * 30 + "\n\n")
            
            for i, cambio in enumerate(cambios_encontrados):
                f.write(f"{i+1}. {cambio['agenda']} ({cambio['fila']})\n")
                for detalle in cambio['cambios']:
                    f.write(f"   └─ {detalle}\n")
                f.write("\n")
        else:
            f.write("RESULTADO: No se detectaron cambios en las filas\n")
    
    print(f"📄 Reporte generado: {os.path.basename(archivo_reporte)}")
    print(f"📂 Ubicación: datos/backup/")
    if cambios_encontrados:
        print(f"🔄 Se encontraron {len(cambios_encontrados)} filas con cambios")
    else:
        print("✅ No se detectaron cambios en las filas")

if __name__ == "__main__":
    main()
