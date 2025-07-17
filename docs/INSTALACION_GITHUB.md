# 📦 Instalación desde GitHub - Agendas Salud

## 🎯 **Para Nuevos Usuarios que Descargan el Proyecto**

### 📋 **Requisitos Previos**

- **Python 3.8+** instalado
- **Git** instalado (opcional, se puede descargar ZIP)
- **Editor de código** (VS Code recomendado)

---

## 🚀 **Opción 1: Clonar con Git**

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/normalizacion_hcsi.git
cd normalizacion_hcsi

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 📁 **Opción 2: Descargar ZIP**

1. **Ir al repositorio**: `https://github.com/TU_USUARIO/normalizacion_hcsi`
2. **Clic en "Code"** → **"Download ZIP"**
3. **Extraer** el archivo ZIP
4. **Abrir terminal** en la carpeta extraída
5. **Seguir pasos** de instalación de dependencias:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## ⚙️ **Configuración Inicial**

### 1. **Verificar Estructura del Proyecto**

```
normalizacion_hcsi/
├── 📁 datos/
│   ├── 📁 excel_originales/agendas_originales/  # 12 archivos Excel
│   ├── 📁 csv_procesado/                        # Datos consolidados
│   └── 📁 csv_extras/                          # Reportes adicionales
├── 📁 docs/                                    # Documentación
├── 📄 app_agendas.py                           # Aplicación principal
├── 📄 agendas.py                               # Procesador de datos
├── 📄 auth_config.py                           # Configuración de autenticación
├── 📄 requirements.txt                         # Dependencias
└── 📄 secrets.toml.example                     # Ejemplo de configuración
```

### 2. **Configurar Autenticación (Opcional)**

```bash
# Copiar archivo de ejemplo
cp secrets.toml.example .streamlit/secrets.toml

# Editar contraseñas (opcional para desarrollo local)
# El archivo ya tiene contraseñas por defecto para desarrollo
```

### 3. **Probar Instalación**

```bash
# Verificar que Python encuentra las dependencias
python -c "import streamlit, pandas, openpyxl; print('✅ Todas las dependencias instaladas')"

# Probar el procesador de datos
python agendas.py

# Iniciar la aplicación web
streamlit run app_agendas.py
```

---

## 🔐 **Sistema de Autenticación**

### **Usuarios por Defecto (Desarrollo Local):**

| Usuario | Password | Acceso |
|---------|----------|--------|
| `admin` | `admin123` | Completo |
| `gerencia` | `gerencia123` | Gerencial + General |
| `medico` | `medico123` | Solo visualización |

### **Tab Gerencial:**
- **Password adicional**: `gerencia2024`
- **Acceso**: Detección de conflictos y análisis avanzado

### **⚠️ Cambiar Contraseñas en Producción:**

Para uso real, editar `.streamlit/secrets.toml`:

```toml
[auth]
admin_password = "TU_NUEVA_CONTRASEÑA_ADMIN"
gerencia_password = "TU_NUEVA_CONTRASEÑA_GERENCIA"
medico_password = "TU_NUEVA_CONTRASEÑA_MEDICO"
master_password = "TU_NUEVA_CONTRASEÑA_MASTER"
```

---

## 📊 **Uso Básico**

### 1. **Ejecutar Aplicación**

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Iniciar aplicación
streamlit run app_agendas.py
```

### 2. **Acceder a la Aplicación**

1. **Abrir navegador**: `http://localhost:8501`
2. **Login**: Usar uno de los usuarios por defecto
3. **Explorar tabs**:
   - 🏥 **Información**: Overview del sistema
   - 📊 **Datos**: Tabla completa de agendas
   - 📈 **Análisis**: Gráficos y estadísticas
   - 🔍 **Búsqueda**: Filtros avanzados
   - 📋 **Reportes**: Exportar datos
   - ⚕️ **Médicos**: Información de profesionales
   - 👔 **Gerencial**: Detección de conflictos (requiere auth adicional)

### 3. **Procesar Nuevos Datos**

```bash
# Si tienes nuevos archivos Excel, colocarlos en:
# datos/excel_originales/agendas_originales/

# Ejecutar procesamiento
python agendas.py

# Los resultados se guardan automáticamente en:
# datos/csv_procesado/agendas_consolidadas.csv
```

---

## 🔧 **Personalización**

### **Agregar Nuevos Centros de Salud:**

Editar `agendas.py`, función `detectar_centro_salud()`:

```python
def detectar_centro_salud(self, filename):
    """Detecta centro de salud desde nombre del archivo"""
    filename_lower = filename.lower()
    
    # Agregar nuevos centros aquí
    if 'nuevo_centro' in filename_lower:
        return 'Nuevo Centro de Salud'
    # ... resto del código
```

### **Agregar Nuevas Especialidades:**

Editar `agendas.py`, lista `especialidades_medicas`:

```python
especialidades_medicas = [
    # Especialidades existentes...
    'nueva_especialidad',
    'otra_especialidad',
]
```

---

## 🚨 **Solución de Problemas**

### **Error: "Module not found"**
```bash
# Verificar entorno virtual activado
venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### **Error: "No data found"**
```bash
# Verificar archivos Excel en la ruta correcta
ls datos/excel_originales/agendas_originales/

# Ejecutar procesamiento
python agendas.py
```

### **Error: "Authentication failed"**
```bash
# Verificar archivo de configuración
cat .streamlit/secrets.toml

# Usar contraseñas por defecto si no existe el archivo
# admin / admin123
# gerencia / gerencia123
# medico / medico123
```

### **Puerto ocupado**
```bash
# Usar puerto diferente
streamlit run app_agendas.py --server.port 8502
```

---

## 📞 **Soporte**

### **Documentación Adicional:**
- `docs/README.md` - Descripción completa del proyecto
- `docs/MANUAL_USUARIO.md` - Guía detallada de uso
- `docs/ARQUITECTURA.md` - Documentación técnica

### **Logs y Debugging:**
```bash
# Ejecutar con logs detallados
streamlit run app_agendas.py --logger.level debug

# Ver errores de Python
python agendas.py 2>&1 | tee error.log
```

---

## 🎉 **¡Listo para Usar!**

Una vez completada la instalación:

✅ **Sistema de agendas médicas** funcionando  
✅ **Autenticación** configurada  
✅ **Datos procesados** y listos  
✅ **Interfaz web** accesible  

**¡Tu sistema de gestión de agendas médicas está listo para usar!** 🏥
