import os
import subprocess
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Resolve absolute paths safely for Streamlit Cloud
# ---------------------------------------------------------
def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

FORECAST_FILE = os.path.join(OUTPUTS_DIR, "forecast_latest.csv")
SEGMENTS_FILE = os.path.join(DATA_DIR, "segments.csv")


# ---------------------------------------------------------
# Load forecast data with graceful fallback
# ---------------------------------------------------------
def load_forecast():
    if not os.path.exists(FORECAST_FILE):
        st.error("No forecast file found. Run the pipeline first.")
        return None
    df = pd.read_csv(FORECAST_FILE)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df


# ---------------------------------------------------------
# Run pipeline on demand (currently hidden)
# ---------------------------------------------------------
def run_pipeline():
    subprocess.run(["python", os.path.join(BASE_DIR, "run_pipeline.py")])


# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------
def main():

    st.title("Thailand–Cambodia Conflict Forecast Dashboard")

    # -----------------------------------------------------
    # Load data
    # -----------------------------------------------------
    forecast_df = load_forecast()
    if forecast_df is None:
        st.stop()

    segments_df = pd.read_csv(SEGMENTS_FILE)

    # -----------------------------------------------------
    # Tabs for clean navigation
    # -----------------------------------------------------
    tab_map, tab_analytics, tab_insights = st.tabs(
        ["🗺️ Map", "📊 Analytics", "🧠 Model Insights"]
    )

    # -----------------------------------------------------
    # MAP TAB
    # -----------------------------------------------------
    with tab_map:
        st.header("Conflict Risk Map")

        m = folium.Map(location=[14.3, 104.8], zoom_start=7)
        merged = forecast_df.merge(segments_df, on="segment_id", how="left")

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

    # -----------------------------------------------------
    # ANALYTICS TAB
    # -----------------------------------------------------
    with tab_analytics:
        st.header("Risk by Segment")

        risk = forecast_df.groupby("segment_id")["conflict_prob"].mean().sort_values()

        fig, ax = plt.subplots(figsize=(8, 6))
        risk.plot(kind="barh", ax=ax, color="firebrick")
        ax.set_title("Predicted Conflict Probability by Segment")
        ax.set_xlabel("Probability")
        st.pyplot(fig)

        st.header("Segment Timeline")

        segment = st.selectbox("Choose a segment:", risk.index)
        seg_df = forecast_df[forecast_df["segment_id"] == segment]

        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.plot(seg_df["date"], seg_df["conflict_prob"], label="Predicted Risk")
        ax2.scatter(seg_df["date"], seg_df["conflict"], color="red", label="Actual Conflict")
        ax2.legend()
        ax2.set_title(f"Timeline for {segment}")
        st.pyplot(fig2)

    # -----------------------------------------------------
    # MODEL INSIGHTS TAB
    # -----------------------------------------------------
    with tab_insights:
        st.header("Model Insights")

        # Feature importance file (optional)
        fi_path = os.path.join(OUTPUTS_DIR, "feature_importance.csv")

        if os.path.exists(fi_path):
            fi_df = pd.read_csv(fi_path)

            st.subheader("Feature Importance")
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            fi_df.sort_values("importance", ascending=True).plot(
                x="feature", y="importance", kind="barh", ax=ax3, color="steelblue"
            )
            st.pyplot(fig3)
        else:
            st.info("Feature importance file not found. Generate it in the pipeline.")

        st.subheader("Model Summary")
        st.write("""
        - The model is a Random Forest classifier.
        - It predicts conflict probability for each border segment.
        - It uses lagged features (previous week’s activity) to forecast future risk.
        - Key drivers typically include:
            - Troop movements
            - Drone activity
            - Sentiment score
            - Article count
            - Previous conflict
        """)


if __name__ == "__main__":
    main()