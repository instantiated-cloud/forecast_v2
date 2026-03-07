from joblib import load
import pandas as pd

# def forecast(df):
#     model = load("models/border_rf.joblib")
#     X = df.drop(columns=["conflict", "date"], errors="ignore")
#     df["conflict_prob"] = model.predict_proba(X)[:, 1]
#     df.to_csv("outputs/forecast_latest.csv", index=False)
#     return df

def forecast(df):
    model = load("models/border_rf.joblib")

    drop_cols = ["conflict", "date", "segment_id", "event_type", "source"]

    X = df.drop(columns=drop_cols, errors="ignore")

    df["conflict_prob"] = model.predict_proba(X)[:, 1]
    df.to_csv("outputs/forecast_latest.csv", index=False)
    return df
