#!/usr/bin/env python3
"""
Script simple para crear backup antes de hacer cambios
"""

import pandas as pd
import os
import glob
from datetime import datetime

def limpiar_backups_anteriores(directorio_backup):
    """Elimina todos los archivos de backup y reportes anteriores"""
    try:
        # Buscar archivos de backup
        archivos_backup = glob.glob(os.path.join(directorio_backup, 'agendas_consolidadas_backup_*.xlsx'))
        # Buscar archivos de reporte
        archivos_reporte = glob.glob(os.path.join(directorio_backup, 'reporte_cambios_*.txt'))
        
        archivos_a_eliminar = archivos_backup + archivos_reporte
        
        if archivos_a_eliminar:
            print(f"🧹 Limpiando {len(archivos_a_eliminar)} archivos anteriores...")
            for archivo in archivos_a_eliminar:
                os.remove(archivo)
                print(f"   🗑️  Eliminado: {os.path.basename(archivo)}")
        else:
            print("🧹 No hay archivos anteriores que limpiar")
            
    except Exception as e:
        print(f"⚠️  Error limpiando archivos anteriores: {e}")

def crear_backup():
    # Configurar directorios
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directorio_procesado = os.path.join(script_dir, '..', 'datos', 'csv_procesado')
    directorio_backup = os.path.join(script_dir, '..', 'datos', 'backup')
    
    archivo_actual = os.path.join(directorio_procesado, 'agendas_consolidadas.xlsx')
    
    if not os.path.exists(archivo_actual):
        print("❌ No se encontró agendas_consolidadas.xlsx")
        return
    
    # Limpiar archivos anteriores
    limpiar_backups_anteriores(directorio_backup)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_backup = os.path.join(directorio_backup, f'agendas_consolidadas_backup_{timestamp}.xlsx')
    
    try:
        df = pd.read_excel(archivo_actual)
        df.to_excel(archivo_backup, index=False)
        print(f"✅ Backup creado: {os.path.basename(archivo_backup)}")
        print(f"📊 Registros guardados: {len(df)}")
        print(f"📂 Ubicación: datos/backup/")
    except Exception as e:
        print(f"❌ Error creando backup: {e}")

if __name__ == "__main__":
    crear_backup()
