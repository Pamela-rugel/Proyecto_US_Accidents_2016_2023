import pandas as pd
import kagglehub
import os

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
        "Start_Time",
        "Start_Lat",
        "Start_Lng",
        "Severity",
        "State",
        "Weather_Condition",
        "Temperature(F)",
        "Visibility(mi)",
        "Pressure(in)",
        "Wind_Speed(mph)"
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

sample_size = 500000

print("Generando muestra estratificada...")

sample_df = (
    df.groupby("Year", group_keys=False)
      .apply(
          lambda x: x.sample(
              n=max(
                  1,
                  round(
                      len(x) / len(df) * sample_size
                  )
              ),
              random_state=42
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

print(
    sample_df["Year"]
    .value_counts()
    .sort_index()
)