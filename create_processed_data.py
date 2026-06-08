import os
import pandas as pd

from preprocessing import preprocess_data

RAW_FILE = "data/US_Accidents.csv"
PROCESSED_FOLDER = "processed"
PROCESSED_FILE = ( f"{PROCESSED_FOLDER}/US_Accidents_Processed.parquet")


def main():
    print("Leyendo dataset original...")

    data = pd.read_csv( RAW_FILE, low_memory=False)
    print( f"Registros originales: {len(data):,}")
    print("Aplicando preprocessing...")
    data = preprocess_data(data)

    print( f"Registros procesados: {len(data):,}")

    os.makedirs( PROCESSED_FOLDER, exist_ok=True)

    print("Guardando archivo procesado...")

    data.to_parquet( PROCESSED_FILE, index=False )

    print( f"Archivo generado: {PROCESSED_FILE}")
    
    data.to_csv( PROCESSED_FILE.replace(".parquet", ".csv"), index=False)


if __name__ == "__main__":
    main()