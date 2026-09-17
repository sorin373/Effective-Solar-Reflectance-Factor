import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = Path("results/final_samples.csv")
OUTPUT_DIR = Path("results/plots")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_FILE)

q = df["q"].to_numpy()
kx = df["kx"].to_numpy()
ky = df["ky"].to_numpy()
kz = df["kz"].to_numpy()

A_proj = df["A_proj"].to_numpy()
force_factor = df["force_factor"].to_numpy()

mean_q = np.mean(q)
std_q = np.std(q, ddof=1)

p05 = np.percentile(q, 5)
median = np.percentile(q, 50)
p95 = np.percentile(q, 95)

idx_q_max = np.argmax(q)
idx_force_max = np.argmax(force_factor)

# ============================================================
# 1. Histogram of effective reflectance
# ============================================================

plt.figure(figsize=(9, 6))
plt.hist(q, bins=80, alpha=0.8)
plt.axvline(mean_q, color="red", linestyle="--", linewidth=2, label=f"Mean = {mean_q:.3f}")
plt.axvline(median, color="green", linestyle="-.", linewidth=2, label=f"Median = {median:.3f}")
plt.axvline(p05, color="orange", linestyle=":", linewidth=2, label=f"P05 = {p05:.3f}")
plt.axvline(p95, color="purple", linestyle=":", linewidth=2, label=f"P95 = {p95:.3f}")
plt.xlabel("Effective reflectance factor, q")
plt.ylabel("Frequency")
plt.title("Distribution of Effective Spacecraft Reflectance")
plt.grid(alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_reflectance_histogram.png", dpi=300)
plt.close()

# ============================================================
# 2. Empirical CDF
# ============================================================

q_sorted = np.sort(q)
cdf = (np.arange(1, len(q_sorted) + 1) / len(q_sorted))
plt.figure(figsize=(9, 6))
plt.plot(q_sorted, cdf, linewidth=2)
plt.axhline(0.95, linestyle="--", linewidth=1.5)
plt.axvline(p95, linestyle="--", linewidth=1.5, label=f"P95 = {p95:.3f}")
plt.axvline(mean_q, linestyle=":", linewidth=1.5, label=f"Mean = {mean_q:.3f}")
plt.xlabel("Effective reflectance factor, q")
plt.ylabel("Cumulative probability")
plt.title("CDF of Effective Spacecraft Reflectance")
plt.xlim(0.0, 1.0)
plt.ylim(0.0, 1.0)
plt.grid(alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_reflectance_cdf.png", dpi=300)
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
latitude = np.arcsin( np.clip(kz, -1.0, 1.0))

# ============================================================
# 3. Mollweide map of q
# ============================================================

fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(111, projection="mollweide")
scatter = ax.scatter(longitude, latitude, c=q, s=3, alpha=0.7, rasterized=True)
cbar = fig.colorbar(scatter, ax=ax, orientation="horizontal", pad=0.08, shrink=0.8)
cbar.set_label("Effective reflectance factor, q")
ticks_deg = np.arange(-90, 91, 15)
ticks_rad = np.deg2rad(ticks_deg)
ax.set_yticks(ticks_rad)
ax.set_yticklabels([f"{d}°" for d in ticks_deg])

# principal illumination directions
principal_dirs = {
    "+X face": np.array([-1.0,  0.0,  0.0]),
    "-X face": np.array([ 1.0,  0.0,  0.0]),
    "+Y face": np.array([ 0.0, -1.0,  0.0]),
    "-Y face": np.array([ 0.0,  1.0,  0.0]),
    "+Z face": np.array([ 0.0,  0.0, -1.0]),
    "-Z face": np.array([ 0.0,  0.0,  1.0]),
}

for label, k in principal_dirs.items():
    lon = np.arctan2(k[1], k[0])
    lat = np.arcsin(k[2])

    ax.scatter(lon, lat, s=80, c="red", edgecolors="black", zorder=5)
    ax.text(lon, lat, " " + label, fontsize=9, ha="left", va="bottom", bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=1.5))

ax.grid(True, alpha=0.3)
ax.set_title("Directional Distribution of Effective Reflectance", pad=30  )
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_reflectance_mollweide.png", dpi=300)
plt.close()

# ============================================================
# 4. Mollweide map of A_proj * (1 + q)
# ============================================================

fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(111, projection="mollweide")
scatter = ax.scatter(longitude, latitude, c=force_factor, s=3, alpha=0.7, rasterized=True)
cbar = fig.colorbar(scatter, ax=ax, orientation="horizontal", pad=0.08, shrink=0.8)
cbar.set_label(r"$A_{\mathrm{proj}}(1+q)$ [mm$^2$]")
ax.grid(True, alpha=0.3)
ax.set_title("Directional Radiation-Pressure Force Factor")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_force_factor_mollweide.png", dpi=300)
plt.close()

# ============================================================
# 5. Projected area vs reflectance
# ============================================================

plt.figure(figsize=(9, 6))

scatter = plt.scatter(A_proj, q, c=force_factor, s=5, alpha=0.5, rasterized=True)
cbar = plt.colorbar(scatter)
cbar.set_label(r"$A_{\mathrm{proj}}(1+q)$ [mm$^2$]")
plt.xlabel(r"Projected area, $A_{\mathrm{proj}}$ [mm$^2$]")
plt.ylabel("Effective reflectance factor, q")
plt.title("Projected Area vs Effective Reflectance")
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_area_vs_reflectance.png", dpi=300)
plt.close()

print(f"\nPlots saved to: {OUTPUT_DIR.resolve()}")