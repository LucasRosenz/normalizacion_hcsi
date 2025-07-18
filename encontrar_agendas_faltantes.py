import pandas as pd
import os

def extraer_todas_agendas_excel():
    """
    Extrae TODAS las agendas de los Excel usando el mismo criterio que el conteo manual
    """
    directorio = "datos/excel_originales/agendas_originales"
    
    agendas_excel = []  # Lista de (nombre_agenda, efector)
    
    print("=== EXTRAYENDO TODAS LAS AGENDAS DE EXCEL ===\n")
    
    for archivo in sorted(os.listdir(directorio)):
        if archivo.endswith(('.xlsx', '.xls')):
            # Excluir archivos HCSI
            if 'HCSI' in archivo.upper():
                continue
                
            archivo_path = os.path.join(directorio, archivo)
            efector = inferir_efector(archivo)
            
            try:
                df = pd.read_excel(archivo_path, header=None)
                
                print(f"📄 {archivo} ({efector})")
                agendas_archivo = []
                
                for i in range(len(df)):
                    if pd.notna(df.iloc[i, 0]):
                        celda = str(df.iloc[i, 0]).strip().upper()
                        if celda == 'DÍA' or celda == 'DIA':
                            # Buscar la agenda anterior a este "DÍA"
                            agenda_nombre = None
                            for prev_i in range(i - 1, -1, -1):
                                if pd.notna(df.iloc[prev_i, 0]):
                                    prev_celda = str(df.iloc[prev_i, 0]).strip()
                                    if prev_celda.upper() not in ['DÍA', 'DIA', 'HORA INICIO', 'HORA FIN']:
                                        agenda_nombre = prev_celda
                                        break
                            
                            if agenda_nombre:
                                agendas_archivo.append(agenda_nombre)
                                agendas_excel.append((agenda_nombre, efector))
                
                print(f"   └─ {len(agendas_archivo)} agendas encontradas")
                
                # Mostrar algunas agendas de ejemplo
                for j, agenda in enumerate(agendas_archivo[:3]):
                    print(f"      {j+1}. {agenda[:70]}{'...' if len(agenda) > 70 else ''}")
                if len(agendas_archivo) > 3:
                    print(f"      ... y {len(agendas_archivo) - 3} más")
                print()
                    
            except Exception as e:
                print(f"❌ Error procesando {archivo}: {e}")
    
    return agendas_excel

def extraer_agendas_procesadas():
    """
    Extrae agendas de la base procesada
    """
    df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
    
    # Obtener agendas únicas (nombre + efector)
    agendas_procesadas = []
    agendas_unicas = df.groupby(['nombre_original_agenda', 'efector']).first().reset_index()
    
    for _, row in agendas_unicas.iterrows():
        agendas_procesadas.append((row['nombre_original_agenda'], row['efector']))
    
    return agendas_procesadas

def inferir_efector(nombre_archivo):
    """Misma lógica que en agendas.py"""
    nombre_base = os.path.splitext(nombre_archivo)[0]
    nombre_upper = nombre_base.upper()
    
    if 'HOSPITAL BOULOGNE' in nombre_upper:
        return 'Hospital Boulogne'
    elif 'HOSPITAL MATERNO' in nombre_upper:
        return 'Hospital Materno'
    elif 'HOSPITAL ODONTOLOGICO' in nombre_upper:
        return 'Hospital Odontológico'
    elif 'CAPS BARRIO OBRERO' in nombre_upper:
        return 'CAPS Barrio Obrero'
    elif 'CAPS BECCAR' in nombre_upper:
        return 'CAPS Beccar'
    elif 'CAPS LA RIBERA' in nombre_upper:
        return 'CAPS La Ribera'
    elif 'CAPS BAJO BOULOGNE' in nombre_upper:
        return 'CAPS Bajo Boulogne'
    elif 'CAPS DIAGONAL SALTA' in nombre_upper:
        return 'CAPS Diagonal Salta'
    elif 'CAPS SAN ISIDRO LABRADOR' in nombre_upper:
        return 'CAPS San Isidro Labrador'
    elif 'CAPS SAN PANTALEON' in nombre_upper:
        return 'CAPS San Pantaleón'
    elif 'CAPS VILLA ADELINA' in nombre_upper:
        return 'CAPS Villa Adelina'
    elif 'CENTRO EL NIDO' in nombre_upper:
        return 'Centro El Nido'
    
    return nombre_base

def encontrar_agendas_faltantes():
    """
    Encuentra las agendas que están en Excel pero no en la base procesada
    """
    print("=" * 70)
    print("BÚSQUEDA DE AGENDAS FALTANTES")
    print("=" * 70)
    
    # Extraer agendas de ambos lugares
    agendas_excel = extraer_todas_agendas_excel()
    agendas_procesadas = extraer_agendas_procesadas()
    
    print(f"\n=== RESUMEN ===")
    print(f"Agendas en Excel: {len(agendas_excel)}")
    print(f"Agendas procesadas: {len(agendas_procesadas)}")
    
    # Convertir a sets para comparación
    set_excel = set(agendas_excel)
    set_procesadas = set(agendas_procesadas)
    
    # Encontrar diferencias
    faltantes = set_excel - set_procesadas
    extras = set_procesadas - set_excel
    
    print(f"\n=== ANÁLISIS DE DIFERENCIAS ===")
    print(f"❌ Agendas en Excel pero NO procesadas: {len(faltantes)}")
    print(f"✅ Agendas procesadas pero NO en Excel: {len(extras)}")
    
    if faltantes:
        print(f"\n🔍 AGENDAS FALTANTES ({len(faltantes)}):")
        for i, (agenda, efector) in enumerate(sorted(faltantes), 1):
            print(f"  {i}. '{agenda}' ({efector})")
            print(f"      → Longitud: {len(agenda)} caracteres")
            
            # Analizar por qué no se procesó
            print("      → Análisis:")
            
            # Verificar criterio estructural básico
            if not agenda.strip():
                print("        • Agenda vacía después de strip()")
            elif len(agenda.strip()) < 3:
                print("        • Agenda muy corta (< 3 caracteres)")
            else:
                print("        • Posible problema con criterio estructural o formato especial")
            print()
    
    if extras:
        print(f"\n⚠️  AGENDAS EXTRAS EN PROCESADAS ({len(extras)}):")
        for i, (agenda, efector) in enumerate(sorted(extras), 1):
            print(f"  {i}. '{agenda}' ({efector})")
    
    return faltantes, extras

if __name__ == "__main__":
    encontrar_agendas_faltantes()
