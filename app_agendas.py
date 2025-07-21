import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Agendas salud",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Agendas salud")
st.markdown("### Dashboard interactivo para visualización de horarios")

@st.cache_data
def cargar_datos():
    """Carga los datos de agendas consolidadas"""
    try:
        df = pd.read_csv("datos/csv_procesado/agendas_consolidadas.csv")
        
        # Limpiar datos
        df['doctor'] = df['doctor'].fillna('Sin asignar')
        df['area'] = df['area'].fillna('Sin área')
        df['tipo_turno'] = df['tipo_turno'].fillna('No especificado')
        
        # Convertir horas a datetime para mejor manejo
        df['hora_inicio_dt'] = pd.to_datetime(df['hora_inicio'], format='%H:%M', errors='coerce').dt.time
        df['hora_fin_dt'] = pd.to_datetime(df['hora_fin'], format='%H:%M', errors='coerce').dt.time
        
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

# Cargar datos
df = cargar_datos()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica que existe el archivo datos/csv_procesado/agendas_consolidadas.csv")
    st.stop()

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Resumen general", "Horarios por día", "Análisis por médico", "Comparativa centros", "Tabla completa", "Calendario", "Gestión", "Control de calidad"])

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
    dias_orden = ['TODOS', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dia_analisis = st.selectbox(
        "Día para análisis detallado:",
        dias_orden,
        key="dia_analisis"
    )
    
    # Filtrar datos según selección
    if dia_analisis == 'TODOS':
        df_dia = df_filtrado.copy()
    else:
        df_dia = df_filtrado[df_filtrado['dia'] == dia_analisis]
    
    if not df_dia.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap de horarios
            if 'hora_inicio' in df_dia.columns:
                # Crear bins de horas
                df_dia_copy = df_dia.copy()
                df_dia_copy['hora_inicio_num'] = pd.to_datetime(df_dia_copy['hora_inicio'], format='%H:%M', errors='coerce').dt.hour
                
                if dia_analisis == 'TODOS':
                    # Para TODOS los días, agrupar por día y hora
                    heatmap_data = df_dia_copy.groupby(['dia', 'hora_inicio_num']).size().reset_index(name='count')
                    titulo_heatmap = "Intensidad de agendas - Todos los días"
                    y_label = 'Día'
                    y_column = 'dia'
                else:
                    # Para un día específico, agrupar por efector y hora
                    heatmap_data = df_dia_copy.groupby(['efector', 'hora_inicio_num']).size().reset_index(name='count')
                    titulo_heatmap = f"Intensidad de agendas - {dia_analisis}"
                    y_label = 'Centro de salud'
                    y_column = 'efector'
                
                if not heatmap_data.empty:
                    fig_heatmap = px.density_heatmap(
                        heatmap_data,
                        x='hora_inicio_num',
                        y=y_column,
                        z='count',
                        title=titulo_heatmap,
                        labels={'hora_inicio_num': 'Hora', y_column: y_label, 'count': 'Número de agendas'}
                    )
                    fig_heatmap.update_layout(height=400)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # Top médicos del día/todos los días (agendas únicas)
            df_medicos_dia = df_dia[df_dia['doctor'] != 'Sin asignar']
            if not df_medicos_dia.empty:
                medicos_dia = df_medicos_dia.groupby('doctor').apply(lambda x: x.groupby(['nombre_original_agenda', 'efector']).ngroups).sort_values(ascending=False).head(10)

                titulo_medicos = f"Top médicos - {dia_analisis}" if dia_analisis != 'TODOS' else "Top médicos - Todos los días"
                fig_medicos = px.bar(
                    x=medicos_dia.values,
                    y=medicos_dia.index,
                    orientation='h',
                    title=titulo_medicos,
                    labels={'x': 'Número de agendas', 'y': 'Médico'}
                )
                fig_medicos.update_layout(height=400)
                st.plotly_chart(fig_medicos, use_container_width=True)
            else:
                mensaje_medicos = f"No hay médicos con agendas disponibles para {dia_analisis}." if dia_analisis != 'TODOS' else "No hay médicos con agendas disponibles."
                st.info(mensaje_medicos)

        # Tabla detallada del día/todos los días
        titulo_tabla = f"Detalle de agendas - {dia_analisis}" if dia_analisis != 'TODOS' else "Detalle de agendas - Todos los días"
        st.subheader(titulo_tabla)
        
        if dia_analisis == 'TODOS':
            # Para TODOS, incluir la columna día
            df_mostrar = df_dia[['agenda_id', 'dia', 'efector', 'area', 'doctor', 'hora_inicio', 'hora_fin', 'tipo_turno']].copy()
            df_mostrar = df_mostrar.sort_values(['dia', 'efector', 'hora_inicio'])
        else:
            # Para un día específico, no incluir la columna día
            df_mostrar = df_dia[['agenda_id', 'efector', 'area', 'doctor', 'hora_inicio', 'hora_fin', 'tipo_turno']].copy()
            df_mostrar = df_mostrar.sort_values(['efector', 'hora_inicio'])
        
        st.dataframe(
            df_mostrar,
            use_container_width=True,
            height=300
        )
    else:
        mensaje_warning = f"No hay datos disponibles para {dia_analisis} con los filtros aplicados." if dia_analisis != 'TODOS' else "No hay datos disponibles con los filtros aplicados."
        st.warning(mensaje_warning)

with tab3:
    st.header("Análisis por médico")
    
    # Selector de doctor
    doctores_disponibles = sorted(df_filtrado[df_filtrado['doctor'] != 'Sin asignar']['doctor'].unique().tolist())
    
    if doctores_disponibles:
        doctor_seleccionado = st.selectbox(
            "Médico:",
            doctores_disponibles
        )
        
        df_doctor = df_filtrado[df_filtrado['doctor'] == doctor_seleccionado]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Contar agendas únicas del médico
            agendas_unicas_doctor = df_doctor.groupby(['nombre_original_agenda', 'efector']).ngroups
            st.metric("Total de agendas", agendas_unicas_doctor)
        
        with col2:
            especialidades_doctor = df_doctor['area'].nunique()
            st.metric("Especialidades", especialidades_doctor)
        
        with col3:
            centros_doctor = df_doctor['efector'].nunique()
            st.metric("Centros de salud", centros_doctor)
        
        # Horarios del doctor por día
        horarios_doctor = df_doctor.groupby('dia').agg({
            'hora_inicio': lambda x: ', '.join(sorted(set(x.astype(str)))),
            'hora_fin': lambda x: ', '.join(sorted(set(x.astype(str)))),
            'efector': lambda x: ', '.join(set(x)),
            'area': lambda x: ', '.join(set(x))
        }).reset_index()
        
        st.subheader(f"Horarios de {doctor_seleccionado}")
        st.dataframe(horarios_doctor, use_container_width=True)
        
    else:
        st.warning("No hay médicos disponibles con los filtros aplicados.")

with tab4:
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

with tab5:
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
    columnas_mostrar = ['agenda_id']  # Siempre incluir agenda_id
    
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
        'agenda_id': 'ID de Agenda',
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

with tab6:
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
        st.subheader("Agenda Semanal")
        
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
                st.markdown(f"### {dia}")
                
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
            st.markdown("**PROGRAMADA** (Azul)")
        with col2:
            st.markdown("**ESPONTANEA** (Naranja)")
        with col3:
            st.markdown("**URGENCIA** (Rojo)")
        with col4:
            st.markdown("**CONTROL** (Violeta)")
        with col5:
            st.markdown("**SOBRETURNO** (Verde)")
        
    else:
        st.warning(f"No se encontraron agendas para **{area_calendario}** en **{efector_calendario}**")
        st.info("Intenta seleccionar otra combinación de hospital y especialidad.")

with tab7:
    st.header("Gestión")
    
    # Sistema de autenticación
    if 'authenticated_gerencial' not in st.session_state:
        st.session_state.authenticated_gerencial = False
    
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
                        st.session_state.authenticated_gerencial = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta")
            
            with col_btn2:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state.password_gerencial = ""
        
        
    else:
        # Botón de logout
        col1, col2, col3 = st.columns([4, 1, 1])
        with col3:
            if st.button("Cerrar sesión"):
                st.session_state.authenticated_gerencial = False
                st.rerun()
        
        st.success("Acceso autorizado")
        
        # Mostrar estado de filtros aplicados
        st.subheader("Estado de filtros aplicados")
        
        # Crear un resumen visual de los filtros activos
        filtros_activos = []
        if efector_seleccionado != 'Todos':
            filtros_activos.append(f"**Hospital/CAPS:** {efector_seleccionado}")
        if area_seleccionada != 'Todas':
            filtros_activos.append(f"**Área:** {area_seleccionada}")
        if dia_seleccionado != 'Todos':
            filtros_activos.append(f"**Día:** {dia_seleccionado}")
        if tipo_turno_seleccionado != 'Todos':
            filtros_activos.append(f"**Tipo de agenda:** {tipo_turno_seleccionado}")
        
        if filtros_activos:
            st.info("**Filtros activos desde la barra lateral:**\n\n" + " • ".join(filtros_activos))
        else:
            st.info("**Mostrando todos los datos** (sin filtros aplicados)")
        
        # Filtro adicional específico para gestión
        st.subheader("Filtro adicional de gestión")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por médico específico (usando datos ya filtrados)
            medicos_gerencial = ['Todos'] + sorted(df_filtrado[df_filtrado['doctor'] != 'Sin asignar']['doctor'].unique().tolist())
            medico_gerencial = st.selectbox(
                "Médico específico:",
                medicos_gerencial,
                key="medico_gerencial",
                help="Filtro adicional que se aplica sobre los filtros de la barra lateral"
            )
        
        with col2:
            # Mostrar estadísticas de los datos filtrados
            total_registros_filtrados = len(df_filtrado)
            medicos_disponibles = len(medicos_gerencial) - 1  # -1 para excluir "Todos"
            st.metric("Registros filtrados", f"{total_registros_filtrados:,}")
        
        with col3:
            st.metric("Médicos disponibles", f"{medicos_disponibles:,}")
        
        # Aplicar filtro adicional de médico específico a los datos ya filtrados
        df_gerencial = df_filtrado.copy()
        
        if medico_gerencial != 'Todos':
            df_gerencial = df_gerencial[df_gerencial['doctor'] == medico_gerencial]
            st.success(f"Análisis enfocado en: **{medico_gerencial}**")
        
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
            st.success("No se detectaron conflictos de horarios en los datos filtrados.")
            st.info("Todos los médicos tienen horarios sin superposiciones.")

# TAB 8: CONTROL DE CALIDAD
with tab8:
    st.header("Control de calidad de datos")
    
    # Verificar si existe la columna agenda_id
    if 'agenda_id' in df.columns:
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_registros = len(df_filtrado)
            st.metric("Total registros", total_registros)
        
        with col2:
            agendas_unicas_id = df_filtrado['agenda_id'].nunique()
            st.metric("Agendas únicas (ID)", agendas_unicas_id)
        
        with col3:
            agendas_unicas_nombre = df_filtrado['nombre_original_agenda'].nunique()
            st.metric("Nombres únicos", agendas_unicas_nombre)
        
        with col4:
            duplicados_detectados = agendas_unicas_id - agendas_unicas_nombre
            if duplicados_detectados > 0:
                st.metric("Duplicados detectados", duplicados_detectados, delta=f"+{duplicados_detectados}")
            else:
                st.metric("Duplicados detectados", duplicados_detectados)

        st.markdown("---")
        
        # Análisis de duplicados
        st.subheader("Análisis de agendas duplicadas")
        
        # Encontrar agendas con el mismo nombre pero diferentes IDs
        nombre_counts = df_filtrado.groupby(['nombre_original_agenda', 'efector']).agg({
            'agenda_id': 'nunique'
        }).reset_index()
        
        duplicados = nombre_counts[nombre_counts['agenda_id'] > 1]
        
        if len(duplicados) > 0:
            st.warning(f"Se encontraron {len(duplicados)} agendas con nombres duplicados en el mismo centro:")
            
            for _, row in duplicados.iterrows():
                nombre_agenda = row['nombre_original_agenda']
                efector = row['efector']
                num_duplicados = row['agenda_id']
                
                st.write(f"**{efector}**")
                st.write(f"Agenda: `{nombre_agenda}`")
                st.write(f"Instancias: {num_duplicados}")
                
                # Mostrar los IDs específicos
                ids_agenda = df_filtrado[
                    (df_filtrado['nombre_original_agenda'] == nombre_agenda) & 
                    (df_filtrado['efector'] == efector)
                ]['agenda_id'].unique()
                
                st.write(f"IDs: {', '.join(ids_agenda)}")
                
                # Mostrar tabla detallada de estas agendas duplicadas
                df_duplicado = df_filtrado[
                    (df_filtrado['nombre_original_agenda'] == nombre_agenda) & 
                    (df_filtrado['efector'] == efector)
                ].groupby(['agenda_id', 'dia']).agg({
                    'hora_inicio': 'first',
                    'hora_fin': 'first',
                    'doctor': 'first',
                    'area': 'first'
                }).reset_index()
                
                st.dataframe(
                    df_duplicado.rename(columns={
                        'agenda_id': 'ID de agenda',
                        'dia': 'Día',
                        'hora_inicio': 'Hora inicio',
                        'hora_fin': 'Hora fin',
                        'doctor': 'Médico',
                        'area': 'Área'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown("---")
        else:
            st.success("No se detectaron agendas duplicadas en los datos filtrados.")
        
        # Análisis por centro
        st.subheader("Análisis por centro de salud")
        
        resumen_centros = df_filtrado.groupby('efector').agg({
            'agenda_id': 'nunique',
            'nombre_original_agenda': 'nunique'
        }).reset_index()
        
        resumen_centros['duplicados'] = resumen_centros['agenda_id'] - resumen_centros['nombre_original_agenda']
        resumen_centros = resumen_centros.sort_values('duplicados', ascending=False)
        
        st.dataframe(
            resumen_centros.rename(columns={
                'efector': 'Centro de salud',
                'agenda_id': 'Agendas únicas (ID)',
                'nombre_original_agenda': 'Nombres únicos',
                'duplicados': 'Duplicados'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de duplicados por centro
        fig_duplicados = px.bar(
            resumen_centros[resumen_centros['duplicados'] > 0],
            x='efector',
            y='duplicados',
            title='Duplicados por centro de salud',
            labels={'efector': 'Centro de salud', 'duplicados': 'Número de duplicados'}
        )
        fig_duplicados.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_duplicados, use_container_width=True)
        
    else:
        st.error("La columna 'agenda_id' no está disponible en los datos.")
        st.info("Para usar esta funcionalidad, reprocesa los datos con la versión actualizada del sistema.")

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
