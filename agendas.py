import pandas as pd
import os
import re
from typing import List, Dict, Tuple, Optional
import numpy as np

# Para exportar a Excel
try:
    import openpyxl
except ImportError:
    print("Advertencia: openpyxl no está instalado. La exportación a Excel no estará disponible.")
    print("Instale openpyxl con: pip install openpyxl")

class AgendaNormalizer:
    """
    Clase para normalizar y consolidar agendas médicas de múltiples centros de salud
    """
    
    def __init__(self):
        self.df_consolidado = pd.DataFrame(columns=[
            'agenda_id', 'nombre_original_agenda', 'doctor', 'area', 'tipo_turno', 
            'dia', 'hora_inicio', 'hora_fin', 'efector', 'ventanilla'
        ])
        
    def decodificar_caracteres_especiales(self, texto: str) -> str:
        """
        Decodifica caracteres especiales corruptos comunes en la base de datos.
        Esto corrige la codificación UTF-8 mal interpretada como Latin-1.
        """
        if not texto:
            return texto
            
        # Mapeo de caracteres corruptos a caracteres correctos
        # Basado en codificación UTF-8 mal interpretada como Latin-1
        correcciones = {
            # Casos más específicos PRIMERO - orden importante!
            'MUÃ\u2019OZ': 'MUÑOZ',  # MUÑOZ completo con comilla curva derecha (8217)
            'MUÃ\u2018OZ': 'MUÑOZ',  # MUÑOZ completo con comilla curva izquierda (8216)
            'MUÁ\u2018OZ': 'MUÑOZ',  # MUÑOZ ya parcialmente convertido (Á + comilla izquierda)
            'Á\u2018': 'Ñ',         # Á + comilla curva izquierda -> Ñ (para casos ya convertidos)
            'Ã\u2019': 'Ñ',         # Ã + comilla curva derecha -> Ñ
            'Ã\u2018': 'Ñ',         # Ã + comilla curva izquierda -> Ñ  
            'Ã_x008d_': 'Í',        # Para NOEMÍ
            'Ã"NICA': 'ÓNICA',      # Para VERÓNICA - patrón específico primero
            'Á\u201d': 'Ó',         # Á + comilla doble derecha (8221) -> Ó (para casos ya convertidos)
            'Á\u201c': 'Ó',         # Á + comilla doble izquierda (8220) -> Ó (para casos ya convertidos)
            'Ã\u201d': 'Ó',         # Ã + comilla doble derecha (8221) -> Ó
            'Ã\u201c': 'Ó',         # Ã + comilla doble izquierda (8220) -> Ó
            'Ã"': 'Ó',              # Ó mayúscula - debe ir antes que el patrón general
            'Í"': 'Ó',              # Corrección exacta: Í" -> Ó (ord 8220)
            'Ã_x0081_': 'Á',        # Corrección exacta: Ã_x0081_ -> Á
            
            # Patrones comunes de UTF-8 mal interpretado
            'Ã¡': 'á',   'Ã©': 'é',   'Ã­': 'í',   'Ã³': 'ó',   'Ãº': 'ú',    # Vocales con tilde minúsculas
            'Ã‰': 'É',   'Ãš': 'Ú',                                            # Vocales con tilde mayúsculas
            'Ã ': 'à',   'Ã¨': 'è',   'Ã¬': 'ì',   'Ã²': 'ò',   'Ã¹': 'ù',    # Vocales con acento grave
            'Ã¤': 'ä',   'Ã«': 'ë',   'Ã¯': 'ï',   'Ã¶': 'ö',   'Ã¼': 'ü',    # Vocales con diéresis
            'Ã¢': 'â',   'Ãª': 'ê',   'Ã®': 'î',   'Ã´': 'ô',   'Ã»': 'û',    # Vocales con circunflejo
            'Ã§': 'ç',   'Ã‡': 'Ç',                                           # C cedilla
            'Ã±': 'ñ',   'Ã\u00d1': 'Ñ',                                     # Eñe
            'Ã¢': 'â',   'Ãª': 'ê',   'Ã®': 'î',   'Ã´': 'ô',   'Ã»': 'û',    # Vocales con circunflejo
            'Ã§': 'ç',   'Ã‡': 'Ç',                                           # C cedilla
            'Ã±': 'ñ',   'Ã\u00d1': 'Ñ',                                     # Eñe
            
            # Patrones específicos de codificación hexadecimal
            '_x008d_': 'Í',         # Patrón hex para Í
            '_x0081_': 'Á',         # Patrón hex para Á
            
            # Casos específicos completos para nombres comunes
            'MUÃ_x0081_OZ': 'MUÑOZ',
            'MUÃOZ': 'MUÑOZ',
            'MUÃIÃ±OZ': 'MUÑOZ',    # Variante doble corrupción
            'JIMÃ©NEZ': 'JIMÉNEZ',
            'MÃ¡RQUEZ': 'MÁRQUEZ',
            'GÃ³MEZ': 'GÓMEZ',
            
            # Regla general AL FINAL - solo cuando no hay patrones más específicos
            'Ã': 'Á'               # Corrección general: Ã -> Á (SOLO cuando no hay patrones más específicos)
        }
        
        texto_corregido = texto
        # Aplicar correcciones en orden (más específicas primero)
        # Ordenar por longitud descendente para que los patrones más largos se apliquen primero
        for corrupto in sorted(correcciones.keys(), key=len, reverse=True):
            if corrupto in texto_corregido:
                texto_corregido = texto_corregido.replace(corrupto, correcciones[corrupto])
            
        return texto_corregido
    
    def extraer_componentes_agenda(self, nombre_agenda: str) -> Dict[str, str]:
        """
        Extrae doctor, área y tipo de turno del nombre de la agenda
        Maneja diferentes formatos posibles
        """
        if not nombre_agenda or pd.isna(nombre_agenda):
            return {'doctor': '', 'area': '', 'tipo_turno': ''}
            
        # PASO 1: Decodificar caracteres especiales corruptos
        nombre_limpio = self.decodificar_caracteres_especiales(str(nombre_agenda).strip())
        
        # Inicializar componentes
        doctor = ""
        area = ""
        tipo_turno = ""
        
        # Patrones para identificar áreas médicas
        areas_patterns = {
            'PEDIATRIA': r'\bPEDIATRIA\b',
            'CARDIOLOGIA': r'\bCARDIOLOGIA\b',
            'NEUROLOGIA': r'\bNEUROLOGIA\b',
            'GINECOLOGIA': r'\bGINECOLOGIA\b',
            'UROLOGIA': r'\bUROLOGIA\b',
            'DERMATOLOGIA': r'\bDERMATOLOGIA\b',
            'OFTALMOLOGIA': r'\bOFTALMOLOGIA\b',
            'TRAUMATOLOGIA': r'\bTRAUMATOLOGIA\b',
            'ENDOCRINOLOGIA': r'\bENDOCRINOLOGIA\b',
            'GASTROENTEROLOGIA': r'\bGASTROENTEROLOGIA\b',
            'NEUMOLOGIA': r'\bNEUMOLOGIA\b',
            'HEMATOLOGIA': r'\bHEMATOLOGIA\b',
            'ONCOLOGIA': r'\bONCOLOGIA\b',
            'REUMATOLOGIA': r'\bREUMATOLOGIA\b',
            'INFECTOLOGIA': r'\bINFECTOLOGIA\b',
            'NEFROLOGIA': r'\bNEFROLOGIA\b',
            'CLINICA MEDICA': r'\bCLINICA\s+MEDICA\b|\bMEDICO\s+CLINICO\b|\bMEDICA\s+CLINICA\b|\bMEDICO\s+CLINCO\b',
            'MEDICINA INTERNA': r'\bMEDICINA\s+INTERNA\b',
            'CIRUGIA': r'\bCIRUGIA\b',
            'ANESTESIOLOGIA': r'\bANESTESIOLOGIA\b',
            'PSIQUIATRIA': r'\bPSIQUIATRIA\b',
            'HEMOTERAPIA': r'\bHEMOTERAPIA\b',
            'KINESIOLOGIA': r'\bKINESIOLOGIA\b',
            'LABORATORIO': r'\bLABORATORIO\b',
            'NUTRICION': r'\bNUTRICION\b|\bNUTRICIONISTA\b',
            'NEUROCIRUGÍA': r'\bNEUROCIRUGIA\b',
            'MEDICINA LABORAL': r'\bMEDICINA\s+LABORAL\b',
            'SERVICIO SOCIAL': r'\bSERVICIO\s+SOCIAL\b|\bLIC\.\s*EN\s+TRABAJO\s+SOCIAL\b|\bTRABAJO\s+SOCIAL\b|\bTRABAJADORA\s+SOCIAL\b',
            'DIABETOLOGIA': r'\bDIABETOLOGIA\b',
            'GUARDIA MEDICA': r'\bGUARDIA\s+MEDICA\b(?!\s+(?:CLINICA|PEDIATRICA|PEDI))',
            'GUARDIA CLINICA': r'\bGUARDIA\s+M[EÉ]DICA\s+CL[IÍ]NICA\b',
            'GUARDIA PEDIATRICA': r'\bGUARDIA\s+M[EÉ]DICA\s+PEDI[AÁ]TRICA\b',
            'DIRECCION MEDICA': r'\bDIRECCION\s+MEDICA\b',
            'ANATOMIA PATOLOGICA': r'\bANATOMIA\s+PATOLOGICA\b|A\.\s*PATOLOGICA',
            'CIRUGIA VASCULAR': r'\bCIRUGIA\s+VASCULAR\b',
            'OTORRINOLARINGOLOGIA': r'\bOTORRINOLARINGOLOGIA\b',
            'NEUMONOLOGIA': r'\bNEUMONOLOGIA\b',
            'ODONTOLOGIA': r'\bODONTOLOGIA\b|\bODONTOLOGÍA\b|\bODONTOLGIA\b',
            'ADOLESCENCIA': r'\bADOLESCENCIA\b',
            'RADIOLOGIA': r'\bRADIOLOGIA\b',
            'ENDODONCIA': r'\bENDODONCIA\b',
            'PROTESIS': r'\bPROTESIS\b',
            'ESTIMULACION TEMPRANA': r'\bESTIMULACION\s+TEMPRANA\b',
            'PSICOLOGIA': r'\bPSICOLOG[AO]\b|\bLIC\.\s*EN\s+PSICOLOGIA\b|\bPSICOLOGIA\s+INFANTIL\b|\bPSICOLOGIA\s*(?:-\s*(?:LIC|DR|DRA))?\b',
            'OBSTETRICIA': r'\bOBSTETRICIA\b',
            'ECOGRAFIA': r'\bECOGRAFIAS?\b|\bDIAGNOSTICO\s+POR\s+IMAGENES\b',
            'PSICOFISICO': r'\bPSICOFISICO\b',
            'DIRECCION MEDICA': r'\bDIRECTOR\s+MEDICO\b|\bDIRECCION\s+MEDICA\b',
            'GENETICA': r'\bGENETICA\b|\bGENÉTICA\b',
            'TRACTO GENITAL INFERIOR': r'\bTRACTO\s+GENITAL\s+INFERIOR\b',
            'MEDICINA GENERAL': r'\bGENERALISTA\b|\bMEDICINA\s+GENERAL\b',
            'MEDICINA FAMILIAR': r'\bMEDICINA\s+FAMILIAR\b',
            'SALUD SEXUAL': r'\bSALUD\s+SEXUAL\b',
            'MEDICINA PREVENTIVA': r'\bCHARLA\s+TABAQUISMO\b|\bRONDA\s+SANITARIA\b|\bMEDICINA\s+PREVENTIVA\b',
            'MUSICOTERAPIA': r'\bMUSICOTERAPIA\b',
            'FONOAUDIOLOGIA': r'\bFONOAUDIOLOGIA\b',
            'TERAPIA OCUPACIONAL': r'\bTERAPIA\s+OCUPACIONAL\b',
            'PSICOPEDAGOGIA': r'\bPSICOPEDAGOGIA\b',
            'ENFERMERIA': r'\bENFERMERIA\b|\bENFERMERÍA\b|\bLIC\.\s*EN\s+ENFERMERIA\b|\bLIC\.\s*EN\s+ENFERMERÍA\b|\bENFERMER[AO]\b'
        }
        
        # Buscar área médica
        texto_upper = nombre_limpio.upper()
        for area_nombre, pattern in areas_patterns.items():
            if re.search(pattern, texto_upper):
                area = area_nombre
                break
        
        # Buscar doctor - patrones mejorados
        doctor_patterns = [
            # Patrón específico para "ESPECIALIDAD - DRA/DR NOMBRE APELLIDO - EVENTUAL" (solo EVENTUAL)
            r'\b(?:ODONTOLOGIA|PEDIATRIA)\s+(?:ADULTOS?|PEDIATRIA|INFANTIL)?\s*-\s*(DRA?\.\s*[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)+)\s*-\s*EVENTUAL\s*$',
            # Patrón específico para "ESPECIALIDAD - DRA/DR NOMBRE APELLIDO - TIPO" con EVENTUAL ESPONTANEA
            r'\b(?:ODONTOLOGIA|PEDIATRIA)\s+(?:ADULTOS?|PEDIATRIA|INFANTIL)?\s*-\s*(DRA?\.\s*[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)+)\s*-\s*(?:EVENTUAL\s+)?(?:ESPONTANEA|PROGRAMADA)',
            # Patrón para profesiones que incluyen DR/DRA en el medio - PROFESION - DRA/DR NOMBRE - ACTIVIDAD (opcional)
            r'\b(?:PSICOLOG[OA]|NUTRICIONISTA|KINESIOLOGO|FONOAUDIOLOGO)\s*-\s*(DRA?\.\s*[A-Z].+?\s+.+?|DRA?\s+[A-Z].+?\s+.+?)(?:\s*-\s*\w+.*|\s*$)',
            # Patrón específico para ESTIMULACION TEMPRANA - DRA/DR NOMBRE (maneja caracteres corruptos)
            r'\bESTIMULACION\s+TEMPRANA\s*-\s*(DRA?\.\s*[A-Z].+?\s+.+?)(?:\s*$|\s*-)',
            # Patrón para profesiones seguido de nombre - NUTRICIONISTA/KINESIOLOGO/etc - NOMBRE - TIPO  
            r'\b(?:NUTRICIONISTA|KINESIOLOGO|FONOAUDIOLOGO|TRABAJADOR[A]?\s+SOCIAL|TRABAJO\s+SOCIAL|PSICOLOG[OA])[\.\s]*[-\.\s]\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)+)\s*(?:-\s*(?:GENERAL|TRATAMIENTO|PROGRAMADA|ESPONTANEA|ESPONTÁNEA|PAP|CAI|CONTROL|URGENCIA|SOBRETURNO|REUNION\s+DE\s+EQUIPO)|\s*$)',
            # Patrón para DRA/DR seguido del nombre - detener antes de palabras clave (PRESERVAR DR/DRA con o sin punto)
            r'\b(DRA?\.\s*[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)*)\s*(?:-\s*(?:EVENTUAL\s+)?(?:PROGRAMADA|ESPONTANEA|ESPONTÁNEA|GENERAL|TRATAMIENTO|PAP|CAI|RECITADOS|RECIEN\s+NACIDOS|EMBARAZADAS|CONTROL|URGENCIA|SOBRETURNO|DIU|IMPLANTE|EXTRACCION|COLOCACION|AGENDA\s+BIS|REUNION\s+EQUIPO)|\s*$)',
            # Patrón para DRA/DR SIN punto seguido del nombre (PRESERVAR DR/DRA sin punto)
            r'\b(DRA?\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)*)\s*(?:-\s*(?:EVENTUAL\s+)?(?:PROGRAMADA|ESPONTANEA|ESPONTÁNEA|GENERAL|TRATAMIENTO|PAP|CAI|RECITADOS|RECIEN\s+NACIDOS|EMBARAZADAS|CONTROL|URGENCIA|SOBRETURNO|DIU|IMPLANTE|EXTRACCION|COLOCACION|AGENDA\s+BIS|REUNION\s+EQUIPO)|\s*$)',
            # Patrón para DOCTOR/DOCTORA seguido del nombre (PRESERVAR DOCTOR/DOCTORA)
            r'\b(DOCTOR[A]?\s+[A-ZÁÉÍÓÚÑ].+?)(?:\s*-\s*(?:EVENTUAL\s+)?(?:PROGRAMADA|ESPONTANEA|ESPONTÁNEA|GENERAL|TRATAMIENTO|PAP|CAI|RECITADOS|RECIEN\s+NACIDOS|EMBARAZADAS|CONTROL|URGENCIA|SOBRETURNO|DIU|IMPLANTE|EXTRACCION|COLOCACION|AGENDA\s+BIS|REUNION\s+EQUIPO)|\s*$)',
            # Patrón específico para formato "APELLIDO ,NOMBRE" después de tipo de turno
            r'-\s*(?:A\s+LA\s+BREVEDAD|URGENCIA|PROGRAMADA|ESPONTANEA|ESPONTÁNEA)\s*-\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+\s*,\s*[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)',
            # Patrón específico para LIC. EN PSICOLOGIA - buscar el nombre después de PSICOLOGIA
            r'\bLIC\.\s*EN\s+PSICOLOGIA\s+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ_x0-9]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ_x0-9]+)*)',
            # Patrón específico para LIC. EN TRABAJO SOCIAL - buscar al final, con patrón más flexible
            r'\bLIC\.\s*EN\s+TRABAJO\s+SOCIAL\s+(.+)$',
            # Patrón específico para LIC.EN NUTRICION - buscar después del guión y TRATAMIENTO, con patrón más flexible
            r'\bLIC\.EN\s+NUTRICION\s*-\s*TRATAMIENTO\s*-\s*(.+)$',
            # Patrón específico para LIC. EN KINESIOLOGIA - buscar el nombre después de KINESIOLOGIA
            r'\bLIC\.\s*EN\s+KINESIOLOGIA\s+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ_x0-9]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ_x0-9]+)*)',
            # Patrón específico para LIC. EN NUTRICION - buscar el nombre después de NUTRICION
            r'\bLIC\.\s*EN\s+NUTRICION\s+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ_x0-9]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ_x0-9]+)*)',
            # Patrón general para LIC. seguido directamente del nombre (sin especialidad)
            r'\bLIC\.\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)*)',
            # Patrón para nombres al final después de guión - solo nombres de personas (DEBE IR AL FINAL)
            r'[-\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)$',
        ]
        
        for i, pattern in enumerate(doctor_patterns):
            match = re.search(pattern, nombre_limpio)
            if match:
                nombre_candidato = match.group(1).strip()
                # Verificar que no sea una especialidad o palabra clave, pero permitir nombres largos
                palabras_excluir = [
                    'PSICOLOGIA', 'NUTRICION', 'TRABAJO SOCIAL', 'KINESIOLOGIA', 
                    'TRATAMIENTO', 'GENERAL', 'PAP', 'ESPONTANEA', 'PROGRAMADA',
                    'EN PSICOLOGIA', 'EN NUTRICION', 'EN TRABAJO', 'EN KINESIOLOGIA',
                    'LICENCIADA', 'LICENCIADO', 'MEDICO', 'MEDICA', 'AGENDA SÁBADOS',
                    'AGENDA SABADOS', 'RESIDENTE', 'AGENDA', 'ESPONTANEA', 'AGENDA BIS',
                    'BIS', 'DIU', 'IMPLANTE', 'EXTRACCION', 'COLOCACION', 'REUNION EQUIPO',
                    'ADULTOS', 'ADULTO', 'INFANTIL', 'INFANTILES', 'NINOS', 'NIÑOS',
                    'ADOLESCENTES', 'DISCAPACIDAD', 'REHABILITACION', 'REHABILITACIÓN',
                    'PEDIATRICA', 'PEDIÁTRICA', 'CLINICA', 'CLÍNICA', 'EXTERNA',
                    'CONSULTORIO', 'SALA', 'BOX', 'QUIROFANO', 'QUIRÓFANO',
                    'ECG', 'EKG', 'RX', 'LAB', 'LABORATORIO', 'RADIOLOGIA', 'ECOGRAFIA', 'TAC', 'RMN'
                ]
                
                # Verificar si es un consultorio/sala/ubicación con número o palabra identificativa
                es_ubicacion = re.match(r'^(?:CONSULTORIO|SALA|BOX|QUIROFANO|QUIRÓFANO|PISO|PLANTA)\s*(?:\d+|[A-Z]|\w+)$', nombre_candidato.upper().strip())
                
                # Verificar si contiene solo números o palabras que indican ubicación
                es_solo_numero = re.match(r'^\d+$', nombre_candidato.strip())
                
                # Verificar patrones de ubicación específicos
                contiene_ubicacion = re.search(r'\b(?:CONSULTORIO|SALA|BOX|QUIROFANO|QUIRÓFANO|PISO|PLANTA)\b', nombre_candidato.upper())
                
                # Solo procesar si no es una ubicación
                if nombre_candidato.strip() and len(nombre_candidato.strip()) > 2 and not es_ubicacion and not es_solo_numero and not contiene_ubicacion:
                    # Verificar que no contenga palabras clave (no solo coincidencias exactas)
                    es_palabra_clave = any(palabra in nombre_candidato.upper().strip() for palabra in palabras_excluir)
                    # Verificar que no sea exactamente una palabra clave
                    es_exactamente_palabra_clave = any(nombre_candidato.upper().strip() == palabra for palabra in palabras_excluir)
                    
                    if not es_palabra_clave and not es_exactamente_palabra_clave:
                        # Limpiar palabras específicas del final del nombre
                        nombre_limpio = re.sub(r'\s*-\s*(DIU|IMPLANTE|EXTRACCION|COLOCACION|AGENDA\s+BIS|REUNION\s+EQUIPO)\s*$', '', nombre_candidato, flags=re.IGNORECASE)
                        
                        # Si ya contiene DR./DRA/DOCTOR/DOCTORA al inicio, preservarlo tal como está
                        if re.match(r'^(DRA?\.\s*|DRA?\s+|DOCTOR[A]?\s+)', nombre_limpio, re.IGNORECASE):
                            doctor = nombre_limpio.strip()
                        # Procesar formato "APELLIDO ,NOMBRE" y convertir a "NOMBRE APELLIDO"
                        elif ',' in nombre_limpio:
                            partes = nombre_limpio.split(',')
                            if len(partes) == 2:
                                apellido = partes[0].strip()
                                nombre = partes[1].strip()
                                doctor = f"{nombre} {apellido}"
                            else:
                                doctor = nombre_limpio.strip()
                        else:
                            doctor = nombre_limpio.strip()
                        break
        
        # Buscar tipo de turno - patrones mejorados con orden de prioridad
        # IMPORTANTE: Verificar primero patrones más específicos como "A LA BREVEDAD"
        if re.search(r'\bA\s+LA\s+BREVEDAD\b', texto_upper):
            tipo_turno = 'A LA BREVEDAD'
        else:
            tipo_patterns = {
                'GUARDIA': r'\bGUARDIA\b|\bGUARDIA\s+MEDICA\b|\bGUARDIAS\b',
                'EVENTUAL ESPONTANEA': r'\bEVENTUAL\s+ESPONTANEA\b|\bEVENTUAL\s+ESPONTÁNEA\b',
                'EVENTUAL': r'\bEVENTUAL\b',
                'CAI/Espontánea': r'\bESPONTANEA\b|\bESPONTÁNEA\b|\bESPONTÃ_x0081_NEA\b|\bCAI\b',
                'URGENCIA': r'\bURGENCIA\b|\bURGENTE\b',
                'PROGRAMADA': r'\bPROGRAMADA\b|\bTURNO\s+PROGRAMADO\b|\bPROGRAMADO\b',
                'SOBRETURNO': r'\bSOBRETURNO\b|\bSOBRETURNOS\b',
                'CONTROL': r'\bCONTROL\b',
                'INTERCONSULTA': r'\bINTERCONSULTA\b',
                'CONSULTA EXTERNA': r'\bCONSULTA\s+EXTERNA\b|\bEXTERNA\b',
                'TRATAMIENTO': r'\bTRATAMIENTO\b',
                'GENERAL': r'\bGENERAL\b',
                'PAP': r'\bPAP\b',
                'REUNION DE EQUIPO': r'\bREUNION\s+DE\s+EQUIPO\b|\bREUNIÓN\s+DE\s+EQUIPO\b'
            }
            
            for tipo_nombre, pattern in tipo_patterns.items():
                if re.search(pattern, texto_upper):
                    tipo_turno = tipo_nombre
                    break
        
        # Limpiar campo doctor - reglas de corrección manual
        # Corrección #1: Los consultorios no son doctores, sino ubicaciones físicas
        if doctor and re.search(r'CONSULTORIO\s+\d+', doctor, re.IGNORECASE):
            doctor = ""
        
        # Corrección #3: Procedimientos/siglas médicas y términos técnicos no son doctores
        procedimientos_medicos = [
            'ECG', 'EKG', 'RX', 'LAB', 'LABORATORIO', 'RADIOLOGIA', 'ECOGRAFIA', 'TAC', 'RMN', 'PREOCUPACIONAL',
            'QUIROFANO', 'CURACIONES', 'PLASTICA', 'TORAX', 'ADULTOS', 'NIÑOS HSI', 'GENERAL DOS', 'GENERAL UNO',
            'CABEZA Y CUELLO DOS', 'CABEZA Y CUELLO UNO', 'COLOPROCTOLOGIA UNO', 'COLOPROCTOLOGIA DOS',
            '173 TECNICO', '200 TECNICO', '233 TECNICO', '122 TECNICO', 'CARDIO RESIDENTES', 'DIABETOLOGIA PRODIABA'
        ]
        if doctor and any(proc.upper() == doctor.upper().strip() for proc in procedimientos_medicos):
            doctor = ""
        
        return {
            'doctor': doctor,
            'area': area,
            'tipo_turno': tipo_turno
        }
    
    def procesar_archivo_excel(self, archivo_path: str, efector: str) -> pd.DataFrame:
        """
        Procesa un archivo Excel con formato de agenda no tabular
        """
        try:
            # Leer el archivo Excel sin encabezados
            df = pd.read_excel(archivo_path, header=None)
            
            # Detectar si es el formato especial del Hospital Odontológico
            if 'Hospital Odontologico' in archivo_path:
                return self._procesar_formato_odontologico(df, efector)
            
            registros = []
            agenda_actual = ""
            agenda_id_counter = 0  # Contador para generar IDs únicos de agenda
            agenda_actual_id = ""
            encontro_encabezado_horarios = False
            
            for idx, row in df.iterrows():
                # Verificar si es una fila de encabezado de horarios "Día | Hora inicio | Hora fin"
                if (pd.notna(row.iloc[0]) and str(row.iloc[0]).upper().strip() == 'DÍA' and
                    len(row) >= 3 and pd.notna(row.iloc[1]) and pd.notna(row.iloc[2])):
                    encontro_encabezado_horarios = True
                    continue
                
                # Verificar si es una fila de agenda (contiene información del doctor/área)
                if self._es_titulo_agenda(row):
                    # Extraer el nombre de la agenda de la primera celda y decodificar caracteres especiales
                    agenda_actual = self.decodificar_caracteres_especiales(str(row.iloc[0]).strip())
                    agenda_id_counter += 1
                    # Generar ID único que incluye el efector y un contador secuencial
                    agenda_actual_id = f"{efector}_{agenda_id_counter:03d}_{agenda_actual}"
                    encontro_encabezado_horarios = False  # Reset para la nueva agenda
                    continue
                
                # Verificar si es una fila de horarios (contiene día, hora inicio, hora fin)
                if self._es_fila_horarios(row):
                    # Solo procesar horarios si tenemos una agenda actual Y hemos visto un encabezado
                    if agenda_actual and encontro_encabezado_horarios:
                        registro = self._extraer_datos_horarios(row, agenda_actual, efector, agenda_actual_id)
                        if registro:
                            registros.append(registro)
            
            return pd.DataFrame(registros)
            
        except Exception as e:
            print(f"Error procesando {archivo_path}: {e}")
            return pd.DataFrame()
    
    def _es_titulo_agenda(self, row: pd.Series) -> bool:
        """
        Determina si una fila es un título de agenda
        CRITERIO PURAMENTE ESTRUCTURAL: Solo detecta títulos de agenda cuando:
        - La primera columna tiene contenido (no es nan)
        - La segunda columna está vacía (es nan)
        - La tercera columna está vacía (es nan)
        - La primera celda no está vacía después de hacer strip()
        
        Este criterio es independiente del contenido y se basa únicamente en la estructura.
        """
        # Verificar que tengamos al menos 3 columnas
        if len(row) < 3:
            return False
        
        # CRITERIO ESTRICTO: Primera columna con contenido, segunda y tercera vacías
        if pd.isna(row.iloc[0]):
            return False
        
        # Verificar que las columnas 2 y 3 estén vacías (nan)
        if pd.notna(row.iloc[1]) or pd.notna(row.iloc[2]):
            return False
        
        primera_celda = str(row.iloc[0]).strip()
        
        # Si la primera celda está vacía después de strip(), no es un título
        if not primera_celda:
            return False
        
        # Si cumple con el formato estructural "NOMBRE AGENDA, nan, nan", es un título
        return True
    
    def _es_fila_horarios(self, row: pd.Series) -> bool:
        """Determina si una fila contiene información de horarios"""
        # Si la primera celda es "Día" (encabezado de tabla), NO es fila de horarios
        if pd.notna(row.iloc[0]) and str(row.iloc[0]).upper().strip() == 'DÍA':
            return False
        
        # Buscar días de la semana en la primera columna
        dias_semana = ['LUNES', 'MARTES', 'MIÉRCOLES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'SABADO', 'DOMINGO']
        
        if pd.notna(row.iloc[0]):
            primera_celda = str(row.iloc[0]).upper()
            if any(dia in primera_celda for dia in dias_semana):
                # Verificar que también tenga horarios en las columnas 2 y 3
                if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                    return True
        
        return False
    
    def _extraer_datos_horarios(self, row: pd.Series, agenda_actual: str, efector: str, agenda_id: Optional[str] = None) -> Optional[Dict]:
        """Extrae datos de horarios de una fila"""
        try:
            # MANTENER el nombre de la agenda EXACTAMENTE como está (sin limpiar)
            # Solo limpiar los componentes extraídos
            
            # Extraer componentes de la agenda (usando versión limpia para procesamiento)
            agenda_limpia_para_procesamiento = self.limpiar_texto(agenda_actual)
            componentes = self.extraer_componentes_agenda(agenda_limpia_para_procesamiento)
            
            # Extraer día de la primera columna
            dia = ""
            if pd.notna(row.iloc[0]):
                dia_raw = str(row.iloc[0]).strip()
                # Normalizar días de la semana
                dia_mapping = {
                    'LUNES': 'Lunes',
                    'MARTES': 'Martes', 
                    'MIÉRCOLES': 'Miércoles',
                    'MIERCOLES': 'Miércoles',
                    'JUEVES': 'Jueves',
                    'VIERNES': 'Viernes',
                    'SÁBADO': 'Sábado',
                    'SABADO': 'Sábado',
                    'SÁB': 'Sábado',
                    'DOMINGO': 'Domingo'
                }
                dia = dia_mapping.get(dia_raw.upper(), dia_raw)
            
            # Extraer hora inicio (segunda columna)
            hora_inicio = ""
            if pd.notna(row.iloc[1]):
                hora_raw = str(row.iloc[1]).strip()
                # Si es un tiempo de pandas, convertirlo
                try:
                    if hasattr(row.iloc[1], 'time'):
                        hora_inicio = row.iloc[1].time().strftime('%H:%M')
                    else:
                        # Buscar patrón de hora
                        match = re.search(r'(\d{1,2}):(\d{2})', hora_raw)
                        if match:
                            hora_inicio = f"{match.group(1).zfill(2)}:{match.group(2)}"
                except:
                    pass
            
            # Extraer hora fin (tercera columna)
            hora_fin = ""
            if pd.notna(row.iloc[2]):
                hora_raw = str(row.iloc[2]).strip()
                try:
                    if hasattr(row.iloc[2], 'time'):
                        hora_fin = row.iloc[2].time().strftime('%H:%M')
                    else:
                        # Buscar patrón de hora
                        match = re.search(r'(\d{1,2}):(\d{2})', hora_raw)
                        if match:
                            hora_fin = f"{match.group(1).zfill(2)}:{match.group(2)}"
                except:
                    pass
            
            # Crear registro si tenemos información básica
            if dia and (hora_inicio or hora_fin):
                # Para otros centros: preservar el formato original del doctor (sin limpiar)
                doctor_original = componentes['doctor']  # Mantener formato original
                
                registro = {
                    'nombre_original_agenda': agenda_actual,  # SIN LIMPIAR - exactamente como está
                    'doctor': doctor_original,  # SIN LIMPIAR - exactamente como está extraído
                    'area': self.limpiar_texto(componentes['area']),
                    'tipo_turno': self.limpiar_texto(componentes['tipo_turno']),
                    'dia': dia,
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'efector': efector,
                    'ventanilla': ''  # Nueva variable Ventanilla (vacía por ahora)
                }
                
                # Asignar ventanilla para Hospital Materno
                if efector == 'Hospital Materno':
                    registro['ventanilla'] = self.asignar_ventanilla_hospital_materno(componentes['area'])
                
                # Agregar agenda_id si se proporciona
                if agenda_id:
                    registro['agenda_id'] = agenda_id
                
                return registro
        
        except Exception as e:
            print(f"Error extrayendo datos de horarios: {e}")
        
        return None
    
    def procesar_directorio(self, directorio: str) -> pd.DataFrame:
        """
        Procesa todos los archivos de agenda en un directorio
        """
        archivos_procesados = []
        
        # Primero, buscar y procesar el archivo HCSI CSV (si existe)
        archivo_hcsi = os.path.join(os.path.dirname(directorio), "Agendas HCSI.csv")
        if os.path.exists(archivo_hcsi):
            print(f"Procesando archivo HCSI CSV: {os.path.basename(archivo_hcsi)}")
            df_hcsi = self._procesar_archivo_hcsi_csv(archivo_hcsi)
            if not df_hcsi.empty:
                archivos_procesados.append(df_hcsi)
                print(f"  - {len(df_hcsi)} registros extraídos del HCSI")
        
        # Luego procesar los archivos Excel normales
        for archivo in os.listdir(directorio):
            if archivo.endswith(('.xlsx', '.xls')):
                # Excluir archivos HCSI ya que tienen formato diferente
                if 'HCSI' in archivo.upper():
                    print(f"Saltando archivo HCSI: {archivo} (formato diferente)")
                    continue
                
                archivo_path = os.path.join(directorio, archivo)
                
                # Inferir efector del nombre del archivo
                efector = self._inferir_efector(archivo)
                
                print(f"Procesando: {archivo}")
                df_archivo = self.procesar_archivo_excel(archivo_path, efector)
                
                if not df_archivo.empty:
                    archivos_procesados.append(df_archivo)
                    print(f"  - {len(df_archivo)} registros extraídos")
        
        # Consolidar todos los archivos
        if archivos_procesados:
            df_consolidado = pd.concat(archivos_procesados, ignore_index=True)
            
            # Aplicar normalizaciones post-procesamiento
            # Corrección #2: Normalizar días de la semana (corregir "Sáb" -> "Sábado")
            df_consolidado['dia'] = df_consolidado['dia'].replace({'Sáb': 'Sábado'})
            
            return df_consolidado
        
        return pd.DataFrame()
    
    def _procesar_archivo_hcsi_csv(self, archivo_path: str) -> pd.DataFrame:
        """
        Procesa el archivo CSV del HCSI
        que tiene formato tabular con columnas: Especialidad, Profesional, Dia, Horario, TipoTurno
        """
        try:
            df = pd.read_csv(archivo_path)
            registros = []
            agenda_id_counter = 0
            
            print(f"Procesando {len(df)} registros del HCSI...")
            
            for idx, row in df.iterrows():
                # Saltar filas con datos faltantes esenciales
                if pd.isna(row.get('Especialidad')) or pd.isna(row.get('Dia')) or pd.isna(row.get('Horario')):
                    continue
                
                agenda_id_counter += 1
                
                # Extraer datos básicos
                especialidad = str(row['Especialidad']).strip()
                profesional = str(row.get('Profesional', '')).strip() if pd.notna(row.get('Profesional')) else ""
                dia_raw = str(row['Dia']).strip()
                horario_raw = str(row['Horario']).strip()
                tipo_turno_raw = str(row.get('TipoTurno', '')).strip() if pd.notna(row.get('TipoTurno')) else ""
                subespecialidad = str(row.get('Subespecialidad', '')).strip() if pd.notna(row.get('Subespecialidad')) else ""
                
                # Mapear días de la semana
                dia_mapping = {
                    'LUN': 'Lunes', 'LUNES': 'Lunes',
                    'MAR': 'Martes', 'MARTES': 'Martes', 
                    'MIE': 'Miércoles', 'MIERCOLES': 'Miércoles', 'MIÉRCOLES': 'Miércoles',
                    'JUE': 'Jueves', 'JUEVES': 'Jueves',
                    'VIE': 'Viernes', 'VIERNES': 'Viernes',
                    'SAB': 'Sábado', 'SABADO': 'Sábado', 'SÁBADO': 'Sábado', 'SÁB': 'Sábado',
                    'DOM': 'Domingo', 'DOMINGO': 'Domingo'
                }
                dia = dia_mapping.get(dia_raw.upper(), dia_raw)
                
                # Procesar horario (formato: "08:00 a 12:00" o "13:00 a 18:00")
                hora_inicio = ""
                hora_fin = ""
                if " a " in horario_raw:
                    partes_horario = horario_raw.split(" a ")
                    if len(partes_horario) == 2:
                        hora_inicio = partes_horario[0].strip()
                        hora_fin = partes_horario[1].strip()
                
                # Crear nombre de agenda combinando especialidad + subespecialidad + profesional
                nombre_agenda_partes = [especialidad]
                if subespecialidad and subespecialidad != "GENERAL":
                    nombre_agenda_partes.append(subespecialidad)
                if profesional:
                    nombre_agenda_partes.append(profesional)
                
                nombre_agenda = " - ".join(nombre_agenda_partes)
                
                # Generar ID único
                agenda_id = f"HCSI_{agenda_id_counter:03d}_{especialidad}"
                
                # Normalizar tipo de turno - USAR SIEMPRE el valor de la base de datos HCSI
                tipo_turno_normalizado = ""
                if tipo_turno_raw.upper() == "PROGRAMADO":
                    tipo_turno_normalizado = "PROGRAMADA"
                elif tipo_turno_raw.upper() in ["ESPONTANEO", "ESPONTÁNEO"]:
                    tipo_turno_normalizado = "CAI/Espontánea"
                else:
                    tipo_turno_normalizado = tipo_turno_raw.upper()
                
                # Limpiar nombre del profesional - Para HCSI: usar directamente sin normalizar
                doctor_limpio = ""
                if profesional:
                    # Para HCSI: Tomar el profesional exactamente como está en la base de datos
                    doctor_limpio = profesional.strip()
                
                # Crear registro
                registro = {
                    'agenda_id': agenda_id,
                    'nombre_original_agenda': nombre_agenda,
                    'doctor': doctor_limpio,
                    'area': especialidad.upper(),
                    'tipo_turno': tipo_turno_normalizado,
                    'dia': dia,
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'efector': 'HCSI',
                    'ventanilla': ''  # Nueva variable Ventanilla (vacía por ahora)
                }
                
                registros.append(registro)
            
            # Crear DataFrame
            df = pd.DataFrame(registros)
            
            # Asignar ventanillas para Hospital Materno (HCSI incluye Hospital Materno)
            # Nota: En los datos CSV, algunos efectores pueden ser Hospital Materno
            for idx, row in df.iterrows():
                if 'MATERNO' in str(row.get('efector', '')).upper():
                    df.at[idx, 'ventanilla'] = self.asignar_ventanilla_hospital_materno(row['area'])
            
            return df
            
        except Exception as e:
            print(f"Error procesando archivo HCSI CSV: {e}")
            return pd.DataFrame()

    def _inferir_efector(self, nombre_archivo: str) -> str:
        """Infiere el nombre del efector desde el nombre del archivo"""
        nombre_base = os.path.splitext(nombre_archivo)[0]
        nombre_upper = nombre_base.upper()
        
        # Patrones específicos - ORDEN IMPORTANTE: más específicos primero
        if 'HCSI' in nombre_upper:
            return 'HCSI'
        elif 'HOSPITAL BOULOGNE' in nombre_upper:
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
        elif 'CAPS BAJO BOULOGNE' in nombre_upper or 'CAPS BAJO BOULOGNE' in nombre_upper:
            return 'CAPS Bajo Boulogne'
        elif 'CAPS DIAGONAL SALTA' in nombre_upper:
            return 'CAPS Diagonal Salta'
        elif 'CAPS SAN ISIDRO LABRADOR' in nombre_upper:
            return 'CAPS San Isidro Labrador'
        elif 'CAPS SAN PANTALEON' in nombre_upper:
            return 'CAPS San Pantaleón'
        elif 'CAPS MARTINEZ' in nombre_upper:
            return 'CAPS Martínez'
        elif 'CAPS VILLA ADELINA' in nombre_upper:
            return 'CAPS Villa Adelina'
        elif 'CENTRO EL NIDO' in nombre_upper:
            return 'Centro El Nido'
        elif 'CAPS' in nombre_upper:
            return 'CAPS'  # Fallback genérico
        elif 'CENTRO' in nombre_upper:
            return 'Centro de Salud'
        
        return nombre_base
    
    def asignar_ventanilla_hospital_materno(self, area: str) -> str:
        """
        Asigna ventanilla según el área médica para Hospital Materno
        Basado en el archivo ventanillas_materno.xlsx
        """
        if not area:
            return ""
        
        area_upper = area.upper().strip()
        
        # Ventanilla PEDIATRIA
        ventanilla_a = [
            'PEDIATRIA', 'ADOLESCENCIA', 'ALERGIA', 'ALTO RIESGO', 'DEGLUCION',
            'CARDIOLOGIA INFANTIL', 'ENDOCRINOLOGIA', 'ESPEIROMETRIA', 'FONOAUDIOLOGIA',
            'GASTROENTEROLOGIA', 'HEPATOLOGIA', 'GENETICA INFANTIL', 'INFANTO JUVENIL',
            'INFECTOLOGIA INFANTIL', 'MEDIANO RIESGO', 'NEFROLOGIA', 'NEUMOLOGIA',
            'NEUROLOGIA', 'ELECTROENCEFALOGRAMA', 'NUTRICION', 'OAES- PEAT',
            'OFTAMOLOGIA', 'RESIDENTES PEDIATRIA (POST ALTA)', 'RESIDENTES NIÑO SANO',
            'PSICOLOGIA', 'PSIQUIATRIA', 'TBC (TUBERCULOSIS)'
        ]
        
        # Ventanilla GUARDIA VIEJA
        ventanilla_b = [
            'GUARDIA VIEJA', 'TRAUMATOLOGIA', 'DERMATOLOGIA', 'CIRUGIA', 'UROLOGIA',
            'CRANEO FACIAL', 'OTORRINO', 'AUDIOMETRIA', 'KINESIOLOGIA', 'CIRUGIA PLASTICA'
        ]
        
        # Ventanilla OBSTETRICIA
        ventanilla_c = [
            'OBSTETRICIA', 'INFECTOLOGIA ADULTOS', 'TRACTO GENITAL (PAP)', 'CARDIOLOGIA',
            'PUERPERIO', 'OBSTETRICIA ALTO RIESGO', 'OBSTETRICIA BAJO RIESGO',
            'RESIDENTES 1º VEZ', 'GINECOLOGIA QUIRURGICA', 'GENETICA', 'INFANTO JUVENIL',
            'ELECTROCARDIOGRAMA', 'PSICOLOGIA', 'ODONTOLOGIA', 'NUTRICION',
            'DIABETOLOGIA', 'PLANIFICACION FAMILIAR', 'HEMOTERAPIA'
        ]
        
        # Verificar asignación de ventanilla
        if area_upper in ventanilla_a:
            return "PEDIATRIA"
        elif area_upper in ventanilla_b:
            return "GUARDIA VIEJA"
        elif area_upper in ventanilla_c:
            return "OBSTETRICIA"
        else:
            return ""  # No asignada
    
    def exportar_consolidado(self, df: pd.DataFrame, archivo_salida: str = 'agendas_consolidadas.csv'):
        """Exporta el DataFrame consolidado a CSV y Excel con agenda_id al final en Excel"""
        try:
            # Exportar a CSV (orden original)
            df.to_csv(archivo_salida, index=False, encoding='utf-8')
            print(f"Archivo CSV exportado a: {archivo_salida}")
            
            # Para Excel: reorganizar columnas con agenda_id al final
            df_excel = df.copy()
            if 'agenda_id' in df_excel.columns:
                # Crear lista de columnas sin agenda_id
                columnas_sin_agenda_id = [col for col in df_excel.columns if col != 'agenda_id']
                # Agregar agenda_id al final
                columnas_reordenadas = columnas_sin_agenda_id + ['agenda_id']
                # Reordenar el DataFrame
                df_excel = df_excel[columnas_reordenadas]
            
            archivo_excel = archivo_salida.replace('.csv', '.xlsx')
            
            # Crear el archivo Excel simple con formato básico
            with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
                # Una sola hoja con las columnas reordenadas
                df_excel.to_excel(writer, sheet_name='Agendas Consolidadas', index=False)
                
                # Obtener el worksheet para aplicar formato básico
                worksheet = writer.sheets['Agendas Consolidadas']
                
                # Ajustar ancho de columnas automáticamente
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    # Establecer un ancho máximo razonable
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Archivo Excel exportado a: {archivo_excel}")
            print(f"Total de registros: {len(df)}")
            
        except Exception as e:
            print(f"Error exportando archivos: {e}")
            # Intentar exportar solo CSV como fallback
            try:
                df.to_csv(archivo_salida, index=False, encoding='utf-8')
                print(f"Exportación de CSV exitosa como fallback: {archivo_salida}")
            except Exception as e2:
                print(f"Error crítico en exportación: {e2}")
    
    def generar_reporte(self, df: pd.DataFrame):
        """Genera un reporte estadístico de los datos consolidados"""
        print("\n=== REPORTE DE CONSOLIDACIÓN ===")
        print(f"Total de registros: {len(df)}")
        print(f"Número de efectores: {df['efector'].nunique()}")
        
        # Contar doctores únicos (excluyendo vacíos)
        doctores_no_vacios = df[df['doctor'].str.strip() != '']['doctor'].nunique()
        print(f"Número de doctores únicos: {doctores_no_vacios}")
        
        # Contar áreas únicas (excluyendo vacíos)
        areas_no_vacias = df[df['area'].str.strip() != '']['area'].nunique()
        print(f"Número de áreas únicas: {areas_no_vacias}")
        
        print("\n--- Efectores ---")
        print(df['efector'].value_counts())
        
        print("\n--- Áreas más comunes ---")
        areas_counts = df[df['area'].str.strip() != '']['area'].value_counts()
        print(areas_counts.head(10))
        
        print("\n--- Días de la semana ---")
        print(df['dia'].value_counts())
        
        print("\n--- Registros con campos vacíos ---")
        print(f"Sin doctor: {len(df[df['doctor'].str.strip() == ''])}")
        print(f"Sin área: {len(df[df['area'].str.strip() == ''])}")
        print(f"Sin tipo de turno: {len(df[df['tipo_turno'].str.strip() == ''])}")
        print(f"Sin día: {len(df[df['dia'].str.strip() == ''])}")

    def limpiar_texto(self, texto: str) -> str:
        """Limpia caracteres especiales y de codificación problemáticos"""
        if not texto or pd.isna(texto):
            return ""
        
        # Limpiar caracteres de codificación problemáticos
        texto_limpio = str(texto)
        
        # Reemplazar caracteres problemáticos comunes
        reemplazos = {
            'Ã_x008d_': 'Í',
            'Ã_x0081_': 'Á',
            'Ã_x0081_N': 'ÁN',
            'MÃ‰DICA': 'MÉDICA',
            'CLÃ_x008d_NICA': 'CLÍNICA',
            'PEDIÃ_x0081_TRICA': 'PEDIÁTRICA',
            'BARILÃ_x0081_': 'BARILÁ',
            'INÃ‰S': 'INÉS',
            'Ã‰S': 'ÉS',
            'Ã‰': 'É',
            'Ã\u201dNICA': 'ÓNICA',
            'Ã\u201d': 'Ó',
            'VERÃ\u201dNICA': 'VERÓNICA',
            '├ô': 'Ó',  # Mapeo específico para VER├ôNICA
            'VER├ôNICA': 'VERÓNICA',  # Mapeo completo para VERÓNICA
            'MUÃ\u2019OZ': 'MUÑOZ',  # Mapeo para MUÑOZ
            'Ã\u2019OZ': 'ÑOZ',  # Mapeo genérico para Ñ
            'Ã\u2019': 'Ñ',  # Mapeo genérico para Ñ
            'NOEMÃ_x008d_': 'NOEMÍ',  # Mapeo específico para NOEMÍ
            'ODONTOLOGÃ_x008d_A': 'ODONTOLOGÍA',  # Mapeo específico para ODONTOLOGÍA
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã±': 'ñ',
            'Ã\u00d1': 'Ñ',
            'Ãü': 'ü',
            'Ã‚': 'Â',
            'Ã¢': 'â',
            'Ã¨': 'è',
            'Ã¬': 'ì',
            'Ã²': 'ò',
            'Ã¹': 'ù',
            'Ã§': 'ç'
        }
        
        for problema, solucion in reemplazos.items():
            if problema in texto_limpio:
                texto_limpio = texto_limpio.replace(problema, solucion)
        
        # Mapeo adicional para casos específicos como TABOADA
        if 'TABOADA' in texto_limpio:
            # Usar expresión regular para capturar cualquier secuencia problemática antes de NICA
            import re
            texto_limpio = re.sub(r'VER[^A-Z]*NICA', 'VERÓNICA', texto_limpio)
        
        return texto_limpio.strip()
    
    def _procesar_formato_odontologico(self, df: pd.DataFrame, efector: str) -> pd.DataFrame:
        """
        Procesa el formato específico del Hospital Odontológico donde:
        - Una fila tiene el nombre de la agenda/doctor en columna A
        - Las filas siguientes tienen Día, Hora inicio, Hora fin en columnas A, B, C
        """
        registros = []
        agenda_actual = ""
        agenda_id_counter = 0  # Contador para generar IDs únicos de agenda
        agenda_actual_id = ""
        
        i = 0
        while i < len(df):
            row = df.iloc[i]
            
            # Saltar filas vacías
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
                i += 1
                continue
                
            primera_celda = str(row.iloc[0]).strip().upper()
            
            # Saltar encabezados del archivo
            if primera_celda in ['HOSPITAL ODONTOLOGICO SAN ISIDRO']:
                i += 1
                continue
            
            # Si es una fila de encabezado de tabla (Día, Hora inicio, Hora fin)
            if primera_celda in ['DÍA', 'DIA']:
                i += 1
                continue
            
            # Si la columna B está vacía, probablemente sea una agenda/doctor
            if pd.isna(row.iloc[1]) or str(row.iloc[1]).strip() == "" or str(row.iloc[1]).strip() == "NaN":
                agenda_actual = self.decodificar_caracteres_especiales(str(row.iloc[0]).strip())
                agenda_id_counter += 1
                # Generar ID único que incluye el efector y un contador secuencial  
                agenda_actual_id = f"{efector}_{agenda_id_counter:03d}_{agenda_actual}"
                i += 1
                continue
            
            # Si llegamos aquí, debería ser una fila de horario
            # Verificar que tenga día, hora inicio y hora fin
            if len(row) >= 3 and pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                dia_raw = str(row.iloc[0]).strip()
                hora_inicio = self._formatear_hora(row.iloc[1])
                hora_fin = self._formatear_hora(row.iloc[2])
                
                # Mapear días
                dia_mapping = {
                    'LUNES': 'Lunes', 'MARTES': 'Martes', 'MIÉRCOLES': 'Miércoles',
                    'MIERCOLES': 'Miércoles', 'JUEVES': 'Jueves', 'VIERNES': 'Viernes',
                    'SÁBADO': 'Sábado', 'SABADO': 'Sábado', 'SÁB': 'Sábado', 'DOMINGO': 'Domingo'
                }
                dia = dia_mapping.get(dia_raw.upper(), dia_raw)
                
                # Solo procesar si tenemos datos completos
                if agenda_actual and dia and hora_inicio and hora_fin:
                    # Procesar componentes de la agenda
                    agenda_limpia_para_procesamiento = self.limpiar_texto(agenda_actual)
                    componentes = self.extraer_componentes_agenda(agenda_limpia_para_procesamiento)
                    
                    # Para otros centros: preservar el formato original del doctor (sin limpiar)
                    doctor_original = componentes['doctor']  # Mantener formato original
                    
                    registro = {
                        'agenda_id': agenda_actual_id,
                        'nombre_original_agenda': agenda_actual,  # SIN LIMPIAR - exactamente como está
                        'doctor': doctor_original,  # SIN LIMPIAR - exactamente como está extraído
                        'area': self.limpiar_texto(componentes['area']),
                        'tipo_turno': self.limpiar_texto(componentes['tipo_turno']),
                        'dia': dia,
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'efector': efector,
                        'ventanilla': ''  # Nueva variable Ventanilla (vacía por ahora)
                    }
                    
                    # Asignar ventanilla para Hospital Materno
                    if efector == 'Hospital Materno':
                        registro['ventanilla'] = self.asignar_ventanilla_hospital_materno(componentes['area'])
                    
                    registros.append(registro)
            
            i += 1
        
        return pd.DataFrame(registros)

    def _formatear_hora(self, valor_hora) -> str:
        """Formatea una hora desde diferentes formatos posibles"""
        try:
            if hasattr(valor_hora, 'time'):
                return valor_hora.time().strftime('%H:%M')
            else:
                hora_str = str(valor_hora).strip()
                # Buscar patrón de hora
                match = re.search(r'(\d{1,2}):(\d{2})', hora_str)
                if match:
                    return f"{match.group(1).zfill(2)}:{match.group(2)}"
                # Si es solo número (como 7.5 para 7:30)
                try:
                    hora_float = float(hora_str)
                    horas = int(hora_float)
                    minutos = int((hora_float - horas) * 60)
                    return f"{horas:02d}:{minutos:02d}"
                except:
                    pass
        except:
            pass
        return ""
    
# Función principal para uso fácil
def main():
    """Función principal para ejecutar el procesamiento"""
    # Configurar rutas
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_agendas = os.path.join(directorio_actual, "datos", "excel_originales", "agendas_originales")
    archivo_salida = os.path.join(directorio_actual, "datos", "csv_procesado", "agendas_consolidadas.csv")
    
    # Verificar que existe el directorio de agendas
    if not os.path.exists(directorio_agendas):
        print(f"Error: No se encontró el directorio {directorio_agendas}")
        return
    
    # Crear instancia del normalizador
    normalizador = AgendaNormalizer()
    
    # Procesar archivos
    print("Iniciando procesamiento de agendas...")
    print(f"Procesando archivos desde: {directorio_agendas}")
    df_consolidado = normalizador.procesar_directorio(directorio_agendas)
    
    if not df_consolidado.empty:
        # Exportar resultados
        normalizador.exportar_consolidado(df_consolidado, archivo_salida)
        
        # Generar reporte
        normalizador.generar_reporte(df_consolidado)
        
        print("\n¡Procesamiento completado exitosamente!")
    else:
        print("No se encontraron archivos para procesar o no se pudo extraer información.")

if __name__ == "__main__":
    main()