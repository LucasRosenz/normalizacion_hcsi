"""
Script para normalizar nombres de efectores y corregir las discrepancias
"""
import pandas as pd
import re

def normalizar_nombre_efector(nombre):
    """
    Normaliza nombres de efectores para consistencia
    """
    if not nombre:
        return nombre
    
    # Convertir a string y hacer strip
    nombre_normalizado = str(nombre).strip()
    
    # Normalizar mayúsculas/minúsculas en palabras clave
    nombre_normalizado = re.sub(r'\bbajo\b', 'Bajo', nombre_normalizado, flags=re.IGNORECASE)
    
    # Normalizar acentos específicos
    nombre_normalizado = nombre_normalizado.replace('Pantaleon', 'Pantaleón')
    nombre_normalizado = nombre_normalizado.replace('Odontologico', 'Odontológico')
    
    return nombre_normalizado

def corregir_nombres_efectores():
    """
    Corrige los nombres de efectores en el archivo procesado
    """
    print("🔧 CORRIGIENDO NOMBRES DE EFECTORES...")
    
    try:
        # Cargar datos
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        
        print(f"📊 Efectores originales:")
        efectores_originales = df['efector'].value_counts()
        for efector, count in efectores_originales.items():
            print(f"   • {efector}: {count} registros")
        
        # Aplicar normalización
        df['efector'] = df['efector'].apply(normalizar_nombre_efector)
        
        print(f"\n📊 Efectores corregidos:")
        efectores_corregidos = df['efector'].value_counts()
        for efector, count in efectores_corregidos.items():
            print(f"   • {efector}: {count} registros")
        
        # Guardar archivo corregido
        df.to_csv('datos/csv_procesado/agendas_consolidadas.csv', index=False)
        print(f"\n✅ Archivo corregido guardado")
        
        # Mostrar cambios realizados
        cambios = []
        for orig, nuevo in zip(efectores_originales.index, efectores_corregidos.index):
            if orig != nuevo:
                cambios.append(f"{orig} → {nuevo}")
        
        if cambios:
            print(f"\n🔄 Cambios realizados:")
            for cambio in cambios:
                print(f"   • {cambio}")
        else:
            print(f"\n✅ No se requirieron cambios")
        
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo efectores: {e}")
        return False

def verificar_correccion():
    """
    Verifica que la corrección haya solucionado las diferencias
    """
    print(f"\n🔍 VERIFICANDO CORRECCIÓN...")
    
    # Recontear después de la corrección
    try:
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        
        print(f"📊 Agendas únicas por efector (después de corrección):")
        agendas_por_efector = df.groupby('efector')['nombre_original_agenda'].nunique().sort_values(ascending=False)
        
        total_agendas = agendas_por_efector.sum()
        print(f"   🎯 Total agendas únicas: {total_agendas}")
        
        for efector, count in agendas_por_efector.items():
            print(f"   • {efector}: {count} agendas")
        
        return total_agendas
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("CORRECCIÓN DE NOMBRES DE EFECTORES")
    print("=" * 60)
    
    # Corregir nombres
    if corregir_nombres_efectores():
        # Verificar corrección
        total_final = verificar_correccion()
        
        print(f"\n📈 RESULTADO:")
        print(f"   • Agendas en Excel (manual): 612")
        print(f"   • Agendas procesadas (corregidas): {total_final}")
        diferencia_final = 612 - total_final
        print(f"   • Diferencia final: {diferencia_final}")
        
        if diferencia_final == 2:
            print(f"\n✅ Corrección exitosa: Solo quedan las 2 agendas realmente perdidas de CAPS San Isidro Labrador")
        elif diferencia_final == 0:
            print(f"\n🎉 ¡PERFECTO! Todas las discrepancias se debían a nombres de efectores")
        else:
            print(f"\n⚠️  Aún hay {diferencia_final} agendas con diferencias por investigar")
    else:
        print(f"\n❌ Error en la corrección")
