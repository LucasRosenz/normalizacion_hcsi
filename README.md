# Sistema de Normalización y Análisis de Agendas Médicas

Una aplicación completa para procesar, normalizar y analizar agendas médicas de múltiples centros de salud con detección automática de duplicados y control de calidad.

## 🚀 Características principales

### Procesamiento de Datos
- **Extracción automática** de agendas desde archivos Excel con formatos variados
- **Detección estructural** de agendas usando criterios robustos
- **Generación de IDs únicos** para cada instancia de agenda (incluso duplicadas)
- **Preservación de fidelidad** a los datos originales del Excel

### Dashboard Interactivo
- **Análisis general**: Métricas y gráficos de resumen
- **Análisis por día**: Visualización detallada por día de la semana  
- **Análisis por médico**: Horarios y distribución por doctor
- **Comparativa entre centros**: Comparación de métricas entre hospitales/CAPS
- **Tabla completa**: Visualización tabular con filtros, paginación y agenda_id
- **Vista calendario**: Visualización tipo agenda semanal
- **Gestión**: Panel gerencial con detección de conflictos de horarios
- **Control de Calidad**: Detección y análisis de agendas duplicadas

### Control de Calidad
- **Detección automática** de agendas duplicadas en el mismo centro
- **Análisis por centro** con métricas de duplicados
- **Verificación de integridad** de datos procesados
- **Reportes detallados** con IDs específicos de agendas problemáticas

## 📁 Estructura del Proyecto

```
normalizacion_hcsi/
├── 📋 Archivos principales
│   ├── agendas.py              # Procesador principal de agendas
│   ├── app_agendas.py          # Dashboard Streamlit
│   ├── auth.py                 # Sistema de autenticación  
│   └── auth_config.py          # Configuración de usuarios
│
├── 📊 Datos
│   ├── csv_procesado/          # Agendas consolidadas procesadas
│   ├── excel_originales/       # Archivos Excel originales
│   └── csv_extras/            # Datos auxiliares
│
├── 🔬 Scripts de Análisis
│   ├── analizar_diferencias_conteo.py
│   ├── detectar_duplicados_mismo_centro.py
│   ├── verificar_agenda_ids.py
│   ├── encontrar_agendas_faltantes.py
│   ├── encontrar_agendas_perdidas.py
│   ├── examinar_san_pantaleon.py
│   └── investigar_dias_problematicos.py
│
├── ✅ Scripts de Verificación  
│   ├── comparacion_por_centro.py
│   ├── corregir_efectores.py
│   ├── verificar_integridad_agendas.py
│   ├── verificar_san_pantaleon.py
│   ├── analizar_errores.py
│   └── test_app.py
│
└── 📖 Documentación
    ├── README.md              # Este archivo
    ├── ESTADO_FINAL.md        # Estado del proyecto
    └── docs/                  # Documentación adicional
```

## 🛠 Tecnologías utilizadas

- **Backend**: Python 3.8+
- **Frontend**: Streamlit
- **Visualización**: Plotly Express, Plotly Graph Objects
- **Procesamiento**: Pandas, NumPy
- **Archivos**: openpyxl (Excel), CSV
- **Control de versiones**: Git

## 🚀 Instalación y ejecución

### Prerequisitos
- Python 3.8 o superior
- Archivos Excel originales en `datos/excel_originales/agendas_originales/`

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/LucasRosenz/normalizacion_hcsi.git
cd normalizacion_hcsi
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Procesar los datos**
```bash
python agendas.py
```

4. **Ejecutar la aplicación**
```bash
streamlit run app_agendas.py
```

5. **Acceder al dashboard**
- Abrir navegador en: `http://localhost:8501`
- Usuario: `admin`, Password: `admin123`

## 📊 Funcionalidades del Dashboard

### Control de Calidad (Nuevo)
- **Detección automática** de agendas duplicadas
- **Métricas por centro** de duplicados encontrados
- **Análisis detallado** con IDs específicos
- **Visualización gráfica** de problemas por centro

### Características Destacadas
- **Agenda ID único**: Cada agenda tiene un identificador único (`{Centro}_{Secuencia}_{Nombre}`)
- **Preservación de duplicados**: Los duplicados se mantienen para análisis posterior
- **Fidelidad de datos**: 100% de coincidencia con conteos manuales (612/612)
- **Detección de problemas**: Identificación automática de inconsistencias

## 🔧 Scripts Disponibles

### Análisis Principal
```bash
# Procesar todas las agendas
python agendas.py

# Verificar agenda IDs
python scripts_analisis/verificar_agenda_ids.py

# Detectar duplicados específicos
python scripts_analisis/detectar_duplicados_mismo_centro.py
```

### Verificación de Integridad
```bash
# Comparación centro por centro
python scripts_verificacion/comparacion_por_centro.py

# Verificar integridad general
python scripts_verificacion/verificar_integridad_agendas.py

# Análisis de diferencias
python scripts_analisis/analizar_diferencias_conteo.py
```

## 📈 Métricas del Sistema

- **Centros procesados**: 12 centros de salud
- **Agendas totales**: 612 agendas únicas
- **Registros de horarios**: 1,589 registros
- **Precisión**: 100% (612/612 agendas detectadas)
- **Duplicados identificados**: 2 agendas en CAPS San Isidro Labrador

## 🎯 Casos de Uso

### Para Administradores
- Detectar agendas duplicadas que requieren revisión
- Analizar distribución de horarios por centro
- Verificar integridad de datos procesados
- Generar reportes de calidad

### Para Gestores de Centros
- Visualizar horarios de su centro específico
- Identificar conflictos de horarios entre médicos
- Analizar cobertura por especialidad
- Optimizar asignación de recursos

### Para Analistas de Datos
- Acceso a datasets limpios y estructurados  
- Herramientas de análisis y verificación
- Trazabilidad completa de procesamiento
- APIs para integraciones futuras

## 🐛 Resolución de Problemas

### Errores Comunes

**Error: No se encuentra el archivo CSV**
```bash
# Solución: Procesar los datos primero
python agendas.py
```

**Warning: DataFrameGroupBy.apply**
- Son warnings normales de pandas, no afectan funcionalidad

**Agendas faltantes**
- Verificar formato de Excel original
- Usar scripts de verificación para diagnóstico

## 🤝 Contribución

1. Fork del proyecto
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)  
5. Abrir Pull Request

## 📝 Changelog

### v2.0.0 (Actual)
- ✅ Implementación de agenda_id único
- ✅ Detección automática de duplicados
- ✅ Tab de Control de Calidad
- ✅ 100% de fidelidad a datos originales
- ✅ Reorganización de estructura de archivos

### v1.0.0
- ✅ Dashboard básico de visualización
- ✅ Procesamiento inicial de agendas
- ✅ Sistema de autenticación

## 👥 Autores

- **Lucas Rosenzvit** - *Desarrollo principal* - lrosenzvit@sanisidro.gob.ar

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- Municipio de San Isidro - Secretaría de Salud
- Equipo de sistemas del HCSI
- Centros de salud participantes
   ```bash
   pip install -r requirements.txt
   ```
5. Ejecuta la aplicación:
   ```bash
   streamlit run app_agendas.py
   ```

## Estructura del proyecto

```
normalizacion_hcsi/
├── agendas.py              # Módulo principal de procesamiento
├── app_agendas.py          # Aplicación Streamlit
├── auth.py                 # Módulo de autenticación
├── auth_config.py          # Configuración de autenticación
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Este archivo
├── ESTADO_FINAL.md        # Estado final del proyecto
├── datos/                 # Directorio de datos
│   ├── excel_originales/   # Archivos Excel originales
│   └── csv_procesado/     # Archivos CSV procesados
├── docs/                  # Documentación del proyecto
├── scripts_verificacion/  # Scripts de verificación y testing
│   ├── verificar_integridad_agendas.py
│   ├── analizar_errores.py
│   ├── test_app.py
│   └── README.md
└── .streamlit/            # Configuración de Streamlit
```

### Archivos principales

- **`agendas.py`**: Módulo principal que procesa archivos Excel y normaliza agendas médicas
- **`app_agendas.py`**: Aplicación web Streamlit con 7 pestañas de análisis
- **`auth.py`**: Sistema de autenticación para acceso controlado
- **`ESTADO_FINAL.md`**: Documentación del estado final y logros del proyecto

### Scripts de verificación

Los scripts de verificación están organizados en `scripts_verificacion/`:
- **`verificar_integridad_agendas.py`**: Verifica integridad entre Excel originales y tabla final
- **`analizar_errores.py`**: Analiza errores en el procesamiento
- **`test_app.py`**: Pruebas unitarias para la aplicación
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
