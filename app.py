import streamlit as st
import pandas as pd
import numpy as np
import os
from preprocessing import preprocess_data

try:
    os.environ["KAGGLE_API_TOKEN"] = st.secrets["KAGGLE_API_TOKEN"]
except:
    os.environ["KAGGLE_API_TOKEN"] = "KGAT_6982f2553b685ee4e9b9acb994bfd776"
import kagglehub

st.set_page_config( page_title="US Accidents Dashboard", page_icon="🚗", layout="wide")

DATE_COLUMN = 'Start_Time'

@st.cache_data(show_spinner=False)
def load_data(nrows):
    path = kagglehub.dataset_download( "sobhanmoosavi/us-accidents")
    csv_path = os.path.join( path, "US_Accidents_March23.csv")
    data = pd.read_csv( csv_path, nrows=nrows)
    data = preprocess_data(data)
    return data

st.title("🚗 Dashboard de Accidentes de Tránsito en EE.UU.")
st.caption("Accidentes registrados en Estados Unidos entre 2016 y 2023.")

st.text(""" Este conjunto de datos contiene información sobre accidentes de tránsito registrados en Estados Unidos. Incluye ubicación geográfica, severidad, condiciones climáticas y horarios de ocurrencia.""")

# Cargar datos
with st.spinner("Cargando datos..."):
    data = load_data(1000000)

# Mostrar datos
#if st.checkbox('Mostrar datos', value=True):
#    st.write(data)

# Sidebar
st.sidebar.header("Filtros")

selected_year = st.sidebar.selectbox(
    "Año",
    ["Todos"] + sorted(data["Year"].unique().tolist())
)


selected_severity = st.sidebar.multiselect(
    "Severidad",
    sorted(data["Severity"].unique()),
    default=sorted(data["Severity"].unique())
)

selected_hour = st.sidebar.selectbox(
    "Hora",
    ["Todas"] + list(range(24))
)

selected_state = st.sidebar.selectbox(
    "Estado",
    ["Todos"] + sorted(data["State"].dropna().unique().tolist())
)

# Aplicar filtros
filtered_data = data.copy()

if selected_year != "Todos":
    filtered_data = filtered_data[
        filtered_data["Year"] == selected_year
    ]

filtered_data = filtered_data[
    filtered_data["Severity"].isin(selected_severity)
]

if selected_hour != "Todas":
    filtered_data = filtered_data[
        filtered_data["Hour"] == selected_hour
    ]

if selected_state != "Todos":
    filtered_data = filtered_data[
        filtered_data["State"] == selected_state
    ]

# Cards de KPI
st.markdown("### Resumen General")

total_accidents = len(filtered_data)
total_states = filtered_data["State"].nunique()
avg_severity = round(filtered_data["Severity"].mean(), 2)
peak_hour = filtered_data[DATE_COLUMN].dt.hour.value_counts().idxmax()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Accidentes", f"{total_accidents:,}")
col2.metric("Estados", total_states)
col3.metric("Severidad Prom.", avg_severity)
col4.metric("Hora Pico", f"{peak_hour}:00")

col1, col2 = st.columns(2)

with col1:
    st.subheader('Accidentes por Hora')
    hist_values = np.histogram(filtered_data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
    st.bar_chart(hist_values)

with col2:
    st.subheader('Distribución de Severidad')
    severity_counts = filtered_data['Severity'].value_counts().sort_index()
    st.bar_chart(severity_counts)



st.markdown("### Distribución Geográfica")

map_data = filtered_data[['Start_Lat', 'Start_Lng']].rename(
    columns={'Start_Lat': 'lat', 'Start_Lng': 'lon'}
)

st.map(map_data, zoom=3)