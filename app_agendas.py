import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Visualización de agendas",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Visualización de agendas")
st.markdown("### Dashboard interactivo para visualización de horarios")

@st.cache_data
def cargar_datos():
    """Carga los datos de agendas consolidadas"""
    try:
        df = pd.read_csv("agendas_consolidadas.csv")
        
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
    st.error("No se pudieron cargar los datos. Verifica que existe el archivo agendas_consolidadas.csv")
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
    total_turnos = len(df_filtrado)
    st.metric(
        label="Total de Agendas",
        value=f"{total_turnos:,}",
        delta=f"{len(df)} total" if total_turnos != len(df) else None
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Resumen general", "Horarios por día", "Análisis por médico", "Comparativa centros", "Tabla completa", "Calendario"])

with tab1:
    st.header("Resumen general")

    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de turnos por área médica
        areas_count = df_filtrado[df_filtrado['area'] != 'Sin área']['area'].value_counts().head(10)
        
        fig_areas = px.bar(
            x=areas_count.values,
            y=areas_count.index,
            orientation='h',
            title="Top 10 especialidades por número de agendas",
            labels={'x': 'Número de agendas', 'y': 'Especialidad'},
            color=areas_count.values,
            color_continuous_scale='viridis'
        )
        fig_areas.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_areas, use_container_width=True)
    
    with col2:
        # Gráfico de turnos por día de la semana
        dias_count = df_filtrado['dia'].value_counts()
        
        fig_dias = px.pie(
            values=dias_count.values,
            names=dias_count.index,
            title="Distribución de agendas por día de la semana"
        )
        fig_dias.update_traces(textposition='inside', textinfo='percent+label')
        fig_dias.update_layout(height=400)
        st.plotly_chart(fig_dias, use_container_width=True)
    
    # Gráfico de turnos por efector
    efectores_count = df_filtrado['efector'].value_counts()
    
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
            # Top médicos del día
            medicos_dia = df_dia[df_dia['doctor'] != 'Sin asignar']['doctor'].value_counts().head(10)

            fig_medicos = px.bar(
                x=medicos_dia.values,
                y=medicos_dia.index,
                orientation='h',
                title=f"Top médicos - {dia_analisis}",
                labels={'x': 'Número de agendas', 'y': 'Médico'}
            )
            fig_medicos.update_layout(height=400)
            st.plotly_chart(fig_medicos, use_container_width=True)

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
            st.metric("Total de Agendas", len(df_doctor))
        
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
    metricas_efector = df_filtrado.groupby('efector').agg({
        'doctor': lambda x: x[x != 'Sin asignar'].nunique(),
        'area': lambda x: x[x != 'Sin área'].nunique(),
        'dia': 'count'
    }).rename(columns={
        'doctor': 'Médicos',
        'area': 'Especialidades',
        'dia': 'Total agendas'
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
        st.metric("Registros mostrados", len(df_mostrar))
    
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
            # Top 5 doctores en la vista actual
            if 'doctor' in df_mostrar.columns:
                top_doctores = df_mostrar[df_mostrar['doctor'] != 'Sin asignar']['doctor'].value_counts().head(5)
                if not top_doctores.empty:
                    st.write("**Top 5 médicos:**")
                    for i, (doctor, count) in enumerate(top_doctores.items(), 1):
                        st.write(f"{i}. {doctor}: {count} agendas")
        
        with col2:
            # Top 5 especialidades en la vista actual
            if 'area' in df_mostrar.columns:
                top_areas = df_mostrar[df_mostrar['area'] != 'Sin área']['area'].value_counts().head(5)
                if not top_areas.empty:
                    st.write("**Top 5 especialidades:**")
                    for i, (area, count) in enumerate(top_areas.items(), 1):
                        st.write(f"{i}. {area}: {count} agendas")

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
            total_turnos_calendario = len(df_calendario)
            st.metric("Total Agendas", total_turnos_calendario)
        
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
        
        resumen_doctores = df_calendario.groupby('doctor').agg({
            'dia': lambda x: ', '.join(sorted(set(x))),
            'hora_inicio': lambda x: f"{min(x)} - {max(x)}",
            'tipo_turno': lambda x: ', '.join(set(x.dropna()))
        }).rename(columns={
            'dia': 'Días que atiende',
            'hora_inicio': 'Rango horario',
            'tipo_turno': 'Tipos de agenda'
        })
        
        resumen_doctores['Total agendas'] = df_calendario['doctor'].value_counts()
        
        st.dataframe(resumen_doctores, use_container_width=True)
        
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

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Desarrollado por Lucas Rosenzvit</p>
    </div>
    """,
    unsafe_allow_html=True
)
