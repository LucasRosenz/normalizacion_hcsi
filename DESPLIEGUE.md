# Configuración para despliegue en Streamlit Cloud

## Pasos para desplegar la aplicación:

### 1. Subir el código a GitHub

1. Crea un repositorio en GitHub (por ejemplo: `normalizacion-hcsi-app`)
2. Sube todos los archivos del proyecto:
   - `app_agendas.py`
   - `agendas.py`
   - `requirements.txt`
   - `README.md`
   - `.streamlit/config.toml`
   - `agendas_consolidadas.csv` (si existe)

### 2. Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona el repositorio creado
4. Configura:
   - **Main file path**: `app_agendas.py`
   - **Python version**: 3.9+
   - **Advanced settings** (opcional):
     - Variables de entorno si las necesitas

### 3. Configuración recomendada

La aplicación está configurada para:
- **Auto-detectar datos**: Si no existe `agendas_consolidadas.csv`, intentará generarlo
- **Subida manual**: Permite subir el archivo CSV si es necesario
- **Configuración responsive**: Se adapta a diferentes tamaños de pantalla
- **Caché optimizado**: Mejora el rendimiento con `@st.cache_data`

### 4. URL de acceso

Una vez desplegada, la aplicación estará disponible en:
`https://tu-usuario-normalizacion-hcsi-app-streamlit-app.streamlit.app`

### 5. Actualizaciones

- **Automáticas**: Cada commit al repositorio actualiza la aplicación
- **Manuales**: Puedes reiniciar la aplicación desde el panel de Streamlit Cloud

## Ventajas del despliegue en la nube:

✅ **Acceso universal**: Cualquier persona con el link puede acceder
✅ **Siempre disponible**: No depende de que tu PC esté encendida
✅ **Actualizaciones automáticas**: Se actualiza con cada cambio en GitHub
✅ **Escalabilidad**: Maneja múltiples usuarios simultáneamente
✅ **Gratuito**: Streamlit Cloud es gratuito para aplicaciones públicas

## Consideraciones de seguridad:

- La pestaña "Gestión" tiene autenticación con contraseña
- Los datos se procesan en la nube de Streamlit
- Para mayor seguridad, puedes hacer el repositorio privado

## Alternativas de despliegue:

1. **Streamlit Cloud** (Recomendado): Más fácil y gratuito
2. **Heroku**: Más control, pero requiere configuración adicional
3. **AWS/Azure**: Para aplicaciones empresariales
4. **Servidor propio**: Máximo control, pero requiere mantenimiento
