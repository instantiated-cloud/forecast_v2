import pandas as pd
from .config import DATA_RAW

def load_incidents():
    return pd.read_csv(f"{DATA_RAW}/incidents.csv", parse_dates=["date"])

def load_military():
    return pd.read_csv(f"{DATA_RAW}/military_activity.csv", parse_dates=["date"])

def load_news():
    return pd.read_csv(f"{DATA_RAW}/news_sentiment.csv", parse_dates=["date"])

def load_trade():
    return pd.read_csv(f"{DATA_RAW}/trade_migration.csv", parse_dates=["date"])

def load_displacement():
    return pd.read_csv(f"{DATA_RAW}/displacement.csv", parse_dates=["date"])

def load_segments():
    return pd.read_csv(f"{DATA_RAW}/segments.csv")
