import streamlit as st
import pandas as pd
import numpy as np
import os

try:
    os.environ["KAGGLE_API_TOKEN"] = st.secrets["KAGGLE_API_TOKEN"]
except:
    os.environ["KAGGLE_API_TOKEN"] = "KGAT_6982f2553b685ee4e9b9acb994bfd776"
import kagglehub

st.set_page_config( page_title="US Accidents Dashboard", page_icon="🚗", layout="wide")

DATE_COLUMN = 'Start_Time'

@st.cache_data
def load_data(nrows):
    path = kagglehub.dataset_download( "sobhanmoosavi/us-accidents")
    csv_path = os.path.join( path, "US_Accidents_March23.csv")
    data = pd.read_csv( csv_path, nrows=nrows)
    data["Start_Time"] = pd.to_datetime(data["Start_Time"], format="mixed", errors="coerce")
    return data

st.title("🚗 Dashboard de Accidentes de Tránsito en EE.UU.")
st.caption("Accidentes registrados en Estados Unidos entre 2016 y 2023.")

st.text(""" Este conjunto de datos contiene información sobre accidentes de tránsito registrados en Estados Unidos. Incluye ubicación geográfica, severidad, condiciones climáticas y horarios de ocurrencia.""")

# Cargar datos
with st.spinner("Cargando datos..."):
    data = load_data(100000)

# Mostrar datos
#if st.checkbox('Mostrar datos', value=True):
#    st.write(data)

st.markdown("### Resumen General")

total_accidents = len(data)
total_states = data["State"].nunique()
avg_severity = round(data["Severity"].mean(), 2)
peak_hour = data[DATE_COLUMN].dt.hour.value_counts().idxmax()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Accidentes", f"{total_accidents:,}")
col2.metric("Estados", total_states)
col3.metric("Severidad Prom.", avg_severity)
col4.metric("Hora Pico", f"{peak_hour}:00")

col1, col2 = st.columns(2)

with col1:
    st.subheader('Accidentes por Hora')
    hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
    st.bar_chart(hist_values)

with col2:
    st.subheader('Distribución de Severidad')
    severity_counts = data['Severity'].value_counts().sort_index()
    st.bar_chart(severity_counts)



st.markdown("### Distribución Geográfica")

map_data = data[['Start_Lat', 'Start_Lng']].rename(
    columns={'Start_Lat': 'lat', 'Start_Lng': 'lon'}
)

st.map(map_data, zoom=3)