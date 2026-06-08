# app2_v3_visual_fix.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import pydeck as pdk
import os
import base64

st.set_page_config(page_title="Dashboard Accidentes EE.UU.", page_icon="🚗", layout="wide")

pio.templates.default = "plotly_white"

# =====================================================
# ESTILO CORREGIDO
# =====================================================
st.markdown("""
<style>
.stApp{
    background-color:#f5f7fb;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#061736 0%,#081f4d 100%);
}
/* Titulos y etiquetas del sidebar */
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{
    color:white !important;
}

/* Caja de filtros */
[data-testid="stSidebar"] [data-baseweb="select"]{
    background:white !important;
    border-radius:8px;
}

/* Valor seleccionado */
[data-testid="stSidebar"] [data-baseweb="select"] span{
    color:#111827 !important;
}

/* Texto de búsqueda */
[data-testid="stSidebar"] [data-baseweb="select"] input{
    color:#111827 !important;
}

/* Multiselect tags */
[data-testid="stSidebar"] [data-baseweb="tag"]{
    background:#e5e7eb !important;
}

[data-testid="stSidebar"] [data-baseweb="tag"] span{
    color:#111827 !important;
}


/* NO cambiar color global del contenido principal */
h1,h2,h3,label,p,span{
    color:#16213e;
}



.kpi-card{
    border-radius:18px;
    padding:18px;
    border:1px solid #e5e7eb;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
    min-height:120px;
    display:flex;
    flex-direction:column;
    justify-content:flex-start;
}


/* Tabla resumen */
[data-testid="stDataFrame"]{
    background:white;
    border:1px solid #e5e7eb;
    border-radius:12px;
}

</style>
""", unsafe_allow_html=True)


def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

@st.cache_data
def load_data():
    return pd.read_csv(
        os.path.join("processed","US_Accidents_Processed.csv"),
        parse_dates=["Start_Time"]
    )

df = load_data()

STATE_NAMES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas",
    "CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware",
    "FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho",
    "IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas",
    "KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
    "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
    "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
    "NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York",
    "NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma",
    "OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina",
    "SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah",
    "VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia",
    "WI":"Wisconsin","WY":"Wyoming"
}


df["State_Name"] = df["State"].map(STATE_NAMES).fillna(df["State"])

SEVERITY_LABELS = {
    1: "Baja",
    2: "Moderada",
    3: "Alta",
    4: "Fatal"
}

SEVERITY_COLORS = {
    "Baja": "#22C55E",
    "Moderada": "#EAB308",
    "Alta": "#F97316",
    "Fatal": "#DC2626"
}

df["Severity_Label"] = df["Severity"].map(SEVERITY_LABELS)



# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.image("assets/car.png", width=70)
st.sidebar.markdown("## Accidentes de Tránsito EE.UU.")

year = st.sidebar.selectbox("Año", ["Todos"] + sorted(df["Year"].unique().tolist()))

selected_state_name = st.sidebar.selectbox(
    "Estado",
    ["Todos"] + sorted(df["State_Name"].dropna().unique().tolist())
)

weather = st.sidebar.selectbox("Condición climática", ["Todas"] + sorted(df["Weather_Group"].dropna().unique().tolist()))
period = st.sidebar.selectbox("Momento del día", ["Todos","Madrugada","Mañana","Tarde","Noche"])
hours = st.sidebar.slider("Rango horario",0,23,(0,23))
severity = st.sidebar.multiselect("Nivel de severidad", ["Baja","Moderada","Alta","Fatal"], default=["Baja","Moderada","Alta","Fatal"])

filtered = df.copy()

if year != "Todos":
    filtered = filtered[filtered["Year"] == year]


if weather != "Todas":
    filtered = filtered[filtered["Weather_Group"] == weather]

filtered = filtered[filtered["Severity_Label"].isin(severity)]
filtered = filtered[filtered["Hour"].between(hours[0], hours[1])]

if period != "Todos":
    filtered = filtered[filtered["Time_Period"] == period]

# =====================================================
# HEADER
# =====================================================
st.title("Dashboard de Accidentes de Tránsito en EE.UU.")
st.caption("Accidentes registrados entre 2016 y 2023")

if selected_state_name != "Todos":
    filtered = filtered[filtered["State_Name"] == selected_state_name]

# =====================================================
# TEMPLATE PLOTLY CLARO
# =====================================================
PLOTLY_LAYOUT = dict(
    template="plotly_white",

    paper_bgcolor="white",
    plot_bgcolor="white",

    font=dict(
        color="#111827",
        size=14
    ),

    hoverlabel=dict(
        bgcolor="white",
        font_size=14,
        font_color="#111827"
    ),

    title=None
)
def style_plotly(fig):

    fig.update_layout(**PLOTLY_LAYOUT)

    try:
        fig.layout.title.text = ""
    except:
        pass
    
    fig.update_xaxes(
        title_font=dict(color="#111827"),
        tickfont=dict(color="#111827"),
        showgrid=True,
        gridcolor="#e5e7eb"
    )

    fig.update_yaxes(
        title_font=dict(color="#111827"),
        tickfont=dict(color="#111827"),
        showgrid=True,
        gridcolor="#e5e7eb"
    )

    fig.update_traces(
        hoverlabel=dict(
            bgcolor="white",
            font_color="#111827"
        )
    )

    return fig

# =====================================================
# KPIs
# =====================================================
c1,c2,c3,c4,c5 = st.columns(5)

kpi_data = [
    ("🚗","Accidentes",f"{len(filtered):,}","#DBEAFE"),
    ("🗺️","Estados",filtered["State"].nunique(),"#DCFCE7"),
    (
        "📊",
        "Severidad",
        (
            SEVERITY_LABELS.get(
                round(filtered["Severity"].mean()),
                "N/D"
            ) if len(filtered) else "-"
        ),
        "#FEE2E2"
    ),
    ("🕒","Hora Pico",f"{int(filtered['Hour'].mode().iloc[0])}:00" if len(filtered) else "-","#FFEDD5"),
    ("📍","Duración",f"{round(filtered['Duration_Minutes'].mean(),1)} min" if len(filtered) else "-","#FEE2E2"),
]

for col, (icon, title, value, bg) in zip([c1,c2,c3,c4,c5], kpi_data):
    with col:
        st.markdown(
            f'''
            <div style="
                background:{bg};
                border-radius:18px;
                padding:18px;
                border:1px solid #e5e7eb;
                min-height:110px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                text-align:center;
            ">
                <div style="font-size:42px;">{icon}</div>
                <div style="font-size:18px;font-weight:600;color:#334155;">
                    {title}
                </div>
                <div style="font-size:24px;font-weight:800;color:#0f172a;">
                    {value}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

# =====================================================
# MAPA
# =====================================================
left,right = st.columns([4,1])

with left:
    st.subheader("Zonas geográficas de alta concentración")

    map_df = filtered[["Start_Lat","Start_Lng"]].rename(
        columns={"Start_Lat":"lat","Start_Lng":"lon"}
    )

    deck = pdk.Deck(
        map_style="light",
        layers=[
            pdk.Layer(
    "HeatmapLayer",
    data=map_df.sample(
        min(len(map_df), 50000),
        random_state=42
    ),

    get_position="[lon, lat]",

    opacity=0.95,

    intensity=1.8,

    threshold=0.03,

    radiusPixels=40,

    colorRange=[
        [44, 123, 229],    # Azul
        [0, 191, 255],     # Celeste
        [50, 205, 50],     # Verde
        [255, 215, 0],     # Amarillo
        [255, 69, 0]       # Rojo
    ]
)
        ],
        initial_view_state=pdk.ViewState(
            latitude=39,
            longitude=-98,
            zoom=3
        )
    )
    st.pydeck_chart(deck)

with right:

    c_icon, c_title = st.columns([0.7,3])

    with c_icon:
        st.image(
            "assets/state.png",
            width=60
        )
    
    with c_title:

        st.markdown("### Estado seleccionado")

        if selected_state_name == "Todos":

            st.markdown("### Estados Unidos")

            st.info(
                "Mostrando todos los estados"
            )

        else:

            st.markdown(
                f"### {selected_state_name}"
            )
    
        
        active_filters = []

        if selected_state_name != "Todos":
            active_filters.append(selected_state_name)

        if year != "Todos":
            active_filters.append(str(year))

        if weather != "Todas":
            active_filters.append(weather)

        if period != "Todos":
            active_filters.append(period)

        if len(severity) < len(df["Severity"].unique()):
            active_filters.append("Severidad: " + ",".join(map(str, severity)))

        if active_filters:
            st.caption("Filtros activos")
            st.info(" | ".join(active_filters))

# =====================================================
# FILA 2
# =====================================================
a,b,c = st.columns(3)

with a:
    st.subheader("Accidentes por hora")
    hc = filtered["Hour"].value_counts().sort_index()

    fig = px.bar(
        x=hc.index,
        y=hc.values,
        labels={"x":"Hora","y":"Accidentes"},
        color_discrete_sequence=["#2563eb"]
    )
    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

with b:
    st.subheader("Patrones día y hora")

    heat = pd.crosstab(filtered["Hour"], filtered["Weekday"])

    ordered_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_map = {
        "Monday":"Lunes",
        "Tuesday":"Martes",
        "Wednesday":"Miércoles",
        "Thursday":"Jueves",
        "Friday":"Viernes",
        "Saturday":"Sábado",
        "Sunday":"Domingo"
    }

    heat = heat.reindex(columns=[d for d in ordered_days if d in heat.columns])
    heat.columns = [day_map.get(c,c) for c in heat.columns]

    fig = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale="RdYlBu_r"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Día:</b> %{x}<br>" +
            "<b>Hora:</b> %{y}:00<br>" +
            "<b>Accidentes registrados:</b> %{z:,}<extra></extra>"
        )
    )

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

with c:
    st.subheader("Evolución temporal")

    yearly = filtered.groupby("Year").size().reset_index(name="Accidentes")

    fig = px.line(
        yearly,
        x="Year",
        y="Accidentes",
        markers=True
    )
    fig = style_plotly(fig)
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# FILA 3
# =====================================================
a,b,c = st.columns(3)

with a:
    st.subheader("Clima vs severidad")

    table = pd.crosstab(
        filtered["Weather_Group"],
        filtered["Severity_Label"],
        normalize="index"
    )

    severity_order = ["Baja","Moderada","Alta","Fatal"]
    table = table.reindex(columns=[c for c in severity_order if c in table.columns])

    fig = px.imshow(
        table,
        text_auto=".0%",
        color_continuous_scale="YlOrRd"
    )
    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

with b:
    st.subheader("Severidad promedio por estado")

    sev = (
        filtered
        .groupby(["State","State_Name"])["Severity"]
        .mean()
        .reset_index()
    )

    fig = px.choropleth(
        sev,
        locations="State",
        locationmode="USA-states",
        color="Severity",
        color_continuous_scale="YlOrRd",
        scope="usa",
        hover_name="State_Name"
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Severidad promedio: %{z:.2f}<extra></extra>"
    )

    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

with c:

    if selected_state_name != "Todos":

        st.subheader("Top ciudades")

        summary = (
            filtered.groupby("City")
            .agg(
                Accidentes=("City","count"),
                Severidad=("Severity","mean")
            )
            .reset_index()
        )

        # Ranking combinado: cantidad de accidentes + severidad
        summary["Score"] = (
            summary["Accidentes"] * summary["Severidad"]
        )

        summary = (
            summary
            .sort_values("Score", ascending=False)
            .head(10)
        )

    else:

        st.subheader("Top estados")

        summary = (
            filtered.groupby("State_Name")
            .agg(
                Accidentes=("State_Name","count"),
                Severidad=("Severity","mean")
            )
            .sort_values("Accidentes", ascending=False)
            .head(10)
            .reset_index()
        )

    entity_col = "City" if selected_state_name != "Todos" else "State_Name"

    fig = px.bar(
        summary.sort_values("Accidentes", ascending=True),
        x="Accidentes",
        y=entity_col,
        orientation="h",
        color="Severidad",
        color_continuous_scale="YlOrRd",
        text="Accidentes"
    )

    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Accidentes: %{x:,}<br>" +
            "Severidad promedio: %{marker.color:.2f}<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="Cantidad de accidentes",
        yaxis_title="",
        coloraxis_colorbar_title="Severidad promedio (1-4)"
    )

    fig = style_plotly(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# FILA 4
# =====================================================
a,b = st.columns(2)

with a:
    st.subheader("Accidentes por estación")

    season = (
        filtered["Season"]
        .value_counts()
        .reset_index()
    )

    season.columns = [
        "Season",
        "Accidentes"
    ]

    season_order = [
        "Winter",
        "Spring",
        "Summer",
        "Fall"
    ]

    season["Season"] = pd.Categorical(
        season["Season"],
        categories=season_order,
        ordered=True
    )

    season = season.sort_values("Season")

    season_colors = {
        "Winter": "#3B82F6",
        "Spring": "#22C55E",
        "Summer": "#EAB308",
        "Fall": "#F97316"
    }

    fig = px.bar(
        season,
        x="Accidentes",
        y="Season",
        orientation="h",
        color="Season",
        color_discrete_map=season_colors
    )

    fig = style_plotly(fig)

    fig.update_layout(
        showlegend=False,
        yaxis_title="",
        xaxis_title="Cantidad de accidentes"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with b:
    st.subheader("Patrones climáticos por estado (%)")

    weather_state = pd.crosstab(
        filtered["State_Name"],
        filtered["Weather_Group"],
        normalize="index"
    ) * 100

    top_states = (
        filtered["State_Name"]
        .value_counts()
        .head(10)
        .index
    )

    weather_state = weather_state.loc[
        weather_state.index.intersection(top_states)
    ]

    fig = px.imshow(
        weather_state,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale=[
            [0.0, "#3B82F6"],   # Azul
            [0.33, "#22C55E"],  # Verde
            [0.66, "#EAB308"],  # Amarillo
            [1.0, "#F97316"]    # Naranja
        ]
    )

    fig.update_layout(
        xaxis_title="Condición climática",
        yaxis_title="Estado"
    )

    fig = style_plotly(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )
