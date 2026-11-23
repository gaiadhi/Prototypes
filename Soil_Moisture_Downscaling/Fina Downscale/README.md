# Soil Moisture Downscaling with NISAR Radar

Estimates soil moisture at 100 m and 50 m over a fallow field from NISAR GCOV radar (10 m pixels), anchored to NASA's SME2
soil moisture (200 m).

## Folder layout

| Folder / file | Contents |
|---|---|
| `Soil_Moisture_Downscaling_Presentation.pptx` | Final presentation, with speaker notes |
| `Subgroup 1 presentation.pptx` | Earlier group presentation (background on GCOV and SME2) |
| `Project_Summary.md` | Plain-English summary for the script and report |
| `Raw Data/` | GCOV radar files (6 dates, HH and HV) and the SME2 file |
| `Processed Data/` | Dataset, results and figures written by the notebooks |
| `Code/` | The two notebooks, run in order from this folder |

| Step | Notebook | Writes to `Processed Data/` |
|---|---|---|
| 1 | `Data_Preparation_GCOV_SME2.ipynb` | `Downscaling_Dataset.xlsx`, `Figure_Alignment_Check.png`, `Figure_Edge_Profile.png`, `Figure_Data_Prep_Validation.png` |
| 2 | `Final_Downscaling_Model.ipynb` | `Final_Soil_Moisture_Results.xlsx` and five figures: model test, maps, radar-to-moisture, β comparison, all dates at 50 m |

Tested with Python 3.13.1, pandas 3.0.2, numpy 2.4.4, pyproj 3.8.0, scikit-learn 1.8.0, matplotlib 3.10.8, openpyxl 3.1.5.

## 1. Data preparation

- Each radar file is converted from its own coordinate system (UTM 10N, UTM 11N or lat/lon) to lat/lon, then to
  EASE-Grid 2.0 metres (EPSG:6933). Every 10 m pixel goes into the cell its centre falls in (NASA's drop-in-bucket method).
- The SME2 file has only block IDs. The client's Config block centres go through the same projection and land within 0.4 m
  of NASA cell centres, which ties each SME2 block ID to its cell. Radar and SME2 are matched by UTC date.
- EASE-Grid 2.0 is equal-area: at 36.8°N a "200 m" cell is about 185 m × 217 m on the ground, still about 400 pixels.
- Radar is averaged in linear power, then converted to dB, for 200 m blocks and 100 m / 50 m pieces.
- Features: **HH_dB** (moisture signal), **HV_dB** (vegetation and roughness), **HV_HH_Ratio** (canopy vs bare soil).
- Alignment is checked on all six dates: pixel counts per block, the crop edge (a 10 dB drop at 36.8258° every date, 70%
  of the way down row 1), an overlay of radar, grid and Config centres, and image matching (best match at zero shift on every
  date, sub-pixel offset under 5 m). A whole-pixel error would change Clean fallow block HH by at most 0.14 dB.
- Blocks are labelled **Clean**, **Mixed** (contains almond) or **Edge** (under 80% radar cover). The labels use radar
  cover and the crop edge only, never SME2. Mixed blocks are about 6 dB brighter than Clean fallow while SME2 is only 0.02
  m³/m³ wetter, so they stay out of training.

| Records | Count | Use |
|---|---|---|
| All block-dates | 120 | |
| Clean (24 fallow + 24 almond) | 48 | Quality label, not a training set |
| **Clean fallow** (B0_0 to B0_3) | **24** | Trains and tests β; the only blocks mapped |
| Clean + Mixed + Edge fallow (rows 0 and 1) | 60 | Stress test only |

## 2. Model

Machine learning learns one number, **β** (soil moisture change per 1 dB of HH), and NASA's equation does the downscaling.

- **Absolute:** Ridge and Random Forest predict SME2 from HH_dB, HV_dB and HV_HH_Ratio.
- **Anomaly:** the same models predict block minus field on the same date, from the same features as block minus field.
- β is the slope of a straight line through a model's predictions against HH.
- Everything is tested on dates the model never saw: nested leave-one-date-out, with settings tuned on the training dates
  only. Scoring uses one target, the soil moisture pattern inside the field (block minus field). No downscaling scores R² 0.
- Anomalies use the same date's field average only, never other dates. Scrambling a held-out date's SME2 and radar leaves
  that fold's β unchanged, so no held-out information leaks into training.

| β from | β range (clean) | Own predictions R² (clean) | NASA eq., clean: RMSE · R² | NASA eq., + Mixed + Edge: RMSE · R² |
|---|---|---|---|---|
| No downscaling | - | 0.00 | 0.0166 · 0.00 | 0.0190 · 0.00 |
| **Absolute, Ridge** | **0.016 to 0.022** | 0.32 | **0.0122 · 0.45** | 0.0174 · 0.17 |
| Absolute, Random Forest | 0.013 to 0.022 | 0.01 | 0.0123 · 0.45 | 0.0183 · 0.08 |
| Anomaly, Ridge | 0.002 to 0.013 | 0.07 | 0.0159 · 0.08 | 0.0173 · 0.18 |
| Anomaly, Random Forest | 0.003 to 0.011 | 0.17 | 0.0144 · 0.24 | 0.0163 · 0.27 |

- RMSE is in m³/m³. Guessing SME2 from scratch gives an RMSE of 0.049 to 0.061, against 0.0166 for the field's own SME2.
- Per held-out date, the chosen β beats no downscaling only on Mar 1, the one date with a strong pattern.
- **Ridge vs Random Forest.** The two Absolute β tie (3 dates each). Random Forest on the HH difference alone reaches R²
  0.49 on its own and wins 5 of 6 dates at 200 m, mostly by predicting a weak pattern; on Mar 1 its error is eight times
  Ridge's. Ridge's β is used for the maps: it varies less across folds (14% vs 19%), a slope extends to the 14% of 50 m
  pieces outside the training range where a forest goes flat, and it has the same linear form as NASA's equation.
- Check by pass: β = 0.012 from the 2 morning dates and 0.019 from the 4 evening dates.

## 3. Maps

**piece SM = block SME2 + β × (piece HH_dB − block HH_dB)**, with β = 0.0171 (Absolute Ridge, all 24 Clean records), then
shifted so the pieces average back to SME2. This gives 96 pieces at 100 m and 384 at 50 m per date over blocks B0_0 to B0_3.
At 50 m, 6% of pieces differ from their block by more than 0.05 m³/m³. On the most varied date (Mar 1) the 50 m spread is
0.048 vs 0.040 in SME2; on the most uniform (Feb 4) it is 0.018 vs 0.003, mostly speckle.

## 4. Comparison with NASA's SME2 algorithm

NASA's multiscale fusion (ATBD JPL D-107679, eq. 4.3.7): SM(F) = SM(C) + β(C) · { [σHH(F) − σHH(C)] + Γ · [σHV(C) − σHV(F)] }

| Step | NASA | Ours |
|---|---|---|
| Scale | 9 km to 200 m | 200 m to 100 m and 50 m |
| Learning β | Time series of each 9 km cell (eq. 4.3.2) | Absolute model trained across dates (same idea); the same-day β was less stable |
| HV | Γ term in the equation | Used as model inputs when learning β, not in the equation |
| Averaging | Outlier filter, then linear drop-in-bucket | Linear drop-in-bucket; the filter is a next step |
| Passes | Kept separate | Mixed across 6 dates; per-pass β needs more dates |

## 5. What is and is not shown

- **Shown:** on unseen dates, NASA's equation with the learned β explains 45% of the pattern inside the clean fallow field
  and cuts the error by 26% over all six dates, almost all of it on Mar 1. The maps always agree with SME2 at 200 m.
- **Not shown:** that the 100 m and 50 m values match measured soil moisture. There is no ground truth at those scales, and
  SME2 is made from the same radar. Six dates is a small sample, β differs between passes, and 50 m pieces carry the most
  speckle.

## Next steps

1. More radar dates (SME2 has 73) so β can be learned per pass.
2. NASA's outlier filter (ATBD section 5.3) before averaging pixels.
3. Soil probe readings at a few 50 m pieces, plus rainfall and flow-meter data, for an independent check.
