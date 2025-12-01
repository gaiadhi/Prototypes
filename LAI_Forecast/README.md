# 🌱 LAI Driver What-If Demo  
### Interactive tool to explore how environmental drivers affect cotton LAI

![Streamlit](https://img.shields.io/badge/Platform-Streamlit-red?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square)

> **Live app:** https://laiforecasting-jt7zdh3ojum66hcq3a6fgw.streamlit.app

This app lets you change environmental conditions (temperature, soil water, nitrogen, radiation, etc.) and instantly see how those changes affect **Leaf Area Index (LAI)** for cotton, based on simulated DSSAT runs and machine learning models.

It’s designed so that **non-ML users** (agronomists, domain experts, clients) can use it comfortably.

---

## 📋 Table of Contents

- [1. What This App Does](#1-what-this-app-does)
- [2. How to Open and Use the App](#2-how-to-open-and-use-the-app)
  - [2.1 Open the app](#21-open-the-app)
  - [2.2 Main screen](#22-main-screen)
  - [2.3 Picking a RUN and DAP](#23-picking-a-run-and-dap)
  - [2.4 Adjusting drivers](#24-adjusting-environmental-drivers)
  - [2.5 Reading the LAI graph](#25-reading-the-lai-graph)
- [3. Example Questions You Can Explore](#3-example-questions-you-can-explore)
- [4. Screenshots](#4-screenshots)
- [5. Access Control and Privacy](#5-access-control-and-privacy)
- [6. For Developers / Internal Notes](#6-for-developers--internal-notes)
  - [6.1 Project structure](#61-project-structure)
  - [6.2 Running locally](#62-running-locally)
  - [6.3 Model loading via `modelszip`](#63-model-loading-via-modelszip)
  - [6.4 CI / Deployment](#64-ci--deployment)
- [7. Contact](#7-contact)

---

## 1. What This App Does

At a high level:

- Uses **simulated crop model data (DSSAT)** for cotton at Snook / College Station.
- For each “run” (year + treatment), we have **daily LAI** and environmental variables.
- We trained ML models to learn how changes in environment affect LAI.
- The app lets you interactively tweak those drivers and see:

> “If the environment looks like *this* on this day, what LAI should I expect?”

You don’t need to understand the internals of the machine learning model to use this tool.

---

## 2. How to Open and Use the App

### 2.1 Open the app

Just click:

> **https://laiforecasting-jt7zdh3ojum66hcq3a6fgw.streamlit.app**

It opens in your browser (Chrome, Edge, etc.).  
No installation, no Python, nothing else required.

---

### 2.2 Main screen

When the app loads, you’ll see:

- A **left sidebar** with:
  - RUN selector
  - Day-After-Planting (DAP) selector
  - Sliders for environmental drivers
- A **main panel** with:
  - A graph of LAI over DAP
  - Baseline vs. adjusted prediction curves
  - Optional numeric outputs / details

---

### 2.3 Picking a RUN and DAP

- **RUN** = a specific combination of:
  - Year
  - Treatment (e.g., nitrogen level, tillage practice, etc.)

Each RUN has a different LAI curve and environmental profile.

- **DAP (Days After Planting)** = where you are in the season.
  - Early DAP → emergence / early vegetative
  - Mid DAP → strong vegetative growth
  - Late DAP → reproductive / senescence phases

You typically:

1. Select a **RUN**  
2. Choose a **DAP** you care about (e.g., 50–80)

---

### 2.4 Adjusting environmental drivers

On the sidebar, you’ll see sliders like:

| Driver        | Interpretation                                                  |
|---------------|-----------------------------------------------------------------|
| `TMAX`, `TMIN`| Daily maximum and minimum temperature                           |
| `TGRD`        | Temperature growth effect (how favorable temperature is)        |
| `SW4D–SW6D`   | Soil water content at certain depths (layer 4, 5, 6)            |
| `NITD`, `NIAD`| Nitrogen in the soil / available nitrogen                       |
| `SRAD`, `PARD`| Solar radiation / photosynthetically active radiation           |

What you do:

- Move a slider up or down.
- The app will immediately recompute the **predicted LAI** for that day (and optionally a range of days).
- The graph updates live so you can see the effect.

---

### 2.5 Reading the LAI graph

The graph typically shows:

- **Baseline LAI**  
  LAI from the original crop model simulation (no modifications).

- **Adjusted LAI predictions**  
  LAI predicted by ML models when you change the environment.

Rough interpretation:

- **Lower adjusted curve** → plant is under more stress (water, heat, nitrogen, etc.), lower LAI.
- **Higher adjusted curve** → more favorable conditions, more leaf area.
- **Curve shifted to the right** → slower development (delayed growth).
- **Curve shifted to the left** → faster development (earlier canopy buildup).

This helps answer: _“Is this crop on track, or are conditions pushing it off track?”_

---

## 3. Example Questions You Can Explore

Some examples of what this app can illustrate:

- **Heat stress scenario**  
  - Increase `TMAX`, keep everything else constant → see how LAI responds.

- **Water limitation**  
  - Reduce `SW4D–SW6D` around key growth stages → observe LAI drop or flatten.

- **Nitrogen deficit**  
  - Lower `NITD` / `NIAD` → see if canopy fails to reach peak LAI.

- **“What if we had better conditions?”**  
  - Raise moisture and nitrogen together → see if LAI increases mid-season.

This makes it easy to have visual, data-driven conversations about stress and interventions.

---

## 4. Screenshots

> These image paths assume you add screenshots under an `images/` folder in the repo.  
> - `images/app_home.png` – main app view  
> - `images/app_controls.png` – sidebar controls / sliders  
> - `images/app_lai_curve.png` – LAI curve comparison

Place the PNG files there and these will render automatically on GitHub.

### Home screen

![Home screen](images/app_home.png)

### Controls and sliders

![Controls and sliders](images/app_controls.png)

### LAI curve visualization

![LAI curve](images/app_lai_curve.png)

---

## 5. Access Control and Privacy

This app can be made **private** so only specific people can access it.

### GitHub repo

- Set the repository to **Private** in GitHub settings if needed.

### Streamlit Cloud app access

On Streamlit:

1. Go to the app page.  
2. Click **“Manage app”** (bottom-right).  
3. Under **Access**:
   - Choose **“Only invited users can view this app”** (or similar wording).
4. Add the email addresses of users who should have access.

Only those authenticated users will be able to open the app.

---

## 6. For Developers / Internal Notes

This section is for anyone maintaining or extending the app.

### 6.1 Project structure

```text
LAI_Forecast/
│
├── app.py                # Streamlit UI entrypoint
├── inference.py          # All prediction / feature logic
├── DSSAT_Merged_Neat.csv # Cleaned DSSAT-based dataset
├── models.zip            # Compressed model artifacts (RF, XGB, scaler)
│
├── requirements.txt      # Python dependencies for Streamlit
├── packages.txt          # Linux packages for Streamlit Cloud
├── Procfile              # Process definition for Streamlit Cloud
│
└── .github/
    └── workflows/
        └── deploy.yml    # GitHub Actions workflow

6.2 Running locally

Prereqs:

Python 3.11

virtualenv / venv recommended

Steps:

git clone <this-repo-url>
cd LAI_Forecast

# (optional but recommended)
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

# make sure models.zip is present in the project root
streamlit run app.py


The app will start at a URL like http://localhost:8501.

6.3 Model loading via models.zip
Because GitHub has a 100 MB file limit, the individual model files (rf_model.pkl, etc.) are not stored as raw files in the repo.
Instead:


All model artifacts are compressed into models.zip:


rf_model.pkl


scaler.pkl


xgb_model.json




On startup, inference.py calls ensure_models_unzipped(), which:


Checks if the unzipped files exist.


If not, extracts them from models.zip in the app’s working directory.




The ML models (Random Forest, XGBoost) are then loaded using the usual code.


If you ever retrain and update the models:


Replace the local .pkl / .json files.


Rebuild the zip:
Compress-Archive -Path "rf_model.pkl","scaler.pkl","xgb_model.json" -DestinationPath "models.zip" -Force



Commit and push the new models.zip.



6.4 CI / Deployment


Deployment target: Streamlit Community Cloud


GitHub Actions workflow: .github/workflows/deploy.yml


Runs on push to main


Installs dependencies from requirements.txt


Does a basic Python syntax check




Streamlit Cloud pulls from main and runs streamlit run app.py (via Procfile).

7. Contact
For questions, support, or feature requests:
Maintainer: Aishwarya
Email: your-email-here
If you need enhancements (e.g., satellite LAI integration, yield prediction, multi-field scaling), reach out and we can extend this app accordingly.

---

### What you do now

1. In VS Code → create `README.md` in the root of `LAI_Forecast`.
2. Paste the content above.
3. Optional but nice: create an `images/` folder and later add:
   - `app_home.png`
   - `app_controls.png`
   - `app_lai_curve.png`
4. Then:

```bash
git add README.md
git commit -m "Add full client + dev README"
git push

Once you refresh GitHub, this will show up beautifully on the repo home page.