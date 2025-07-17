#!/usr/bin/env python3
"""
Script para verificar que FERNANDEZ tenga correctamente asignado el horario jueves 15:00-16:00
"""

import pandas as pd

def verificar_fernandez():
    """Busca registros de FERNANDEZ y el horario problemático específico"""
    try:
        # Leer el archivo consolidado
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        
        # Buscar FERNANDEZ
        fernandez_mask = df['nombre_original_agenda'].str.contains('FERNANDEZ', case=False, na=False) | \
                        df['doctor'].str.contains('FERNANDEZ', case=False, na=False)
        
        fernandez_records = df[fernandez_mask]
        
        print(f"=== REGISTROS DE FERNANDEZ ===")
        print(f"Total de registros: {len(fernandez_records)}")
        print()
        
        if len(fernandez_records) > 0:
            for idx, record in fernandez_records.iterrows():
                print(f"Agenda: {record['nombre_original_agenda']}")
                print(f"Doctor: {record['doctor']}")
                print(f"Día: {record['dia']} | Hora: {record['hora_inicio']}-{record['hora_fin']}")
                print(f"Efector: {record['efector']}")
                print(f"Área: {record['area']}")
                print()
        
        # Buscar específicamente jueves 15:00-16:00 en Hospital Boulogne
        jueves_problema = df[(df['dia'] == 'Jueves') & 
                            (df['hora_inicio'] == '15:00') & 
                            (df['hora_fin'] == '16:00') & 
                            (df['efector'] == 'Hospital Boulogne')]
        
        print(f"=== HORARIO JUEVES 15:00-16:00 EN HOSPITAL BOULOGNE ===")
        print(f"Total de registros con este horario: {len(jueves_problema)}")
        print()
        
        for idx, record in jueves_problema.iterrows():
            print(f"Agenda: {record['nombre_original_agenda']}")
            print(f"Doctor: {record['doctor']}")
            print(f"Área: {record['area']}")
            print(f"Tipo turno: {record['tipo_turno']}")
            print()
    
    except Exception as e:
        print(f"Error verificando FERNANDEZ: {e}")

if __name__ == "__main__":
    verificar_fernandez()
