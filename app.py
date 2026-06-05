import streamlit as st
import pandas as pd
import numpy as np
import kagglehub
import os

DATE_COLUMN = 'Start_Time'

@st.cache_data
def load_data(nrows):
    path = kagglehub.dataset_download( "sobhanmoosavi/us-accidents")
    csv_path = os.path.join( path, "US_Accidents_March23.csv")
    data = pd.read_csv( csv_path, nrows=nrows)
    data["Start_Time"] = pd.to_datetime(data["Start_Time"], format="mixed", errors="coerce")
    return data

st.title("Análisis de Accidentes de Tránsito en EE.UU.")

st.header("Análisis Exploratorio de Datos")

st.subheader("Descripción")

st.text(""" Este conjunto de datos contiene información sobre accidentes de tránsito registrados en Estados Unidos. Incluye ubicación geográfica, severidad, condiciones climáticas y horarios de ocurrencia.""")

# Cargar datos
data_load_state = st.text('Cargando datos...')
data = load_data(500000)
data_load_state.success('Datos cargados correctamente')

# Mostrar datos
if st.checkbox('Mostrar datos', value=True):
    st.write(data)

# -----------------------------------
# Accidentes por hora
# -----------------------------------
st.subheader('Número de accidentes por hora')

hist_values = np.histogram( data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]

st.bar_chart( hist_values, x_label="Hora", y_label="Número de accidentes")

st.text("""El gráfico muestra la distribución de accidentes durante el día, permitiendo identificar horas pico de siniestralidad.""")

# -----------------------------------
# Mapa general
# -----------------------------------
st.subheader('Mapa de accidentes')

st.text("""Distribución geográfica de los accidentes registrados.""")

map_data = data[['Start_Lat', 'Start_Lng']].rename( columns={ 'Start_Lat': 'lat', 'Start_Lng': 'lon'})

st.map(map_data, zoom=3)

# -----------------------------------
# Filtro por hora
# -----------------------------------
hour_to_filter = st.slider('Seleccione una hora', 0, 23, 17)

filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader( f'Accidentes registrados a las {hour_to_filter}:00')

filtered_map = filtered_data[['Start_Lat', 'Start_Lng']].rename(columns={'Start_Lat': 'lat','Start_Lng': 'lon'})

st.map(filtered_map, zoom=4)

# -----------------------------------
# Severidad
# -----------------------------------
st.subheader("Distribución de severidad")

severity_counts = ( data['Severity'].value_counts().sort_index())

st.bar_chart( severity_counts, x_label="Nivel de severidad", y_label="Cantidad de accidentes")