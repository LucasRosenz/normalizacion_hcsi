import pandas as pd
import os
from collections import defaultdict

def contar_encabezados_dia_manual():
    """
    Cuenta exactamente como lo hace el usuario: 
    número de veces que aparece "DÍA" en la columna A de cada Excel
    """
    directorio = "datos/excel_originales/agendas_originales"
    
    total_general = 0
    detalle_por_archivo = {}
    
    print("=== CONTEO MANUAL: 'DÍA' EN COLUMNA A ===\n")
    
    for archivo in sorted(os.listdir(directorio)):
        if archivo.endswith(('.xlsx', '.xls')):
            # Excluir archivos HCSI
            if 'HCSI' in archivo.upper():
                print(f"❌ Saltando: {archivo} (formato HCSI)")
                continue
                
            archivo_path = os.path.join(directorio, archivo)
            
            try:
                # Leer Excel sin encabezados
                df = pd.read_excel(archivo_path, header=None)
                
                # Contar ocurrencias de "DÍA" en la primera columna (índice 0)
                count_dia = 0
                dias_encontrados = []
                
                for i in range(len(df)):
                    if pd.notna(df.iloc[i, 0]):
                        celda = str(df.iloc[i, 0]).strip().upper()
                        if celda == 'DÍA' or celda == 'DIA':
                            count_dia += 1
                            # Buscar la agenda anterior a este "DÍA"
                            agenda_anterior = "Sin identificar"
                            for prev_i in range(i - 1, -1, -1):
                                if pd.notna(df.iloc[prev_i, 0]):
                                    prev_celda = str(df.iloc[prev_i, 0]).strip()
                                    if prev_celda.upper() not in ['DÍA', 'DIA', 'HORA INICIO', 'HORA FIN']:
                                        agenda_anterior = prev_celda[:60] + "..." if len(prev_celda) > 60 else prev_celda
                                        break
                            dias_encontrados.append((i + 1, agenda_anterior))
                
                detalle_por_archivo[archivo] = {
                    'count': count_dia,
                    'detalles': dias_encontrados
                }
                
                total_general += count_dia
                
                print(f"📄 {archivo}")
                print(f"   └─ 'DÍA' encontrado: {count_dia} veces")
                
                # Mostrar las primeras 3 ocurrencias para verificación
                for i, (fila, agenda) in enumerate(dias_encontrados[:3]):
                    print(f"      {i+1}. Fila {fila}: después de '{agenda}'")
                if len(dias_encontrados) > 3:
                    print(f"      ... y {len(dias_encontrados) - 3} más")
                print()
                    
            except Exception as e:
                print(f"❌ Error procesando {archivo}: {e}")
    
    print(f"🎯 TOTAL MANUAL: {total_general} ocurrencias de 'DÍA'")
    return total_general, detalle_por_archivo

def contar_agendas_procesadas():
    """
    Cuenta agendas únicas en la base procesada
    """
    try:
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        agendas_unicas = df.groupby(['nombre_original_agenda', 'efector']).ngroups
        nombres_unicos = df['nombre_original_agenda'].nunique()
        
        # Análisis detallado de nombres repetidos
        nombre_counts = df['nombre_original_agenda'].value_counts()
        nombres_repetidos = nombre_counts[nombre_counts > 1]
        
        print(f"\n=== CONTEO EN BASE PROCESADA ===")
        print(f"🎯 Agendas únicas (nombre + efector): {agendas_unicas}")
        print(f"🎯 Nombres únicos de agendas: {nombres_unicos}")
        print(f"🎯 Total registros: {len(df)}")
        
        if len(nombres_repetidos) > 0:
            print(f"\n📊 NOMBRES REPETIDOS EN DIFERENTES CENTROS:")
            for nombre, cantidad in nombres_repetidos.head(10).items():
                efectores = df[df['nombre_original_agenda'] == nombre]['efector'].unique()
                print(f"   • '{nombre}' aparece en {cantidad} centros: {', '.join(efectores)}")
            if len(nombres_repetidos) > 10:
                print(f"   ... y {len(nombres_repetidos) - 10} nombres más repetidos")
        
        return agendas_unicas, nombres_unicos, len(nombres_repetidos)
        
    except Exception as e:
        print(f"❌ Error leyendo base procesada: {e}")
        return 0, 0, 0

def analizar_diferencias():
    """
    Analiza las diferencias entre conteo manual y procesado
    """
    print("=" * 60)
    print("ANÁLISIS DE DIFERENCIAS")
    print("=" * 60)
    
    # Conteo manual
    total_manual, detalle_archivos = contar_encabezados_dia_manual()
    
    # Conteo procesado
    total_procesado, nombres_unicos, nombres_repetidos_count = contar_agendas_procesadas()
    
    # Mostrar diferencia
    diferencia = total_manual - total_procesado
    diferencia_nombres = total_manual - nombres_unicos
    
    print(f"\n=== COMPARACIÓN FINAL ===")
    print(f"📊 Conteo manual ('DÍA' en Excel): {total_manual}")
    print(f"📊 Agendas procesadas (nombre + efector): {total_procesado}")
    print(f"📊 Nombres únicos de agendas: {nombres_unicos}")
    print(f"📊 Nombres que se repiten entre centros: {nombres_repetidos_count}")
    print(f"📊 Diferencia (manual vs procesado): {diferencia}")
    print(f"📊 Diferencia (manual vs nombres únicos): {diferencia_nombres}")
    
    if diferencia > 0:
        print(f"\n⚠️  HAY {diferencia} AGENDA(S) QUE SE PERDIERON EN EL PROCESAMIENTO")
        if diferencia_nombres == nombres_repetidos_count * 2:
            print(f"✅ Explicación: La diferencia se debe a {nombres_repetidos_count} nombres repetidos entre centros")
        else:
            print("\nPosibles causas:")
            print("1. Agendas con formato diferente que no se detectaron")
            print("2. Encabezados 'DÍA' sin agenda válida arriba")
            print("3. Agendas que no cumplen criterio estructural")
            print("4. Errores en el procesamiento")
    elif diferencia < 0:
        print(f"\n✅ Se procesaron {abs(diferencia)} agendas más de lo esperado")
    else:
        print(f"\n✅ COINCIDENCIA PERFECTA")
    
    return detalle_archivos

if __name__ == "__main__":
    analizar_diferencias()
