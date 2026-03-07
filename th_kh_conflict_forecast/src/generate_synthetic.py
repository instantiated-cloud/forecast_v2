import pandas as pd
import numpy as np
import os
from datetime import timedelta

OUTPUT_DIR = "data/raw/"

segments = [
    "PREAH_VIHEAR_TEMPLE",
    "TA_MUEN_THOM_TEMPLE",
    "TA_KRABEY_TEMPLE",
    "OSMACH_CHECKPOINT",
    "CHONG_CHOM_CHECKPOINT",
    "ARANYAPRATHET_POIPET",
    "PHANOM_DONG_RAK_RIDGE",
    "BAN_KRUAT",
    "KANTHARALAK",
    "SAMRAONG"
]

start_date = pd.to_datetime("2024-01-07")
end_date = pd.to_datetime("2025-12-28")
weeks = pd.date_range(start_date, end_date, freq="W")

def write_csv(name, df):
    df.to_csv(os.path.join(OUTPUT_DIR, name), index=False)

# ---------------------------------------------------------
# SYNTHETIC DATA GENERATION
# ---------------------------------------------------------
rows = []
for date in weeks:
    for seg in segments:
        conflict = np.random.binomial(1, 0.15)
        fatalities = np.random.poisson(0.2 if conflict else 0.05)
        injuries = np.random.poisson(0.3 if conflict else 0.1)
        event_type = np.random.choice(["none", "skirmish", "artillery", "border_incident"])
        source = np.random.choice(["local_news", "military_report", "ngo", "none"])

        rows.append({
            "date": date,
            "segment_id": seg,
            "conflict": conflict,
            "fatalities": fatalities,
            "injuries": injuries,
            "event_type": event_type,
            "source": source
        })

incidents_df = pd.DataFrame(rows)
write_csv("incidents.csv", incidents_df)

# Military
mil_df = pd.DataFrame({
    "date": np.repeat(weeks, len(segments)),
    "segment_id": segments * len(weeks),
    "troop_movements": np.random.poisson(5, len(weeks) * len(segments)),
    "exercises": np.random.poisson(1, len(weeks) * len(segments)),
    "drone_activity": np.random.poisson(2, len(weeks) * len(segments)),
    "landmine_incidents": np.random.poisson(0.3, len(weeks) * len(segments)),
    "checkpoint_closures": np.random.binomial(1, 0.1, len(weeks) * len(segments))
})
write_csv("military_activity.csv", mil_df)

# News
news_df = pd.DataFrame({
    "date": np.repeat(weeks, len(segments)),
    "segment_id": segments * len(weeks),
    "article_count": np.random.poisson(3, len(weeks) * len(segments)),
    "sentiment_score": np.random.normal(0, 1, len(weeks) * len(segments)),
    "keyword_border": np.random.binomial(1, 0.2, len(weeks) * len(segments)),
    "keyword_temple": np.random.binomial(1, 0.1, len(weeks) * len(segments))
})
write_csv("news_sentiment.csv", news_df)

# Trade
trade_df = pd.DataFrame({
    "date": np.repeat(weeks, len(segments)),
    "segment_id": segments * len(weeks),
    "trade_value": np.random.normal(100, 20, len(weeks) * len(segments)),
    "truck_crossings": np.random.poisson(50, len(weeks) * len(segments)),
    "migrant_flow": np.random.poisson(10, len(weeks) * len(segments)),
    "market_closures": np.random.binomial(1, 0.05, len(weeks) * len(segments))
})
write_csv("trade_migration.csv", trade_df)

# Displacement
disp_df = pd.DataFrame({
    "date": np.repeat(weeks, len(segments)),
    "segment_id": segments * len(weeks),
    "displaced_persons": np.random.poisson(3, len(weeks) * len(segments)),
    "civilian_casualties": np.random.poisson(0.2, len(weeks) * len(segments)),
    "aid_deliveries": np.random.poisson(1, len(weeks) * len(segments))
})
write_csv("displacement.csv", disp_df)

# ---------------------------------------------------------
# WRITE SEGMENTS FILE (STATIC)
# ---------------------------------------------------------
segments_df = pd.DataFrame({
    "segment_id": segments,
    "lat": [14.390, 14.420, 14.130, 14.430, 14.640, 13.660, 14.450, 14.610, 14.650, 13.800],
    "lon": [104.680, 103.200, 103.150, 103.030, 102.720, 102.560, 104.000, 103.120, 104.650, 103.520]
})
write_csv("segments.csv", segments_df)

print("Synthetic CSV files updated in:", OUTPUT_DIR)