# Estructura del Proyecto - Agendas Salud

## Organización de Carpetas

### 📁 **docs/**
Contiene toda la documentación del proyecto:
- `README.md` - Documentación principal
- `AUTENTICACION.md` - Información sobre el sistema de autenticación
- `CAMBIOS_SOLO_EXCEL.md` - Cambios específicos para procesamiento Excel
- `CREDENCIALES_TEMPORALES.md` - Credenciales temporales del sistema
- `DESPLIEGUE.md` - Instrucciones de despliegue
- `IMPLEMENTACION.md` - Detalles de implementación
- `IMPLEMENTACION_AUTENTICACION.md` - Implementación del sistema de autenticación
- `SOLUCION_FINAL.md` - Documentación de la solución final
- `ESTRUCTURA_PROYECTO.md` - Este archivo (estructura del proyecto)

### 📁 **datos/**
Contiene todos los archivos de datos organizados por categorías:

#### 📁 **datos/excel_originales/**
- `agendas_originales/` - Carpeta con todos los archivos Excel originales de los centros de salud

#### 📁 **datos/csv_procesado/**
- `agendas_consolidadas.csv` - Archivo CSV principal con todas las agendas procesadas
- `agendas_consolidadas.xlsx` - Versión Excel del archivo consolidado

#### 📁 **datos/csv_extras/**
- `conflictos.csv` - Archivo con conflictos de horarios detectados
- `2025-07-16T18-34_export.csv` - Archivos de exportación temporal
- Otros archivos CSV generados por la aplicación

### 📁 **Archivos de código principales**
- `agendas.py` - Script principal de procesamiento de datos
- `app_agendas.py` - Aplicación Streamlit principal
- `auth.py` - Sistema de autenticación
- `auth_config.py` - Configuración de autenticación
- `requirements.txt` - Dependencias de Python

### 📁 **Otros archivos**
- `.streamlit/` - Configuración de Streamlit
- `__pycache__/` - Cache de Python
- `.git/` - Repositorio Git
- `.github/` - Configuración de GitHub

## Flujo de Datos

```
Excel Originales → Procesamiento → CSV Consolidado → Aplicación Web
     ↓                  ↓              ↓                ↓
datos/excel_     →   agendas.py   →  datos/csv_   →  app_agendas.py
originales/                         procesado/
```

## Rutas Actualizadas

### En `agendas.py`:
- **Entrada**: `datos/excel_originales/agendas_originales/`
- **Salida**: `datos/csv_procesado/agendas_consolidadas.csv`

### En `app_agendas.py`:
- **Entrada**: `datos/csv_procesado/agendas_consolidadas.csv`
- **Exports**: Se guardan en `datos/csv_extras/`

## Comandos Principales

### Procesar datos:
```bash
python agendas.py
```

### Ejecutar aplicación:
```bash
streamlit run app_agendas.py
```

## Beneficios de la Nueva Estructura

1. **Organización clara**: Cada tipo de archivo tiene su lugar específico
2. **Separación de responsabilidades**: Datos originales, procesados y extras están separados
3. **Documentación centralizada**: Toda la documentación está en `docs/`
4. **Fácil mantenimiento**: La estructura es intuitiva y escalable
5. **Backup seguro**: Los datos originales están protegidos en su propia carpeta

## Datos Estadísticos Actuales

- **Total de registros**: 1,589
- **Centros de salud**: 12
- **Médicos únicos**: 391
- **Áreas médicas**: 46
- **Archivos Excel originales**: 12
