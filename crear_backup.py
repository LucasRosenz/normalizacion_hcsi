#!/usr/bin/env python3
"""
Script simple para crear backup antes de hacer cambios
"""

import pandas as pd
import os
from datetime import datetime

def crear_backup():
    archivo_actual = 'agendas_consolidadas.xlsx'
    
    if not os.path.exists(archivo_actual):
        print("❌ No se encontró agendas_consolidadas.xlsx")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_backup = f'agendas_consolidadas_backup_{timestamp}.xlsx'
    
    try:
        df = pd.read_excel(archivo_actual)
        df.to_excel(archivo_backup, index=False)
        print(f"✅ Backup creado: {archivo_backup}")
        print(f"📊 Registros guardados: {len(df)}")
    except Exception as e:
        print(f"❌ Error creando backup: {e}")

if __name__ == "__main__":
    crear_backup()
