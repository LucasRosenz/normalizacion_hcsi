"""
Análisis de diferencias centro por centro para identificar exactamente dónde están las discrepancias
"""
import pandas as pd
import os
from collections import defaultdict

def normalizar_efector(nombre):
    """
    Normaliza nombres de efectores para comparación
    """
    if not nombre:
        return nombre
    
    nombre_norm = str(nombre).strip()
    
    # Normalizar mayúsculas/minúsculas
    nombre_norm = nombre_norm.replace('bajo', 'Bajo')
    nombre_norm = nombre_norm.replace('San Pantaleon', 'San Pantaleón')
    nombre_norm = nombre_norm.replace('Odontologico', 'Odontológico')
    
    return nombre_norm

def contar_agendas_por_centro():
    """
    Cuenta agendas por centro tanto en Excel como en datos procesados
    """
    directorio = "datos/excel_originales/agendas_originales"
    
    # Conteo manual por centro
    conteo_excel = {}
    detalle_excel = {}
    
    print("=== CONTEO MANUAL POR CENTRO ===")
    
    for archivo in sorted(os.listdir(directorio)):
        if archivo.endswith(('.xlsx', '.xls')) and 'HCSI' not in archivo.upper():
            # Extraer nombre del efector del nombre del archivo
            efector = archivo.replace('Agendas activas ', '').replace('Agendas Activas ', '').replace('.xlsx', '')
            efector = normalizar_efector(efector)  # Normalizar nombre
            archivo_path = os.path.join(directorio, archivo)
            
            try:
                df = pd.read_excel(archivo_path, header=None)
                
                count_dia = 0
                agendas_encontradas = []
                
                for i in range(len(df)):
                    if pd.notna(df.iloc[i, 0]):
                        celda = str(df.iloc[i, 0]).strip().upper()
                        if celda == 'DÍA' or celda == 'DIA':
                            count_dia += 1
                            
                            # Buscar la agenda anterior
                            agenda_nombre = "Sin identificar"
                            for prev_i in range(i - 1, -1, -1):
                                if pd.notna(df.iloc[prev_i, 0]):
                                    prev_celda = str(df.iloc[prev_i, 0]).strip()
                                    if prev_celda.upper() not in ['DÍA', 'DIA', 'HORA INICIO', 'HORA FIN']:
                                        agenda_nombre = prev_celda
                                        break
                            agendas_encontradas.append(agenda_nombre)
                
                conteo_excel[efector] = count_dia
                detalle_excel[efector] = agendas_encontradas
                
                print(f"📄 {efector}: {count_dia} agendas")
                
            except Exception as e:
                print(f"❌ Error procesando {archivo}: {e}")
    
    # Conteo en datos procesados
    print(f"\n=== CONTEO EN DATOS PROCESADOS ===")
    conteo_procesado = {}
    detalle_procesado = {}
    
    try:
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        
        # Agrupar por efector y contar agendas únicas
        for efector in df['efector'].unique():
            df_efector = df[df['efector'] == efector]
            agendas_unicas = df_efector.groupby(['nombre_original_agenda']).ngroups
            nombres_agendas = df_efector['nombre_original_agenda'].unique().tolist()
            
            conteo_procesado[efector] = agendas_unicas
            detalle_procesado[efector] = sorted(nombres_agendas)
            
            print(f"📊 {efector}: {agendas_unicas} agendas")
            
    except Exception as e:
        print(f"❌ Error leyendo datos procesados: {e}")
    
    return conteo_excel, conteo_procesado, detalle_excel, detalle_procesado

def comparar_centros(conteo_excel, conteo_procesado, detalle_excel, detalle_procesado):
    """
    Compara las diferencias centro por centro
    """
    print(f"\n" + "=" * 80)
    print("COMPARACIÓN CENTRO POR CENTRO")
    print("=" * 80)
    
    todos_efectores = set(conteo_excel.keys()) | set(conteo_procesado.keys())
    diferencias_encontradas = []
    
    for efector in sorted(todos_efectores):
        excel_count = conteo_excel.get(efector, 0)
        procesado_count = conteo_procesado.get(efector, 0)
        diferencia = excel_count - procesado_count
        
        if diferencia != 0:
            diferencias_encontradas.append((efector, excel_count, procesado_count, diferencia))
            
        status = "✅" if diferencia == 0 else "❌"
        print(f"{status} {efector:30} | Excel: {excel_count:3d} | Procesado: {procesado_count:3d} | Dif: {diferencia:3d}")
    
    # Análisis detallado de las diferencias
    if diferencias_encontradas:
        print(f"\n🔍 ANÁLISIS DETALLADO DE DIFERENCIAS:")
        
        for efector, excel_count, procesado_count, diferencia in diferencias_encontradas:
            print(f"\n--- {efector} ---")
            print(f"Diferencia: {diferencia} agenda(s)")
            
            if efector in detalle_excel and efector in detalle_procesado:
                agendas_excel = set(detalle_excel[efector])
                agendas_procesadas = set(detalle_procesado[efector])
                
                # Agendas en Excel pero no procesadas
                solo_excel = agendas_excel - agendas_procesadas
                if solo_excel:
                    print(f"📄 En Excel pero NO procesadas ({len(solo_excel)}):")
                    for agenda in sorted(solo_excel)[:5]:  # Mostrar primeras 5
                        print(f"   • {agenda}")
                    if len(solo_excel) > 5:
                        print(f"   ... y {len(solo_excel) - 5} más")
                
                # Agendas procesadas pero no en Excel
                solo_procesadas = agendas_procesadas - agendas_excel
                if solo_procesadas:
                    print(f"📊 Procesadas pero NO en Excel ({len(solo_procesadas)}):")
                    for agenda in sorted(solo_procesadas)[:5]:  # Mostrar primeras 5
                        print(f"   • {agenda}")
                    if len(solo_procesadas) > 5:
                        print(f"   ... y {len(solo_procesadas) - 5} más")
            
            elif efector in detalle_excel:
                print(f"📄 Centro completamente no procesado - {excel_count} agendas perdidas")
            elif efector in detalle_procesado:
                print(f"📊 Centro procesado sin archivo Excel - {procesado_count} agendas extra")
    
    # Resumen final
    total_excel = sum(conteo_excel.values())
    total_procesado = sum(conteo_procesado.values())
    diferencia_total = total_excel - total_procesado
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   • Total agendas en Excel: {total_excel}")
    print(f"   • Total agendas procesadas: {total_procesado}")
    print(f"   • Diferencia total: {diferencia_total}")
    print(f"   • Centros con diferencias: {len(diferencias_encontradas)}")
    
    return diferencias_encontradas

def limpiar_archivos_temporales():
    """
    Limpia archivos temporales y los organiza en las carpetas correctas
    """
    print(f"\n🧹 LIMPIANDO Y ORGANIZANDO ARCHIVOS...")
    
    # Archivos temporales que se pueden eliminar
    archivos_temporales = [
        'encontrar_agendas_faltantes.py',
        'encontrar_agendas_perdidas.py',
        'investigar_dias_problematicos.py',
        'examinar_san_pantaleon.py'
    ]
    
    archivos_eliminados = []
    for archivo in archivos_temporales:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                archivos_eliminados.append(archivo)
                print(f"   ✅ Eliminado: {archivo}")
            except Exception as e:
                print(f"   ❌ Error eliminando {archivo}: {e}")
    
    # Mover scripts de verificación a la carpeta correcta
    scripts_verificacion = [
        'analizar_diferencias_conteo.py'
    ]
    
    if not os.path.exists('scripts_verificacion'):
        os.makedirs('scripts_verificacion')
    
    for script in scripts_verificacion:
        if os.path.exists(script):
            destino = os.path.join('scripts_verificacion', script)
            if not os.path.exists(destino):  # Solo mover si no existe
                try:
                    os.rename(script, destino)
                    print(f"   📁 Movido a scripts_verificacion/: {script}")
                except Exception as e:
                    print(f"   ❌ Error moviendo {script}: {e}")
    
    print(f"   🎯 {len(archivos_eliminados)} archivos eliminados")

if __name__ == "__main__":
    # Análisis principal
    conteo_excel, conteo_procesado, detalle_excel, detalle_procesado = contar_agendas_por_centro()
    diferencias = comparar_centros(conteo_excel, conteo_procesado, detalle_excel, detalle_procesado)
    
    # Limpieza de archivos
    limpiar_archivos_temporales()
    
    print(f"\n✅ Análisis completado. {len(diferencias)} centro(s) con diferencias identificados.")
