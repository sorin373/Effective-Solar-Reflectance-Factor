# Effective Solar Reflectance Factor — ROSPIN-SAT-1

Numerical model for determining the effective solar reflectance factor
of ROSPIN-SAT-1 for solar-radiation-pressure analysis.

## Method

The model evaluates:

1. wavelength-dependent Fresnel reflectance;
2. AM0 solar spectral weighting;
3. projected-area weighting of illuminated spacecraft surfaces;
4. Monte Carlo sampling of solar propagation directions.

The resulting effective reflectance is

\[
q_{\mathrm{eff}}(\hat{k})
=
\frac{
\sum_j q_{\odot,j}(\alpha_j) A_j \cos\alpha_j
}{
\sum_j A_j \cos\alpha_j
}.
\]

## Final result

For 100,000 uniformly sampled solar propagation directions:

- Mean reflectance: `0.667812`
- Standard deviation: `0.175791`
- Median: `0.723773`
- P95: `0.904695`

Nominal value used for SRP analysis:

\[
q_{\mathrm{nominal}} \approx 0.67
\]

which corresponds to

\[
C_R = 1 + q \approx 1.67.
\]

## Input data

- Aluminium optical constants: Rakić dataset
- Solar spectrum: ASTM E490 AM0
- CMG-100 coverglass: simplified model with `n = 1.516`, `k = 0`
- Spacecraft external surface geometry derived from ROSPIN-SAT-1 geometry

## Build

Requires a C++17 compiler.

```bash
g++ -std=c++17 -O3 src/main.cpp include/solver.cpp -o main