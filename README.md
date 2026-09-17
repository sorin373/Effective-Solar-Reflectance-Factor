# Effective Solar Reflectance Factor — ROSPIN-SAT-1

**Author:** Sorin Tudose  
**Project:** ROSPIN-SAT-1

## Overview

This repository contains the numerical implementation used to determine the effective solar reflectance factor of the ROSPIN-SAT-1 spacecraft for solar-radiation-pressure analysis.

The model includes:

- Fresnel reflection
- wavelength-dependent optical properties
- ASTM E490 AM0 solar spectral weighting
- projected-area weighting of spacecraft surfaces
- Monte Carlo sampling of solar propagation directions

## Build

Requires a C++17-compatible compiler.

Using `g++` from the project root:

```bash
g++ -std=c++17 -O3 src/main.cpp include/solver.cpp -o main
```

## Input Data

The current model uses:

- Rakić optical data for aluminium
- ASTM E490 AM0 solar spectrum
- simplified CMG-100 coverglass optical model
- ROSPIN-SAT-1 external surface geometry

## Monte Carlo Analysis

Solar propagation directions are sampled uniformly over the unit sphere.

A fixed random seed is used for reproducibility:

```text
12345
```

## Main Results

Final Monte Carlo sample count:

```text
M = 100000
```

| Quantity | Value |
|---|---:|
| Mean reflectance | 0.667812 |
| Standard deviation | 0.175791 |
| 5th percentile | 0.348638 |
| Median | 0.723773 |
| 95th percentile | 0.904695 |

Nominal effective reflectance factor:

```text
q_nominal = 0.67
```

For the simplified solar-radiation-pressure formulation used in this project:

```text
CR = 1 + q = 1.67
```

## Principal Illumination Directions

| Illuminated Face | q_eff |
|---|---:|
| +X | 0.280207 |
| -X | 0.685767 |
| +Y | 0.924324 |
| -Y | 0.924324 |
| +Z | 0.924324 |
| -Z | 0.924324 |

## Output

Monte Carlo samples are written to:

```text
results/final_samples.csv
```

The output includes:

- sample number
- solar propagation vector components `kx`, `ky`, `kz`
- effective reflectance factor `q`
- projected illuminated area
- SRP loading factor `A_proj * (1 + q)`

## Technical Report

The full derivation, numerical methodology, spacecraft surface model, verification procedure, results, and limitations are documented in:

**Determination of the Effective Solar Reflectance Factor**  
ROSPIN-SAT-1 Technical Analysis Report

## Limitations

The present implementation uses several simplifying assumptions:

- all aluminium alloys use the same bulk aluminium optical dataset
- CMG-100 is represented using a simplified optical model
- spacecraft surfaces are modeled as planar elements
- self-shadowing is not included
- Monte Carlo directions are uniformly distributed over the sphere rather than derived from a mission-specific attitude profile
