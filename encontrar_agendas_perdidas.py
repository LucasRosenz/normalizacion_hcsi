"""
Script para encontrar exactamente las 2 agendas que se pierden en el procesamiento
"""
import pandas as pd
import os
from pathlib import Path

def leer_agendas_procesadas():
    """Lee las agendas procesadas"""
    try:
        csv_path = 'datos/csv_procesado/agendas_consolidadas.csv'
        df = pd.read_csv(csv_path)
        agendas_procesadas = set()
        for _, row in df.iterrows():
            nombre_agenda = str(row['nombre_original_agenda']).strip()
            efector = str(row['efector']).strip()
            agenda_completa = f"{nombre_agenda} ({efector})"
            agendas_procesadas.add(agenda_completa)
        return agendas_procesadas
    except Exception as e:
        print(f"Error leyendo agendas procesadas: {e}")
        return set()

def extraer_agendas_excel():
    """Extrae todas las agendas de los archivos Excel siguiendo el patrón DÍA"""
    excel_path = 'datos/excel_originales/agendas_originales'
    archivos_excel = [f for f in os.listdir(excel_path) if f.endswith('.xlsx')]
    agendas_excel = []
    
    for archivo in archivos_excel:
        print(f"📄 Procesando {archivo}...")
        efector = archivo.replace('Agendas activas ', '').replace('Agendas Activas ', '').replace('.xlsx', '')
        archivo_completo = os.path.join(excel_path, archivo)
        
        try:
            df = pd.read_excel(archivo_completo, header=None)
            
            for i in range(len(df)):
                # Buscar filas con 'DÍA' en columna A
                if pd.notna(df.iloc[i, 0]) and str(df.iloc[i, 0]).strip().upper() == 'DÍA':
                    # Buscar el nombre de agenda anterior
                    for j in range(i-1, -1, -1):
                        if pd.notna(df.iloc[j, 0]):
                            valor = str(df.iloc[j, 0]).strip()
                            # Verificar que no sea otro 'DÍA' o valor vacío
                            if valor.upper() != 'DÍA' and valor != '':
                                agenda_completa = f"{valor} ({efector})"
                                agendas_excel.append({
                                    'archivo': archivo,
                                    'fila_dia': i+1,
                                    'fila_agenda': j+1,
                                    'nombre_agenda': valor,
                                    'efector': efector,
                                    'agenda_completa': agenda_completa
                                })
                                break
                            
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")
    
    return agendas_excel

def main():
    print("=" * 70)
    print("BÚSQUEDA ESPECÍFICA DE AGENDAS PERDIDAS")
    print("=" * 70)
    
    # Cargar agendas procesadas
    print("📊 Cargando agendas procesadas...")
    agendas_procesadas = leer_agendas_procesadas()
    print(f"   └─ {len(agendas_procesadas)} agendas procesadas encontradas")
    
    # Extraer agendas de Excel
    print("\n📄 Extrayendo agendas de Excel...")
    agendas_excel = extraer_agendas_excel()
    print(f"   └─ {len(agendas_excel)} agendas en Excel encontradas")
    
    # Crear conjunto de agendas Excel para comparación
    agendas_excel_set = {agenda['agenda_completa'] for agenda in agendas_excel}
    
    # Encontrar diferencias
    print("\n🔍 ANÁLISIS DE DIFERENCIAS:")
    print(f"📊 Agendas en Excel: {len(agendas_excel_set)}")
    print(f"📊 Agendas procesadas: {len(agendas_procesadas)}")
    
    # Agendas en Excel pero no procesadas
    solo_en_excel = agendas_excel_set - agendas_procesadas
    print(f"\n❌ Agendas en Excel pero NO procesadas: {len(solo_en_excel)}")
    
    if solo_en_excel:
        print("   AGENDAS PERDIDAS:")
        for i, agenda in enumerate(sorted(solo_en_excel), 1):
            print(f"   {i}. {agenda}")
            
            # Buscar detalles de esta agenda
            for agenda_detail in agendas_excel:
                if agenda_detail['agenda_completa'] == agenda:
                    print(f"      📍 Archivo: {agenda_detail['archivo']}")
                    print(f"      📍 Fila agenda: {agenda_detail['fila_agenda']}")
                    print(f"      📍 Fila DÍA: {agenda_detail['fila_dia']}")
                    print(f"      📍 Nombre: {agenda_detail['nombre_agenda']}")
                    break
    
    # Agendas procesadas pero no en Excel (por completitud)
    solo_procesadas = agendas_procesadas - agendas_excel_set
    print(f"\n✅ Agendas procesadas pero NO en Excel: {len(solo_procesadas)}")
    
    if solo_procesadas:
        print("   AGENDAS EXTRA:")
        for i, agenda in enumerate(sorted(solo_procesadas), 1):
            print(f"   {i}. {agenda}")
    
    print(f"\n🎯 DIFERENCIA TOTAL: {len(agendas_excel_set) - len(agendas_procesadas)} agendas")

if __name__ == "__main__":
    main()
