import pandas as pd

def preprocess_data(data):
    # Casi todos sus valores nulos
    data = data.drop(
        columns=["End_Lng", "End_Lat"],
        errors="ignore"
    )
    # Conversión de fecha
    data["Start_Time"] = pd.to_datetime(
        data["Start_Time"],
        format="mixed",
        errors="coerce"
    )

    # Eliminación de registros inválidos
    data = data.dropna(
        subset=[
            "Start_Time",
            "Start_Lat",
            "Start_Lng",
            "Severity"
        ]
    )

    # Eliminación de duplicados
    data = data.drop_duplicates()

    # Filtrado geográfico (Estados Unidos)
    data = data[
        (data["Start_Lat"].between(24, 50))
        & (data["Start_Lng"].between(-125, -66))
    ]

    # Conversión de tipos
    data["Severity"] = data["Severity"].astype(int)

    # Tratamiento de valores faltantes
    if "Weather_Condition" in data.columns:
        data["Weather_Condition"] = data["Weather_Condition"].fillna("Unknown")

    if "Temperature(F)" in data.columns:
        data["Temperature(F)"] = data["Temperature(F)"].fillna(
            data["Temperature(F)"].median()
        )

    # Variables temporales
    data["Year"] = data["Start_Time"].dt.year
    data["Month"] = data["Start_Time"].dt.month
    data["Day"] = data["Start_Time"].dt.day
    data["Hour"] = data["Start_Time"].dt.hour
    data["Weekday"] = data["Start_Time"].dt.day_name()

    # Indicador de fin de semana
    data["Is_Weekend"] = data["Start_Time"].dt.dayofweek >= 5

    # Estación del año
    data["Season"] = data["Month"].map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Fall", 10: "Fall", 11: "Fall"
    })

    # Agrupación de condiciones climáticas
    if "Weather_Condition" in data.columns:

        data["Weather_Group"] = "Other"

        weather_groups = {
            "Rain": "Rain",
            "Snow": "Snow",
            "Fog": "Fog",
            "Cloud": "Cloudy",
            "Clear": "Clear"
        }

        for keyword, group in weather_groups.items():
            data.loc[
                data["Weather_Condition"].str.contains(
                    keyword,
                    case=False,
                    na=False
                ),
                "Weather_Group"
            ] = group

    return data