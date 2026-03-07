def add_lags(df, col, lags=[1, 2, 4]):
    for lag in lags:
        df[f"{col}_lag{lag}"] = df.groupby("segment_id")[col].shift(lag)
    return df

def build_features(df):
    df = add_lags(df, "conflict")
    df = add_lags(df, "sentiment_score")
    df = add_lags(df, "troop_movements")
    df = add_lags(df, "trade_value")
    df = df.dropna()
    return df
