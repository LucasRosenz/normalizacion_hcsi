#!/usr/bin/env python3
"""
Script de debugging para analizar el procesamiento específico de CORONEL MARIEL
"""

import pandas as pd
import re
from typing import Dict, Optional

def es_titulo_agenda_debug(row: pd.Series) -> bool:
    """Función de debugging que replica la lógica de _es_titulo_agenda"""
    if len(row) < 3:
        return False
    
    if pd.isna(row.iloc[0]):
        return False
    
    if pd.notna(row.iloc[1]) or pd.notna(row.iloc[2]):
        return False
    
    primera_celda = str(row.iloc[0]).strip()
    
    if not primera_celda:
        return False
    
    palabras_medicas = ['PEDIATRIA', 'DR.', 'DRA.', 'DOCTOR', 'DOCTORA', 'LIC.', 'MEDICO', 'CLINICO']
    if any(palabra in primera_celda.upper() for palabra in palabras_medicas):
        return True
    
    if 'PERFIL PROFESIONAL' in primera_celda.upper():
        return True
    
    especialidades_medicas = [
        'CARDIOLOGIA', 'NEUROLOGIA', 'DERMATOLOGIA', 'GINECOLOGIA', 'OBSTETRICIA',
        'TRAUMATOLOGIA', 'OFTALMOLOGIA', 'OTORRINOLARINGOLOGIA', 'UROLOGIA',
        'NEUMOLOGIA', 'HEMATOLOGIA', 'ONCOLOGIA', 'REUMATOLOGIA', 'INFECTOLOGIA',
        'NEFROLOGIA', 'CLINICA MEDICA', 'MEDICINA INTERNA', 'CIRUGIA',
        'ANESTESIOLOGIA', 'PSIQUIATRIA', 'HEMOTERAPIA', 'KINESIOLOGIA',
        'LABORATORIO', 'NUTRICION', 'NEUROCIRUGÍA', 'MEDICINA LABORAL',
        'SERVICIO SOCIAL', 'DIABETOLOGIA', 'GUARDIA MEDICA', 'DIRECCION MEDICA',
        'ANATOMIA PATOLOGICA', 'CIRUGIA VASCULAR', 'NEUMONOLOGIA', 'ODONTOLOGIA',
        'ADOLESCENCIA', 'RADIOLOGIA', 'ENDODONCIA', 'PROTESIS',
        'ESTIMULACION TEMPRANA', 'FONOAUDIOLOGIA', 'TERAPIA OCUPACIONAL',
        'PSICOPEDAGOGIA', 'MUSICOTERAPIA', 'SALUD SEXUAL', 'MEDICINA PREVENTIVA',
        'RONDA SANITARIA', 'ENFERMERIA', 'VACUNACION', 'ECOGRAFIA', 'FARMACIA',
        'ESTADISTICA', 'TRABAJO SOCIAL', 'ADMINISTRACION', 'DIRECCION',
        'COORDINACION', 'SECRETARIA', 'ARCHIVO', 'INFORMES', 'CONSULTORIOS',
        'CONTROL', 'POST ALTA', 'DEMANDA', 'MEDICINA', 'CIRUGIA MAXILOFACIAL',
        'CIRUGIA PLASTICA', 'MEDICINA FAMILIAR', 'ATENCION', 'CONSULTORIO',
        'UNIDAD', 'SALA', 'TURNO', 'AGENDA', 'GUARDIA', 'EMERGENCIA'
    ]
    
    texto_upper = primera_celda.upper()
    if any(especialidad in texto_upper for especialidad in especialidades_medicas):
        return True
    
    return False

def es_fila_horarios_debug(row: pd.Series) -> bool:
    """Función de debugging que replica la lógica de _es_fila_horarios"""
    if pd.notna(row.iloc[0]) and str(row.iloc[0]).upper().strip() == 'DÍA':
        return False
    
    dias_semana = ['LUNES', 'MARTES', 'MIÉRCOLES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'SABADO', 'DOMINGO']
    
    if pd.notna(row.iloc[0]):
        primera_celda = str(row.iloc[0]).upper()
        if any(dia in primera_celda for dia in dias_semana):
            if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                return True
    
    return False

def debug_hospital_boulogne():
    """Analiza el procesamiento específico del Hospital Boulogne alrededor de CORONEL MARIEL"""
    df = pd.read_excel('datos/excel_originales/agendas_originales/Agendas activas Hospital Boulogne.xlsx', header=None)
    
    print("=== DEBUGGING PROCESAMIENTO HOSPITAL BOULOGNE ===")
    
    # Buscar las filas alrededor de CORONEL MARIEL TARDE
    coronel_tarde_idx = None
    for idx, row in df.iterrows():
        if 'NUTRICION TRATAMIENTO - TARDE - CORONEL MARIEL' in str(row.iloc[0]):
            coronel_tarde_idx = idx
            break
    
    if coronel_tarde_idx is None:
        print("No se encontró NUTRICION TRATAMIENTO - TARDE - CORONEL MARIEL")
        return
    
    print(f"CORONEL MARIEL TARDE encontrado en fila {coronel_tarde_idx}")
    
    # Simular el procesamiento línea por línea
    agenda_actual = ""
    encontro_encabezado_horarios = False
    
    start_idx = max(0, coronel_tarde_idx - 5)
    end_idx = min(len(df), coronel_tarde_idx + 15)
    
    print(f"\nSimulando procesamiento desde fila {start_idx} hasta {end_idx}:")
    
    for idx in range(start_idx, end_idx):
        row = df.iloc[idx]
        row_str = ' | '.join([str(cell) if pd.notna(cell) else 'nan' for cell in row[:5]])
        
        # Verificar encabezado de horarios
        es_encabezado = (pd.notna(row.iloc[0]) and str(row.iloc[0]).upper().strip() == 'DÍA' and
                        len(row) >= 3 and pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]))
        
        # Verificar si es título de agenda
        es_titulo = es_titulo_agenda_debug(row)
        
        # Verificar si es fila de horarios
        es_horarios = es_fila_horarios_debug(row)
        
        if es_encabezado:
            encontro_encabezado_horarios = True
            print(f"Fila {idx}: {row_str}")
            print(f"         -> ENCABEZADO DE HORARIOS detectado")
        elif es_titulo:
            agenda_actual = str(row.iloc[0]).strip()
            encontro_encabezado_horarios = False
            print(f"Fila {idx}: {row_str}")
            print(f"         -> NUEVA AGENDA: '{agenda_actual}'")
        elif es_horarios:
            procesaria = agenda_actual and encontro_encabezado_horarios
            print(f"Fila {idx}: {row_str}")
            print(f"         -> HORARIOS (agenda_actual='{agenda_actual}', encabezado={encontro_encabezado_horarios}, procesaría={procesaria})")
        else:
            print(f"Fila {idx}: {row_str}")
            print(f"         -> (ignorada)")
    
    print(f"\nEstado final:")
    print(f"agenda_actual: '{agenda_actual}'")
    print(f"encontro_encabezado_horarios: {encontro_encabezado_horarios}")

if __name__ == "__main__":
    debug_hospital_boulogne()
