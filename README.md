# Visualización de agendas médicas HCSI

Una aplicación web interactiva para visualizar y analizar agendas médicas consolidadas de múltiples centros de salud.

## Características principales

- **Análisis general**: Métricas y gráficos de resumen
- **Análisis por día**: Visualización detallada por día de la semana
- **Comparativa entre centros**: Comparación de métricas entre diferentes hospitales/CAPS
- **Tabla completa**: Visualización tabular con filtros y paginación
- **Vista calendario**: Visualización tipo agenda semanal
- **Análisis UNIQUE**: Exploración de valores únicos con filtros avanzados
- **Gestión**: Panel gerencial con detección de conflictos de horarios

## Tecnologías utilizadas

- **Frontend**: Streamlit
- **Visualización**: Plotly
- **Procesamiento de datos**: Pandas
- **Análisis**: NumPy

## Instalación y ejecución local

### Prerequisitos

Asegúrate de tener:
- Python 3.8 o superior
- Los archivos Excel originales en el directorio `agendas_originales/`

### Pasos

1. Clona el repositorio
2. Crea el directorio de datos:
   ```bash
   mkdir agendas_originales
   ```
3. Coloca los archivos Excel de las agendas en `agendas_originales/`
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
5. Ejecuta la aplicación:
   ```bash
   streamlit run app_agendas.py
   ```

## Estructura del proyecto

- `app_agendas.py`: Aplicación principal de Streamlit
- `agendas.py`: Módulo de procesamiento de archivos Excel
- `requirements.txt`: Dependencias del proyecto
- `agendas_originales/`: Directorio con archivos Excel originales
- `agendas_consolidadas.csv`: Datos consolidados (generado automáticamente)

## Fuente de datos

La aplicación procesa archivos Excel originales ubicados en `agendas_originales/` que contienen:
- Agendas de múltiples hospitales y CAPS
- Información de médicos, especialidades y horarios
- Datos de turnos programados y espontáneos

## Uso

La aplicación permite:

1. **Filtrar datos** por hospital, especialidad, día, tipo de turno y médico
2. **Visualizar métricas** como total de agendas, médicos activos, especialidades y centros
3. **Explorar horarios** con vistas de calendario y timeline
4. **Analizar conflictos** de horarios entre médicos
5. **Exportar datos** filtrados en formato CSV
6. **Realizar análisis UNIQUE** para explorar valores únicos de cualquier campo

## Funcionalidad UNIQUE

La nueva funcionalidad de análisis UNIQUE permite:

- Explorar valores únicos de cualquier campo (hospital, especialidad, médico, etc.)
- Aplicar filtros avanzados
- Visualizar conteos y proporciones
- Realizar análisis cruzado entre campos
- Exportar resultados en CSV

### Ejemplos de uso UNIQUE:

1. **Ver todas las especialidades de un hospital específico**:
   - Campo: Especialidad médica
   - Filtro: Hospital Materno Infantil

2. **Listar todos los médicos de una especialidad**:
   - Campo: Médico
   - Filtro: Especialidad = PEDIATRIA

3. **Analizar horarios por día**:
   - Campo: Hora de inicio
   - Filtro: Día = Lunes

## Desarrollador

Lucas Rosenzvit - lrosenzvit@sanisidro.gob.ar
