# Sistema de Autenticación - HCSI
## Configuración de Seguridad

### Credenciales por defecto

**IMPORTANTE: Cambiar estas credenciales antes del despliegue en producción**

#### Usuarios del sistema:
- **admin** / `hcsi2024` - Administrador del sistema
- **medico** / `agendas123` - Personal médico  
- **director** / `director2024` - Dirección médica
- **enfermeria** / `enfermeria2024` - Personal de enfermería
- **secretaria** / `secretaria2024` - Personal administrativo

#### Acceso rápido:
- **Contraseña maestra:** `HCSI_SanIsidro_2024`

### Características de seguridad

✅ **Protección por contraseña**: Acceso restringido solo a personal autorizado
✅ **Múltiples usuarios**: Diferentes roles y permisos
✅ **Contraseña maestra**: Acceso rápido para administradores
✅ **Límite de intentos**: Máximo 5 intentos fallidos antes del bloqueo temporal
✅ **Sesión persistente**: No requiere re-login en cada recarga
✅ **Configuración externa**: Credenciales en archivo separado para fácil modificación

### Cómo cambiar las credenciales

1. **Editar archivo `auth_config.py`**:
   ```python
   USERS = {
       "admin": "tu_nueva_contraseña_admin",
       "medico": "tu_nueva_contraseña_medico",
       "director": "tu_nueva_contraseña_director"
   }
   
   MASTER_PASSWORD = "Tu_Nueva_Contraseña_Maestra_2024"
   ```

2. **Reiniciar la aplicación** después de los cambios

### Funcionalidades del sistema de autenticación

- **Pantalla de login elegante**: Interfaz profesional con logo y información
- **Doble método de acceso**: Usuario/contraseña individual o contraseña maestra
- **Información de usuarios**: Lista de usuarios disponibles sin revelar contraseñas
- **Botón de logout**: Cierre de sesión seguro desde la sidebar
- **Protección contra ataques**: Límite de intentos fallidos
- **Feedback visual**: Mensajes claros de éxito y error

### Contacto y soporte

- **Email**: lrosenzvit@sanisidro.gob.ar
- **Sistema**: Sistema de Agendas HCSI
- **Organización**: Hospital de Clínicas San Isidro

### Notas importantes

1. **Seguridad**: Aunque la aplicación es pública en Streamlit Cloud, los datos están protegidos por autenticación
2. **Performance**: La autenticación no afecta el rendimiento de la aplicación
3. **Usabilidad**: Una vez autenticado, el usuario puede usar todas las funcionalidades normalmente
4. **Escalabilidad**: Fácil añadir nuevos usuarios editando el archivo de configuración

### Despliegue en Streamlit Cloud

Para desplegar con autenticación:

1. Subir todos los archivos incluidos `auth.py` y `auth_config.py`
2. La aplicación será pública pero protegida por login
3. Solo usuarios con credenciales correctas podrán acceder
4. Cambiar las credenciales por defecto antes del despliegue

### Archivos del sistema de autenticación

- `auth.py` - Lógica principal del sistema de autenticación
- `auth_config.py` - Configuración de usuarios y contraseñas
- `app_agendas.py` - Aplicación principal con autenticación integrada
