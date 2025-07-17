# Configuración para despliegue en Streamlit Cloud

## Pasos para desplegar la aplicación:

### 1. Subir el código a GitHub

1. Crea un repositorio en GitHub (por ejemplo: `normalizacion-hcsi-app`)
2. Sube todos los archivos del proyecto:
   - `app_agendas.py`
   - `agendas.py`
   - `auth.py` ⭐ **NUEVO: Sistema de autenticación**
   - `auth_config.py` ⭐ **NUEVO: Configuración de credenciales**
   - `requirements.txt`
   - `README.md`
   - `AUTENTICACION.md` ⭐ **NUEVO: Documentación de seguridad**
   - `.streamlit/config.toml`
   - `agendas_originales/` (directorio con archivos Excel)
   - `agendas_consolidadas.csv` (si existe)

### 2. ⚠️ IMPORTANTE: Configurar credenciales

**ANTES del despliegue, cambiar las credenciales por defecto:**

1. Edita `auth_config.py`:
   ```python
   USERS = {
       "admin": "TU_CONTRASEÑA_SEGURA_ADMIN",
       "medico": "TU_CONTRASEÑA_SEGURA_MEDICO", 
       "director": "TU_CONTRASEÑA_SEGURA_DIRECTOR"
   }
   
   MASTER_PASSWORD = "TU_CONTRASEÑA_MAESTRA_SUPER_SEGURA"
   ```

2. Usar contraseñas fuertes (mínimo 12 caracteres, combinando letras, números y símbolos)

### 3. Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona el repositorio creado
4. Configura:
   - **Main file path**: `app_agendas.py`
   - **Python version**: 3.9+
   - **Advanced settings** (opcional):
     - Variables de entorno si las necesitas

### 4. Configuración recomendada

La aplicación está configurada para:
- **🔐 Autenticación obligatoria**: Solo usuarios autorizados pueden acceder
- **Procesar archivos Excel**: Si no existe `agendas_consolidadas.csv`, procesará los archivos Excel en `agendas_originales/`
- **Subida manual**: Permite subir el archivo CSV si es necesario
- **Configuración responsive**: Se adapta a diferentes tamaños de pantalla
- **Caché optimizado**: Mejora el rendimiento con `@st.cache_data`
- **Sesión persistente**: No requiere re-login en cada recarga

### 5. Sistema de Seguridad

✅ **Aplicación pública pero protegida**: La URL es pública pero el contenido requiere login
✅ **Múltiples usuarios**: Diferentes credenciales para diferentes roles
✅ **Contraseña maestra**: Acceso rápido para administradores
✅ **Límite de intentos**: Protección contra ataques de fuerza bruta
✅ **Datos sensibles protegidos**: Solo personal autorizado puede ver las agendas médicas

### 6. URL de acceso

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
