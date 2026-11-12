import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


import inference

st.set_page_config(page_title="LAI Driver What-if Demo", layout="wide")
st.title("LAI Driver What-if Demo (env inputs → LAI)")

# -----------------------------------------
# Load data + models
# -----------------------------------------
@st.cache_data
def load_df():
    BASE_DIR = "/workspaces/Prototypes/LAI_Forecast" #for streamlit hosting
    return inference.load_data(BASE_DIR/"DSSAT_Merged_Neat.csv")

@st.cache_resource
def load_models():
    return inference.load_models(
        scaler_path="scaler.pkl",
        rf_path="rf_model.pkl",
        xgb_path="xgb_model.json",
    )

@st.cache_data
def build_env(df):
    df_lag = inference.build_global_lag_table(df)
    ranges = inference.compute_driver_ranges(df_lag)
    return df_lag, ranges

df = load_df()
models = load_models()
df_lag, driver_ranges = build_env(df)

# -----------------------------------------
# Sidebar controls
# -----------------------------------------
st.sidebar.header("Driver what-if controls")

runno = st.sidebar.selectbox(
    "Scenario (RUNNO)", sorted(df_lag.RUNNO.unique())
)

# DAP range
daps = sorted(df_lag[df_lag.RUNNO == runno].DAP.unique())
dap_min, dap_max = int(min(daps)), int(max(daps))

dap_range = st.sidebar.slider(
    "DAP range",
    dap_min,
    dap_max,
    (dap_min, dap_max)
)

dap_start, dap_end = dap_range

# baseline row for defaults
baseline_row = inference.get_baseline_row(df_lag, runno, dap_start)

st.sidebar.write("---")
st.sidebar.write(f"RUNNO: {runno}")
st.sidebar.write(f"DAP range: {dap_start} → {dap_end}")

st.sidebar.write("Adjust environmental drivers:")

env_overrides = {}
for feat in inference.ENV_FEATS:
    if feat not in driver_ranges:
        continue

    lo, hi = driver_ranges[feat]
    base_val = baseline_row.get(feat, (lo + hi) / 2)

    env_overrides[feat] = st.sidebar.slider(
        feat, float(lo), float(hi), float(base_val)
    )

# -----------------------------------------
# RANGE PREDICTION
# -----------------------------------------
pred_df = inference.predict_range(
    df_lag=df_lag,
    env_overrides=env_overrides,
    runno=runno,
    dap_start=dap_start,
    dap_end=dap_end,
    models=models,
)

st.subheader("Predicted LAI curve for selected DAP range")

# -----------------------------------------
# Metrics display (last point)
# -----------------------------------------
if not pred_df.empty:
    last = pred_df.iloc[-1]
    c1, c2 = st.columns(2)
    c1.metric("RF LAI (final day)", f"{last['RF']:.3f}")
    c2.metric("XGB LAI (final day)", f"{last['XGB']:.3f}")

# -----------------------------------------
# Plot
# -----------------------------------------
if not pred_df.empty:
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(pred_df["DAP"], pred_df["RF"], label="RF predicted LAI", linewidth=2)
    ax.plot(pred_df["DAP"], pred_df["XGB"], label="XGB predicted LAI", linewidth=2)

    ax.set_xlabel("DAP")
    ax.set_ylabel("Predicted LAI")
    ax.set_title(f"Predicted LAI Curve (RUNNO {runno})")
    ax.grid(True, alpha=0.3)
    ax.legend()

    st.pyplot(fig, clear_figure=True)

# -----------------------------------------
# Show table of driver inputs
# -----------------------------------------
with st.expander("Show driver inputs used"):
    df_inputs = pd.DataFrame({
        "Feature": list(env_overrides.keys()),
        "Adjusted value": list(env_overrides.values()),
    })
    st.dataframe(df_inputs, use_container_width=True)
