import pandas as pd

USE_SYNTHETIC = False

if USE_SYNTHETIC:
    from src import generate_synthetic

from src.load_data import (
    load_incidents, load_military, load_news,
    load_trade, load_displacement, load_segments
)
from src.preprocess import merge_all
from src.feature_engineering import build_features
from src.model_training import train
from src.forecast import forecast
from src.visualize import map_forecast, bar_forecast, feature_importance

def main():

    print("\n=== STEP 1: Generating synthetic data ===")
    # Running the module executes the generator

    print("\n=== STEP 2: Loading raw CSVs ===")
    inc = load_incidents()
    mil = load_military()
    news = load_news()
    trade = load_trade()
    disp = load_displacement()

    print("Loaded:")
    print(f"  incidents: {len(inc)} rows")
    print(f"  military: {len(mil)} rows")
    print(f"  news: {len(news)} rows")
    print(f"  trade: {len(trade)} rows")
    print(f"  displacement: {len(disp)} rows")

    print("\n=== STEP 3: Preprocessing & merging ===")
    merged = merge_all(inc, mil, news, trade, disp)
    merged.to_csv("data/processed/merged_features.csv", index=False)
    print(f"Merged dataset saved: {len(merged)} rows")

    print("\n=== STEP 4: Feature engineering ===")
    features = build_features(merged)
    features.to_csv("data/processed/merged_features_lagged.csv", index=False)
    print(f"Feature dataset saved: {len(features)} rows")

    #### === NEW STEP: Save full model input for analytics ===
    model_input_path = "outputs/model_input_latest.csv"
    features.to_csv(model_input_path, index=False)
    print(f"Model input saved: {model_input_path}")

    print("\n=== STEP 5: Training model ===")
    train(features)

    print("\n=== STEP 6: Forecasting ===")
    forecast_df = forecast(features)
    print("Forecast saved to outputs/forecast_latest.csv")

    print("\n=== STEP 7: Visualization ===")
    segments_df = load_segments()

    map_forecast(forecast_df, segments_df)
    bar_forecast(forecast_df)

    from joblib import load
    model = load("models/border_rf.joblib")

    drop_cols = ["conflict", "date", "segment_id", "event_type", "source"]
    X = features.drop(columns=drop_cols, errors="ignore")

    feature_importance(model, X)

    print("\n=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    main()
