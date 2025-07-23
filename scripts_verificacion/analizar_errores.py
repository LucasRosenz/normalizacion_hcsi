import pandas as pd
import os
from collections import defaultdict

def analizar_asignaciones_incorrectas():
    """
    Analiza el CSV consolidado para detectar casos donde una agenda
    puede estar tomando horarios de agendas posteriores incorrectamente
    """
    # Leer el CSV consolidado
    archivo_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datos', 'csv_procesado', 'agendas_consolidadas.csv')
    df = pd.read_csv(archivo_csv)
    
    print("=== ANÁLISIS DE ASIGNACIONES INCORRECTAS ===\n")
    
    # 1. Buscar médicos/agendas que aparecen con múltiples áreas médicas diferentes
    print("1. MÉDICOS/AGENDAS CON MÚLTIPLES ÁREAS MÉDICAS:")
    print("-" * 60)
    
    medicos_multiples_areas = defaultdict(set)
    
    for _, row in df.iterrows():
        nombre_agenda = row['nombre_original_agenda']
        doctor = row['doctor'] if pd.notna(row['doctor']) and row['doctor'].strip() else "SIN_DOCTOR"
        area = row['area'] if pd.notna(row['area']) and row['area'].strip() else "SIN_AREA"
        efector = row['efector']
        
        # Crear una clave única por doctor/agenda y efector
        clave = f"{doctor} ({efector})"
        medicos_multiples_areas[clave].add(area)
    
    # Encontrar casos sospechosos
    casos_sospechosos = []
    for clave, areas in medicos_multiples_areas.items():
        if len(areas) > 1:
            casos_sospechosos.append((clave, areas))
    
    casos_sospechosos.sort(key=lambda x: len(x[1]), reverse=True)
    
    for clave, areas in casos_sospechosos[:20]:  # Top 20 casos más sospechosos
        print(f"{clave}: {len(areas)} áreas diferentes")
        print(f"   Áreas: {', '.join(sorted(areas))}")
        print()
    
    # 2. Buscar nombres de agenda que claramente NO deberían tener doctor
    print("\n2. AGENDAS DE SERVICIOS GENERALES CON DOCTOR ASIGNADO:")
    print("-" * 60)
    
    servicios_generales = ['AGENDA BIS', 'ENFERMERIA', 'VACUNACION', 'LABORATORIO', 
                          'FARMACIA', 'ESTADISTICA', 'ADMINISTRACION', 'RADIOLOGIA',
                          'ECOGRAFIA', 'DIRECCION', 'COORDINACION']
    
    for servicio in servicios_generales:
        registros_servicio = df[df['nombre_original_agenda'].str.contains(servicio, case=False, na=False)]
        if not registros_servicio.empty:
            doctores_unicos = registros_servicio['doctor'].dropna().unique()
            doctores_no_vacios = [d for d in doctores_unicos if d.strip()]
            
            if doctores_no_vacios:
                print(f"{servicio}:")
                print(f"   Aparece con {len(doctores_no_vacios)} doctores diferentes:")
                for doctor in doctores_no_vacios[:5]:  # Solo mostrar los primeros 5
                    print(f"     - {doctor}")
                if len(doctores_no_vacios) > 5:
                    print(f"     ... y {len(doctores_no_vacios) - 5} más")
                print()
    
    # 3. Buscar patrones de horarios sospechosos
    print("\n3. PATRONES DE HORARIOS SOSPECHOSOS:")
    print("-" * 60)
    
    # Agrupar por efector y día para buscar horarios idénticos con doctores diferentes
    for efector in df['efector'].unique():
        df_efector = df[df['efector'] == efector]
        
        for dia in df_efector['dia'].unique():
            df_dia = df_efector[df_efector['dia'] == dia]
            
            # Buscar horarios idénticos
            horarios_duplicados = defaultdict(list)
            for _, row in df_dia.iterrows():
                horario = f"{row['hora_inicio']}-{row['hora_fin']}"
                doctor = row['doctor'] if pd.notna(row['doctor']) and row['doctor'].strip() else "SIN_DOCTOR"
                area = row['area'] if pd.notna(row['area']) and row['area'].strip() else "SIN_AREA"
                agenda = row['nombre_original_agenda']
                
                horarios_duplicados[horario].append((doctor, area, agenda))
            
            # Encontrar horarios con múltiples doctores/áreas
            for horario, registros in horarios_duplicados.items():
                if len(registros) > 1:
                    doctores_unicos = set([r[0] for r in registros])
                    areas_unicas = set([r[1] for r in registros])
                    
                    if len(doctores_unicos) > 1 or len(areas_unicas) > 1:
                        print(f"{efector} - {dia} - {horario}:")
                        for doctor, area, agenda in registros:
                            print(f"   {doctor} ({area}) - {agenda}")
                        print()
    
    return casos_sospechosos

if __name__ == "__main__":
    # Cambiar al directorio correcto
    os.chdir(r"c:\Users\Rodri Paz\Desktop\normalizacion_hcsi")
    analizar_asignaciones_incorrectas()
