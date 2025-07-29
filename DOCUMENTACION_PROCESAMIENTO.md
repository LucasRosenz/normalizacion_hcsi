# Documentación de Procesamiento de Variables - Dashboard Agendas HCSI

## Descripción General
Este documento describe el procesamiento exacto de cada variable en el sistema de agendas HCSI, incluyendo las **reglas de asignación** y **lógica de transformación** para cada valor específico.

---

## 1. Variable: DOCTOR

### Procesamiento Actual:
```python
df['doctor'] = df['doctor'].fillna('Sin asignar')

# Limpiar valores incorrectos en campo doctor
# Regla: Si doctor contiene "CONSULTORIO" seguido de números, asignar "Sin asignar"
df.loc[df['doctor'].str.contains(r'CONSULTORIO\s+\d+', case=False, na=False), 'doctor'] = 'Sin asignar'
```

### Lógica de Transformación:
- **Valores nulos (NaN)** → `'Sin asignar'`
- **Valores vacíos ('')** → Se mantienen como están
- **Patrones incorrectos** → Se corrigen según reglas específicas
- **Otros valores** → Se mantienen sin modificación

### Reglas de Asignación:
1. **Consultorio como doctor**: Si el valor contiene "CONSULTORIO" seguido de espacios y números → se asigna campo vacío `''`
   - **Patrón detectado**: `CONSULTORIO 23`, `CONSULTORIO 15`, etc.
   - **Motivo**: Los consultorios no son doctores, son ubicaciones físicas
   - **Ejemplo**: `"CONSULTORIO 23"` → `""`
   - **Implementación**: Regex `r'CONSULTORIO\s+\d+'` con flag `re.IGNORECASE` en `agendas.py`, método `extraer_componentes_agenda`

2. **Normalización de días abreviados**: Si el valor contiene "Sáb" → se normaliza a "Sábado"
   - **Patrón detectado**: `"Sáb"`
   - **Motivo**: Mantener consistencia en nombres de días
   - **Ejemplo**: `"Sáb"` → `"Sábado"`
   - **Implementación**: `df['dia'].replace({'Sáb': 'Sábado'})` en `agendas.py`, método `procesar_directorio`

3. **Procedimientos médicos como doctor**: Si el valor es exactamente una sigla de procedimiento médico → se asigna campo vacío `''`
   - **Patrones detectados**: `ECG`, `EKG`, `RX`, `LAB`, `LABORATORIO`, `RADIOLOGIA`, `ECOGRAFIA`, `TAC`, `RMN`, `PREOCUPACIONAL`
   - **Motivo**: Las siglas de procedimientos y tipos de exámenes no son nombres de doctores
   - **Ejemplo**: `"ECG"` → `""`, `"PREOCUPACIONAL"` → `""`
   - **Implementación**: Lista de procedimientos médicos con comparación exacta en `agendas.py`, método `extraer_componentes_agenda`

---

## 2. Variable: ÁREA

### Procesamiento Actual:
```python
df['area'] = df['area'].fillna('Sin área')
```

### Lógica de Transformación:
- **Valores nulos (NaN)** → `'Sin área'`
- **Valores vacíos ('')** → Se mantienen como están
- **Otros valores** → Se mantienen sin modificación

### Reglas de Asignación:
*(Pendiente de análisis - se documentarán las reglas específicas como:)*
- *Ejemplo: Si aparece "Pediatría" → se asigna como área específica*
- *Ejemplo: Si aparece patrón X → se normaliza a valor Y*

---

## 3. Variable: TIPO_TURNO

### Procesamiento Actual:
```python
df['tipo_turno'] = df['tipo_turno'].fillna('No especificado')
```

### Lógica de Transformación:
- **Valores nulos (NaN)** → `'No especificado'`
- **Valores vacíos ('')** → Se mantienen como están
- **Otros valores** → Se mantienen sin modificación

### Reglas de Asignación:
*(Pendiente de análisis - se documentarán las reglas específicas como:)*
- *Ejemplo: Si aparece "Espontanea" → se asigna como tipo de turno específico*
- *Ejemplo: Si aparece "Programada" → se procesa de manera particular*

---

## 4. Variable: DÍA

### Procesamiento Actual:
```python
df['dia'] = df['dia'].replace({'Sáb': 'Sábado'})
```

### Lógica de Transformación:
- **'Sáb'** → `'Sábado'`
- **Otros valores** → Se mantienen sin modificación

### Reglas de Asignación:
- **Normalización de días abreviados**: Convierte abreviaciones inconsistentes a nombres completos
- **Patrón específico**: `'Sáb'` se normaliza a `'Sábado'` para mantener consistencia

---

## Historial de Cambios
- **29/07/2025**: Creación inicial del documento
- **29/07/2025**: Actualización para incluir sección "Reglas de Asignación" en lugar de solo valores únicos
- **29/07/2025**: **Corrección #1** - Variable DOCTOR: Agregada regla para detectar y corregir "CONSULTORIO + número" como doctor incorrecta. Implementación en `agendas.py`, método `extraer_componentes_agenda`
- **29/07/2025**: **Corrección #2** - Variable DIA: Agregada normalización de "Sáb" → "Sábado" para mantener consistencia. Movido de `app_agendas.py` a `agendas.py`, método `procesar_directorio`
- **29/07/2025**: **Corrección #3** - Variable DOCTOR: Agregada regla para detectar procedimientos médicos (ECG, RX, LAB, etc.) que aparecen incorrectamente como doctores. Implementación en `agendas.py`, método `extraer_componentes_agenda`

---

## Notas Importantes
- **Prioridad**: Este documento debe reflejar las reglas exactas de procesamiento, no solo los resultados
- **Actualización**: Cada corrección aplicada debe documentar la regla específica utilizada
- **Formato**: Para cada valor procesado se debe explicar el patrón que lo identifica y la transformación aplicada
- **Ejemplos**: Incluir ejemplos concretos del tipo "Si aparece X → se procesa como Y"
