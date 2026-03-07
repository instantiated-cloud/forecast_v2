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

    st.title("V2: Simulated Thailand–Cambodia Conflict Forecast Dashboard")

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
        ["🗺️ Map", "📊 Simulated Analytics", "🧠 Model Insights"]
    )

    # -----------------------------------------------------
    # MAP TAB
    # -----------------------------------------------------
    with tab_map:
        st.header("Conflict Risk Map")

        st.write("Unique dates in forecast_df:", forecast_df["date"].unique()[:20])
        st.write("Number of unique dates:", len(forecast_df["date"].unique()))


        # Determine forecast week(s) ONLY
        forecast_dates = forecast_df["date"].dropna().unique()

        if len(forecast_dates) == 1:
            forecast_week = pd.to_datetime(forecast_dates[0]).strftime("%Y-%m-%d")
            st.subheader(f"Forecast for week of: {forecast_week}")
        else:
            min_f = pd.to_datetime(forecast_dates.min()).strftime("%Y-%m-%d")
            max_f = pd.to_datetime(forecast_dates.max()).strftime("%Y-%m-%d")
            st.subheader(f"Forecast period: {min_f} → {max_f}")


        # Base map
        m = folium.Map(location=[14.3, 104.8], zoom_start=7)

        # Merge forecast + segment metadata
        merged = forecast_df.merge(segments_df, on="segment_id", how="left")

        # Color scale for risk
        def risk_color(p):
            if p < 0.2:
                return "green"
            elif p < 0.5:
                return "orange"
            else:
                return "red"

        # Add markers
        for _, row in merged.iterrows():

            # Popup with name, risk, and date — centered, clean, non-bold
            popup_html = f"""
            <div style="
                font-family: Arial, sans-serif;
                font-size: 13px;
                line-height: 18px;
                text-align: center;
                font-weight: normal;
            ">
                {row['segment_id']}<br>
                Risk: {row['conflict_prob']:.2f}<br>
                Date: {row['date'].strftime('%Y-%m-%d')}
            </div>
            """

            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=8,
                color=risk_color(row["conflict_prob"]),
                fill=True,
                fill_color=risk_color(row["conflict_prob"]),
                fill_opacity=0.8,
                tooltip=f"{row['segment_id']} — {row['conflict_prob']:.2f}",
                popup=popup_html
            ).add_to(m)

        # Add legend
        legend_html = """
        <div style="
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 150px;
            background-color: white;
            border: 2px solid grey;
            border-radius: 8px;
            padding: 10px;
            font-size: 13px;
            font-family: Arial, sans-serif;
            z-index: 9999;
        ">
            <b>Risk Levels</b><br>
            <span style="color: green;">●</span> Low (0.00–0.19)<br>
            <span style="color: orange;">●</span> Medium (0.20–0.49)<br>
            <span style="color: red;">●</span> High (0.50+)
        </div>
        """

        m.get_root().html.add_child(folium.Element(legend_html))

        # Render map
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

        # Paths
        fi_csv = os.path.join(OUTPUTS_DIR, "feature_importance.csv")
        fi_png = os.path.join(OUTPUTS_DIR, "feature_importance.png")

        # Debug info (remove later)
        # st.write("Looking for CSV:", fi_csv, "→", os.path.exists(fi_csv))
        # st.write("Looking for PNG:", fi_png, "→", os.path.exists(fi_png))

        # --- CASE 1: CSV exists (new pipeline) ---
        if os.path.exists(fi_csv):
            try:
                fi_df = pd.read_csv(fi_csv)

                if fi_df.empty:
                    st.warning("Simulated Feature importance CSV is empty.")
                else:
                    st.subheader("Feature Importance (CSV)")
                    fig3, ax3 = plt.subplots(figsize=(8, 6))
                    fi_df.sort_values("importance", ascending=True).plot(
                        x="feature", y="importance", kind="barh", ax=ax3, color="steelblue"
                    )
                    st.pyplot(fig3)

            except Exception as e:
                st.error(f"Error loading feature importance CSV: {e}")

        # --- CASE 2: PNG exists (old pipeline) ---
        elif os.path.exists(fi_png):
            st.subheader("Feature Importance (PNG)")
            st.image(fi_png, caption="Feature Importance", width=700)

        # --- CASE 3: Nothing found ---
        else:
            st.info("No feature importance file found. Run the pipeline first.")

        # Model summary
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