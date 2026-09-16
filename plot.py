import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Paths
# ============================================================

CSV_FILE = Path("results/final_samples.csv")
OUTPUT_DIR = Path("results/plots")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Load data
# ============================================================

df = pd.read_csv(CSV_FILE)

q = df["q"].to_numpy()
kx = df["kx"].to_numpy()
ky = df["ky"].to_numpy()
kz = df["kz"].to_numpy()

A_proj = df["A_proj"].to_numpy()
force_factor = df["force_factor"].to_numpy()


# ============================================================
# Statistics
# ============================================================

mean_q = np.mean(q)
std_q = np.std(q, ddof=1)

p05 = np.percentile(q, 5)
median = np.percentile(q, 50)
p95 = np.percentile(q, 95)

idx_q_max = np.argmax(q)
idx_force_max = np.argmax(force_factor)

print("===== STATISTICS =====")
print(f"N       = {len(q)}")
print(f"Mean    = {mean_q:.6f}")
print(f"Std dev = {std_q:.6f}")
print(f"P05     = {p05:.6f}")
print(f"Median  = {median:.6f}")
print(f"P95     = {p95:.6f}")

print("\n===== MAX q =====")
print(df.iloc[idx_q_max])

print("\n===== MAX FORCE FACTOR =====")
print(df.iloc[idx_force_max])


# ============================================================
# 1. Histogram of effective reflectance
# ============================================================

plt.figure(figsize=(9, 6))

plt.hist(
    q,
    bins=80,
    density=True,
    alpha=0.8
)

plt.axvline(
    mean_q,
    linestyle="--",
    linewidth=2,
    label=f"Mean = {mean_q:.3f}"
)

plt.axvline(
    median,
    linestyle="-.",
    linewidth=2,
    label=f"Median = {median:.3f}"
)

plt.axvline(
    p05,
    linestyle=":",
    linewidth=2,
    label=f"P05 = {p05:.3f}"
)

plt.axvline(
    p95,
    linestyle=":",
    linewidth=2,
    label=f"P95 = {p95:.3f}"
)

plt.xlabel("Effective reflectance factor, q")
plt.ylabel("Probability density")
plt.title("Distribution of Effective Spacecraft Reflectance")

plt.grid(alpha=0.25)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "01_reflectance_histogram.png",
    dpi=300
)

plt.close()


# ============================================================
# 2. Empirical CDF
# ============================================================

q_sorted = np.sort(q)

cdf = (
    np.arange(1, len(q_sorted) + 1)
    / len(q_sorted)
)

plt.figure(figsize=(9, 6))

plt.plot(
    q_sorted,
    cdf,
    linewidth=2
)

plt.axhline(
    0.95,
    linestyle="--",
    linewidth=1.5
)

plt.axvline(
    p95,
    linestyle="--",
    linewidth=1.5,
    label=f"P95 = {p95:.3f}"
)

plt.axvline(
    mean_q,
    linestyle=":",
    linewidth=1.5,
    label=f"Mean = {mean_q:.3f}"
)

plt.xlabel("Effective reflectance factor, q")
plt.ylabel("Cumulative probability")
plt.title("CDF of Effective Spacecraft Reflectance")

plt.xlim(0.0, 1.0)
plt.ylim(0.0, 1.0)

plt.grid(alpha=0.25)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "02_reflectance_cdf.png",
    dpi=300
)

plt.close()


# ============================================================
# Convert k vector to spherical map coordinates
#
# longitude = atan2(ky, kx)
# latitude  = asin(kz)
#
# Both are in radians, exactly what Mollweide expects.
# ============================================================

longitude = np.arctan2(ky, kx)

# numerical safety
latitude = np.arcsin(
    np.clip(kz, -1.0, 1.0)
)


# ============================================================
# 3. Mollweide map of q
# ============================================================

fig = plt.figure(figsize=(12, 7))

ax = fig.add_subplot(
    111,
    projection="mollweide"
)

scatter = ax.scatter(
    longitude,
    latitude,
    c=q,
    s=3,
    alpha=0.7,
    rasterized=True
)

cbar = fig.colorbar(
    scatter,
    ax=ax,
    orientation="horizontal",
    pad=0.08,
    shrink=0.8
)

cbar.set_label("Effective reflectance factor, q")

ax.grid(True, alpha=0.3)

ax.set_title(
    "Directional Distribution of Effective Reflectance"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "03_reflectance_mollweide.png",
    dpi=300
)

plt.close()


# ============================================================
# 4. Mollweide map of A_proj * (1 + q)
# ============================================================

fig = plt.figure(figsize=(12, 7))

ax = fig.add_subplot(
    111,
    projection="mollweide"
)

scatter = ax.scatter(
    longitude,
    latitude,
    c=force_factor,
    s=3,
    alpha=0.7,
    rasterized=True
)

cbar = fig.colorbar(
    scatter,
    ax=ax,
    orientation="horizontal",
    pad=0.08,
    shrink=0.8
)

cbar.set_label(
    r"$A_{\mathrm{proj}}(1+q)$ [mm$^2$]"
)

ax.grid(True, alpha=0.3)

ax.set_title(
    "Directional Radiation-Pressure Force Factor"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "04_force_factor_mollweide.png",
    dpi=300
)

plt.close()


# ============================================================
# 5. Projected area vs reflectance
# ============================================================

plt.figure(figsize=(9, 6))

scatter = plt.scatter(
    A_proj,
    q,
    c=force_factor,
    s=5,
    alpha=0.5,
    rasterized=True
)

cbar = plt.colorbar(scatter)

cbar.set_label(
    r"$A_{\mathrm{proj}}(1+q)$ [mm$^2$]"
)

plt.xlabel(
    r"Projected area, $A_{\mathrm{proj}}$ [mm$^2$]"
)

plt.ylabel(
    "Effective reflectance factor, q"
)

plt.title(
    "Projected Area vs Effective Reflectance"
)

plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "05_area_vs_reflectance.png",
    dpi=300
)

plt.close()


# ============================================================
# 6. Optional: q as function of kx, ky, kz
# ============================================================

components = [
    ("kx", kx),
    ("ky", ky),
    ("kz", kz)
]

for name, component in components:

    plt.figure(figsize=(9, 6))

    plt.scatter(
        component,
        q,
        s=3,
        alpha=0.4,
        rasterized=True
    )

    plt.xlabel(name)
    plt.ylabel("Effective reflectance factor, q")

    plt.title(
        f"Effective Reflectance vs {name}"
    )

    plt.grid(alpha=0.25)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / f"06_reflectance_vs_{name}.png",
        dpi=300
    )

    plt.close()


print(
    f"\nPlots saved to: {OUTPUT_DIR.resolve()}"
)