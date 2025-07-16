import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import os
import sys
from contextlib import contextmanager
import warnings

# Configurar warnings para evitar mensajes innecesarios
warnings.filterwarnings('ignore')

# Configuración de optimización
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

# Context manager para manejo de errores
@contextmanager
def error_handler(operation_name="operación"):
    try:
        yield
    except Exception as e:
        st.error(f"Error en {operation_name}: {str(e)[:200]}...")
        st.info("Si el problema persiste, intenta recargar la página o contacta al soporte.")

# Función para limpiar caché si es necesario
def limpiar_cache():
    """Limpia el caché de Streamlit"""
    if st.button("🔄 Limpiar caché y recargar"):
        st.cache_data.clear()
        st.rerun()

# Configuración de la página
st.set_page_config(
    page_title="Agendas HCSI - Visualización",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/LucasRosenz/normalizacion_hcsi',
        'Report a bug': 'mailto:lrosenzvit@sanisidro.gob.ar',
        'About': 'Sistema de visualización de agendas médicas - Hospital de Clínicas San Isidro'
    }
)

# Título principal
st.title("🏥 Visualización de agendas médicas")
st.markdown("### Sistema integral de análisis de horarios - Hospital de Clínicas San Isidro")

# Información sobre la aplicación
with st.expander("ℹ️ Información de la aplicación"):
    st.markdown("""
    **Sistema de visualización de agendas médicas**
    
    Esta aplicación permite analizar y visualizar las agendas médicas consolidadas de múltiples centros de salud.
    
    **Funcionalidades principales:**
    - 📊 Análisis general con métricas y gráficos
    - 📅 Visualización por días de la semana
    - 🏥 Comparativa entre centros de salud
    - 📋 Tabla completa con filtros avanzados
    - 🗓️ Vista calendario tipo agenda
    - 🔍 Análisis UNIQUE para explorar valores únicos
    - ⚙️ Panel de gestión con detección de conflictos
    
    **Desarrollado por:** Lucas Rosenzvit - lrosenzvit@sanisidro.gob.ar
    """)

# Verificar si hay datos disponibles
data_status = st.empty()
with data_status:
    if os.path.exists("agendas_consolidadas.csv"):
        file_size = os.path.getsize("agendas_consolidadas.csv")
        st.success(f"✅ Datos cargados correctamente ({file_size/1024:.1f} KB)")
    else:
        st.warning("⚠️ No se encontró archivo de datos. Se intentará generar automáticamente.")

@st.cache_data(ttl=3600)  # Cache por 1 hora
def cargar_datos():
    """Carga los datos de agendas consolidadas con caché optimizado"""
    with error_handler("carga de datos"):
        # Mostrar progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Verificando archivos...")
        progress_bar.progress(10)
        
        # Intentar cargar el archivo CSV
        if os.path.exists("agendas_consolidadas.csv"):
            status_text.text("Cargando datos existentes...")
            progress_bar.progress(30)
            df = pd.read_csv("agendas_consolidadas.csv")
        else:
            status_text.text("Generando datos...")
            progress_bar.progress(20)
            
            try:
                # Primero intentar con el procesador real
                from agendas import main as procesar_agendas
                status_text.text("Procesando archivos Excel...")
                progress_bar.progress(40)
                procesar_agendas()
                
                # Cargar datos generados
                if os.path.exists("agendas_consolidadas.csv"):
                    df = pd.read_csv("agendas_consolidadas.csv")
                else:
                    raise FileNotFoundError("No se pudo generar con datos reales")
                    
            except Exception as e:
                # Si no funciona el procesador real, usar datos de ejemplo
                status_text.text("Generando datos de ejemplo...")
                progress_bar.progress(60)
                
                from generar_datos_ejemplo import crear_archivo_ejemplo
                crear_archivo_ejemplo()
                df = pd.read_csv("agendas_consolidadas.csv")
                st.info("📊 Usando datos de ejemplo para demostración")
        
        status_text.text("Procesando datos...")
        progress_bar.progress(70)
        
        # Validar que el DataFrame no esté vacío
        if df.empty:
            raise ValueError("El archivo de datos está vacío")
        
        # Limpiar datos de forma eficiente
        df = df.fillna({
            'doctor': 'Sin asignar',
            'area': 'Sin área', 
            'tipo_turno': 'No especificado'
        })
        
        status_text.text("Finalizando...")
        progress_bar.progress(90)
        
        # Convertir horas a datetime para mejor manejo (solo si es necesario)
        try:
            df['hora_inicio_dt'] = pd.to_datetime(df['hora_inicio'], format='%H:%M', errors='coerce').dt.time
            df['hora_fin_dt'] = pd.to_datetime(df['hora_fin'], format='%H:%M', errors='coerce').dt.time
        except:
            pass  # Si hay error, continuar sin las columnas de tiempo
        
        progress_bar.progress(100)
        status_text.text("¡Datos cargados exitosamente!")
        
        # Limpiar elementos de progreso después de un momento
        import time
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return df

# Cargar datos con manejo de errores
with st.spinner("Cargando datos..."):
    df = cargar_datos()

# Verificar carga exitosa
if df.empty:
    st.error("❌ No se pudieron cargar los datos.")
    st.info("💡 Opciones para resolver:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Opción 1: Subir archivo CSV**")
        uploaded_file = st.file_uploader("Sube agendas_consolidadas.csv", type=['csv'])
        
        if uploaded_file is not None:
            try:
                # Guardar archivo subido
                with open("agendas_consolidadas.csv", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("✅ Archivo subido exitosamente")
                st.rerun()
            except Exception as e:
                st.error(f"Error subiendo archivo: {e}")
    
    with col2:
        st.markdown("**Opción 2: Generar datos de ejemplo**")
        if st.button("🔄 Generar datos de ejemplo"):
            try:
                from generar_datos_ejemplo import crear_archivo_ejemplo
                crear_archivo_ejemplo()
                st.success("✅ Datos de ejemplo generados")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Opción para limpiar caché
        st.markdown("**Opción 3: Limpiar caché**")
        limpiar_cache()
    
    st.stop()

# Mostrar información de los datos cargados
st.success(f"✅ Datos cargados: {len(df):,} registros")
data_status.empty()  # Limpiar el mensaje de estado anterior

# Sidebar con filtros
st.sidebar.header("Filtros")

# Filtro por efector
efectores_disponibles = ['Todos'] + sorted(df['efector'].unique().tolist())
efector_seleccionado = st.sidebar.selectbox(
    "Hospital/CAPS:",
    efectores_disponibles
)

# Filtro por área médica
areas_disponibles = ['Todas'] + sorted(df[df['area'] != 'Sin área']['area'].unique().tolist())
area_seleccionada = st.sidebar.selectbox(
    "Área:",
    areas_disponibles
)

# Filtro por día de la semana
dias_disponibles = ['Todos'] + sorted(df['dia'].unique().tolist())
dia_seleccionado = st.sidebar.selectbox(
    "Día:",
    dias_disponibles
)

# Filtro por tipo de turno
tipos_turno_disponibles = ['Todos'] + sorted(df[df['tipo_turno'] != 'No especificado']['tipo_turno'].unique().tolist())
tipo_turno_seleccionado = st.sidebar.selectbox(
    "Tipo de agenda:",
    tipos_turno_disponibles
)

# Filtro por médico
medicos_disponibles = ['Todos'] + sorted(df[df['doctor'] != 'Sin asignar']['doctor'].unique().tolist())
medico_seleccionado = st.sidebar.selectbox(
    "Médico:",
    medicos_disponibles
)

# Aplicar filtros
df_filtrado = df.copy()

if efector_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['efector'] == efector_seleccionado]

if area_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['area'] == area_seleccionada]

if dia_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['dia'] == dia_seleccionado]

if tipo_turno_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['tipo_turno'] == tipo_turno_seleccionado]

if medico_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['doctor'] == medico_seleccionado]

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Contar agendas únicas (combinación de nombre_original_agenda + efector)
    total_agendas_unicas = df_filtrado.groupby(['nombre_original_agenda', 'efector']).ngroups
    total_registros = len(df_filtrado)
    st.metric(
        label="Total de agendas",
        value=f"{total_agendas_unicas:,}",
        delta=f"{total_registros:,} horarios" if total_agendas_unicas != total_registros else None
    )

with col2:
    doctores_unicos = df_filtrado[df_filtrado['doctor'] != 'Sin asignar']['doctor'].nunique()
    st.metric(
        label="Médicos activos",
        value=doctores_unicos
    )

with col3:
    areas_unicas = df_filtrado[df_filtrado['area'] != 'Sin área']['area'].nunique()
    st.metric(
        label="Especialidades",
        value=areas_unicas
    )

with col4:
    efectores_unicos = df_filtrado['efector'].nunique()
    st.metric(
        label="Centros de salud",
        value=efectores_unicos
    )

# Separador
st.markdown("---")

# Layout principal con tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Resumen general", "Horarios por día", "Comparativa centros", "Tabla completa", "Calendario", "Análisis UNIQUE", "Gestión"])

with tab1:
    st.header("Resumen general")

    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de agendas únicas por área médica
        df_areas = df_filtrado[df_filtrado['area'] != 'Sin área']
        if not df_areas.empty:
            areas_count_series = df_areas.groupby('area').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups).sort_values(ascending=False).head(10)
            
            fig_areas = px.bar(
                x=areas_count_series.values,
                y=areas_count_series.index,
                orientation='h',
                title="Top 10 especialidades por número de agendas",
                labels={'x': 'Número de agendas', 'y': 'Especialidad'},
                color=areas_count_series.values,
                color_continuous_scale='viridis'
            )
            fig_areas.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_areas, use_container_width=True)
        else:
            st.info("No hay especialidades disponibles con los filtros aplicados.")
    
    with col2:
        # Gráfico de agendas únicas por día de la semana
        if not df_filtrado.empty:
            dias_count = df_filtrado.groupby('dia').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups)
            
            fig_dias = px.pie(
                values=dias_count.values,
                names=dias_count.index,
                title="Distribución de agendas por día de la semana"
            )
            fig_dias.update_traces(textposition='inside', textinfo='percent+label')
            fig_dias.update_layout(height=400)
            st.plotly_chart(fig_dias, use_container_width=True)
        else:
            st.info("No hay datos disponibles con los filtros aplicados.")
    
    # Gráfico de agendas únicas por efector
    if not df_filtrado.empty:
        efectores_count = df_filtrado.groupby('efector').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups)
        
        fig_efectores = px.bar(
            x=efectores_count.index,
            y=efectores_count.values,
            title="Número de agendas por centro de salud",
            labels={'x': 'Centro de salud', 'y': 'Número de agendas'},
            color=efectores_count.values,
            color_continuous_scale='plasma'
        )
        fig_efectores.update_layout(
            height=400,
            xaxis_tickangle=-45,
            showlegend=False
        )
        st.plotly_chart(fig_efectores, use_container_width=True)
    else:
        st.info("No hay datos disponibles con los filtros aplicados.")

with tab2:
    st.header("Análisis de horarios por día")
    
    # Selector de día específico para análisis detallado
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dia_analisis = st.selectbox(
        "Día para análisis detallado:",
        dias_orden,
        key="dia_analisis"
    )
    
    df_dia = df_filtrado[df_filtrado['dia'] == dia_analisis]
    
    if not df_dia.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap de horarios
            if 'hora_inicio' in df_dia.columns:
                # Crear bins de horas
                df_dia_copy = df_dia.copy()
                df_dia_copy['hora_inicio_num'] = pd.to_datetime(df_dia_copy['hora_inicio'], format='%H:%M', errors='coerce').dt.hour
                
                heatmap_data = df_dia_copy.groupby(['efector', 'hora_inicio_num']).size().reset_index(name='count')
                
                if not heatmap_data.empty:
                    fig_heatmap = px.density_heatmap(
                        heatmap_data,
                        x='hora_inicio_num',
                        y='efector',
                        z='count',
                        title=f"Intensidad de agendas - {dia_analisis}",
                        labels={'hora_inicio_num': 'Hora', 'efector': 'Centro de salud', 'count': 'Número de agendas'}
                    )
                    fig_heatmap.update_layout(height=400)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # Top médicos del día (agendas únicas)
            df_medicos_dia = df_dia[df_dia['doctor'] != 'Sin asignar']
            if not df_medicos_dia.empty:
                medicos_dia = df_medicos_dia.groupby('doctor').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups).sort_values(ascending=False).head(10)

                fig_medicos = px.bar(
                    x=medicos_dia.values,
                    y=medicos_dia.index,
                    orientation='h',
                    title=f"Top médicos - {dia_analisis}",
                    labels={'x': 'Número de agendas', 'y': 'Médico'}
                )
                fig_medicos.update_layout(height=400)
                st.plotly_chart(fig_medicos, use_container_width=True)
            else:
                st.info(f"No hay médicos con agendas disponibles para {dia_analisis}.")

        # Tabla detallada del día
        st.subheader(f"Detalle de agendas - {dia_analisis}")
        
        df_mostrar = df_dia[['efector', 'area', 'doctor', 'hora_inicio', 'hora_fin', 'tipo_turno']].copy()
        df_mostrar = df_mostrar.sort_values(['efector', 'hora_inicio'])
        
        st.dataframe(
            df_mostrar,
            use_container_width=True,
            height=300
        )
    else:
        st.warning(f"No hay datos disponibles para {dia_analisis} con los filtros aplicados.")

with tab3:
    st.header("Comparativa entre centros de salud")
    
    # Comparativa de métricas por efector
    def contar_agendas_unicas_por_efector(x):
        return x.groupby(['nombre_original_agenda', 'efector']).ngroups
    
    metricas_efector = df_filtrado.groupby('efector').agg({
        'doctor': lambda x: x[x != 'Sin asignar'].nunique(),
        'area': lambda x: x[x != 'Sin área'].nunique()
    })
    
    # Calcular agendas únicas por separado
    agendas_por_efector = df_filtrado.groupby('efector').apply(contar_agendas_unicas_por_efector)
    metricas_efector['Total agendas'] = agendas_por_efector
    
    metricas_efector = metricas_efector.rename(columns={
        'doctor': 'Médicos',
        'area': 'Especialidades'
    }).reset_index()
    
    # Gráfico comparativo
    fig_comparativa = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Médicos', 'Especialidades', 'Total agendas'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig_comparativa.add_trace(
        go.Bar(x=metricas_efector['efector'], y=metricas_efector['Médicos'], name='Médicos'),
        row=1, col=1
    )
    
    fig_comparativa.add_trace(
        go.Bar(x=metricas_efector['efector'], y=metricas_efector['Especialidades'], name='Especialidades'),
        row=1, col=2
    )
    
    fig_comparativa.add_trace(
        go.Bar(x=metricas_efector['efector'], y=metricas_efector['Total agendas'], name='Total agendas'),
        row=1, col=3
    )
    
    fig_comparativa.update_layout(
        height=500,
        showlegend=False,
        title_text="Comparativa de métricas por centro de salud"
    )
    
    # Rotar etiquetas del eje x
    fig_comparativa.update_xaxes(tickangle=-45)
    
    st.plotly_chart(fig_comparativa, use_container_width=True)
    
    # Tabla comparativa
    st.subheader("Tabla comparativa detallada")
    metricas_efector_sorted = metricas_efector.sort_values('Total agendas', ascending=False)
    st.dataframe(metricas_efector_sorted, use_container_width=True)

with tab4:
    st.header("Tabla completa de agendas")
    
    # Información sobre los datos mostrados
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"Mostrando **{len(df_filtrado):,} registros** de un total de **{len(df):,}** agendas")
    
    with col2:
        # Botón para descargar datos filtrados
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name=f"agendas_filtradas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Opciones de visualización
    st.subheader("Opciones de visualización")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mostrar_nombre_original = st.checkbox("Mostrar nombre original de agenda", value=True)
    
    with col2:
        filas_por_pagina = st.selectbox(
            "Registros por página:",
            [10, 25, 50, 100, 500, "Todos"],
            index=2
        )
    
    with col3:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            ["efector", "area", "doctor", "dia", "hora_inicio"],
            index=0
        )
    
    # Preparar datos para mostrar
    columnas_mostrar = []
    
    if mostrar_nombre_original:
        columnas_mostrar.append('nombre_original_agenda')
    
    columnas_mostrar.extend(['efector', 'area', 'doctor', 'tipo_turno', 'dia', 'hora_inicio', 'hora_fin'])
    
    # Aplicar ordenamiento
    df_mostrar = df_filtrado[columnas_mostrar].copy()
    df_mostrar = df_mostrar.sort_values(ordenar_por)
    
    # Aplicar paginación si es necesario
    if filas_por_pagina != "Todos":
        filas_por_pagina = int(filas_por_pagina)
        
        # Calcular número de páginas
        total_paginas = (len(df_mostrar) - 1) // filas_por_pagina + 1
        
        if total_paginas > 1:
            pagina_actual = st.selectbox(
                f"Página (de {total_paginas}):",
                range(1, total_paginas + 1),
                key="pagina_tabla"
            )
            
            inicio = (pagina_actual - 1) * filas_por_pagina
            fin = inicio + filas_por_pagina
            df_mostrar = df_mostrar.iloc[inicio:fin]
    
    # Mostrar tabla con formato mejorado
    st.subheader(f"Registros de Agendas")
    
    # Aplicar estilos a la tabla
    def highlight_rows(val):
        """Aplica estilos alternados a las filas"""
        return ['background-color: #f0f2f6' if i % 2 == 0 else '' for i in range(len(val))]
    
    # Renombrar columnas para mejor visualización
    nombres_columnas = {
        'nombre_original_agenda': 'Nombre original de agenda',
        'efector': 'Centro de salud',
        'area': 'Especialidad',
        'doctor': 'Médico',
        'tipo_turno': 'Tipo de agenda',
        'dia': 'Día',
        'hora_inicio': 'Hora inicio',
        'hora_fin': 'Hora fin'
    }
    
    df_display = df_mostrar.rename(columns=nombres_columnas)
    
    # Mostrar tabla
    st.dataframe(
        df_display,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Resumen de la tabla actual
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        agendas_mostradas = df_mostrar.groupby(['nombre_original_agenda', 'efector']).ngroups
        st.metric("Agendas mostradas", agendas_mostradas, delta=f"{len(df_mostrar)} horarios")
    
    with col2:
        doctores_tabla = df_mostrar[df_mostrar['doctor'] != 'Sin asignar']['doctor'].nunique()
        st.metric("Médicos", doctores_tabla)
    
    with col3:
        areas_tabla = df_mostrar[df_mostrar['area'] != 'Sin área']['area'].nunique()
        st.metric("Especialidades", areas_tabla)
    
    with col4:
        efectores_tabla = df_mostrar['efector'].nunique()
        st.metric("Centros", efectores_tabla)
    
    # Estadísticas adicionales
    if len(df_mostrar) > 0:
        st.subheader("Estadísticas de la vista actual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 5 médicos en la vista actual (agendas únicas)
            if 'doctor' in df_mostrar.columns:
                df_medicos_vista = df_mostrar[df_mostrar['doctor'] != 'Sin asignar']
                if not df_medicos_vista.empty:
                    top_doctores = df_medicos_vista.groupby('doctor').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups).sort_values(ascending=False).head(5)
                    if not top_doctores.empty:
                        st.write("**Top 5 médicos:**")
                        for i, (doctor, count) in enumerate(top_doctores.items(), 1):
                            st.write(f"{i}. {doctor}: {count} agendas")
                    else:
                        st.info("No hay médicos disponibles.")
                else:
                    st.info("No hay médicos con agendas disponibles.")
        
        with col2:
            # Top 5 especialidades en la vista actual (agendas únicas)
            if 'area' in df_mostrar.columns:
                df_areas_vista = df_mostrar[df_mostrar['area'] != 'Sin área']
                if not df_areas_vista.empty:
                    top_areas = df_areas_vista.groupby('area').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups).sort_values(ascending=False).head(5)
                    if not top_areas.empty:
                        st.write("**Top 5 especialidades:**")
                        for i, (area, count) in enumerate(top_areas.items(), 1):
                            st.write(f"{i}. {area}: {count} agendas")
                    else:
                        st.info("No hay especialidades disponibles.")
                else:
                    st.info("No hay especialidades con agendas disponibles.")

with tab5:
    st.header("Vista calendario - agenda semanal")
    
    # Selectores específicos para la vista calendario
    st.subheader("Configuración de vista")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selector de hospital específico (obligatorio)
        efectores_calendario = sorted(df['efector'].unique().tolist())
        efector_calendario = st.selectbox(
            "Hospital/CAPS:",
            efectores_calendario,
            key="efector_calendario"
        )
    
    with col2:
        # Selector de área específica (obligatorio)
        df_efector = df[df['efector'] == efector_calendario]
        areas_calendario = sorted(df_efector[df_efector['area'] != 'Sin área']['area'].unique().tolist())
        
        if areas_calendario:
            area_calendario = st.selectbox(
                "Especialidad:",
                areas_calendario,
                key="area_calendario"
            )
        else:
            st.warning("No hay especialidades disponibles para este centro de salud.")
            st.stop()
    
    # Filtrar datos para la vista calendario
    df_calendario = df[(df['efector'] == efector_calendario) & (df['area'] == area_calendario)]
    
    if not df_calendario.empty:
        st.success(f"Mostrando agenda de **{area_calendario}** en **{efector_calendario}**")
        
        # Métricas específicas del calendario
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Contar agendas únicas en el calendario
            total_agendas_calendario = df_calendario.groupby(['nombre_original_agenda', 'efector']).ngroups
            total_horarios_calendario = len(df_calendario)
            st.metric("Total agendas", total_agendas_calendario, delta=f"{total_horarios_calendario} horarios")
        
        with col2:
            doctores_calendario = df_calendario[df_calendario['doctor'] != 'Sin asignar']['doctor'].nunique()
            st.metric("Médicos", doctores_calendario)
        
        with col3:
            dias_calendario = df_calendario['dia'].nunique()
            st.metric("Días activos", dias_calendario)
        
        with col4:
            # Calcular rango horario
            horarios = df_calendario['hora_inicio'].dropna()
            if not horarios.empty:
                hora_min = horarios.min()
                hora_max = df_calendario['hora_fin'].dropna().max()
                st.metric("Rango horario", f"{hora_min} - {hora_max}")
        
        st.markdown("---")
        
        # Crear la vista de calendario
        st.subheader("📅 Agenda Semanal")
        
        # Ordenar días de la semana
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dias_disponibles = [dia for dia in dias_orden if dia in df_calendario['dia'].values]
        
        # Crear columnas para cada día
        if len(dias_disponibles) <= 3:
            cols = st.columns(len(dias_disponibles))
        else:
            # Si hay más de 3 días, dividir en dos filas
            cols_fila1 = st.columns(min(4, len(dias_disponibles)))
            if len(dias_disponibles) > 4:
                cols_fila2 = st.columns(len(dias_disponibles) - 4)
                cols = list(cols_fila1) + list(cols_fila2)
            else:
                cols = cols_fila1
        
        for i, dia in enumerate(dias_disponibles):
            with cols[i]:
                st.markdown(f"### 📅 {dia}")
                
                # Filtrar turnos del día
                turnos_dia = df_calendario[df_calendario['dia'] == dia].copy()
                turnos_dia = turnos_dia.sort_values(['hora_inicio', 'doctor'])
                
                # Crear tarjetas para cada turno
                for _, turno in turnos_dia.iterrows():
                    doctor = turno['doctor'] if turno['doctor'] != 'Sin asignar' else 'No asignado'
                    hora_inicio = turno['hora_inicio']
                    hora_fin = turno['hora_fin']
                    tipo_turno = turno['tipo_turno'] if turno['tipo_turno'] != 'No especificado' else ''
                    
                    # Color basado en el tipo de turno - colores más profesionales y legibles
                    color_config = {
                        'PROGRAMADA': {'bg': '#e8f4f8', 'border': '#1976d2', 'text': '#0d47a1'},
                        'ESPONTANEA': {'bg': '#fff8e1', 'border': '#f57c00', 'text': '#e65100'},
                        'URGENCIA': {'bg': '#ffebee', 'border': '#d32f2f', 'text': '#b71c1c'},
                        'CONTROL': {'bg': '#f3e5f5', 'border': '#7b1fa2', 'text': '#4a148c'},
                        'SOBRETURNO': {'bg': '#e8f5e8', 'border': '#388e3c', 'text': '#1b5e20'}
                    }
                    
                    config = color_config.get(tipo_turno, {'bg': '#f5f5f5', 'border': '#757575', 'text': '#424242'})
                    
                    # Crear tarjeta del turno
                    st.markdown(
                        f"""
                        <div style="
                            background-color: {config['bg']};
                            color: {config['text']};
                            padding: 12px;
                            border-radius: 6px;
                            border-left: 4px solid {config['border']};
                            margin-bottom: 10px;
                            font-size: 13px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        ">
                            <div style="font-weight: bold; margin-bottom: 4px;">
                                {hora_inicio} - {hora_fin}
                            </div>
                            <div style="margin-bottom: 2px;">
                                <strong>Dr.</strong> {doctor}
                            </div>
                            {f'<div style="font-size: 11px; opacity: 0.8;">{tipo_turno}</div>' if tipo_turno else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        st.markdown("---")
        
        # Vista de timeline (alternativa visual)
        st.subheader("Timeline de horarios")
        
        # Preparar datos para el timeline
        df_timeline = df_calendario.copy()
        df_timeline['hora_inicio_num'] = pd.to_datetime(df_timeline['hora_inicio'], format='%H:%M', errors='coerce').dt.hour + \
                                       pd.to_datetime(df_timeline['hora_inicio'], format='%H:%M', errors='coerce').dt.minute / 60
        df_timeline['hora_fin_num'] = pd.to_datetime(df_timeline['hora_fin'], format='%H:%M', errors='coerce').dt.hour + \
                                    pd.to_datetime(df_timeline['hora_fin'], format='%H:%M', errors='coerce').dt.minute / 60
        
        # Crear gráfico Gantt-style
        fig_timeline = go.Figure()
        
        # Asignar colores a cada doctor
        doctores_unicos = df_timeline[df_timeline['doctor'] != 'Sin asignar']['doctor'].unique()
        colores = px.colors.qualitative.Set3[:len(doctores_unicos)]
        color_map = dict(zip(doctores_unicos, colores))
        
        # Rastrear doctores ya agregados a la leyenda
        doctores_en_leyenda = set()
        
        for _, turno in df_timeline.iterrows():
            if pd.notna(turno['hora_inicio_num']) and pd.notna(turno['hora_fin_num']):
                doctor = turno['doctor'] if turno['doctor'] != 'Sin asignar' else 'Sin asignar'
                color = color_map.get(doctor, '#cccccc')
                
                # Solo mostrar en leyenda la primera vez que aparece el doctor
                mostrar_leyenda = doctor not in doctores_en_leyenda
                doctores_en_leyenda.add(doctor)
                
                fig_timeline.add_trace(go.Scatter(
                    x=[turno['hora_inicio_num'], turno['hora_fin_num'], turno['hora_fin_num'], turno['hora_inicio_num'], turno['hora_inicio_num']],
                    y=[turno['dia'], turno['dia'], turno['dia'], turno['dia'], turno['dia']],
                    fill='toself',
                    fillcolor=color,
                    line=dict(color=color, width=2),
                    name=doctor,
                    hovertemplate=f"<b>{doctor}</b><br>" +
                                f"Día: {turno['dia']}<br>" +
                                f"Horario: {turno['hora_inicio']} - {turno['hora_fin']}<br>" +
                                f"Tipo: {turno['tipo_turno']}<extra></extra>",
                    showlegend=mostrar_leyenda
                ))
        
        fig_timeline.update_layout(
            title=f"Timeline de horarios - {area_calendario} ({efector_calendario})",
            xaxis_title="Hora del día",
            yaxis_title="Día de la semana",
            height=400,
            hovermode='closest'
        )
        
        # Configurar eje X con horas
        fig_timeline.update_xaxes(
            tickmode='linear',
            tick0=8,
            dtick=2,
            tickformat='%H:00'
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Tabla resumen por médico
        st.subheader("Resumen por médico")
        
        if not df_calendario.empty:
            resumen_doctores = df_calendario.groupby('doctor').agg({
                'dia': lambda x: ', '.join(sorted(set(x))),
                'hora_inicio': lambda x: f"{min(x)} - {max(x)}",
                'tipo_turno': lambda x: ', '.join(set(x.dropna()))
            }).rename(columns={
                'dia': 'Días que atiende',
                'hora_inicio': 'Rango horario',
                'tipo_turno': 'Tipos de agenda'
            })
            
            # Contar agendas únicas por médico
            resumen_doctores['Total agendas'] = df_calendario.groupby('doctor').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups)
            
            st.dataframe(resumen_doctores, use_container_width=True)
        else:
            st.info("No hay datos disponibles para mostrar el resumen por médico.")
        
        # Leyenda de colores para tipos de turno
        st.subheader("Leyenda de colores")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown("� **PROGRAMADA**")
        with col2:
            st.markdown("� **ESPONTANEA**")
        with col3:
            st.markdown("� **URGENCIA**")
        with col4:
            st.markdown("� **CONTROL**")
        with col5:
            st.markdown("� **SOBRETURNO**")
        
    else:
        st.warning(f"No se encontraron agendas para **{area_calendario}** en **{efector_calendario}**")
        st.info("Intenta seleccionar otra combinación de hospital y especialidad.")

with tab6:
    st.header("📊 Análisis UNIQUE")
    st.markdown("Explora valores únicos de cualquier campo con filtros avanzados")
    
    # Configuración del análisis UNIQUE
    st.subheader("Configuración del análisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selector del campo a analizar
        campos_disponibles = {
            'efector': '🏥 Centro de salud',
            'area': '⚕️ Especialidad médica',
            'doctor': '👨‍⚕️ Médico',
            'tipo_turno': '📋 Tipo de turno',
            'dia': '📅 Día de la semana',
            'hora_inicio': '🕐 Hora de inicio',
            'hora_fin': '🕑 Hora de fin',
            'nombre_original_agenda': '📝 Nombre original de agenda'
        }
        
        campo_unique = st.selectbox(
            "Campo a analizar:",
            options=list(campos_disponibles.keys()),
            format_func=lambda x: campos_disponibles[x],
            key="campo_unique"
        )
    
    with col2:
        # Opciones de visualización
        mostrar_conteos = st.checkbox("Mostrar conteos", value=True)
        mostrar_grafico = st.checkbox("Mostrar gráfico", value=True)
        limite_resultados = st.number_input(
            "Límite de resultados (0 = todos):",
            min_value=0,
            max_value=1000,
            value=0,
            step=10
        )
    
    # Filtros específicos para el análisis UNIQUE
    st.subheader("Filtros adicionales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por efector para UNIQUE
        efectores_unique = ['Todos'] + sorted(df['efector'].unique().tolist())
        efector_unique = st.selectbox(
            "Filtrar por centro:",
            efectores_unique,
            key="efector_unique"
        )
    
    with col2:
        # Filtro por área para UNIQUE
        areas_unique = ['Todas'] + sorted(df[df['area'] != 'Sin área']['area'].unique().tolist())
        area_unique = st.selectbox(
            "Filtrar por especialidad:",
            areas_unique,
            key="area_unique"
        )
    
    with col3:
        # Filtro por día para UNIQUE
        dias_unique = ['Todos'] + sorted(df['dia'].unique().tolist())
        dia_unique = st.selectbox(
            "Filtrar por día:",
            dias_unique,
            key="dia_unique"
        )
    
    # Aplicar filtros al DataFrame
    df_unique = df.copy()
    
    if efector_unique != 'Todos':
        df_unique = df_unique[df_unique['efector'] == efector_unique]
    
    if area_unique != 'Todas':
        df_unique = df_unique[df_unique['area'] == area_unique]
    
    if dia_unique != 'Todos':
        df_unique = df_unique[df_unique['dia'] == dia_unique]
    
    # Realizar análisis UNIQUE
    if not df_unique.empty:
        st.markdown("---")
        st.subheader(f"Análisis UNIQUE: {campos_disponibles[campo_unique]}")
        
        with st.spinner("Procesando análisis UNIQUE..."):
            # Obtener valores únicos con manejo de errores
            try:
                valores_unicos = df_unique[campo_unique].dropna().unique()
                
                if len(valores_unicos) == 0:
                    st.warning("No se encontraron valores únicos para el campo seleccionado.")
                    st.stop()
                
                if mostrar_conteos:
                    # Contar ocurrencias de forma eficiente
                    conteos = df_unique[campo_unique].value_counts()
                    
                    # Aplicar límite si se especifica
                    if limite_resultados > 0:
                        conteos = conteos.head(limite_resultados)
                        valores_unicos = conteos.index.tolist()
                    
                    # Limitar a máximo 1000 resultados para evitar problemas de rendimiento
                    if len(conteos) > 1000:
                        st.warning("⚠️ Demasiados resultados. Mostrando solo los primeros 1000.")
                        conteos = conteos.head(1000)
                        valores_unicos = conteos.index.tolist()
                    
                    # Métricas principales
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total valores únicos", len(valores_unicos))
                    
                    with col2:
                        st.metric("Total registros", len(df_unique))
                    
                    with col3:
                        if len(conteos) > 0:
                            st.metric("Más común", str(conteos.index[0])[:20] + "..." if len(str(conteos.index[0])) > 20 else str(conteos.index[0]))
                        else:
                            st.metric("Más común", "N/A")
                    
                    with col4:
                        if len(conteos) > 0:
                            st.metric("Ocurrencias máx.", int(conteos.iloc[0]))
                        else:
                            st.metric("Ocurrencias máx.", "N/A")
                    
                    # Tabla de conteos con paginación para mejor rendimiento
                    st.subheader("Tabla de conteos")
                    
                    # Crear DataFrame para mostrar
                    df_conteos = pd.DataFrame({
                        campos_disponibles[campo_unique]: conteos.index,
                        'Cantidad': conteos.values,
                        'Porcentaje': (conteos.values.astype(float) / len(df_unique) * 100).round(2)
                    })
                    
                    # Agregar número de fila
                    df_conteos.insert(0, '#', range(1, len(df_conteos) + 1))
                    
                    # Mostrar con altura limitada para mejor rendimiento
                    st.dataframe(df_conteos, use_container_width=True, height=min(400, len(df_conteos) * 35 + 100))
                    
                    # Botón para descargar resultados
                    csv_unique = df_conteos.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar resultados CSV",
                        data=csv_unique,
                        file_name=f"unique_{campo_unique}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Gráfico si se solicita (con límites para rendimiento)
                    if mostrar_grafico and len(conteos) > 0:
                        st.subheader("Visualización gráfica")
                        
                        # Limitar datos para gráfico
                        conteos_grafico = conteos.head(50)  # Máximo 50 para gráfico
                        
                        with error_handler("generación de gráfico"):
                            # Seleccionar tipo de gráfico según el número de valores
                            if len(conteos_grafico) <= 20:
                                # Gráfico de barras para pocos valores
                                fig_unique = px.bar(
                                    x=conteos_grafico.index,
                                    y=conteos_grafico.values,
                                    title=f"Distribución de {campos_disponibles[campo_unique]} (Top {len(conteos_grafico)})",
                                    labels={'x': campos_disponibles[campo_unique], 'y': 'Cantidad'},
                                    color=conteos_grafico.values,
                                    color_continuous_scale='viridis'
                                )
                                fig_unique.update_layout(
                                    height=500,
                                    xaxis_tickangle=-45,
                                    showlegend=False
                                )
                            else:
                                # Gráfico de barras horizontales para muchos valores
                                fig_unique = px.bar(
                                    x=conteos_grafico.values,
                                    y=conteos_grafico.index,
                                    orientation='h',
                                    title=f"Distribución de {campos_disponibles[campo_unique]} (Top {len(conteos_grafico)})",
                                    labels={'x': 'Cantidad', 'y': campos_disponibles[campo_unique]},
                                    color=conteos_grafico.values,
                                    color_continuous_scale='viridis'
                                )
                                fig_unique.update_layout(
                                    height=max(400, min(800, len(conteos_grafico) * 20)),
                                    showlegend=False
                                )
                            
                            st.plotly_chart(fig_unique, use_container_width=True)
                            
                            # Gráfico de pastel para proporciones (solo si hay pocos valores)
                            if len(conteos_grafico) <= 10:
                                fig_pie = px.pie(
                                    values=conteos_grafico.values,
                                    names=conteos_grafico.index,
                                    title=f"Proporción de {campos_disponibles[campo_unique]}"
                                )
                                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                                fig_pie.update_layout(height=500)
                                st.plotly_chart(fig_pie, use_container_width=True)
                
                else:
                    # Solo mostrar lista de valores únicos sin conteos
                    # Aplicar límite si se especifica
                    if limite_resultados > 0:
                        valores_unicos = valores_unicos[:limite_resultados]
                    
                    # Limitar a máximo 1000 para rendimiento
                    if len(valores_unicos) > 1000:
                        st.warning("⚠️ Demasiados resultados. Mostrando solo los primeros 1000.")
                        valores_unicos = valores_unicos[:1000]
                    
                    st.metric("Total valores únicos", len(valores_unicos))
                    
                    # Mostrar valores únicos en una tabla simple
                    df_valores = pd.DataFrame({
                        campos_disponibles[campo_unique]: valores_unicos
                    })
                    df_valores.insert(0, '#', range(1, len(df_valores) + 1))
                    
                    st.dataframe(df_valores, use_container_width=True, height=min(400, len(df_valores) * 35 + 100))
                    
                    # Botón para descargar
                    csv_valores = df_valores.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar valores únicos CSV",
                        data=csv_valores,
                        file_name=f"valores_unicos_{campo_unique}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
            except Exception as e:
                st.error(f"Error procesando análisis UNIQUE: {e}")
                st.info("Intenta con un campo diferente o aplica más filtros para reducir el tamaño de los datos.")
        
        # Análisis cruzado opcional
        st.markdown("---")
        st.subheader("Análisis cruzado")
        
        # Permitir seleccionar un segundo campo para análisis cruzado
        campos_cruzado = {k: v for k, v in campos_disponibles.items() if k != campo_unique}
        
        if campos_cruzado:
            campo_cruzado = st.selectbox(
                "Campo para análisis cruzado (opcional):",
                options=['Ninguno'] + list(campos_cruzado.keys()),
                format_func=lambda x: 'Ninguno' if x == 'Ninguno' else campos_cruzado[x]
            )
            
            if campo_cruzado != 'Ninguno':
                with st.spinner("Generando análisis cruzado..."):
                    with error_handler("análisis cruzado"):
                        # Verificar tamaño de datos antes del análisis cruzado
                        unique_campo1 = df_unique[campo_unique].nunique()
                        unique_campo2 = df_unique[campo_cruzado].nunique()
                        
                        if unique_campo1 * unique_campo2 > 10000:
                            st.warning("⚠️ El análisis cruzado podría ser muy grande. Aplicando límites para mejor rendimiento.")
                            # Limitar a los 50 valores más comunes de cada campo
                            top_campo1 = df_unique[campo_unique].value_counts().head(50).index
                            top_campo2 = df_unique[campo_cruzado].value_counts().head(50).index
                            
                            df_cruzado = df_unique[
                                (df_unique[campo_unique].isin(top_campo1)) & 
                                (df_unique[campo_cruzado].isin(top_campo2))
                            ]
                        else:
                            df_cruzado = df_unique
                        
                        # Crear tabla cruzada
                        tabla_cruzada = pd.crosstab(
                            df_cruzado[campo_unique],
                            df_cruzado[campo_cruzado],
                            margins=True
                        )
                        
                        st.subheader(f"Tabla cruzada: {campos_disponibles[campo_unique]} vs {campos_disponibles[campo_cruzado]}")
                        
                        # Mostrar información sobre la tabla
                        st.info(f"Tabla de {len(tabla_cruzada)-1} filas x {len(tabla_cruzada.columns)-1} columnas")
                        
                        # Mostrar tabla con altura limitada
                        st.dataframe(tabla_cruzada, use_container_width=True, height=min(500, len(tabla_cruzada) * 35 + 100))
                        
                        # Heatmap de la tabla cruzada (excluyendo totales y limitando tamaño)
                        if len(tabla_cruzada) > 1 and len(tabla_cruzada.columns) > 1:
                            tabla_sin_totales = tabla_cruzada.iloc[:-1, :-1]
                            
                            # Limitar tamaño del heatmap para rendimiento
                            if len(tabla_sin_totales) > 50 or len(tabla_sin_totales.columns) > 50:
                                st.warning("⚠️ Tabla muy grande para heatmap. Mostrando solo una muestra.")
                                tabla_sin_totales = tabla_sin_totales.head(50).iloc[:, :50]
                            
                            if not tabla_sin_totales.empty:
                                fig_heatmap = px.imshow(
                                    tabla_sin_totales,
                                    title=f"Heatmap: {campos_disponibles[campo_unique]} vs {campos_disponibles[campo_cruzado]}",
                                    labels={'x': campos_disponibles[campo_cruzado], 'y': campos_disponibles[campo_unique]},
                                    color_continuous_scale='Blues'
                                )
                                fig_heatmap.update_layout(height=min(700, max(400, len(tabla_sin_totales) * 15)))
                                st.plotly_chart(fig_heatmap, use_container_width=True)
                        
                        # Botón para descargar tabla cruzada
                        csv_cruzado = tabla_cruzada.to_csv()
                        st.download_button(
                            label="📥 Descargar tabla cruzada CSV",
                            data=csv_cruzado,
                            file_name=f"tabla_cruzada_{campo_unique}_{campo_cruzado}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
        
        # Ejemplos y ayuda
        with st.expander("💡 Ejemplos de uso"):
            st.markdown("""
            **Casos de uso comunes:**
            
            1. **Análisis de especialidades por hospital:**
               - Campo: Especialidad médica
               - Filtro: Hospital Materno Infantil
               - Resultado: Todas las especialidades disponibles en ese hospital
            
            2. **Médicos por especialidad:**
               - Campo: Médico
               - Filtro: Especialidad = PEDIATRIA
               - Resultado: Todos los pediatras del sistema
            
            3. **Horarios de atención:**
               - Campo: Hora de inicio
               - Filtro: Día = Lunes
               - Resultado: Todos los horarios de inicio los lunes
            
            4. **Análisis cruzado - Especialidades por centro:**
               - Campo principal: Especialidad médica
               - Campo cruzado: Centro de salud
               - Resultado: Matriz de especialidades disponibles por centro
            """)
    
    else:
        st.warning("No hay datos disponibles con los filtros aplicados.")
        st.info("Intenta ajustar los filtros para obtener resultados.")

with tab7:
    st.header("Gestión")
    
    # Sistema de autenticación con persistencia
    def inicializar_autenticacion():
        """Inicializa el estado de autenticación verificando si hay una sesión guardada"""
        if 'authenticated_gerencial' not in st.session_state:
            st.session_state.authenticated_gerencial = False
        
        # Verificar si hay una autenticación persistente guardada
        if 'auth_timestamp' not in st.session_state:
            st.session_state.auth_timestamp = None
        
        # Verificar si la autenticación no ha expirado (24 horas)
        if (st.session_state.auth_timestamp and 
            (datetime.datetime.now() - st.session_state.auth_timestamp).total_seconds() < 86400):
            st.session_state.authenticated_gerencial = True
        elif st.session_state.auth_timestamp:
            # Si ha expirado, limpiar la autenticación
            st.session_state.authenticated_gerencial = False
            st.session_state.auth_timestamp = None
    
    # Función para autenticar y guardar timestamp
    def autenticar_usuario():
        """Autentica al usuario y guarda el timestamp"""
        st.session_state.authenticated_gerencial = True
        st.session_state.auth_timestamp = datetime.datetime.now()
    
    # Función para cerrar sesión
    def cerrar_sesion():
        """Cierra la sesión y limpia la autenticación"""
        st.session_state.authenticated_gerencial = False
        st.session_state.auth_timestamp = None
    
    # Inicializar autenticación
    inicializar_autenticacion()
    
    if not st.session_state.authenticated_gerencial:
        st.info("Esta sección requiere autenticación")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password_input = st.text_input(
                "Contraseña:", 
                type="password",
                key="password_gerencial"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Ingresar", type="primary", use_container_width=True):
                    # Contraseña
                    if password_input == "maxisalas":
                        autenticar_usuario()
                        st.success("✅ Sesión iniciada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
            
            with col_btn2:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state.password_gerencial = ""
        
        
    else:
        # Información de sesión y botón de logout
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if st.session_state.auth_timestamp:
                tiempo_sesion = datetime.datetime.now() - st.session_state.auth_timestamp
                horas_sesion = int(tiempo_sesion.total_seconds() // 3600)
                minutos_sesion = int((tiempo_sesion.total_seconds() % 3600) // 60)
                st.info(f"🔐 Sesión activa desde hace {horas_sesion}h {minutos_sesion}m")
        
        with col2:
            # Botón para extender sesión
            if st.button("Extender sesión", use_container_width=True):
                st.session_state.auth_timestamp = datetime.datetime.now()
                st.success("✅ Sesión extendida por 24 horas más")
                st.rerun()
        
        with col3:
            if st.button("Cerrar sesión", use_container_width=True):
                cerrar_sesion()
                st.success("✅ Sesión cerrada correctamente")
                st.rerun()
        
        st.success("🔓 Acceso autorizado - Sesión persistente activa")
        
        # Filtros específicos para gestión gerencial
        st.subheader("Filtros de análisis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por médico específico
            medicos_gerencial = ['Todos'] + sorted(df[df['doctor'] != 'Sin asignar']['doctor'].unique().tolist())
            medico_gerencial = st.selectbox(
                "Médico específico:",
                medicos_gerencial,
                key="medico_gerencial"
            )
        
        with col2:
            # Filtro por área médica para gestión
            areas_gerencial = ['Todas'] + sorted(df[df['area'] != 'Sin área']['area'].unique().tolist())
            area_gerencial = st.selectbox(
                "Área médica:",
                areas_gerencial,
                key="area_gerencial"
            )
        
        with col3:
            # Filtro por día para gestión
            dias_gerencial = ['Todos'] + sorted(df['dia'].unique().tolist())
            dia_gerencial = st.selectbox(
                "Día de análisis:",
                dias_gerencial,
                key="dia_gerencial"
            )
        
        # Aplicar filtros
        df_gerencial = df.copy()
        
        if medico_gerencial != 'Todos':
            df_gerencial = df_gerencial[df_gerencial['doctor'] == medico_gerencial]
        
        if area_gerencial != 'Todas':
            df_gerencial = df_gerencial[df_gerencial['area'] == area_gerencial]
        
        if dia_gerencial != 'Todos':
            df_gerencial = df_gerencial[df_gerencial['dia'] == dia_gerencial]
        
        # NUEVA FUNCIONALIDAD: Análisis de superposición de horarios
        st.markdown("---")
        st.subheader("Superposición de horarios")
        
        def detectar_superposiciones(df_analisis):
            """Detecta médicos con horarios superpuestos"""
            superposiciones = []
            
            # Agrupar por médico
            medicos_horarios = df_analisis[df_analisis['doctor'] != 'Sin asignar'].groupby('doctor')
            
            for medico, datos_medico in medicos_horarios:
                # Convertir horas a formato datetime para comparación
                datos_medico = datos_medico.copy()
                datos_medico['hora_inicio_dt'] = pd.to_datetime(datos_medico['hora_inicio'], format='%H:%M', errors='coerce')
                datos_medico['hora_fin_dt'] = pd.to_datetime(datos_medico['hora_fin'], format='%H:%M', errors='coerce')
                
                # Agrupar por día
                dias_medico = datos_medico.groupby('dia')
                
                for dia, horarios_dia in dias_medico:
                    horarios_dia = horarios_dia.sort_values('hora_inicio_dt')
                    
                    # Comparar horarios del mismo día
                    for i, (idx1, row1) in enumerate(horarios_dia.iterrows()):
                        for idx2, row2 in horarios_dia.iloc[i+1:].iterrows():
                            # Verificar superposición
                            if (row1['hora_inicio_dt'] < row2['hora_fin_dt'] and 
                                row1['hora_fin_dt'] > row2['hora_inicio_dt']):
                                
                                superposiciones.append({
                                    'medico': medico,
                                    'dia': dia,
                                    'centro_1': row1['efector'],
                                    'area_1': row1['area'],
                                    'horario_1': f"{row1['hora_inicio']} - {row1['hora_fin']}",
                                    'centro_2': row2['efector'],
                                    'area_2': row2['area'],
                                    'horario_2': f"{row2['hora_inicio']} - {row2['hora_fin']}",
                                    'tipo_conflicto': 'Mismo centro' if row1['efector'] == row2['efector'] else 'Centros diferentes'
                                })
            
            return pd.DataFrame(superposiciones)
        
        # Detectar superposiciones en los datos filtrados
        df_superposiciones = detectar_superposiciones(df_gerencial)
        
        if not df_superposiciones.empty:
            # Métricas de superposiciones
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                medicos_con_conflictos = df_superposiciones['medico'].nunique()
                st.metric("Médicos con conflictos", medicos_con_conflictos)
            
            with col2:
                total_conflictos = len(df_superposiciones)
                st.metric("Total conflictos", total_conflictos)
            
            with col3:
                conflictos_mismo_centro = len(df_superposiciones[df_superposiciones['tipo_conflicto'] == 'Mismo centro'])
                st.metric("Conflictos mismo centro", conflictos_mismo_centro)
            
            with col4:
                conflictos_centros_diferentes = len(df_superposiciones[df_superposiciones['tipo_conflicto'] == 'Centros diferentes'])
                st.metric("Conflictos entre centros", conflictos_centros_diferentes)
            
            # Tabla de conflictos
            st.subheader("Detalle de conflictos de horarios")
            
            # Aplicar colores según el tipo de conflicto
            def color_conflictos(val):
                if val == 'Mismo centro':
                    return 'background-color: #ffebee'  # Rojo claro
                elif val == 'Centros diferentes':
                    return 'background-color: #fff3e0'  # Naranja claro
                return ''
            
            # Renombrar columnas para mejor visualización
            df_superposiciones_display = df_superposiciones.rename(columns={
                'medico': 'Médico',
                'dia': 'Día',
                'centro_1': 'Centro 1',
                'area_1': 'Área 1',
                'horario_1': 'Horario 1',
                'centro_2': 'Centro 2',
                'area_2': 'Área 2',
                'horario_2': 'Horario 2',
                'tipo_conflicto': 'Tipo de conflicto'
            })
            
            st.dataframe(
                df_superposiciones_display,
                use_container_width=True,
                height=400
            )
            
            # Resumen por médico
            st.subheader("Resumen de conflictos por médico")
            resumen_conflictos = df_superposiciones.groupby('medico').agg({
                'dia': lambda x: ', '.join(sorted(set(x))),
                'tipo_conflicto': lambda x: ', '.join(set(x))
            }).rename(columns={
                'dia': 'Días con conflictos',
                'tipo_conflicto': 'Tipos de conflicto'
            })
            resumen_conflictos['Total conflictos'] = df_superposiciones['medico'].value_counts()
            
            st.dataframe(resumen_conflictos, use_container_width=True)
            
            # Gráfico de conflictos por día
            if len(df_superposiciones) > 0:
                conflictos_por_dia = df_superposiciones['dia'].value_counts()
                
                fig_conflictos = px.bar(
                    x=conflictos_por_dia.index,
                    y=conflictos_por_dia.values,
                    title="Conflictos de horarios por día de la semana",
                    labels={'x': 'Día', 'y': 'Número de conflictos'},
                    color=conflictos_por_dia.values,
                    color_continuous_scale='Reds'
                )
                fig_conflictos.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_conflictos, use_container_width=True)
            
        else:
            st.success("✅ No se detectaron conflictos de horarios en los datos filtrados.")
            st.info("Todos los médicos tienen horarios sin superposiciones.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Desarrollado por Lucas Rosenzvit - lrosenzvit@sanisidro.gob.ar</p>
    </div>
    """,
    unsafe_allow_html=True
)
