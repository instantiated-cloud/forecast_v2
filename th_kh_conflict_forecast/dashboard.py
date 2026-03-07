import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# Load data
forecast_df = pd.read_csv("outputs/forecast_latest.csv")
segments_df = pd.read_csv("data/raw/segments.csv")

st.title("Thailand–Cambodia Conflict Forecast Dashboard")

# -----------------------------
# MAP
# -----------------------------
st.header("Conflict Risk Map")

m = folium.Map(location=[14.3, 104.8], zoom_start=7)
merged = forecast_df.merge(segments_df, on="segment_id")

for _, row in merged.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=8,
        color="red",
        fill=True,
        fill_opacity=row["conflict_prob"],
        popup=f"{row['segment_id']}: {row['conflict_prob']:.2f}"
    ).add_to(m)

st_folium(m, width=700, height=500)

# -----------------------------
# BAR CHART
# -----------------------------
st.header("Risk by Segment")

risk = forecast_df.groupby("segment_id")["conflict_prob"].mean().sort_values()

fig, ax = plt.subplots(figsize=(8,6))
risk.plot(kind="barh", ax=ax, color="firebrick")
st.pyplot(fig)

# -----------------------------
# TIMELINE
# -----------------------------
st.header("Segment Timeline")

segment = st.selectbox("Choose a segment:", risk.index)

seg_df = forecast_df[forecast_df["segment_id"] == segment]

fig2, ax2 = plt.subplots(figsize=(10,4))
ax2.plot(seg_df["date"], seg_df["conflict_prob"], label="Predicted Risk")
ax2.scatter(seg_df["date"], seg_df["conflict"], color="red", label="Actual Conflict")
ax2.legend()
st.pyplot(fig2)
