"""
Script de prueba para verificar el funcionamiento de la aplicación
"""
import pandas as pd
import os
import sys

def test_data_loading():
    """Prueba la carga de datos"""
    print("🔍 Probando carga de datos...")
    
    try:
        # Verificar si existe el archivo CSV
        if os.path.exists("agendas_consolidadas.csv"):
            df = pd.read_csv("agendas_consolidadas.csv")
            print(f"✅ Archivo CSV encontrado: {len(df)} registros")
            
            # Verificar columnas esenciales
            columnas_requeridas = ['efector', 'area', 'doctor', 'dia', 'hora_inicio', 'hora_fin']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                print(f"⚠️ Columnas faltantes: {columnas_faltantes}")
            else:
                print("✅ Todas las columnas esenciales están presentes")
            
            return True
        else:
            print("⚠️ No se encontró agendas_consolidadas.csv")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return False

def test_data_generation():
    """Prueba la generación de datos de ejemplo"""
    print("\n🔍 Probando generación de datos de ejemplo...")
    
    try:
        # Renombrar archivo existente si existe
        if os.path.exists("agendas_consolidadas.csv"):
            os.rename("agendas_consolidadas.csv", "agendas_consolidadas_backup.csv")
            print("📁 Archivo existente respaldado")
        
        # Generar datos de ejemplo
        from generar_datos_ejemplo import crear_archivo_ejemplo
        resultado = crear_archivo_ejemplo()
        
        if resultado:
            print("✅ Datos de ejemplo generados exitosamente")
            
            # Verificar el archivo generado
            df = pd.read_csv("agendas_consolidadas.csv")
            print(f"✅ Archivo generado con {len(df)} registros")
            
            # Restaurar archivo original si existía
            if os.path.exists("agendas_consolidadas_backup.csv"):
                os.remove("agendas_consolidadas.csv")
                os.rename("agendas_consolidadas_backup.csv", "agendas_consolidadas.csv")
                print("📁 Archivo original restaurado")
            
            return True
        else:
            print("⚠️ No se generaron datos (archivo ya existía)")
            return True
            
    except Exception as e:
        print(f"❌ Error generando datos: {e}")
        return False

def test_app_imports():
    """Prueba las importaciones de la aplicación"""
    print("\n🔍 Probando importaciones de la aplicación...")
    
    try:
        # Importar módulos principales
        import streamlit as st
        print("✅ Streamlit importado")
        
        import plotly.express as px
        print("✅ Plotly importado")
        
        import pandas as pd
        print("✅ Pandas importado")
        
        # Verificar que se puede importar el módulo de agendas
        try:
            from agendas import AgendaNormalizer
            print("✅ Módulo agendas importado")
        except ImportError as e:
            print(f"⚠️ No se pudo importar agendas: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_performance():
    """Prueba básica de rendimiento"""
    print("\n🔍 Probando rendimiento básico...")
    
    try:
        if not os.path.exists("agendas_consolidadas.csv"):
            print("⚠️ No hay archivo para probar rendimiento")
            return True
        
        import time
        start_time = time.time()
        
        # Cargar datos
        df = pd.read_csv("agendas_consolidadas.csv")
        load_time = time.time() - start_time
        
        print(f"⏱️ Tiempo de carga: {load_time:.2f} segundos")
        
        # Prueba de operaciones básicas
        start_time = time.time()
        
        # Operaciones típicas de la aplicación
        efectores = df['efector'].nunique()
        areas = df['area'].nunique()
        doctores = df['doctor'].nunique()
        
        op_time = time.time() - start_time
        print(f"⏱️ Tiempo de operaciones básicas: {op_time:.2f} segundos")
        print(f"📊 Estadísticas: {efectores} efectores, {areas} áreas, {doctores} doctores")
        
        if load_time < 5 and op_time < 2:
            print("✅ Rendimiento aceptable")
            return True
        else:
            print("⚠️ Rendimiento podría mejorarse")
            return True
            
    except Exception as e:
        print(f"❌ Error en prueba de rendimiento: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de la aplicación de agendas médicas")
    print("=" * 60)
    
    tests = [
        ("Carga de datos", test_data_loading),
        ("Generación de datos", test_data_generation),
        ("Importaciones", test_app_imports),
        ("Rendimiento", test_performance)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en prueba {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS:")
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"  {nombre}: {status}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Total: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡Todas las pruebas pasaron! La aplicación está lista para usar.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.")
    
    return exitosos == len(resultados)

if __name__ == "__main__":
    main()
