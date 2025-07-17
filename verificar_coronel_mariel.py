#!/usr/bin/env python3
"""
Script para verificar los horarios de CORONEL MARIEL después de la corrección
"""

import pandas as pd

def verificar_coronel_mariel():
    """Busca todos los registros relacionados con CORONEL MARIEL"""
    try:
        # Leer el archivo consolidado
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        
        # Buscar registros que contengan "CORONEL" o "MARIEL"
        coronel_mask = df['nombre_original_agenda'].str.contains('CORONEL', case=False, na=False) | \
                      df['doctor'].str.contains('CORONEL', case=False, na=False) | \
                      df['nombre_original_agenda'].str.contains('MARIEL', case=False, na=False) | \
                      df['doctor'].str.contains('MARIEL', case=False, na=False)
        
        coronel_records = df[coronel_mask]
        
        print(f"=== REGISTROS DE CORONEL MARIEL ===")
        print(f"Total de registros encontrados: {len(coronel_records)}")
        print()
        
        if len(coronel_records) > 0:
            # Mostrar todos los registros
            for idx, record in coronel_records.iterrows():
                print(f"Registro {idx + 1}:")
                print(f"  Agenda original: {record['nombre_original_agenda']}")
                print(f"  Doctor: {record['doctor']}")
                print(f"  Área: {record['area']}")
                print(f"  Día: {record['dia']}")
                print(f"  Hora inicio: {record['hora_inicio']}")
                print(f"  Hora fin: {record['hora_fin']}")
                print(f"  Efector: {record['efector']}")
                print(f"  Tipo turno: {record['tipo_turno']}")
                print()
            
            # Buscar específicamente el caso problemático: jueves 15-16 en Hospital Boulogne
            problema_mask = (coronel_records['dia'] == 'Jueves') & \
                           (coronel_records['hora_inicio'] == '15:00') & \
                           (coronel_records['hora_fin'] == '16:00') & \
                           (coronel_records['efector'] == 'Hospital Boulogne')
            
            registros_problema = coronel_records[problema_mask]
            
            if len(registros_problema) > 0:
                print("⚠️  PROBLEMA DETECTADO: Sigue apareciendo el horario Jueves 15:00-16:00 en Hospital Boulogne")
                for idx, record in registros_problema.iterrows():
                    print(f"  Agenda problemática: {record['nombre_original_agenda']}")
            else:
                print("✅ CORRECCIÓN EXITOSA: No se detectó el horario problemático Jueves 15:00-16:00 en Hospital Boulogne")
        
        else:
            print("No se encontraron registros de CORONEL MARIEL.")
    
    except Exception as e:
        print(f"Error verificando CORONEL MARIEL: {e}")

if __name__ == "__main__":
    verificar_coronel_mariel()
