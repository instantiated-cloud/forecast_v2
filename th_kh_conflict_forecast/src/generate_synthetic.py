# import numpy as np
# import pandas as pd
# import os

# # ---------------------------------------------------------
# # CONFIG — 10 border segments
# # ---------------------------------------------------------
# segments = [
#     "PREAH_VIHEAR_TEMPLE",
#     "TA_MUEN_THOM_TEMPLE",
#     "TA_KRABEY_TEMPLE",
#     "OSMACH_CHECKPOINT",
#     "CHONG_CHOM_CHECKPOINT",
#     "ARANYAPRATHET_POIPET",
#     "PHANOM_DONG_RAK_RIDGE",
#     "BAN_KRUAT",
#     "KANTHARALAK",
#     "SAMRAONG"
# ]

# start_date = "2024-01-07"
# end_date   = "2025-12-28"

# weekly_index = pd.date_range(start=start_date, end=end_date, freq="W")

# # Output folder
# OUTPUT_DIR = "data/raw/"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # ---------------------------------------------------------
# # BASE GRID (week × segment)
# # ---------------------------------------------------------
# def base_grid():
#     rows = []
#     for date in weekly_index:
#         for seg in segments:
#             rows.append({"date": date, "segment_id": seg})
#     return pd.DataFrame(rows)

# base = base_grid()

# # ---------------------------------------------------------
# # 1. INCIDENTS (ground truth)
# # ---------------------------------------------------------
# def generate_incidents():
#     df = base.copy()

#     base_prob = 0.04
#     hotspot_boost = {
#         "PREAH_VIHEAR_TEMPLE": 0.10,
#         "TA_MUEN_THOM_TEMPLE": 0.07,
#         "PHANOM_DONG_RAK_RIDGE": 0.06,
#         "TA_KRABEY_TEMPLE": 0.05
#     }

#     probs = []
#     for _, row in df.iterrows():
#         p = base_prob + hotspot_boost.get(row["segment_id"], 0)
#         probs.append(p)

#     df["conflict"] = np.random.binomial(1, probs)

#     event_types = ["none", "skirmish", "artillery", "drone", "landmine", "arrest"]
#     df["event_type"] = df["conflict"].apply(
#         lambda x: np.random.choice(event_types[1:]) if x == 1 else "none"
#     )

#     df["fatalities"] = df["conflict"] * np.random.poisson(0.3)
#     df["injuries"] = df["conflict"] * np.random.poisson(1.0)
#     df["source"] = "synthetic"

#     return df

# incidents_df = generate_incidents()
# incidents_df.to_csv(os.path.join(OUTPUT_DIR, "incidents.csv"), index=False)

# # ---------------------------------------------------------
# # 2. MILITARY ACTIVITY
# # ---------------------------------------------------------
# def generate_military():
#     df = base.copy()
#     conflict_map = incidents_df.set_index(["date", "segment_id"])["conflict"]

#     df["troop_movements"] = conflict_map.values * np.random.randint(2, 6, len(df)) + np.random.poisson(1, len(df))
#     df["exercises"] = np.random.binomial(1, 0.1, len(df))
#     df["drone_activity"] = conflict_map.values * np.random.binomial(1, 0.4, len(df))
#     df["landmine_incidents"] = np.random.binomial(1, 0.05, len(df))
#     df["checkpoint_closures"] = conflict_map.values * np.random.binomial(1, 0.3, len(df))

#     return df

# military_df = generate_military()
# military_df.to_csv(os.path.join(OUTPUT_DIR, "military_activity.csv"), index=False)

# # ---------------------------------------------------------
# # 3. NEWS SENTIMENT
# # ---------------------------------------------------------
# def generate_news():
#     df = base.copy()
#     conflict_map = incidents_df.set_index(["date", "segment_id"])["conflict"]

#     df["article_count"] = np.random.randint(3, 15, len(df))
#     df["sentiment_score"] = -0.1 - conflict_map.values * np.random.uniform(0.2, 0.6, len(df))
#     df["keyword_border"] = np.random.poisson(2, len(df)) + conflict_map.values * 2
#     df["keyword_temple"] = np.random.poisson(1, len(df)) + conflict_map.values

#     return df

# news_df = generate_news()
# news_df.to_csv(os.path.join(OUTPUT_DIR, "news_sentiment.csv"), index=False)

# # ---------------------------------------------------------
# # 4. TRADE & MIGRATION
# # ---------------------------------------------------------
# def generate_trade():
#     df = base.copy()
#     conflict_map = incidents_df.set_index(["date", "segment_id"])["conflict"]

#     df["trade_value"] = np.random.normal(100000, 15000, len(df))
#     df["trade_value"] -= conflict_map.values * np.random.uniform(10000, 30000, len(df))

#     df["truck_crossings"] = np.random.randint(100, 200, len(df)) - conflict_map.values * np.random.randint(10, 40, len(df))
#     df["migrant_flow"] = np.random.randint(20, 60, len(df))
#     df["market_closures"] = conflict_map.values * np.random.binomial(1, 0.4, len(df))

#     return df

# trade_df = generate_trade()
# trade_df.to_csv(os.path.join(OUTPUT_DIR, "trade_migration.csv"), index=False)

# # ---------------------------------------------------------
# # 5. DISPLACEMENT
# # ---------------------------------------------------------
# def generate_displacement():
#     df = base.copy()
#     conflict_map = incidents_df.set_index(["date", "segment_id"])["conflict"]

#     df["displaced_persons"] = conflict_map.values * np.random.randint(10, 200, len(df))
#     df["civilian_casualties"] = conflict_map.values * np.random.binomial(1, 0.3, len(df))
#     df["aid_deliveries"] = conflict_map.values * np.random.randint(0, 3, len(df))

#     return df

# displacement_df = generate_displacement()
# displacement_df.to_csv(os.path.join(OUTPUT_DIR, "displacement.csv"), index=False)

# print("Synthetic CSV files updated in:", OUTPUT_DIR)

# # ---------------------------------------------------------
# # WRITE SEGMENTS FILE (STATIC)
# # ---------------------------------------------------------
# segments_df = pd.DataFrame({
#     "segment_id": segments,
#     "lat": [14.390, 14.420, 14.130, 14.430, 14.640, 13.660, 14.450, 14.610, 14.650, 13.800],
#     "lon": [104.680, 103.200, 103.150, 103.030, 102.720, 102.560, 104.000, 103.120, 104.650, 103.520]
# })

# segments_df.to_csv(os.path.join(OUTPUT_DIR, "segments.csv"), index=False)


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