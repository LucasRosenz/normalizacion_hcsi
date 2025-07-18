import pandas as pd
import os
import re
from typing import Set, Dict, List
from collections import defaultdict

class VerificadorIntegridadAgendas:
    """
    Verifica la integridad entre nombres de agenda en archivos Excel originales 
    y la tabla final procesada usando criterios estructurales
    """
    
    def __init__(self):
        self.agendas_originales = set()  # Agendas encontradas en Excel originales
        self.agendas_procesadas = set()  # Agendas en tabla final
        self.archivo_origen = {}  # Mapeo agenda -> archivo origen
        
    def extraer_agendas_excel(self, archivo_path: str) -> Set[str]:
        """
        Extrae nombres de agenda de un archivo Excel usando criterio estructural
        """
        agendas_encontradas = set()
        
        try:
            # Leer archivo Excel sin encabezados
            df = pd.read_excel(archivo_path, header=None)
            
            for idx, row in df.iterrows():
                if self._es_titulo_agenda_estructural(row):
                    # Extraer el nombre de la agenda de la primera celda
                    agenda_nombre = str(row.iloc[0]).strip()
                    if agenda_nombre:  # Solo agregar si no está vacío
                        agendas_encontradas.add(agenda_nombre)
                        # Mapear agenda a su archivo origen
                        archivo_nombre = os.path.basename(archivo_path)
                        self.archivo_origen[agenda_nombre] = archivo_nombre
                        
        except Exception as e:
            print(f"Error leyendo {archivo_path}: {e}")
            
        return agendas_encontradas
    
    def _es_titulo_agenda_estructural(self, row: pd.Series) -> bool:
        """
        Determina si una fila es un título de agenda usando criterio estructural puro:
        - Primera columna tiene contenido (no es nan)
        - Segunda columna está vacía (es nan) 
        - Tercera columna está vacía (es nan)
        - La primera celda no está vacía después de strip()
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
        
        return True
    
    def extraer_agendas_tabla_final(self, archivo_csv: str) -> Set[str]:
        """
        Extrae nombres de agenda únicos de la tabla final procesada
        """
        agendas_encontradas = set()
        
        try:
            df = pd.read_csv(archivo_csv)
            
            # Verificar que existe la columna 'nombre_original_agenda'
            if 'nombre_original_agenda' not in df.columns:
                print(f"Error: No se encontró la columna 'nombre_original_agenda' en {archivo_csv}")
                return agendas_encontradas
            
            # Extraer nombres únicos (excluyendo valores vacíos o nan)
            nombres_unicos = df['nombre_original_agenda'].dropna().unique()
            
            for nombre in nombres_unicos:
                nombre_limpio = str(nombre).strip()
                if nombre_limpio:  # Solo agregar si no está vacío
                    agendas_encontradas.add(nombre_limpio)
                    
        except Exception as e:
            print(f"Error leyendo {archivo_csv}: {e}")
            
        return agendas_encontradas
    
    def procesar_directorio_excel(self, directorio: str):
        """
        Procesa todos los archivos Excel en un directorio para extraer agendas
        """
        archivos_procesados = 0
        
        if not os.path.exists(directorio):
            print(f"Error: No existe el directorio {directorio}")
            return
        
        for archivo in os.listdir(directorio):
            if archivo.endswith(('.xlsx', '.xls')):
                # Excluir archivos HCSI (formato diferente)
                if 'HCSI' in archivo.upper():
                    print(f"Saltando archivo HCSI: {archivo} (formato diferente)")
                    continue
                
                archivo_path = os.path.join(directorio, archivo)
                print(f"Procesando: {archivo}")
                
                agendas_archivo = self.extraer_agendas_excel(archivo_path)
                self.agendas_originales.update(agendas_archivo)
                
                print(f"  - {len(agendas_archivo)} agendas encontradas")
                archivos_procesados += 1
        
        print(f"\nTotal archivos Excel procesados: {archivos_procesados}")
        print(f"Total agendas únicas en Excel originales: {len(self.agendas_originales)}")
    
    def verificar_integridad(self, directorio_excel: str, archivo_csv: str):
        """
        Ejecuta la verificación completa de integridad
        """
        print("=== VERIFICACIÓN DE INTEGRIDAD DE AGENDAS ===\n")
        
        # 1. Extraer agendas de archivos Excel originales
        print("1. Extrayendo agendas de archivos Excel originales...")
        self.procesar_directorio_excel(directorio_excel)
        
        # 2. Extraer agendas de tabla final
        print(f"\n2. Extrayendo agendas de tabla final: {os.path.basename(archivo_csv)}")
        self.agendas_procesadas = self.extraer_agendas_tabla_final(archivo_csv)
        print(f"Total agendas únicas en tabla final: {len(self.agendas_procesadas)}")
        
        # 3. Comparar y reportar diferencias
        print(f"\n3. Comparando resultados...")
        self.reportar_diferencias()
    
    def reportar_diferencias(self):
        """
        Reporta las diferencias encontradas entre agendas originales y procesadas
        """
        # Agendas en Excel pero NO en tabla final
        solo_en_excel = self.agendas_originales - self.agendas_procesadas
        
        # Agendas en tabla final pero NO en Excel
        solo_en_tabla = self.agendas_procesadas - self.agendas_originales
        
        # Agendas presentes en ambos
        en_ambos = self.agendas_originales & self.agendas_procesadas
        
        print("\n=== RESULTADOS DE VERIFICACIÓN ===")
        print(f"✅ Agendas presentes en ambos: {len(en_ambos)}")
        print(f"⚠️  Agendas solo en Excel originales: {len(solo_en_excel)}")
        print(f"⚠️  Agendas solo en tabla final: {len(solo_en_tabla)}")
        
        # Detallar agendas solo en Excel
        if solo_en_excel:
            print(f"\n--- AGENDAS SOLO EN EXCEL ORIGINALES ({len(solo_en_excel)}) ---")
            for agenda in sorted(solo_en_excel):
                archivo_origen = self.archivo_origen.get(agenda, "Desconocido")
                print(f"  • '{agenda}' (origen: {archivo_origen})")
        
        # Detallar agendas solo en tabla final
        if solo_en_tabla:
            print(f"\n--- AGENDAS SOLO EN TABLA FINAL ({len(solo_en_tabla)}) ---")
            for agenda in sorted(solo_en_tabla):
                print(f"  • '{agenda}'")
        
        # Resumen final
        print(f"\n=== RESUMEN FINAL ===")
        if not solo_en_excel and not solo_en_tabla:
            print("✅ VERIFICACIÓN EXITOSA: Todas las agendas coinciden perfectamente")
        else:
            print("⚠️  DISCREPANCIAS ENCONTRADAS:")
            if solo_en_excel:
                print(f"   - {len(solo_en_excel)} agenda(s) en Excel no procesada(s)")
            if solo_en_tabla:
                print(f"   - {len(solo_en_tabla)} agenda(s) en tabla sin origen claro")
        
        # Estadísticas adicionales
        total_excel = len(self.agendas_originales)
        total_tabla = len(self.agendas_procesadas)
        cobertura_procesamiento = len(en_ambos) / total_excel * 100 if total_excel > 0 else 0
        
        print(f"\nESTADÍSTICAS:")
        print(f"  - Cobertura de procesamiento: {cobertura_procesamiento:.1f}%")
        print(f"  - Total único en Excel: {total_excel}")
        print(f"  - Total único en tabla: {total_tabla}")
    
    def exportar_reporte_detallado(self, archivo_salida: str):
        """
        Exporta un reporte detallado a archivo CSV
        """
        try:
            # Preparar datos para el reporte
            reporte_data = []
            
            # Agendas en ambos
            en_ambos = self.agendas_originales & self.agendas_procesadas
            for agenda in en_ambos:
                reporte_data.append({
                    'nombre_agenda': agenda,
                    'estado': 'EN_AMBOS',
                    'archivo_origen': self.archivo_origen.get(agenda, ''),
                    'observaciones': 'Procesada correctamente'
                })
            
            # Solo en Excel
            solo_en_excel = self.agendas_originales - self.agendas_procesadas
            for agenda in solo_en_excel:
                reporte_data.append({
                    'nombre_agenda': agenda,
                    'estado': 'SOLO_EN_EXCEL',
                    'archivo_origen': self.archivo_origen.get(agenda, ''),
                    'observaciones': 'No procesada - revisar criterios de detección'
                })
            
            # Solo en tabla
            solo_en_tabla = self.agendas_procesadas - self.agendas_originales
            for agenda in solo_en_tabla:
                reporte_data.append({
                    'nombre_agenda': agenda,
                    'estado': 'SOLO_EN_TABLA',
                    'archivo_origen': '',
                    'observaciones': 'Origen no identificado - revisar lógica'
                })
            
            # Crear DataFrame y exportar
            df_reporte = pd.DataFrame(reporte_data)
            df_reporte.to_csv(archivo_salida, index=False, encoding='utf-8')
            
            print(f"\n📄 Reporte detallado exportado a: {archivo_salida}")
            
        except Exception as e:
            print(f"Error exportando reporte: {e}")

def main():
    """
    Función principal para ejecutar la verificación
    """
    # Configurar rutas
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_excel = os.path.join(directorio_actual, "datos", "excel_originales", "agendas_originales")
    archivo_csv = os.path.join(directorio_actual, "datos", "csv_procesado", "agendas_consolidadas.csv")
    archivo_reporte = os.path.join(directorio_actual, "reporte_integridad_agendas.csv")
    
    # Verificar que existen los archivos/directorios necesarios
    if not os.path.exists(directorio_excel):
        print(f"Error: No se encontró el directorio {directorio_excel}")
        return
    
    if not os.path.exists(archivo_csv):
        print(f"Error: No se encontró el archivo {archivo_csv}")
        return
    
    # Crear instancia del verificador
    verificador = VerificadorIntegridadAgendas()
    
    # Ejecutar verificación
    verificador.verificar_integridad(directorio_excel, archivo_csv)
    
    # Exportar reporte detallado
    verificador.exportar_reporte_detallado(archivo_reporte)

if __name__ == "__main__":
    main()
