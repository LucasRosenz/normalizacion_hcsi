"""
Examinar específicamente el archivo CAPS San Pantaleon
"""
import pandas as pd

def examinar_caps_san_pantaleon():
    archivo = "datos/excel_originales/agendas_originales/Agendas activas CAPS San Pantaleon.xlsx"
    
    print("=" * 60)
    print("EXAMEN DETALLADO: CAPS SAN PANTALEÓN")
    print("=" * 60)
    
    try:
        # Leer sin encabezados
        df = pd.read_excel(archivo, header=None)
        
        print(f"📊 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print("\n📄 CONTENIDO COMPLETO:")
        
        # Mostrar todo el contenido con números de fila
        for i in range(min(150, len(df))):  # Primeras 150 filas
            col_a = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else "[VACÍO]"
            col_b = str(df.iloc[i, 1]) if pd.notna(df.iloc[i, 1]) else "[VACÍO]" if df.shape[1] > 1 else ""
            col_c = str(df.iloc[i, 2]) if pd.notna(df.iloc[i, 2]) else "[VACÍO]" if df.shape[1] > 2 else ""
            
            # Marcar las filas con "DÍA"
            marcador = ">>> " if col_a.upper() in ['DÍA', 'DIA'] else "    "
            
            print(f"{marcador}Fila {i+1:3d}: '{col_a}' | '{col_b}' | '{col_c}'")
        
        if len(df) > 150:
            print(f"\n... ({len(df) - 150} filas más)")
            
        # Contar DÍAs
        count_dia = 0
        for i in range(len(df)):
            if pd.notna(df.iloc[i, 0]):
                if str(df.iloc[i, 0]).strip().upper() in ['DÍA', 'DIA']:
                    count_dia += 1
        
        print(f"\n🎯 Total 'DÍA' encontrados: {count_dia}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    examinar_caps_san_pantaleon()
