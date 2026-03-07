import os
import pandas as pd
import joblib

# ---------------------------------------------------------
# Resolve absolute paths
# ---------------------------------------------------------
def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# ---------------------------------------------------------
# Load model + full dataset (your feature dataset)
# ---------------------------------------------------------
def load_inputs():
    model_path = os.path.join(OUTPUTS_DIR, "model_latest.pkl")
    data_path = os.path.join(OUTPUTS_DIR, "forecast_latest.csv")  # <-- your full dataset

    model = joblib.load(model_path)
    df = pd.read_csv(data_path, parse_dates=["date"])

    print(f"[forecast] Loaded model → {model_path}")
    print(f"[forecast] Loaded dataset → {data_path}")
    print(f"[forecast] Total rows: {len(df)}")

    return model, df

# ---------------------------------------------------------
# Select ONLY the rows to forecast
# ---------------------------------------------------------
def select_forecast_rows(df):
    latest_date = df["date"].max()
    forecast_rows = df[df["date"] == latest_date].copy()

    print(f"[forecast] Forecasting for week: {latest_date.date()}")
    print(f"[forecast] Rows for forecast: {len(forecast_rows)}")

    return forecast_rows

# ---------------------------------------------------------
# Run forecast
# ---------------------------------------------------------
def run_forecast():
    model, df = load_inputs()

    # Identify feature columns
    drop_cols = [
        "segment_id",
        "date",
        "conflict",
        "conflict_prob"  # from previous runs
    ]
    feature_cols = [c for c in df.columns if c not in drop_cols]

    # Select only the rows to forecast
    forecast_df = select_forecast_rows(df)

    # Predict conflict probability
    forecast_df["conflict_prob"] = model.predict_proba(forecast_df[feature_cols])[:, 1]

    # Save forecast-only output
    out_path = os.path.join(OUTPUTS_DIR, "forecast_latest.csv")
    forecast_df.to_csv(out_path, index=False)

    print(f"[forecast] Saved forecast → {out_path}")
    print(f"[forecast] Forecast date: {forecast_df['date'].iloc[0].date()}")

    return forecast_df


if __name__ == "__main__":
    run_forecast()
