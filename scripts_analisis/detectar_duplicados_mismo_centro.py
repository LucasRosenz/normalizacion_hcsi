import pandas as pd
import os

def analizar_duplicados_caps_san_isidro():
    """
    Analiza específicamente el archivo de CAPS San Isidro Labrador 
    para detectar agendas duplicadas en el mismo centro
    """
    archivo_path = "datos/excel_originales/agendas_originales/Agendas activas CAPS San Isidro Labrador.xlsx"
    
    print("🔍 ANÁLISIS DE DUPLICADOS - CAPS SAN ISIDRO LABRADOR")
    print("=" * 60)
    
    try:
        # Leer Excel
        df = pd.read_excel(archivo_path, header=None)
        
        # Buscar todas las agendas (usando el mismo criterio que agendas.py)
        agendas_encontradas = []
        
        for i in range(len(df)):
            if pd.notna(df.iloc[i, 0]):
                celda = str(df.iloc[i, 0]).strip()
                
                # Buscar si la siguiente fila tiene "DÍA"
                if i + 1 < len(df) and pd.notna(df.iloc[i + 1, 0]):
                    siguiente_celda = str(df.iloc[i + 1, 0]).strip().upper()
                    if siguiente_celda in ['DÍA', 'DIA']:
                        agendas_encontradas.append({
                            'fila': i + 1,
                            'nombre': celda,
                            'dia_en_fila': i + 2
                        })
        
        print(f"📊 Total agendas encontradas: {len(agendas_encontradas)}")
        print(f"📊 Debe coincidir con 66 'DÍA' encontrados\n")
        
        # Analizar duplicados
        nombres_agendas = [agenda['nombre'] for agenda in agendas_encontradas]
        nombres_unicos = list(set(nombres_agendas))
        
        print(f"📊 Nombres únicos de agendas: {len(nombres_unicos)}")
        print(f"📊 Diferencia (total vs únicos): {len(agendas_encontradas) - len(nombres_unicos)}")
        
        # Encontrar duplicados
        from collections import Counter
        contador_nombres = Counter(nombres_agendas)
        duplicados = {nombre: count for nombre, count in contador_nombres.items() if count > 1}
        
        if duplicados:
            print(f"\n🚨 DUPLICADOS ENCONTRADOS:")
            for nombre, cantidad in duplicados.items():
                print(f"   • '{nombre}' aparece {cantidad} veces")
                # Mostrar en qué filas
                filas = [str(agenda['fila']) for agenda in agendas_encontradas if agenda['nombre'] == nombre]
                print(f"     └─ En filas: {', '.join(filas)}")
        else:
            print("\n✅ No se encontraron duplicados")
        
        return agendas_encontradas, duplicados
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return [], {}

def verificar_procesamiento_duplicados():
    """
    Verifica cómo se procesaron las agendas de CAPS San Isidro Labrador
    """
    print("\n" + "=" * 60)
    print("🔍 VERIFICACIÓN EN BASE PROCESADA")
    print("=" * 60)
    
    try:
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        caps_si = df[df['efector'] == 'CAPS San Isidro Labrador']
        
        print(f"📊 Agendas procesadas para CAPS San Isidro Labrador: {len(caps_si)}")
        
        # Contar duplicados en procesado
        contador_procesado = caps_si['nombre_original_agenda'].value_counts()
        duplicados_procesado = contador_procesado[contador_procesado > 1]
        
        if len(duplicados_procesado) > 0:
            print(f"\n📊 Duplicados en base procesada:")
            for nombre, cantidad in duplicados_procesado.items():
                print(f"   • '{nombre}': {cantidad} veces")
        else:
            print("\n📊 No hay duplicados en base procesada (se deduplicaron)")
        
        # Mostrar todos los nombres para comparar
        print(f"\n📋 TODAS LAS AGENDAS PROCESADAS:")
        for i, nombre in enumerate(sorted(caps_si['nombre_original_agenda'].unique()), 1):
            print(f"   {i:2d}. {nombre}")
        
        return caps_si
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame()

def comparar_resultados():
    """
    Compara los resultados del Excel vs procesado
    """
    print("\n" + "=" * 60)
    print("📊 COMPARACIÓN FINAL")
    print("=" * 60)
    
    # Analizar Excel
    agendas_excel, duplicados_excel = analizar_duplicados_caps_san_isidro()
    
    # Analizar procesado
    caps_procesado = verificar_procesamiento_duplicados()
    
    if agendas_excel and not caps_procesado.empty:
        nombres_excel = [agenda['nombre'] for agenda in agendas_excel]
        nombres_procesado = caps_procesado['nombre_original_agenda'].tolist()
        
        print(f"\n🎯 RESUMEN:")
        print(f"   • Excel original: {len(nombres_excel)} agendas")
        print(f"   • Nombres únicos en Excel: {len(set(nombres_excel))}")
        print(f"   • Base procesada: {len(nombres_procesado)} agendas")
        print(f"   • Nombres únicos procesados: {len(set(nombres_procesado))}")
        
        diferencia = len(nombres_excel) - len(nombres_procesado)
        print(f"   • Diferencia: {diferencia}")
        
        if duplicados_excel:
            print(f"\n💡 EXPLICACIÓN:")
            print(f"   La diferencia de {diferencia} se debe a que el procesamiento")
            print(f"   deduplica agendas con el mismo nombre en el mismo centro.")
            print(f"   Duplicados encontrados: {list(duplicados_excel.keys())}")

if __name__ == "__main__":
    comparar_resultados()
