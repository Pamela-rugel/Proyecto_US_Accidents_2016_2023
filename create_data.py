import pandas as pd
import kagglehub
import os

SAMPLE_SIZE = 500000
RANDOM_STATE = 42

print("Descargando dataset...")

path = kagglehub.dataset_download(
    "sobhanmoosavi/us-accidents"
)

csv_path = os.path.join(
    path,
    "US_Accidents_March23.csv"
)


print("Leyendo dataset...")

df = pd.read_csv(
    csv_path,
    usecols=[
    # Identificador
    "ID",

    # Tiempo
    "Start_Time",
    "End_Time",

    # Geografía
    "Start_Lat",
    "Start_Lng",
    "State",
    "City",
    "County",

    # Severidad
    "Severity",

    # Clima
    "Weather_Condition",
    "Temperature(F)",
    "Visibility(mi)",
    "Pressure(in)",
    "Humidity(%)",
    "Wind_Speed(mph)",
    "Wind_Chill(F)",
    "Precipitation(in)",

    # Infraestructura vial
    "Amenity",
    "Bump",
    "Crossing",
    "Give_Way",
    "Junction",
    "No_Exit",
    "Railway",
    "Roundabout",
    "Station",
    "Stop",
    "Traffic_Calming",
    "Traffic_Signal",
    "Turning_Loop",

    # Astronómico
    "Sunrise_Sunset"
]
)

print("Procesando fechas...")

df["Start_Time"] = pd.to_datetime(
    df["Start_Time"],
    format="mixed",
    errors="coerce"
)

df["Year"] = df["Start_Time"].dt.year

df = df.dropna(subset=["Year"])



print("Generando muestra estratificada...")

sample_df = (
    df.groupby("Year", group_keys=False)
      .apply(
          lambda x: x.sample(
              n=max(
                  1,
                  round(
                      len(x) / len(df) * SAMPLE_SIZE
                  )
              ),
              random_state= RANDOM_STATE
          )
      )
      .reset_index(drop=True)
)

os.makedirs("data", exist_ok=True)

output_file = os.path.join(
    "data",
    "US_Accidents.csv"
)

sample_df.to_csv(
    output_file,
    index=False
)

print(f"Archivo generado: {output_file}")
print(f"Registros: {len(sample_df):,}")

print("\nDistribución por año:")
sample_df["Year"] = (
    pd.to_datetime(sample_df["Start_Time"])
    .dt.year
)
print(
    sample_df["Year"]
    .value_counts()
    .sort_index()
)