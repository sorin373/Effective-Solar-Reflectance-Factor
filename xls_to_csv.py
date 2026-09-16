import pandas as pd

input_file = "data/e490_00a_amo.xls"
output_file = "data/E490_AM0.csv"

df = pd.read_excel(
    input_file,
    sheet_name="NewAM0",
    header=None
)

# Primele doua coloane contin ASTM E490
e490 = df.iloc[1:, [0, 1]].copy()

e490.columns = [
    "wavelength_um",
    "irradiance_W_m2_um"
]

# convert to numeric
e490["wavelength_um"] = pd.to_numeric(
    e490["wavelength_um"],
    errors="coerce"
)

e490["irradiance_W_m2_um"] = pd.to_numeric(
    e490["irradiance_W_m2_um"],
    errors="coerce"
)

# remove invalid rows
e490 = e490.dropna()

# convert units
e490["wavelength_nm"] = (
    e490["wavelength_um"] * 1000.0
)

e490["irradiance_W_m2_nm"] = (
    e490["irradiance_W_m2_um"] / 1000.0
)

# Keep interval supported by current CMG approximation
e490 = e490[
    (e490["wavelength_nm"] >= 250.0)
    & (e490["wavelength_nm"] <= 2500.0)
]

# final two-column CSV
out = e490[
    [
        "wavelength_nm",
        "irradiance_W_m2_nm"
    ]
]

out.to_csv(
    output_file,
    index=False
)

print(out.head())
print(out.tail())
print()
print("Points:", len(out))
print(
    "Range:",
    out["wavelength_nm"].iloc[0],
    "->",
    out["wavelength_nm"].iloc[-1],
    "nm"
)