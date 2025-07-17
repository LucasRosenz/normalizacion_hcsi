# Configuración de Seguridad para Deployment

## 🔐 Estrategias para Proteger Datos Sensibles

### 1. **Repositorio Público + Datos Privados**

#### ✅ QUÉ INCLUIR en el repositorio público:
- Código de la aplicación (`app_agendas.py`, `agendas.py`)
- Estructura del proyecto
- Documentación
- `requirements.txt`
- Datos de ejemplo (NO reales)

#### ❌ QUÉ NO INCLUIR:
- Datos médicos reales
- Credenciales reales
- Archivos Excel con información personal

### 2. **Usar Streamlit Secrets (Recomendado)**

#### En el repositorio (archivo `.streamlit/secrets.toml`):
```toml
# Este archivo NO se sube al repositorio (agregarlo a .gitignore)
[auth]
admin_password = "contraseña_super_segura_123"
gerencia_password = "gerencia_ultra_segura_456" 
master_password = "master_key_extrema_789"

[database]
csv_url = "https://tu-servidor-privado.com/datos.csv"
```

#### En el código (`auth_config.py`):
```python
import streamlit as st

# Para desarrollo local
USERS = {
    "admin": st.secrets.get("auth", {}).get("admin_password", "admin123"),
    "gerencia": st.secrets.get("auth", {}).get("gerencia_password", "gerencia2024")
}

MASTER_PASSWORD = st.secrets.get("auth", {}).get("master_password", "master123")
```

### 3. **Datos Seguros - Opciones:**

#### A) **Servidor de Datos Privado**
- Subir CSV a Google Drive/Dropbox privado
- Usar URL con token de acceso
- La app descarga datos en tiempo real

#### B) **Base de Datos Externa**
- PostgreSQL en Heroku/Railway
- Google Sheets privada con API
- Supabase con autenticación

#### C) **Datos Enmascarados**
- Para demo pública: usar datos ficticios
- Nombres de médicos → "Dr. A", "Dr. B"
- Centros → "Centro 1", "Centro 2"

### 4. **Configuración en Streamlit Cloud**

1. **Secrets Management:**
   - En Streamlit Cloud → App settings → Secrets
   - Agregar variables sensibles

2. **Deploy Settings:**
   ```
   Repository: tu-usuario/agendas-medicas-public
   Branch: main
   Main file: app_agendas.py
   ```

### 5. **Alternativas de Deployment Privado**

#### Opciones con repositorio privado:
- **Heroku** ($7/mes) - soporta repos privados
- **Railway** - plan gratuito con repos privados
- **DigitalOcean App Platform** - desde $5/mes
- **Render** - plan gratuito limitado

### 6. **Configuración .gitignore**

```gitignore
# Datos sensibles
datos/excel_originales/
datos/csv_procesado/agendas_consolidadas.csv
datos/csv_extras/

# Configuración local
.streamlit/secrets.toml
auth_config_real.py

# Archivos temporales
__pycache__/
*.pyc
.env
```

## 🎯 **Recomendación Final**

Para un sistema médico real:

1. **Demo Pública**: Repositorio público con datos ficticios
2. **Sistema Real**: Deployment privado (Heroku/Railway) + datos reales
3. **Autenticación robusta**: OAuth/LDAP en lugar de contraseñas hardcodeadas

## 💡 ¿Cuál prefieres?

- **Opción A**: Demo pública con datos enmascarados
- **Opción B**: Deployment privado ($5-7/mes)
- **Opción C**: Híbrido (demo pública + versión privada)
