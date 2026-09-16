import pandas as pd

df = pd.read_csv("final_samples.csv")

row_q = df.loc[df["q"].idxmax()]
row_f = df.loc[df["force_factor"].idxmax()]

print("MAX q")
print(row_q)

print("\nMAX force factor")
print(row_f)