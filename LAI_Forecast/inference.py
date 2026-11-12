"""
Inference utilities for LAI driver what-if demo (env inputs -> LAI),
extended to support DAP-range predictions + plotting.

This version uses ONLY RF and XGB (no LSTM) and supports loading models
from a compressed models.zip bundle on Streamlit Cloud.
"""

from dataclasses import dataclass
from typing import Dict, List

import os
import zipfile
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb

# ============================================================
# FEATURE SET (14 features: 10 env + 3 lags + DAP)
# ============================================================
ENV_FEATS = [
    "NITD", "NIAD",
    "TMIN", "TMAX",
    "TGRD",
    "SW4D", "SW5D", "SW6D",
    "SRAD", "PARD",
]

TARGET = "LAI"
MAX_LAG = 3


# ============================================================
# Model container
# ============================================================
@dataclass
class Models:
    scaler: object
    rf: object
    xgb_model: xgb.Booster


# ============================================================
# Helpers for correct feature order
# ============================================================
def _get_feature_cols(df: pd.DataFrame, scaler) -> List[str]:
    """Ensure we follow the scaler's expected feature order."""
    if hasattr(scaler, "feature_names_in_"):
        cols = list(scaler.feature_names_in_)
    else:
        cols = ENV_FEATS + [f"LAI_lag{i}" for i in range(1, 4)] + ["DAP"]

    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing model feature columns: {missing}")

    return cols


# ============================================================
# Data loading + lag building
# ============================================================
def load_data(csv_path: str = "DSSAT_Merged_Neat.csv") -> pd.DataFrame:
    return pd.read_csv(csv_path)


def build_lag_table(df, target=TARGET, max_lag=MAX_LAG):
    df2 = df.copy()
    for lag in range(1, max_lag + 1):
        df2[f"{target}_lag{lag}"] = df2.groupby("RUNNO")[target].shift(lag)

    df2 = df2.dropna(subset=[f"{target}_lag{i}" for i in range(1, max_lag + 1)])
    return df2.reset_index(drop=True)


def build_global_lag_table(df):
    return build_lag_table(df, TARGET, MAX_LAG)


# ============================================================
# Compute slider ranges
# ============================================================
def compute_driver_ranges(df_lag, q_low=0.05, q_high=0.95):
    ranges = {}
    for col in ENV_FEATS:
        if col in df_lag.columns:
            low = float(df_lag[col].quantile(q_low))
            high = float(df_lag[col].quantile(q_high))
            ranges[col] = (low, high)
    return ranges


# ============================================================
# NEW: Extract models.zip if needed
# ============================================================
def ensure_models_unzipped(zip_path: str = "models.zip") -> None:
    """
    Ensure that the actual model artifact files exist locally.
    If not, extract them from models.zip (used by Streamlit Cloud).
    """
    BASE_DIR = "/mount/src/prototypes/LAI_Forecast/" #for streamlit hosting
    zip_path = BASE_DIR + zip_path
    needed = ["scaler.pkl", "rf_model.pkl", "xgb_model.json"]

    # Already unzipped → nothing to do
    if all(os.path.exists(p) for p in needed):
        return

    # Zip missing → app error
    if not os.path.exists(zip_path):
        raise FileNotFoundError(
            f"{zip_path} is missing. Cannot load model files."
        )

    # Extract all files into current directory
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(".")


# ============================================================
# Load models (RF + XGB only)
# ============================================================
def load_models(
    scaler_path: str = "scaler.pkl",
    rf_path: str = "rf_model.pkl",
    xgb_path: str = "xgb_model.json",
):
    """
    Unzip model files if needed and then load RF, XGB and scaler.
    """
    ensure_models_unzipped()

    scaler = joblib.load(scaler_path)
    rf = joblib.load(rf_path)

    xgb_model = xgb.Booster()
    xgb_model.load_model(xgb_path)

    return Models(
        scaler=scaler,
        rf=rf,
        xgb_model=xgb_model,
    )


# ============================================================
# Row access
# ============================================================
def get_baseline_row(df_lag, runno, dap):
    row = df_lag[(df_lag.RUNNO == runno) & (df_lag.DAP == dap)]
    if row.empty:
        raise ValueError(f"No lag row for RUNNO={runno}, DAP={dap}")
    return row.iloc[0]


# ============================================================
# Single-step prediction
# ============================================================
def predict_from_env_overrides(df_lag, env_overrides, runno, dap, models):
    feature_cols = _get_feature_cols(df_lag, models.scaler)
    row = get_baseline_row(df_lag, runno, dap).copy()
    print(f"Baseline before override: {row['LAI']}")

    # Override env drivers
    for f, v in env_overrides.items():
        if f in row.index:
            row[f] = v

    print(f"Baseline after override: {type(row)}\n{row} ")
    print(f"Baseline after override: {row['LAI']}")
    
    x = row[feature_cols].values.reshape(1, -1)
    x_s = models.scaler.transform(x)

    rf_pred = float(models.rf.predict(x_s)[0])
    xgb_pred = float(models.xgb_model.predict(xgb.DMatrix(x_s))[0])

    return {
        "RUNNO": runno,
        "DAP": dap,
        "RF": rf_pred,
        "XGB": xgb_pred, 
        #Karthik: replace XGB with baseline
        #"XGB": row['LAI'],
    }


# ============================================================
# Multi-day prediction (DAP_start → DAP_end)
# ============================================================
def predict_range(df_lag, env_overrides, runno, dap_start, dap_end, models):
    preds = []
    for dap in range(dap_start, dap_end + 1):
        try:
            pred = predict_from_env_overrides(df_lag, env_overrides, runno, dap, models)
            preds.append(pred)
        except Exception:
            continue

    return pd.DataFrame(preds)
