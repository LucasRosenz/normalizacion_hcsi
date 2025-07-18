# Scripts de Verificación

Esta carpeta contiene scripts auxiliares para verificar la integridad y calidad de los datos procesados.

## Scripts disponibles

### `verificar_integridad_agendas.py`
- **Propósito**: Verifica que todas las agendas de los Excel originales estén en la tabla final y viceversa
- **Método**: Usa criterio estructural "NOMBRE AGENDA, nan, nan" para detectar agendas
- **Salida**: Reporte detallado de integridad en `reporte_integridad_agendas.csv`
- **Uso**: `python verificar_integridad_agendas.py`

### `analizar_errores.py`
- **Propósito**: Analiza errores y problemas en el procesamiento de datos
- **Método**: Busca patrones problemáticos y genera diagnósticos
- **Uso**: `python analizar_errores.py`

### `test_app.py`
- **Propósito**: Pruebas unitarias para la aplicación Streamlit
- **Método**: Verifica funcionalidad de componentes de la app
- **Uso**: `python test_app.py`

## Archivos generados

### `reporte_integridad_agendas.csv`
Reporte detallado que muestra:
- Agendas presentes en ambos sistemas (Excel y tabla final)
- Agendas solo en Excel originales
- Agendas solo en tabla final
- Archivo de origen para cada agenda

## Ejecución desde la carpeta principal

Para ejecutar estos scripts desde la carpeta principal del proyecto:

```bash
# Verificación de integridad
python scripts_verificacion/verificar_integridad_agendas.py

# Análisis de errores
python scripts_verificacion/analizar_errores.py

# Tests de la aplicación
python scripts_verificacion/test_app.py
```
