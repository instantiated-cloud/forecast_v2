import pandas as pd
from .config import SEGMENTS, START_DATE, END_DATE, FREQ

def make_weekly_grid():
    weeks = pd.date_range(START_DATE, END_DATE, freq=FREQ)
    rows = [{"date": d, "segment_id": s} for d in weeks for s in SEGMENTS]
    return pd.DataFrame(rows)

def merge_all(inc, mil, news, trade, disp):
    df = inc.merge(mil, on=["date", "segment_id"], how="left")
    df = df.merge(news, on=["date", "segment_id"], how="left")
    df = df.merge(trade, on=["date", "segment_id"], how="left")
    df = df.merge(disp, on=["date", "segment_id"], how="left")
    return df.fillna(0)
