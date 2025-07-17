# 🚀 Guía de Deployment - Agendas Salud

## � **Configuración Actual: Repositorio Público con Autenticación**

✅ **Repositorio público** en GitHub  
✅ **Datos médicos reales** incluidos  
✅ **Autenticación robusta** con contraseñas seguras  
✅ **Deployment gratuito** en Streamlit Cloud  

---

## � **Pasos para Deployment en Streamlit Cloud**

### 1. Subir a GitHub

```bash
# Verificar que todo esté actualizado
git status
git add .
git commit -m "Versión final para deployment público con autenticación"
git push origin main
```

### 2. Configurar Streamlit Cloud

1. **Ir a**: [share.streamlit.io](https://share.streamlit.io)
2. **Conectar GitHub** y seleccionar tu repositorio
3. **Configurar app**:
   - **Repository**: `tu-usuario/normalizacion_hcsi`
   - **Branch**: `main`
   - **Main file path**: `app_agendas.py`
   - **Python version**: `3.9+`

### 3. ⚠️ **IMPORTANTE: Configurar Secrets**

En **Advanced settings → Secrets**, agregar:

```toml
[auth]
admin_password = "TU_CONTRASEÑA_ADMIN_SUPER_SEGURA_2024"
gerencia_password = "TU_CONTRASEÑA_GERENCIA_ULTRA_SEGURA_2024"
medico_password = "TU_CONTRASEÑA_MEDICO_MUY_SEGURA_2024"
master_password = "TU_MASTER_PASSWORD_EXTREMADAMENTE_SEGURA_2024"
```

**📝 Recomendaciones para contraseñas:**
- **Mínimo 16 caracteres**
- **Combinación**: letras mayúsculas, minúsculas, números, símbolos
- **Únicas**: no reutilizar
- **Ejemplo**: `MedAgend@2024!#SecAdm`

### 4. Deploy

1. **Hacer clic en "Deploy"**
2. **Esperar 2-3 minutos** mientras se instalan dependencias
3. **¡Tu app estará disponible públicamente!**

---

## 🔐 **Sistema de Autenticación**

### **Usuarios configurados:**
- **`admin`**: Acceso completo a todos los datos y funciones
- **`gerencia`**: Acceso a tab gerencial con detección de conflictos
- **`medico`**: Acceso a visualización de agendas

### **Funciones protegidas:**
- ✅ **Login obligatorio** para acceder a la aplicación
- ✅ **Tab Gerencial** protegido con password adicional
- ✅ **Logout automático** por seguridad
- ✅ **Manejo de sesiones** seguro

---

## 📊 **Datos Incluidos**

### **Estructura actual:**
```
datos/
├── excel_originales/agendas_originales/  # 12 archivos Excel
├── csv_procesado/                        # Datos consolidados
└── csv_extras/                          # Reportes y conflictos
```

### **Estadísticas:**
- **1,589 registros** de horarios médicos
- **391 médicos únicos**
- **12 centros de salud**
- **46 áreas médicas**

---

## 🛡️ **Seguridad Implementada**

### **En Desarrollo Local:**
- Contraseñas por defecto (débiles, solo para pruebas)
- Variables de entorno opcionales

### **En Producción (Streamlit Cloud):**
- **Streamlit Secrets** para contraseñas seguras
- **HTTPS automático** 
- **Autenticación de sesión** robusta

### **Código de seguridad:**
```python
# auth_config.py - Configuración inteligente
def get_auth_config():
    try:
        # Usar Streamlit Secrets en producción
        if hasattr(st, 'secrets') and 'auth' in st.secrets:
            return st.secrets["auth"]
    except:
        pass
    # Fallback para desarrollo local
    return valores_por_defecto
```

---

## 🎯 **URLs de Acceso**

### **Después del deployment:**
- **URL principal**: `https://tu-app-name.streamlit.app`
- **Login requerido**: Todos los usuarios deben autenticarse
- **Tab gerencial**: Password adicional `gerencia2024` (cambiar en secrets)

---

## 🔧 **Configuración Avanzada (Opcional)**

### **Variables de Entorno Locales:**
```bash
# Para desarrollo local con contraseñas personalizadas
export ADMIN_PASSWORD="mi_password_admin"
export GERENCIA_PASSWORD="mi_password_gerencia"
export MEDICO_PASSWORD="mi_password_medico"
export MASTER_PASSWORD="mi_master_password"
```

### **Actualizar después del deployment:**
1. **Cambiar secrets** en Streamlit Cloud
2. **Reiniciar app** automáticamente
3. **Probar login** con nuevas contraseñas

---

## ✅ **Checklist Final**

Antes de hacer público:

- [ ] **Contraseñas configuradas** en Streamlit Secrets
- [ ] **App funcionando** localmente
- [ ] **Datos actualizados** (ejecutar `python agendas.py`)
- [ ] **Repositorio limpio** (sin archivos temporales)
- [ ] **Documentación actualizada**

---

## � **Importante**

⚠️ **Este deployment incluye datos médicos reales**  
⚠️ **Solo personal autorizado debe tener acceso**  
⚠️ **Cambiar contraseñas por defecto obligatoriamente**  
⚠️ **Monitorear accesos regularmente**

---

## � **Soporte**

Si hay problemas con el deployment:

1. **Verificar logs** en Streamlit Cloud
2. **Comprobar secrets** están configurados
3. **Revisar requirements.txt** actualizado
4. **Testear locally** antes de deploy

**¡Tu aplicación de Agendas Salud estará lista para uso profesional!** 🎉
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
