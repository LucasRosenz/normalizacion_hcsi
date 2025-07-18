"""
Script para investigar las 2 agendas perdidas y casos problemáticos de "DÍA"
"""
import pandas as pd
import os

def extraer_agendas_reales_excel():
    """Extrae agendas reales usando el mismo método que el procesador"""
    directorio = "datos/excel_originales/agendas_originales"
    agendas_reales = []
    
    for archivo in sorted(os.listdir(directorio)):
        if archivo.endswith(('.xlsx', '.xls')) and 'HCSI' not in archivo.upper():
            efector = archivo.replace('Agendas activas ', '').replace('Agendas Activas ', '').replace('.xlsx', '')
            archivo_path = os.path.join(directorio, archivo)
            
            try:
                df = pd.read_excel(archivo_path, header=None)
                
                for i in range(len(df)):
                    if pd.notna(df.iloc[i, 0]):
                        celda = str(df.iloc[i, 0]).strip()
                        
                        # Detectar usando el mismo criterio que el procesador
                        if celda.upper() in ['DÍA', 'DIA']:
                            # Buscar nombre de agenda anterior
                            agenda_nombre = None
                            fila_agenda = None
                            for j in range(i-1, -1, -1):
                                if pd.notna(df.iloc[j, 0]):
                                    prev_celda = str(df.iloc[j, 0]).strip()
                                    if prev_celda.upper() not in ['DÍA', 'DIA', 'HORA INICIO', 'HORA FIN', '']:
                                        agenda_nombre = prev_celda
                                        fila_agenda = j + 1
                                        break
                            
                            if agenda_nombre:
                                agendas_reales.append({
                                    'archivo': archivo,
                                    'efector': efector,
                                    'nombre': agenda_nombre,
                                    'fila_dia': i + 1,
                                    'fila_agenda': fila_agenda
                                })
                            else:
                                # DÍA sin agenda válida
                                agendas_reales.append({
                                    'archivo': archivo,
                                    'efector': efector,
                                    'nombre': '*** DÍA SIN AGENDA VÁLIDA ***',
                                    'fila_dia': i + 1,
                                    'fila_agenda': 'N/A'
                                })
                                
            except Exception as e:
                print(f"Error procesando {archivo}: {e}")
    
    return agendas_reales

def obtener_agendas_procesadas():
    """Obtiene las agendas que fueron procesadas exitosamente"""
    try:
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        agendas_procesadas = set()
        
        for _, row in df.iterrows():
            nombre = str(row['nombre_original_agenda']).strip()
            efector = str(row['efector']).strip()
            agendas_procesadas.add((nombre, efector))
        
        return agendas_procesadas
    except Exception as e:
        print(f"Error leyendo agendas procesadas: {e}")
        return set()

def analizar_casos_problematicos():
    """Analiza específicamente los casos problemáticos"""
    print("=" * 80)
    print("INVESTIGACIÓN DE CASOS PROBLEMÁTICOS")
    print("=" * 80)
    
    # Obtener todas las agendas de Excel
    print("📄 Extrayendo agendas de Excel...")
    agendas_excel = extraer_agendas_reales_excel()
    
    # Obtener agendas procesadas
    print("📊 Cargando agendas procesadas...")
    agendas_procesadas = obtener_agendas_procesadas()
    
    # Análisis
    casos_problematicos = []
    agendas_sin_procesar = []
    dias_sin_agenda = []
    
    print(f"\n🔍 ANÁLISIS DE {len(agendas_excel)} OCURRENCIAS DE 'DÍA':")
    
    for agenda in agendas_excel:
        nombre = agenda['nombre']
        efector = agenda['efector']
        
        if nombre == '*** DÍA SIN AGENDA VÁLIDA ***':
            dias_sin_agenda.append(agenda)
        elif (nombre, efector) not in agendas_procesadas:
            agendas_sin_procesar.append(agenda)
    
    # Reporte de días sin agenda válida
    if dias_sin_agenda:
        print(f"\n❌ DÍAS SIN AGENDA VÁLIDA ({len(dias_sin_agenda)}):")
        for caso in dias_sin_agenda:
            print(f"   📍 {caso['archivo']}, fila {caso['fila_dia']}")
    
    # Reporte de agendas no procesadas
    if agendas_sin_procesar:
        print(f"\n⚠️  AGENDAS NO PROCESADAS ({len(agendas_sin_procesar)}):")
        for agenda in agendas_sin_procesar[:10]:  # Mostrar primeras 10
            print(f"   📍 {agenda['archivo']}")
            print(f"      └─ Fila DÍA: {agenda['fila_dia']}, Fila agenda: {agenda['fila_agenda']}")
            print(f"      └─ Nombre: '{agenda['nombre']}'")
            print(f"      └─ Efector: {agenda['efector']}")
            print()
        if len(agendas_sin_procesar) > 10:
            print(f"   ... y {len(agendas_sin_procesar) - 10} más")
    
    # Estadísticas finales
    print(f"\n📊 RESUMEN:")
    print(f"   • Total 'DÍA' encontrados: {len(agendas_excel)}")
    print(f"   • Días sin agenda válida: {len(dias_sin_agenda)}")
    print(f"   • Agendas válidas en Excel: {len(agendas_excel) - len(dias_sin_agenda)}")
    print(f"   • Agendas procesadas: {len(agendas_procesadas)}")
    print(f"   • Agendas no procesadas: {len(agendas_sin_procesar)}")
    
    diferencia_real = (len(agendas_excel) - len(dias_sin_agenda)) - len(agendas_procesadas)
    print(f"   • Diferencia real: {diferencia_real}")
    
    if diferencia_real == 0:
        print(f"\n✅ EXPLICACIÓN ENCONTRADA:")
        print(f"   Los {len(dias_sin_agenda)} 'DÍA' sin agenda válida explican la discrepancia.")
        print(f"   No hay agendas perdidas realmente.")
    else:
        print(f"\n⚠️  AÚN HAY {diferencia_real} AGENDA(S) PERDIDA(S)")
    
    return agendas_sin_procesar, dias_sin_agenda

def investigar_casos_especificos(agendas_sin_procesar):
    """Investiga casos específicos de agendas no procesadas"""
    if not agendas_sin_procesar:
        return
    
    print(f"\n🔬 INVESTIGACIÓN DETALLADA DE AGENDAS NO PROCESADAS:")
    
    for i, agenda in enumerate(agendas_sin_procesar[:5]):  # Primeros 5 casos
        print(f"\n--- CASO {i+1} ---")
        print(f"Archivo: {agenda['archivo']}")
        print(f"Nombre: '{agenda['nombre']}'")
        print(f"Efector: {agenda['efector']}")
        
        # Leer el archivo para ver el contexto
        try:
            archivo_path = os.path.join("datos/excel_originales/agendas_originales", agenda['archivo'])
            df = pd.read_excel(archivo_path, header=None)
            
            fila_dia = agenda['fila_dia'] - 1  # Convertir a índice 0-based
            
            print(f"Contexto alrededor de la fila {agenda['fila_dia']}:")
            inicio = max(0, fila_dia - 3)
            fin = min(len(df), fila_dia + 4)
            
            for idx in range(inicio, fin):
                marcador = ">>> " if idx == fila_dia else "    "
                valor = str(df.iloc[idx, 0]) if pd.notna(df.iloc[idx, 0]) else "[VACÍO]"
                print(f"{marcador}Fila {idx+1}: {valor}")
                
        except Exception as e:
            print(f"Error leyendo contexto: {e}")

if __name__ == "__main__":
    agendas_sin_procesar, dias_sin_agenda = analizar_casos_problematicos()
    investigar_casos_especificos(agendas_sin_procesar)
