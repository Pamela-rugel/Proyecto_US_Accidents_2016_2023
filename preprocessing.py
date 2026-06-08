import pandas as pd

def preprocess_data(data):
    print("PREPROCESSING EJECUTADO")
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

    # En el dataset US Accidents la severidad válida es 1-4
    data = data[
        data["Severity"].between(1, 4)
    ]

    # Eliminamos registros sin estado
    if "State" in data.columns:
        data = data.dropna(
            subset=["State"]
        )


    # Año-Mes para análisis de evolución temporal
    data["YearMonth"] = (
        data["Start_Time"]
        .dt.strftime("%Y-%m")
    )

    # FRANJA HORARIA

    def obtener_franja_horaria(hora):

        if hora < 6:
            return "Madrugada"

        elif hora < 12:
            return "Mañana"

        elif hora < 18:
            return "Tarde"

        return "Noche"

    data["Time_Period"] = (
        data["Hour"]
        .apply(obtener_franja_horaria)
    )

    # ORDEN DE LOS DÍAS DE LA SEMANA
    weekday_order = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 7
    }

    data["Weekday_Order"] = (
        data["Weekday"]
        .map(weekday_order)
    )


    # COORDENADAS DISCRETIZADAS

    data["Lat_Grid"] = (
        data["Start_Lat"]
        .round(1)
    )

    data["Lng_Grid"] = (
        data["Start_Lng"]
        .round(1)
    )

    # DURACIÓN DEL ACCIDENTE
    if "End_Time" in data.columns:
        data["End_Time"] = pd.to_datetime(
            data["End_Time"],
            format="mixed",
            errors="coerce"
        )

        data["Duration_Minutes"] = (
            (
                data["End_Time"]
                - data["Start_Time"]
            )
            .dt.total_seconds()
            / 60
        )

        # Eliminamos duraciones negativas
        data.loc[
            data["Duration_Minutes"] < 0,
            "Duration_Minutes"
        ] = None


    return data