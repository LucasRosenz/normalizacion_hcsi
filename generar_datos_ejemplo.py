"""
Generador de datos de ejemplo para la aplicación de agendas médicas
"""
import pandas as pd
import random
from datetime import datetime, time
import os

def generar_datos_ejemplo():
    """Genera datos de ejemplo para demostrar la aplicación"""
    
    # Datos de ejemplo
    hospitales = [
        'Hospital de Clínicas San Isidro',
        'Hospital Materno Infantil',
        'Hospital Boulogne',
        'CAPS Villa Adelina',
        'CAPS Beccar',
        'CAPS San Isidro Labrador'
    ]
    
    especialidades = [
        'CARDIOLOGIA', 'PEDIATRIA', 'GINECOLOGIA', 'TRAUMATOLOGIA',
        'CLINICA MEDICA', 'NEUROLOGIA', 'DERMATOLOGIA', 'OFTALMOLOGIA',
        'UROLOGIA', 'ODONTOLOGIA', 'PSICOLOGIA', 'NUTRICION',
        'KINESIOLOGIA', 'ENDOCRINOLOGIA', 'GASTROENTEROLOGIA'
    ]
    
    doctores = [
        'DR. JUAN CARLOS MENDEZ', 'DRA. MARIA ELENA RODRIGUEZ',
        'DR. CARLOS ALBERTO GONZALEZ', 'DRA. ANA MARIA LOPEZ',
        'DR. RICARDO ANTONIO SILVA', 'DRA. PATRICIA BEATRIZ MARTINEZ',
        'DR. FERNANDO LUIS GARCIA', 'DRA. LAURA CRISTINA FERNANDEZ',
        'DR. MIGUEL ANGEL TORRES', 'DRA. CLAUDIA ALEJANDRA MORALES',
        'DR. PABLO EDUARDO HERRERA', 'DRA. SUSANA ELIZABETH CASTRO',
        'DR. ADRIAN MARCELO RUIZ', 'DRA. GABRIELA INES VARGAS',
        'DR. ROBERTO DANIEL MENDOZA'
    ]
    
    tipos_turno = ['PROGRAMADA', 'ESPONTANEA', 'URGENCIA', 'CONTROL', 'SOBRETURNO']
    
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    
    # Generar horarios típicos
    horarios = [
        ('08:00', '12:00'), ('08:30', '12:30'), ('09:00', '13:00'),
        ('14:00', '18:00'), ('14:30', '18:30'), ('15:00', '19:00'),
        ('07:00', '13:00'), ('13:00', '19:00'), ('08:00', '16:00'),
        ('16:00', '20:00'), ('10:00', '14:00'), ('11:00', '15:00')
    ]
    
    registros = []
    
    # Generar registros
    for _ in range(1000):  # Generar 1000 registros de ejemplo
        hospital = random.choice(hospitales)
        especialidad = random.choice(especialidades)
        doctor = random.choice(doctores)
        tipo_turno = random.choice(tipos_turno)
        dia = random.choice(dias_semana)
        hora_inicio, hora_fin = random.choice(horarios)
        
        # Generar nombre de agenda realista
        nombre_agenda = f"{especialidad} - {doctor} - {tipo_turno}"
        
        registro = {
            'nombre_original_agenda': nombre_agenda,
            'doctor': doctor,
            'area': especialidad,
            'tipo_turno': tipo_turno,
            'dia': dia,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'efector': hospital
        }
        
        registros.append(registro)
    
    return pd.DataFrame(registros)

def crear_archivo_ejemplo():
    """Crea el archivo de ejemplo si no existe"""
    if not os.path.exists("agendas_consolidadas.csv"):
        print("Generando archivo de datos de ejemplo...")
        df = generar_datos_ejemplo()
        df.to_csv("agendas_consolidadas.csv", index=False)
        print(f"Archivo creado con {len(df)} registros de ejemplo")
        return True
    return False

if __name__ == "__main__":
    crear_archivo_ejemplo()
