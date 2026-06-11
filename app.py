# app2_v3_visual_fix.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import pydeck as pdk
import os

# Configuración inicial de la página (DEBE IR PRIMERO)
st.set_page_config(page_title="Dashboard Accidentes EE.UU.", page_icon="🚗", layout="wide")
pio.templates.default = "plotly_white"

# =====================================================
# 1. ESTILO CSS (Layout + Pestañas)
# =====================================================
st.markdown("""
<style>
/* Fondo general */
.stApp {
    background-color: #f5f7fb;
}

/* NO cambiar color global del contenido principal */
h1, h2, h3, label, p, span {
    color: #16213e;
}

/* =========================================
   ESTILO PARA EL SIDEBAR (Fondo Azul y Ancho)
========================================= */
/* Ajustar el ancho y el fondo del menú lateral */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #061736 0%, #081f4d 100%) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}

/* Títulos y separadores en el sidebar a blanco */
[data-testid="stSidebar"] h2 {
    color: white !important;
    font-size: 22px !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.2) !important;
}

/* Etiquetas de los filtros a celeste claro (Forzando sobreescritura) */
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] label span,
[data-testid="stSidebar"] label {
    font-weight: 700 !important;
    color: #93c5fd !important; 
    font-size: 15px !important;
    margin-bottom: 4px;
}

/* Hacer que la flecha para ocultar/mostrar el sidebar sea blanca */
[data-testid="stSidebarCollapseButton"] svg {
    color: white !important;
    fill: white !important;
}

/* Efecto hover para la flecha del sidebar */
[data-testid="stSidebarCollapseButton"]:hover svg {
    color: #93c5fd !important;
    fill: #93c5fd !important;
}
            
/* Modificar la caja del input (fondo blanco) */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important; 
    border: 1px solid #cbd5e1 !important; 
    border-radius: 8px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02) !important; 
    transition: all 0.2s ease-in-out;
}

div[data-baseweb="select"] > div:hover {
    border-color: #93c5fd !important; 
}

/* Forzar que el texto seleccionado dentro del input sea oscuro */
div[data-baseweb="select"] span {
    color: #16213e !important;
}

/* Etiquetas del Multiselect (Tags) */
.stMultiSelect [data-baseweb="tag"] {
    background-color: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 6px !important;
}
.stMultiSelect [data-baseweb="tag"] span {
    color: #1e293b !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

/* =========================================
   ESTILO DE LAS TARJETAS KPI
========================================= */
.kpi-card {
    background: linear-gradient(135deg, #061736 0%, #081f4d 100%); 
    border-radius: 12px;
    padding: 15px 10px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 6px rgba(0,0,0,.1);
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
.kpi-title {
    font-size: 15px;
    font-weight: 600;
    color: #93c5fd; 
    margin-bottom: 5px;
}
.kpi-value {
    font-size: 26px; /* Reducido levemente para que encajen los 5 */
    font-weight: 800;
    color: white;
}

/* Reducir el padding superior de Streamlit */
.block-container {
    padding-top: 2rem; 
    padding-bottom: 2rem;
}
            
/* Ocultar el botón que permite cerrar el sidebar */
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Opcional: Asegurar que el sidebar no reaccione a eventos de colapso */
[data-testid="stSidebar"] {
    transition: none !important;
}
            
 /* =========================================
   FORZAR RADIO BUTTONS EN UNA SOLA LÍNEA
========================================= */
div[data-testid="stRadio"] div[role="radiogroup"] {
    flex-wrap: nowrap !important;
    white-space: nowrap !important;
}

/* =========================================
   ESTILO PARA LOS TABS (PESTAÑAS)
========================================= */
[data-testid="stTabs"] {
    border-bottom: none;
    margin-top: 10px;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 15px; 
    padding: 10px 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: white;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    padding: 10px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.2s ease-in-out;
}
.stTabs [data-baseweb="tab"] p {
    color: #4b5563; 
    font-weight: 500;
    font-size: 16px;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #061736 0%, #081f4d 100%) !important;
    border: none !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
}
.stTabs [aria-selected="true"] p {
    color: white !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 2. CARGA DE DATOS
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_parquet(os.path.join("processed", "US_Accidents_Processed.parquet"))
    df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")
    return df

df = load_data()

STATE_NAMES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas",
    "CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware",
    "FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho",
    "IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas",
    "KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
    "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
    "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
    "NH":"Nuevo Hampshire","NJ":"Nueva Jersey","NM":"Nuevo México","NY":"Nueva York",
    "NC":"Carolina del Norte","ND":"Dakota del Norte","OH":"Ohio","OK":"Oklahoma",
    "OR":"Oregon","PA":"Pensilvania","RI":"Rhode Island","SC":"Carolina del Sur",
    "SD":"Dakota del Sur","TN":"Tennessee","TX":"Texas","UT":"Utah",
    "VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"Virginia Occidental",
    "WI":"Wisconsin","WY":"Wyoming"
}

df["State_Name"] = df["State"].map(STATE_NAMES).fillna(df["State"])
SEVERITY_LABELS = {1: "Baja", 2: "Moderada", 3: "Alta", 4: "Fatal"}
df["Severity_Label"] = df["Severity"].map(SEVERITY_LABELS)

DIAS_ES = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
ESTACIONES_ES = {"Winter": "Invierno", "Spring": "Primavera", "Summer": "Verano", "Fall": "Otoño"}
CLIMAS_ES = {"Clear": "Despejado", "Cloudy": "Nublado", "Rain": "Lluvia", "Snow": "Nieve", "Fog": "Niebla", "Storm": "Tormenta", "Windy": "Ventoso", "Overcast": "Cubierto", "Other": "Otro"}

# Extraer el mes y traducirlo al español
MESES_ES = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
df["Mes_Es"] = df["Start_Time"].dt.month.map(MESES_ES)

# =====================================================
# 3. SIDEBAR (Filtros Globales)
# =====================================================
st.sidebar.markdown("## Filtros")
st.sidebar.markdown("---")

year = st.sidebar.selectbox("Año", ["Todos"] + sorted(df["Year"].unique().tolist()))

# Filtro de Mes añadido asegurando orden cronológico
meses_opciones = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes = st.sidebar.selectbox("Mes", meses_opciones)

selected_state_name = st.sidebar.selectbox("Estado", ["Todos"] + sorted(df["State_Name"].dropna().unique().tolist()))

opciones_severidad = {"Baja": "Baja", "Moderada": "Moderada", "Alta": "Alta", "Fatal": "Fatal"}
severity_visual = st.sidebar.multiselect("Severidad", options=list(opciones_severidad.keys()), default=list(opciones_severidad.keys()))
severity_real = [opciones_severidad[op] for op in severity_visual]

# Aplicación de filtros
filtered = df.copy()
if year != "Todos": 
    filtered = filtered[filtered["Year"] == year]
if mes != "Todos":
    filtered = filtered[filtered["Mes_Es"] == mes]
if selected_state_name != "Todos": 
    filtered = filtered[filtered["State_Name"] == selected_state_name]
filtered = filtered[filtered["Severity_Label"].isin(severity_real)]

# =====================================================
# 4. CUERPO PRINCIPAL: Título y KPIs
# =====================================================
st.markdown('''
    <div style="margin-bottom: 20px;">
        <h1 style="color: #16213e; font-size: 30px; font-weight: 800;">Accidentes de Tránsito en EE.UU.</h1>
    </div>
''', unsafe_allow_html=True)

# KPIs en una sola fila (5 columnas)
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Total Accidentes</div>
            <div class="kpi-value">{len(filtered):,}</div>
        </div>
    ''', unsafe_allow_html=True)

with k2:
    st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Estados Activos</div>
            <div class="kpi-value">{filtered["State"].nunique()}</div>
        </div>
    ''', unsafe_allow_html=True)

with k3:
    sev_promedio = SEVERITY_LABELS.get(round(filtered["Severity"].mean()), "N/D") if len(filtered) else "-"
    st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Severidad Promedio</div>
            <div class="kpi-value">{sev_promedio}</div>
        </div>
    ''', unsafe_allow_html=True)

with k4:
    duracion = f"{round(filtered['Duration_Minutes'].mean(),1)} min" if len(filtered) else "-"
    st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Duración Promedio</div>
            <div class="kpi-value">{duracion}</div>
        </div>
    ''', unsafe_allow_html=True)

with k5:
    hp = filtered["Hour"].value_counts().idxmax() if not filtered.empty else "-"
    hora_str = f"{int(hp)}:00" if hp != "-" else "-"
    st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Hora Pico</div>
            <div class="kpi-value">{hora_str}</div>
        </div>
    ''', unsafe_allow_html=True)

# =====================================================
# GRÁFICOS (Template)
# =====================================================
PLOTLY_LAYOUT = dict(template="plotly_white", paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#111827", size=14), title="")
def style_plotly(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(title_font=dict(color="#111827"), tickfont=dict(color="#111827"), showgrid=True, gridcolor="#e5e7eb")
    fig.update_yaxes(title_font=dict(color="#111827"), tickfont=dict(color="#111827"), showgrid=True, gridcolor="#e5e7eb")
    return fig

# =====================================================
# 5. MAPA PRINCIPAL Y TOP ZONAS
# =====================================================
# 1. FILA DE ENCABEZADOS 
head_map, head_toggle, head_top = st.columns([1.2, 1, 1])

with head_map:
    estado_texto = selected_state_name if selected_state_name != 'Todos' else 'Nacional'
    st.markdown(f'''
        <div style="font-size: 18px; font-weight: 700; color: #16213e; margin-bottom: 5px; margin-top: 10px;">
            🗺️ Vista Geográfica: 
            <span style="font-weight: 400; color: #4b5563;">{estado_texto}</span>
        </div>
    ''', unsafe_allow_html=True)

with head_toggle:
    map_type = st.radio(
        "Tipo de mapa:", 
        ["Mapa de Calor", "Mapa por Estados"], 
        horizontal=True, 
        label_visibility="collapsed"
    )

with head_top:
    titulo_top = "Ciudades" if selected_state_name != "Todos" else "Estados"
    st.markdown(f'''
        <div style="font-size: 18px; font-weight: 700; color: #16213e; margin-bottom: 5px; margin-top: 10px; text-align: left;">
            Top 10 {titulo_top} de Riesgo
        </div>
    ''', unsafe_allow_html=True)


# 2. FILA DE GRÁFICOS
HEATMAP_SCALE = [
    [0.00, "#2c7be5"],  # Azul
    [0.25, "#00bfff"],  # Celeste
    [0.50, "#32cd32"],  # Verde
    [0.75, "#ffd700"],  # Amarillo
    [1.00, "#ff4500"]   # Naranja/Rojo
]

HEATMAP_COLORS = [
    [44, 123, 229],
    [0, 191, 255],
    [50, 205, 50],
    [255, 215, 0],
    [255, 69, 0]
]

col_map_main, col_map_top = st.columns([2.2, 1])

with col_map_main:
    if map_type == "Mapa de Calor":
        map_df = filtered[["Start_Lat","Start_Lng"]].rename(columns={"Start_Lat":"lat","Start_Lng":"lon"})

        # Lógica de centrado y zoom
        if selected_state_name == "Todos":
            center_lat, center_lon, zoom_lvl = 39.8283, -98.5795, 3.0 
        else:
            center_lat = map_df["lat"].mean() if not map_df.empty else 39.8283
            center_lon = map_df["lon"].mean() if not map_df.empty else -98.5795
            zoom_lvl = 5.0

        # Contenedor principal para superposición
        st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
        
        deck = pdk.Deck(
            map_style="light",
            layers=[
                pdk.Layer(
                    "HeatmapLayer",
                    data=map_df.sample(min(len(map_df), 50000), random_state=42) if not map_df.empty else pd.DataFrame(columns=["lat", "lon"]),
                    get_position="[lon, lat]",
                    opacity=0.95,
                    intensity=1.8,
                    threshold=0.03,
                    radiusPixels=40,
                    colorRange=HEATMAP_COLORS
                )
            ],
            initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom_lvl, pitch=0),
            height=490 # Altura total
        )
        st.pydeck_chart(deck, use_container_width=True)

        # LEYENDA SUPERPUESTA (Flotante sobre el mapa)
        st.markdown('''
            <div style="position: absolute; bottom: 20px; left: 20px; background: rgba(255, 255, 255, 0.85); 
                        padding: 10px; border-radius: 8px; border: 1px solid #ddd; z-index: 100; font-size: 11px;">
                <div style="margin-bottom: 5px;"><b>Densidad de Accidentes</b></div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span>Baja</span>
                    <div style="width: 80px; height: 8px; background: linear-gradient(to right, #2c7be5, #00bfff, #32cd32, #ffd700, #ff4500);"></div>
                    <span>Alta</span>
                </div>
            </div>
            </div> ''', unsafe_allow_html=True)
        
    elif map_type == "Mapa por Estados":
        if not filtered.empty:
            map_agg = filtered.groupby(["State", "State_Name"]).agg(
                Accidentes=("State", "count"),
                Severidad_Media=("Severity", "mean")
            ).reset_index()
            
            fig_map = px.choropleth(
                map_agg, locations="State", locationmode="USA-states", color="Accidentes", 
                color_continuous_scale=HEATMAP_SCALE, scope="usa", hover_name="State_Name",
                hover_data={"State": False, "Accidentes": True, "Severidad_Media": ":.2f"},
                labels={"Accidentes": "Total Accidentes", "Severidad_Media": "Severidad Promedio"}
            )
            
            fig_map.add_scattergeo(
                locations=map_agg["State"],
                locationmode="USA-states",
                text=map_agg["Accidentes"],
                mode="text",
                textfont=dict(size=9, color="white"),
                showlegend=False,
                hoverinfo="skip"
            )

            fig_map.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=515,
                geo=dict(bgcolor='#ffffff', lakecolor='#f5f7fb'), 
                paper_bgcolor="#ffffff", 
                plot_bgcolor="#ffffff"
            )
            st.plotly_chart(fig_map, use_container_width=True, key="choropleth_main")
        else:
            st.warning("No hay datos para mostrar en el mapa.")

with col_map_top:
    if not filtered.empty:
        if selected_state_name != "Todos":
            summary = filtered.groupby("City").agg(Acc=("City","count"), Sev=("Severity","mean")).reset_index()
            summary = summary.assign(Score=summary["Acc"] * summary["Sev"]).sort_values("Score", ascending=False).head(10)
            entity_col = "City"
            axis_labels = {"Acc": "Accidentes", "City": "Ciudad", "Sev": "Severidad"}
        else:
            summary = filtered.groupby("State_Name").agg(Acc=("State_Name","count"), Sev=("Severity","mean")).sort_values("Acc", ascending=False).head(10).reset_index()
            entity_col = "State_Name"
            axis_labels = {"Acc": "Accidentes", "State_Name": "Estado", "Sev": "Severidad"}

        fig_top = px.bar(summary.sort_values("Acc", ascending=True), x="Acc", y=entity_col, orientation="h", color="Acc", 
                     color_continuous_scale=HEATMAP_SCALE, labels=axis_labels)
        
        fig_top.update_coloraxes(showscale=False)
        fig_top.update_layout(
            margin=dict(l=10, r=20, t=0, b=30),
            height=515 
        )
        st.plotly_chart(style_plotly(fig_top), use_container_width=True, key="top_chart_main")
    else:
        st.info("Sin datos suficientes.")

# =====================================================
# 6. PESTAÑAS INFERIORES
# =====================================================
tab_temporal, tab_clima = st.tabs([
    "🕒 Análisis Temporal", 
    "⛅ Factores Climáticos"
])

# --- PESTAÑA 1: TEMPORAL ---
with tab_temporal:
    if filtered.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
    else:
        r1_c1, r1_c2 = st.columns(2)
        
        with r1_c1:
            st.markdown("**Evolución temporal (Anual)**")
            yearly = filtered.groupby("Year").size().reset_index(name="Accidentes")
            fig = px.line(yearly, x="Year", y="Accidentes", markers=True, color_discrete_sequence=["#061736"],
                          labels={"Year": "Año", "Accidentes": "Total Accidentes"})
            fig.update_xaxes(dtick=1)
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(style_plotly(fig), use_container_width=True, key="line_year_unique")

        with r1_c2:
            st.markdown("**Accidentes por hora del día**")
            hc = filtered["Hour"].value_counts().sort_index()
            fig = px.bar(x=hc.index, y=hc.values, color=hc.values, 
                         color_continuous_scale="RdYlBu_r",
                         labels={"x":"Hora del Día","y":"Total Accidentes", "color": "Accidentes"})
            fig.update_xaxes(
                tickvals=[0, 4, 8, 12, 16, 20, 23],
                ticktext=["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:00"]
            )
            fig.update_coloraxes(showscale=False)
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(style_plotly(fig), use_container_width=True, key="bar_hour_unique")

        # --- FILA 2: Mapa de calor y Resumen Dinámico ---
        r2_c1, r2_c2 = st.columns([2, 1])

        with r2_c1:
            st.markdown("**Patrones por día y hora**")
            filtered_time = filtered.copy()
            filtered_time["Weekday_Es"] = filtered_time["Weekday"].map(DIAS_ES).fillna(filtered_time["Weekday"])
            
            heat = pd.crosstab(filtered_time["Hour"], filtered_time["Weekday_Es"])
            ordered_days = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
            heat = heat.reindex(columns=[d for d in ordered_days if d in heat.columns])
            
            fig = px.imshow(heat, aspect="auto", color_continuous_scale="RdYlBu_r", 
                            labels={"x": "Día de la Semana", "y": "Hora", "color": "Accidentes"})
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            fig.update_yaxes(
                tickvals=[0, 4, 8, 12, 16, 20, 23],
                ticktext=["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:00"]
            )
            st.plotly_chart(style_plotly(fig), use_container_width=True, key="heatmap_time_unique")

        with r2_c2:
            hora_pico = hc.idxmax() if not hc.empty else "N/D"
            dia_pico = filtered_time["Weekday_Es"].value_counts().idxmax() if not filtered_time.empty else "N/D"
            
            if "Start_Time" in filtered.columns:
                accidentes_por_dia = filtered.groupby(filtered["Start_Time"].dt.date).size()
                if not accidentes_por_dia.empty:
                    media_diaria = accidentes_por_dia.mean()
                    mediana_diaria = accidentes_por_dia.median()
                    max_diario = accidentes_por_dia.max()
                    min_diario = accidentes_por_dia.min()
                    
                    st.markdown(
                        f"""
                        <div style=" height:500px; display:flex; align-items:center;">
                            <div style="
                                background-color:#f8fafc;
                                border-left:4px solid #061736;
                                padding:25px;
                                border-radius:8px;
                                font-size:15.5px;
                                color:#334155;
                                line-height:1.7;
                                box-shadow:0 2px 4px rgba(0,0,0,0.05);
                                width:100%;
                            ">
                                El análisis estadístico revela una media de <b>{int(media_diaria):,}</b> incidentes diarios, 
                                con una mediana de <b>{int(mediana_diaria):,}</b>. La actividad fluctuó entre un mínimo de 
                                <b>{int(min_diario):,}</b> registros y un pico máximo de <b>{int(max_diario):,}</b> colisiones 
                                en la jornada más crítica.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    

# --- PESTAÑA 2: CLIMA ---
with tab_clima:

    if filtered.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

    else:

        # =====================================================
        # FILA 1
        # =====================================================
        r1_c1, r1_c2 = st.columns(2)

        # -----------------------------------------------------
        # CLIMA VS SEVERIDAD
        # -----------------------------------------------------
        with r1_c1:

            st.markdown("**Clima vs Severidad**")

            filtered_weather = filtered.copy()

            if "Weather_Group" in filtered_weather.columns:
                filtered_weather["Weather_Group_Es"] = (
                    filtered_weather["Weather_Group"]
                    .map(CLIMAS_ES)
                    .fillna(filtered_weather["Weather_Group"])
                )
                weather_col = "Weather_Group_Es"
            else:
                weather_col = "Weather_Group"

            table = pd.crosstab(
                filtered_weather[weather_col],
                filtered_weather["Severity_Label"],
                normalize="index"
            )

            fig = px.imshow(
                table,
                text_auto=".0%",
                aspect="auto",
                color_continuous_scale="YlOrRd",
                labels={
                    "x": "Severidad",
                    "y": "Condición Climática",
                    "color": "Proporción"
                }
            )

            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=420
            )

            st.plotly_chart(
                style_plotly(fig),
                use_container_width=True,
                key="weather_severity"
            )

        # -----------------------------------------------------
        # ACCIDENTES POR ESTACIÓN
        # -----------------------------------------------------
        with r1_c2:
            st.markdown("**Accidentes por Estación del Año**")
            
            # Asegurar que todas las estaciones existan aunque no tengan accidentes (rellenar con 0)
            if not filtered.empty:
                # Mapeo de estaciones
                filtered_season = filtered.copy()
                filtered_season["Season_Es"] = filtered_season["Season"].map(ESTACIONES_ES).fillna(filtered_season["Season"])
                
                # Crear conteo y asegurar que estén las 4 estaciones
                season = filtered_season["Season_Es"].value_counts().reindex(["Invierno", "Primavera", "Verano", "Otoño"], fill_value=0).reset_index()
                season.columns = ["Estación", "Accidentes"]
            else:
                season = pd.DataFrame({"Estación": ["Invierno", "Primavera", "Verano", "Otoño"], "Accidentes": [0, 0, 0, 0]})

            season_colors = {"Invierno": "#3B82F6", "Primavera": "#22C55E", "Verano": "#EAB308", "Otoño": "#F97316"}
            season["Label"] = season["Accidentes"].apply(lambda x: f"{x:,}")

            fig = px.bar(
                season, x="Accidentes", y="Estación", orientation="h", color="Estación",
                color_discrete_map=season_colors, text="Label"
            )
            fig.update_traces(textposition="inside", insidetextanchor="end", texttemplate="%{text}  ", textfont=dict(color="white", size=12))
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=420, showlegend=False, xaxis=dict(showticklabels=False, title=""), plot_bgcolor="white")
            st.plotly_chart(style_plotly(fig), use_container_width=True, key="season_chart")
        # =====================================================
        # FILA 2
        # =====================================================
        r2_c1, r2_c2 = st.columns([2, 1])

        # -----------------------------------------------------
        # MATRIZ CLIMÁTICA
        # -----------------------------------------------------
        with r2_c1:

            st.markdown( f"**Distribución Climática por {'Estado' if selected_state_name == 'Todos' else 'Ciudad'} (%)**")

            filtered_c = filtered.copy()

            if "Weather_Group" in filtered_c.columns:
                filtered_c["Weather_Group_Es"] = (
                    filtered_c["Weather_Group"]
                    .map(CLIMAS_ES)
                    .fillna(filtered_c["Weather_Group"])
                )

                weather_col_matrix = "Weather_Group_Es"
            else:
                weather_col_matrix = "Weather_Group"

            if selected_state_name == "Todos":
                weather_state = pd.crosstab(
                    filtered_c["State_Name"],
                    filtered_c[weather_col_matrix],
                    normalize="index"
                ) * 100

                top_entities = (
                    filtered_c["State_Name"]
                    .value_counts()
                    .head(10)
                    .index
                )

                weather_state = weather_state.loc[
                    weather_state.index.intersection(top_entities)
                ]

                y_label = "Estado"

            else:

                weather_state = pd.crosstab(
                    filtered_c["City"],
                    filtered_c[weather_col_matrix],
                    normalize="index"
                ) * 100

                top_entities = (
                    filtered_c["City"]
                    .value_counts()
                    .head(10)
                    .index
                )

                weather_state = weather_state.loc[
                    weather_state.index.intersection(top_entities)
                ]

                y_label = "Ciudad"

            fig = px.imshow(
                weather_state,
                text_auto=".0f",
                aspect="auto",
                color_continuous_scale=[
                    [0.0, "#3B82F6"],
                    [0.33, "#22C55E"],
                    [0.66, "#EAB308"],
                    [1.0, "#F97316"]
                ],
                labels={
                    "x": "Clima",
                    "y": y_label,
                    "color": "Porcentaje (%)"
                }
            )

            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=500
            )

            st.plotly_chart(
                style_plotly(fig),
                use_container_width=True,
                key="weather_state_matrix"
            )

        # -----------------------------------------------------
        # RESUMEN ESTADÍSTICO
        # -----------------------------------------------------
        with r2_c2:

            clima_mas_comun = (
                filtered_weather[weather_col]
                .value_counts()
                .idxmax()
            )

            porcentaje_clima = (
                filtered_weather[weather_col]
                .value_counts(normalize=True)
                .max() * 100
            )
            
            idx_max = season["Accidentes"].idxmax()
            estacion_pico = season.loc[idx_max, "Estación"]
            
            severidad_clima = (
                filtered_weather
                .groupby(weather_col)["Severity"]
                .mean()
                .sort_values(ascending=False)
            )

            clima_mas_severo = severidad_clima.index[0]
            severidad_media = severidad_clima.iloc[0]

            total_condiciones = (
                filtered_weather[weather_col]
                .nunique()
            )

            if selected_state_name == "Todos":
                texto_clima = f"""
                <div style=" background-color:#f8fafc; border-left:4px solid #061736; padding:25px; border-radius:8px;
                    font-size:15.5px; color:#334155; line-height:1.7; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-top:35px;
                ">
                La mayor proporción de accidentes se registra bajo condiciones de
                <b>{clima_mas_comun}</b>, representando aproximadamente
                <b>{porcentaje_clima:.1f}%</b> del total de incidentes observados.

                Sin embargo, las condiciones de
                <b>{clima_mas_severo}</b>
                presentan la mayor severidad promedio
                (<b>{severidad_media:.2f}</b>), lo que sugiere una mayor probabilidad
                de eventos con consecuencias más graves.

                </div>
                """

            else:

                texto_clima = f"""
                <div style=" background-color:#f8fafc; border-left:4px solid #061736; padding:25px; border-radius:8px;
                    font-size:15.5px; color:#334155; line-height:1.7; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-top:35px;
                ">

                En <b>{selected_state_name}</b>, la mayor proporción de accidentes se registra bajo condiciones de
                <b>{clima_mas_comun}</b>, representando aproximadamente
                <b>{porcentaje_clima:.1f}%</b> de los incidentes observados.

                Las condiciones de
                <b>{clima_mas_severo}</b>
                presentan la severidad promedio más alta
                (<b>{severidad_media:.2f}</b>), indicando un mayor nivel de riesgo
                cuando este fenómeno está presente.

                </div>
                """

            st.markdown(
                f"""
                <div style=" height:500px; display:flex; align-items:center;">
                    {texto_clima}
                </div>
                """,
                unsafe_allow_html=True
            )