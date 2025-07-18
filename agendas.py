import pandas as pd
import os
import re
from typing import List, Dict, Tuple, Optional
import numpy as np

class AgendaNormalizer:
    """
    Clase para normalizar y consolidar agendas médicas de múltiples centros de salud
    """
    
    def __init__(self):
        self.df_consolidado = pd.DataFrame(columns=[
            'agenda_id', 'nombre_original_agenda', 'doctor', 'area', 'tipo_turno', 
            'dia', 'hora_inicio', 'hora_fin', 'efector'
        ])
        
    def extraer_componentes_agenda(self, nombre_agenda: str) -> Dict[str, str]:
        """
        Extrae doctor, área y tipo de turno del nombre de la agenda
        Maneja diferentes formatos posibles
        """
        if not nombre_agenda or pd.isna(nombre_agenda):
            return {'doctor': '', 'area': '', 'tipo_turno': ''}
            
        nombre_limpio = str(nombre_agenda).strip()
        
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
            'PSICOPEDAGOGIA': r'\bPSICOPEDAGOGIA\b'
        }
        
        # Buscar área médica
        texto_upper = nombre_limpio.upper()
        for area_nombre, pattern in areas_patterns.items():
            if re.search(pattern, texto_upper):
                area = area_nombre
                break
        
        # Buscar doctor - patrones mejorados
        doctor_patterns = [
            # Patrón para DRA/DR seguido del nombre - detener antes de palabras clave
            r'\bDRA?\.\s*([A-ZÁÉÍÓÚÑ].+?)(?:\s*-\s*(?:PROGRAMADA|ESPONTANEA|ESPONTÁNEA|GENERAL|TRATAMIENTO|PAP|CAI|RECITADOS|RECIEN\s+NACIDOS|EMBARAZADAS|CONTROL|URGENCIA|SOBRETURNO|DIU|IMPLANTE|EXTRACCION|COLOCACION|AGENDA\s+BIS|REUNION\s+EQUIPO)|\s*$)',
            # Patrón para DOCTOR/DOCTORA seguido del nombre
            r'\bDOCTOR[A]?\s+([A-ZÁÉÍÓÚÑ].+?)(?:\s*-\s*(?:PROGRAMADA|ESPONTANEA|ESPONTÁNEA|GENERAL|TRATAMIENTO|PAP|CAI|RECITADOS|RECIEN\s+NACIDOS|EMBARAZADAS|CONTROL|URGENCIA|SOBRETURNO|DIU|IMPLANTE|EXTRACCION|COLOCACION|AGENDA\s+BIS|REUNION\s+EQUIPO)|\s*$)',
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
            # Patrón para nombres al final después de guión
            r'[-\s]+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)+)$',
            # Patrón específico para "ESPECIALIDAD - NOMBRE APELLIDO - TIPO"
            r'\b(?:ODONTOLOGIA|PEDIATRIA)\s+(?:ADULTOS|PEDIATRIA|INFANTIL)?\s*-\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)+)\s*-\s*(?:ESPONTANEA|PROGRAMADA)',
        ]
        
        for pattern in doctor_patterns:
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
                    'BIS', 'DIU', 'IMPLANTE', 'EXTRACCION', 'COLOCACION', 'REUNION EQUIPO'
                ]
                # Solo excluir si el nombre candidato es exactamente una de estas palabras o si es muy corto
                if nombre_candidato.strip() and len(nombre_candidato.strip()) > 2:
                    # Verificar que no contenga palabras clave (no solo coincidencias exactas)
                    es_palabra_clave = any(palabra in nombre_candidato.upper().strip() for palabra in palabras_excluir)
                    # Verificar que no sea exactamente una palabra clave
                    es_exactamente_palabra_clave = any(nombre_candidato.upper().strip() == palabra for palabra in palabras_excluir)
                    
                    if not es_palabra_clave and not es_exactamente_palabra_clave:
                        # Limpiar palabras específicas del final del nombre
                        nombre_limpio = re.sub(r'\s*-\s*(DIU|IMPLANTE|EXTRACCION|COLOCACION|AGENDA\s+BIS|REUNION\s+EQUIPO)\s*$', '', nombre_candidato, flags=re.IGNORECASE)
                        doctor = nombre_limpio.strip()
                        break
        
        # Buscar tipo de turno - patrones mejorados
        tipo_patterns = {
            'GUARDIA': r'\bGUARDIA\b|\bGUARDIA\s+MEDICA\b|\bGUARDIAS\b',
            'ESPONTANEA': r'\bESPONTANEA\b|\bESPONTÁNEA\b|\bESPONTÃ_x0081_NEA\b',
            'PROGRAMADA': r'\bPROGRAMADA\b|\bTURNO\s+PROGRAMADO\b|\bPROGRAMADO\b',
            'SOBRETURNO': r'\bSOBRETURNO\b|\bSOBRETURNOS\b',
            'URGENCIA': r'\bURGENCIA\b|\bURGENTE\b',
            'CONTROL': r'\bCONTROL\b',
            'INTERCONSULTA': r'\bINTERCONSULTA\b',
            'CONSULTA EXTERNA': r'\bCONSULTA\s+EXTERNA\b|\bEXTERNA\b',
            'TRATAMIENTO': r'\bTRATAMIENTO\b',
            'GENERAL': r'\bGENERAL\b',
            'PAP': r'\bPAP\b',
            'CAI': r'\bCAI\b'
        }
        
        for tipo_nombre, pattern in tipo_patterns.items():
            if re.search(pattern, texto_upper):
                tipo_turno = tipo_nombre
                break
        
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
                    # Extraer el nombre de la agenda de la primera celda
                    agenda_actual = str(row.iloc[0]).strip()
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
                registro = {
                    'nombre_original_agenda': agenda_actual,  # SIN LIMPIAR - exactamente como está
                    'doctor': self.limpiar_texto(componentes['doctor']),
                    'area': self.limpiar_texto(componentes['area']),
                    'tipo_turno': self.limpiar_texto(componentes['tipo_turno']),
                    'dia': dia,
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'efector': efector
                }
                
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
            return df_consolidado
        
        return pd.DataFrame()
    
    def _inferir_efector(self, nombre_archivo: str) -> str:
        """Infiere el nombre del efector desde el nombre del archivo"""
        nombre_base = os.path.splitext(nombre_archivo)[0]
        nombre_upper = nombre_base.upper()
        
        # Patrones específicos - ORDEN IMPORTANTE: más específicos primero
        if 'HCSI' in nombre_upper:
            return 'Hospital de Clínicas San Ignacio'
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
        elif 'CAPS VILLA ADELINA' in nombre_upper:
            return 'CAPS Villa Adelina'
        elif 'CENTRO EL NIDO' in nombre_upper:
            return 'Centro El Nido'
        elif 'CAPS' in nombre_upper:
            return 'CAPS'  # Fallback genérico
        elif 'CENTRO' in nombre_upper:
            return 'Centro de Salud'
        
        return nombre_base
    
    def exportar_consolidado(self, df: pd.DataFrame, archivo_salida: str):
        """Exporta el DataFrame consolidado a Excel y CSV"""
        try:
            # Exportar a Excel
            df.to_excel(archivo_salida.replace('.csv', '.xlsx'), index=False)
            
            # Exportar a CSV
            df.to_csv(archivo_salida, index=False, encoding='utf-8')
            
            print(f"Archivo consolidado exportado a: {archivo_salida}")
            print(f"Total de registros: {len(df)}")
            
        except Exception as e:
            print(f"Error exportando archivo: {e}")
    
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
                agenda_actual = str(row.iloc[0]).strip()
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
                    'SÁBADO': 'Sábado', 'SABADO': 'Sábado', 'DOMINGO': 'Domingo'
                }
                dia = dia_mapping.get(dia_raw.upper(), dia_raw)
                
                # Solo procesar si tenemos datos completos
                if agenda_actual and dia and hora_inicio and hora_fin:
                    # Procesar componentes de la agenda
                    agenda_limpia_para_procesamiento = self.limpiar_texto(agenda_actual)
                    componentes = self.extraer_componentes_agenda(agenda_limpia_para_procesamiento)
                    
                    registro = {
                        'agenda_id': agenda_actual_id,
                        'nombre_original_agenda': agenda_actual,  # SIN LIMPIAR - exactamente como está
                        'doctor': self.limpiar_texto(componentes['doctor']),
                        'area': self.limpiar_texto(componentes['area']),
                        'tipo_turno': self.limpiar_texto(componentes['tipo_turno']),
                        'dia': dia,
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'efector': efector
                    }
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