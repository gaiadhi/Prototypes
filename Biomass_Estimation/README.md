# High-Resolution Biomass Estimation Using Low-Resolution Satellite Data

A machine learning baseline for estimating cotton above-ground biomass from simulated satellite reflectance, developed for Gaiadhi as a Fall 2026 senior capstone project at The University of Texas at Arlington.

> **Important:** Every result in this project comes from **simulated data**. Biomass comes from the DSSAT crop model and reflectance comes from the PROSAIL model. The project does not use real satellite imagery or field-measured biomass, so the results show agreement with simulated biomass, not real-world accuracy.

**Contents:** [Overview](#1-project-overview) · [Team](#2-project-team) · [Repository Structure](#3-repository-structure) · [Dataset](#4-dataset-description) · [Requirements](#5-technical-requirements) · [How to Run the Code](#6-how-to-run-the-code) · [Final Model](#7-final-model) · [Performance](#8-model-performance) · [Key Findings](#9-key-findings) · [Limitations and Recommendations](#10-limitations-and-future-recommendations)

---

## 1. Project Overview

Measuring cotton biomass usually means cutting, drying and weighing plants. That is slow, destructive and impractical to repeat across a whole farm during the season. Satellites observe fields repeatedly at low cost, so Gaiadhi asked whether machine learning could estimate biomass from satellite-like reflectance. Freely available imagery such as NASA HLS has 30 m pixels (900 m², about 0.22 acre), and each pixel mixes many plants with soil and shadow.

No field dataset paired reflectance with measured biomass, so the project used simulated data:

- **DSSAT** simulated daily rainfed cotton growth for eight management treatments from 2019 to 2023.
- **PROSAIL** generated the matching canopy reflectance.

**Objectives**

1. Build a model that estimates cotton biomass (kg/ha) from simulated reflectance.
2. Evaluate how reliably it performs across growing seasons.
3. Identify the treatments, growth stages and conditions in which it succeeds or fails.

**Out of scope:** real satellite imagery, field validation, image super-resolution, NASA's Prithvi model, UAV data and production deployment.

## 2. Project Team

| Role | Name |
|---|---|
| University | The University of Texas at Arlington, College of Business |
| Course | BANA 4326: Capstone for AI in Business, Fall 2026 |
| Industry partner | Gaiadhi |
| Project team | Aakrity Karki, Luisa Lopera, Vanesa Patino, Sangam Thapa |
| Industry mentors | Aishvarya Gopalsamy, Karthik Kannappan |
| Faculty advisor | Dr. Jayarajan Samuel |

## 3. Repository Structure

```
Biomass_Estimation/
├── Codes/
│   ├── Biomass_Model_Demo.ipynb                  # Start here: reproduces the final model
│   └── Biomass_Full_Experimental_Analysis.ipynb  # Complete record of all experiments
├── Version 1 dataset and glossary/               # Archived dataset (not used by either notebook)
├── Version 2 dataset and glossary/               # Active dataset used by both notebooks
├── Diagrams/
│   ├── Data Flow Diagram
│   └── System Architecture Diagram
├── Agricultural_Treatment_Descriptions.docx      # Definitions of the eight treatments
├── Final project report (.docx)                  # Final written report
├── Final capstone presentation (.pptx)           # Final sponsor presentation (November 19, 2026)
└── README.md
```

| Item | Purpose |
|---|---|
| `Codes/Biomass_Model_Demo.ipynb` | Short, self-contained notebook that trains and evaluates the final model. |
| `Codes/Biomass_Full_Experimental_Analysis.ipynb` | Full experimental notebook: baselines, alternative models, feature tests and all diagnostics. |
| `Version 2 dataset and glossary/` | **Active dataset.** `biomass_dataset_v2.csv` and its glossary. Used by both notebooks and all final results. |
| `Version 1 dataset and glossary/` | **Archived dataset.** `dssat_prosail_merged.csv` and its glossary, kept for reference only. Neither notebook uses it. |
| `Diagrams/` | Data flow diagram and system architecture diagram from the final presentation. |
| `Agricultural_Treatment_Descriptions.docx` | Fertilizer, tillage and nitrogen details for Treatments 1–8, as provided by Gaiadhi. |
| Final project report (.docx) | Full methodology, results, findings and limitations. |
| Final capstone presentation (.pptx) | Slides from the November 19, 2026 sponsor presentation. |

## 4. Dataset Description

### How the data were generated

1. DSSAT simulated daily cotton growth, producing biomass, leaf area index (LAI), growth stage, soil water and weather.
2. DSSAT's daily LAI was passed into PROSAIL, which generated canopy reflectance. The other PROSAIL inputs were sampled from realistic ranges or held fixed.
3. Each reflectance record was paired with DSSAT biomass for the same simulated day.

Each row is one simulated treatment-day. The data are tabular. They are not satellite images or geolocated pixels.

### Version 2 (active) and Version 1 (archived)

| | Version 2 (active) | Version 1 (archived) |
|---|---|---|
| File | `biomass_dataset_v2.csv` | `dssat_prosail_merged.csv` |
| Size | 5,265 rows × 37 columns, 2019–2023 | 5,265 rows, 2019–2023 |
| Target column | `dssat_biomass_kg_ha` (simulated, kg/ha) | `real_biomass_cwad` (simulated, despite the name) |
| Leaf parameters | More realistic patterns | Some varied randomly |
| Growth stage | Included | Not available |
| Use | **Both notebooks, final model and all reported results** | Early project baselines only; archived, not used by either notebook |

**Version 2 details**

- **Treatments:** eight (`treatment` 1–8). The table below summarizes them; the full table is in `Agricultural_Treatment_Descriptions.docx`.
- **Growth stages:** Vegetative, R1, R3, R5, R7 and R8 (`dssat_stage_code`, `dssat_stage_name`). They are used for analysis only, not as model inputs.
- **Data quality:** no duplicate rows and no missing values in the model inputs or target.
- **Missing weather:** 1,360 rows (25.8%) have no weather data, all at R7 or R8.
- **Column definitions:** see the glossary in the dataset folder.

| Treatments | Fertilizer | Tillage |
|---|---|---|
| 1 and 5 | 100% UAN | 1 conventional, 5 minimum |
| 2 and 6 | 50% UAN | 2 conventional, 6 minimum |
| 3 and 7 | M-CC | 3 conventional, 7 minimum |
| 4 and 8 | M-NCC | 4 conventional, 8 minimum |

The meanings of M-CC and M-NCC and the units of residual manure nitrogen were not confirmed.

## 5. Technical Requirements

- **Language:** Python
- **Environment:** Google Colab (runs in a web browser; no local installation required)
| Library | Demonstration notebook | Full experimental notebook |
|---|---|---|
| pandas | Yes | Yes |
| NumPy | Yes | Yes |
| scikit-learn | Yes | Yes |
| Matplotlib | Yes | Yes |
| Seaborn | No | Yes |
| SciPy | No | Yes |

All six libraries come preinstalled in Google Colab, so nothing needs to be installed. Library versions were not recorded.

## 6. How to Run the Code

**New users should run `Biomass_Model_Demo.ipynb` first.** It is short and reproduces only the final model. Both notebooks use only the Version 2 dataset, `biomass_dataset_v2.csv`. Use the full experimental notebook only when you need the details of a specific experiment.

| | Demonstration notebook | Full experimental notebook |
|---|---|---|
| Purpose | Reproduce the final model | Complete record of every experiment |
| Length | Eight short sections | More than 100 pages of code and output |
| Dataset | `biomass_dataset_v2.csv` | `biomass_dataset_v2.csv` |
| Best for | Understanding and verifying the final result | Reviewing alternatives, diagnostics and charts |

### Step 1: Open the notebook in Google Colab

1. Go to [colab.research.google.com](https://colab.research.google.com) and sign in with a Google account.
2. Choose **File → Upload notebook** and select `Codes/Biomass_Model_Demo.ipynb`.
   - If the repository is connected to Colab, you can use **File → Open notebook → GitHub** instead.

### Step 2: Upload the dataset

1. In Colab, open the **Files** panel (folder icon on the left).
2. Upload `biomass_dataset_v2.csv` from the `Version 2 dataset and glossary/` folder.
3. Confirm the file appears directly under `/content/`.

Uploaded files are deleted when the Colab session ends, so upload the file again each time you start a new session.

### Step 3: Check the dataset path

The full experimental notebook loads the data with:

```python
df = pd.read_csv('/content/biomass_dataset_v2.csv')
```

This path works without changes when the file is uploaded as in Step 2. In the demonstration notebook, find the line containing `pd.read_csv` and make sure it points to `/content/biomass_dataset_v2.csv`. If you stored the file somewhere else, change the path in that line to match.

### Step 4: Run the cells in order

Choose **Runtime → Run all**, or run each cell from top to bottom with **Shift + Enter**. Do not skip cells, because later cells use variables created by earlier ones.

### Step 5: Check that you reproduced the final model

The demonstration notebook should produce these outputs:

| Section | What it does | Expected output |
|---|---|---|
| 1 | Imports libraries and loads the dataset | 5,265 rows, 37 columns, 5 seasons, 8 treatments |
| 2 | Selects features and target | 13 features (12 Sentinel-2 bands + DAP); target `dssat_biomass_kg_ha` |
| 3 | Splits by year | 4,209 training rows (2019–2022); 1,056 test rows (2023) |
| 4 | Trains Linear Regression | One model for all eight treatments |
| 5 | Predicts and clips | 153 negative predictions set to zero |
| 6 | Evaluates | RMSE 694.235 kg/ha, R² 0.877, mean residual +332.972 kg/ha |
| 7 | Plots actual vs predicted | Scatter plot with a 1:1 reference line |
| 8 | Breaks down errors by treatment | Treatment 5 has the highest RMSE; Treatment 7 is the only treatment with negative mean residual |

Your results should match these values to the precision shown. Very small differences in later decimal places can occur between software versions. If the results differ beyond that, check that you are using Version 2, that the split is by year (not random), and that negative predictions are clipped before the metrics are calculated.

### Step 6: Access the analytical outputs

- Metrics and tables are printed below the cells that create them.
- Charts are displayed in the notebook. To save one, right-click it and save the image, or download any saved PNG from the **Files** panel.
- The full experimental notebook produced the report charts, including `Biomass_distribution_by_year.png`, `Chart_RMSE_by_stage.png`, `Chart_T5R8_T7R5_by_year.png`, `Chart_Treatment_Bias_2023.png` and `Task1_biomass_by_stage_clean.png`. Files saved in Colab are deleted when the session ends, so download anything you want to keep.

### Running the full experimental notebook

Follow the same steps with `Biomass_Full_Experimental_Analysis.ipynb`. Run it from top to bottom, because many experiments build on earlier cells. Because the notebook is long, running everything takes much longer than the demonstration notebook.

## 7. Final Model

| Element | Specification |
|---|---|
| Algorithm | Ordinary least squares Linear Regression (scikit-learn) |
| Inputs (13) | 12 simulated Sentinel-2 bands (B1–B9, B8A, B11, B12) + days after planting (`dap`) |
| Target | `dssat_biomass_kg_ha` |
| Training data | 2019–2022 (4,209 rows) |
| Test data | 2023 (1,056 rows) |
| Post-processing | Negative predictions set to zero |

**Year-based validation.** Rows from the same season share weather and crop development. A random split would let the model recognize seasons it had already seen, so whole seasons are held out instead.

**Why DAP is included.** On the 2023 test season, the 12 Sentinel-2 bands alone reached RMSE 1,034.446 kg/ha and R² 0.728. Adding DAP improved this to RMSE 694.235 kg/ha and R² 0.877.

**Why this model was retained.** More than a dozen alternatives were tested on matched observations, including:

- Random Forest, gradient boosting, Ridge Regression, positive-output models and an exploratory neural network
- reduced band sets and vegetation indices
- growth stage, soil water, tillage, fertilizer and weather features
- separate treatment models

Some of them improved a particular season or treatment, but none improved results consistently across seasons. The simple, reproducible baseline was kept.

## 8. Model Performance

| Held-out season | Setup | n | RMSE (kg/ha) | R² | Mean residual (kg/ha) | Within ±10%* |
|---|---|---|---|---|---|---|
| 2023 | Final model (trained 2019–2022) | 1,056 | 694.235 | 0.877 | +332.972 | 28.65% |
| 2019 | Leave-one-year-out | 1,048 | 937.498 | 0.859 | −263.360 | 24.80% |
| 2020 | Leave-one-year-out | 1,049 | 591.438 | 0.924 | −7.596 | 42.93% |
| 2021 | Leave-one-year-out | 1,048 | 1,019.122 | 0.857 | −464.999 | 14.34% |
| Pooled four years | Leave-one-year-out | 4,201 | 828.762 | 0.877 | −99.898 | 27.75% |
| 2022 (drought year) | Trained 2019–2021 | 1,064 | 1,099.498 | 0.022 | +643.59 | n/a |

\* Share of observations with actual biomass above 500 kg/ha whose prediction is within 10% of the actual value. In 2023 this covers 768 of 1,056 observations.

- In the leave-one-year-out evaluation, each held-out year is predicted by a model trained on all other years, always including 2022.
- Mean residual = predicted − actual, so a positive value means overprediction.
- **R² is not prediction accuracy.** An R² of 0.877 means the model explains most of the seasonal variation in biomass. It does **not** mean 87.7% of predictions are accurate. Only 28.65% of eligible 2023 predictions fall within ±10%.
- 2022 and 2023 were evaluated repeatedly during development, so they are not untouched test sets.

## 9. Key Findings

- **The 2022 drought season.** 2022 had far lower simulated biomass (mean 1,713.5 kg/ha). The model overpredicted it badly, and 89.4% of the squared error came from stage R8. Removing 2022 from training made 2023 worse (RMSE 818.875 kg/ha), so it stays in training.
- **Treatments 5 and 7.** In 2023, Treatment 5 at R8 and Treatment 7 at R5 made up 6.5% of observations but produced about 24.9% of the squared error.
  - Treatment 5 at R8 was underpredicted in 2019–2021 and overpredicted in 2023.
  - Treatment 7 at R5 was underpredicted in all four evaluated seasons.
  - Minimum tillage had higher error in 12 of 16 matched comparisons. This is an association only.
- **Growth stages.** R5, R7 and R8 produce about 88% of the squared error. R1 and R3 were overpredicted in each of the four evaluated years (2019, 2020, 2021 and 2023).
- **LAI exclusion.** DSSAT LAI was used to generate the PROSAIL reflectance, so it is built into the simulated data. Following sponsor guidance, LAI was used only for analysis, not as a model input.
- **Spectral redundancy.** The Sentinel-2 bands are highly collinear (condition number 227,322.2). The model's coefficients should not be read as physical band effects.
- **Weather features rejected.** Apparent gains from minimum temperature depended mostly on missing late-season values that had been filled by carrying earlier values forward. A simple missing-weather flag reproduced most of the gain, and the candidates were worse than the baseline on an additional 2022 check.

## 10. Limitations and Future Recommendations

**Limitations**

- Results measure agreement with simulated DSSAT biomass, not real-world accuracy.
- The data cover only five seasons (about 40 treatment-season units).
- Performance and bias change between seasons, and the drought year is poorly predicted.
- The 2022 and 2023 seasons were examined repeatedly during development.
- The sponsor's accuracy target, the growth-stage label definitions and the M-CC/M-NCC treatment codes were not confirmed.

**Recommendations for Gaiadhi**

1. Define the accuracy metric, threshold and growth stages that matter.
2. Collect field-measured biomass throughout the season and apply the pipeline to real HLS or Sentinel-2 imagery aligned with crop dates.
3. Evaluate a model focused on early growth stages, where current predictions are consistently too high.
4. Test a stage-aware or constrained model that avoids negative predictions.
5. Keep one season untouched for final testing, and report results by season, treatment and growth stage.
