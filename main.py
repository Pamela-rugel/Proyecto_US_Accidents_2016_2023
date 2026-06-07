import pandas as pd

df = pd.read_csv("processed/US_Accidents_Processed.csv")

print(df.columns.tolist())
print(df.head(3))
print(df.dtypes)