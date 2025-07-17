# 🔐 CREDENCIALES DE ACCESO - CAMBIAR ANTES DEL DESPLIEGUE

## ⚠️ IMPORTANTE: SEGURIDAD

**ESTAS SON LAS CREDENCIALES POR DEFECTO - DEBEN SER CAMBIADAS ANTES DEL DESPLIEGUE EN PRODUCCIÓN**

## Credenciales actuales (TEMPORALES):

### Usuarios individuales:
- **admin** / `hcsi2024`
- **medico** / `agendas123`
- **director** / `director2024`
- **enfermeria** / `enfermeria2024`
- **secretaria** / `secretaria2024`

### Contraseña maestra:
- `HCSI_SanIsidro_2024`

## 🚨 Para cambiar las credenciales:

1. **Edita el archivo `auth_config.py`**
2. **Cambia las contraseñas por otras seguras**
3. **Usa contraseñas fuertes:**
   - Mínimo 12 caracteres
   - Combinación de mayúsculas, minúsculas, números y símbolos
   - No usar información personal o predecible

## Ejemplo de credenciales seguras:

```python
USERS = {
    "admin": "Hcsi2024Admin!Seguro",
    "medico": "MedicoHcsi#2024$Fuerte", 
    "director": "DirectorSeguro&2024@Hcsi",
    "enfermeria": "Enfermeria!Hcsi2024#",
    "secretaria": "Secretaria@Hcsi$2024"
}

MASTER_PASSWORD = "MaestraHCSI!2024#SanIsidro$Segura"
```

## 📋 Lista de verificación antes del despliegue:

- [ ] Cambiar todas las contraseñas en `auth_config.py`
- [ ] Verificar que las contraseñas son fuertes
- [ ] Probar el login localmente con las nuevas credenciales
- [ ] Comunicar las nuevas credenciales al personal autorizado
- [ ] Eliminar este archivo después del despliegue (contiene credenciales temporales)

## 👥 Distribución de credenciales:

- **admin**: Para administradores de sistemas/IT
- **director**: Para dirección médica y supervisores
- **medico**: Para personal médico en general
- **enfermeria**: Para personal de enfermería
- **secretaria**: Para personal administrativo

## 🔄 Mantenimiento de credenciales:

- Cambiar las contraseñas periódicamente (cada 3-6 meses)
- No compartir credenciales por medios inseguros
- Usar un gestor de contraseñas institucional si está disponible
- Mantener un registro de quién tiene acceso a cada usuario

---

**RECORDATORIO**: Este archivo contiene credenciales temporales de demostración. Elimínalo después de configurar las credenciales definitivas.
