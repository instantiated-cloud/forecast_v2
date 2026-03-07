import os
import subprocess
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# st.set_page_config(layout="wide")

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

    st.title("Simulated Thailand–Cambodia Conflict Forecast Dashboard")
    st.subheader(":red[_Prototype v2.0_]")

    st.markdown("""
    <style>

        /* MAIN APP BACKGROUND */
        div[data-testid="stAppViewContainer"] {
            background-color: #fafafb;
        }

        /* OPTIONAL: SIDEBAR BACKGROUND */
        section[data-testid="stSidebar"] {
            background-color: #e6e6e6;
        }

        /* OPTIONAL: TABS BACKGROUND */
        div[data-baseweb="tab-list"] {
            background-color: #fafafb;
        }

    </style>
    """, unsafe_allow_html=True)


    # -----------------------------------------------------
    # Load data
    # -----------------------------------------------------
    forecast_df = load_forecast()
    if forecast_df is None:
        st.stop()

    segments_df = pd.read_csv(SEGMENTS_FILE)

    # Step 2 — Coordinate fixes
    coordinate_fixes = {
        "PREAH_VIHEAR_TEMPLE": {"lat": 14.3904, "lon": 104.6802},
        "TA_MUEN_THOM_TEMPLE": {"lat": 14.3554, "lon": 103.2585},
        "TA_KRABEY_TEMPLE": {"lat": 14.3528, "lon": 103.3733}, # Incorrect location
        "OSMACH_CHECKPOINT": {"lat": 14.4340, "lon": 103.6997},
        "CHONG_CHOM_CHECKPOINT": {"lat": 14.4349, "lon": 103.7001},
        "ARANYAPRATHET_POIPET": {"lat": 13.6615, "lon": 102.5504},
        "PHANOM_DONG_RAK_RIDGE": {"lat": 14.3525, "lon": 103.3737},
        "BAN_KRUAT": {"lat": 14.3378, "lon": 103.1749},
        "KANTHARALAK": {"lat": 14.4604, "lon": 104.7183},
        "SAMRAONG": {"lat": 14.3028, "lon": 103.6260},
    }

    # Step 3 — Apply fixes
    for seg, fix in coordinate_fixes.items():
        mask = segments_df["segment_id"] == seg
        segments_df.loc[mask, "lat"] = fix["lat"]
        segments_df.loc[mask, "lon"] = fix["lon"]

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

        #st.write("Unique dates in forecast_df:", forecast_df["date"].unique()[:20])
        #st.write("Number of unique dates:", len(forecast_df["date"].unique()))

        # Determine forecast week(s) ONLY
        forecast_dates = forecast_df["date"].dropna().unique()

        if len(forecast_dates) == 1:
            forecast_week = pd.to_datetime(forecast_dates[0]).strftime("%Y-%m-%d")
            st.subheader(f"Forecast for week of: {forecast_week}")
        else:
            min_f = pd.to_datetime(forecast_dates.min()).strftime("%Y-%m-%d")
            max_f = pd.to_datetime(forecast_dates.max()).strftime("%Y-%m-%d")
            st.subheader(f"Forecast period: {min_f} → {max_f}")

        # Create map with no base tiles
        m = folium.Map(
            location=[13.8, 103.6],
            zoom_start=8,
            tiles=None
        )

        # 1️⃣ Add Hybrid FIRST (this becomes the default)
        hybrid = folium.TileLayer(
            tiles="http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google Hybrid",
            name="Satellite Hybrid",
            control=True,
            show=True
        )
        hybrid.add_to(m)

        # 2️⃣ Add Street Map SECOND
        street = folium.TileLayer(
            "OpenStreetMap",
            name="Street Map",
            control=True,
            show=False
        )
        street.add_to(m)

        # 3️⃣ Add Layer Control
        folium.LayerControl(collapsed=True).add_to(m)

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
            width: 155px;
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


    FEATURE_LABELS = {

    # --- CORE CONFLICT VARIABLES ---
    "conflict": "Conflict Event (0 = no, 1 = yes)",
    "conflict_lag1": "Conflict Event (1-week lag)",
    "conflict_lag2": "Conflict Event (2-week lag)",
    "conflict_lag4": "Conflict Event (4-week lag)",

    # --- HUMAN IMPACT ---
    "fatalities": "Fatalities (count)",
    "injuries": "Injuries (count)",
    "civilian_casualties": "Civilian Casualties (count)",
    "displaced_persons": "Displaced Persons (count)",
    "aid_deliveries": "Aid Deliveries (count)",

    # --- MILITARY ACTIVITY ---
    "troop_movements": "Troop Movements (count)",
    "troop_movements_lag1": "Troop Movements (1-week lag)",
    "troop_movements_lag2": "Troop Movements (2-week lag)",
    "troop_movements_lag4": "Troop Movements (4-week lag)",

    "exercises": "Military Exercises (count)",
    "drone_activity": "Drone Activity (count)",
    "landmine_incidents": "Landmine Incidents (count)",
    "checkpoint_closures": "Checkpoint Closures (count)",

    # --- MEDIA & SENTIMENT ---
    "article_count": "News Article Count (weekly)",
    "sentiment_score": "Sentiment Score (−1 to +1)",
    "sentiment_score_lag1": "Sentiment Score (1-week lag)",
    "sentiment_score_lag2": "Sentiment Score (2-week lag)",
    "sentiment_score_lag4": "Sentiment Score (4-week lag)",

    "keyword_border": "Keyword: 'border' Mentions (count)",
    "keyword_temple": "Keyword: 'temple' Mentions (count)",

    # --- TRADE & ECONOMIC ACTIVITY ---
    "trade_value": "Trade Value (USD or normalized)",
    "trade_value_lag1": "Trade Value (1-week lag)",
    "trade_value_lag2": "Trade Value (2-week lag)",
    "trade_value_lag4": "Trade Value (4-week lag)",

    "truck_crossings": "Truck Crossings (count)",
    "migrant_flow": "Migrant Flow (count)",
    "market_closures": "Market Closures (count)",

    # --- EVENT TYPE FLAGS (binary) ---
    "event_type_border_incident": "Event Type: Border Incident (0/1)",
    "event_type_none": "Event Type: None (0/1)",
    "event_type_skirmish": "Event Type: Skirmish (0/1)",

    # --- SOURCE FLAGS (binary) ---
    "source_military_report": "Source: Military Report (0/1)",
    "source_ngo": "Source: NGO Report (0/1)",
    "source_none": "Source: No Source (0/1)",

    # --- MODEL OUTPUT (not used in feature explorer) ---
    "conflict_prob": "Model Forecast Probability (0–1)",
    }

    ##### -----------------------------------------------------
    # ANALYTICS TAB (Refactored)
    # -----------------------------------------------------
    with tab_analytics:
        st.header("📊 Segment Analytics Dashboard")

        # -------------------------------------------------
        # Load historical + forecast data
        # -------------------------------------------------
        history_path = os.path.join(OUTPUTS_DIR, "model_input_latest.csv")
        history_df = pd.read_csv(history_path, parse_dates=["date"])

        forecast_path = os.path.join(OUTPUTS_DIR, "forecast_latest.csv")
        forecast_df = pd.read_csv(forecast_path, parse_dates=["date"])
        forecast_df = forecast_df.rename(columns={"conflict_prob": "forecast"})

        # -------------------------------------------------
        # Identify feature columns
        # -------------------------------------------------
        feature_cols = [
            c for c in history_df.columns
            if c not in ["date", "segment_id", "conflict"]
        ]

        # -------------------------------------------------
        # Segment selector
        # -------------------------------------------------
        segment_list = sorted(history_df["segment_id"].unique())
        segment = st.selectbox("Select segment:", segment_list)

        seg_hist = history_df[history_df["segment_id"] == segment].sort_values("date")
        seg_fore = forecast_df[forecast_df["segment_id"] == segment].sort_values("date")

        # -------------------------------------------------
        # 1️⃣ TIMELINE: Conflict + Forecast
        # -------------------------------------------------
        st.subheader("📈 Conflict Timeline & Forecast")

        fig, ax = plt.subplots(figsize=(10, 4))

        # Historical conflict (0/1)
        ax.plot(
            seg_hist["date"],
            seg_hist["conflict"],
            marker="o",
            color="gray",
            label="Historical Conflict"
        )

        # Highlight conflict events
        conflict_points = seg_hist[seg_hist["conflict"] == 1]
        ax.scatter(
            conflict_points["date"],
            conflict_points["conflict"],
            color="blue",
            s=60,
            zorder=5,
            label="Conflict Event"
        )

        # Forecast probability
        ax.scatter(
            seg_fore["date"],
            seg_fore["forecast"],
            color="red",
            s=60,
            zorder=4,
            label="Forecast Probability"
        )

        # Probability labels
        for x, y in zip(seg_fore["date"], seg_fore["forecast"]):
            ax.text(
                x, y + 0.03,
                f"{y*100:.0f}%",
                fontsize=8,
                color="red",
                ha="center",
                va="bottom",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
            )

        
        # Add vertical markers for historical conflict events
        levels = 6  # number of stagger levels

        for i, (_, row) in enumerate(conflict_points.iterrows()):
            # Blue dashed vertical line
            ax.axvline(
                row["date"],
                color="blue",
                linestyle=(0, (5, 10)),
                alpha=0.7
            )

            # Center of the plot
            y_center = 0.5

            # Compute stagger level (0 to 5)
            level = i % levels

            # Spread levels evenly above/below center
            offset = (level - (levels - 1) / 2) * 0.12

            # Blue date label with white background
            ax.text(
                row["date"],
                y_center + offset,
                row["date"].strftime("%Y-%m-%d"),
                rotation=0,
                fontsize=8,
                color="blue",          # <-- blue text
                ha="center",
                va="center",
                bbox=dict(
                    facecolor="white",   # <-- white background
                    edgecolor="none",
                    alpha=0.8,
                    boxstyle="round,pad=0.2"
                )
            )

        ax.set_title(f"Timeline for {segment}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Conflict / Probability")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_yticks([0, 1])

        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45)

        st.pyplot(fig)

        # -------------------------------------------------
        # 2️⃣ FEATURE EXPLORER (Clean, no probability)
        # -------------------------------------------------
        st.subheader("🔍 Feature Explorer")

        if len(feature_cols) == 0:
            st.info("No feature columns found in model_input_latest.csv")
        else:
            feature_choice = st.selectbox("Choose a feature to explore:", feature_cols)

            # Human-readable scale label
            y_label = FEATURE_LABELS.get(
                feature_choice,
                f"Feature Value ({feature_choice})"
            )

            fig2, ax2 = plt.subplots(figsize=(10, 4))

            # Feature trend
            ax2.plot(
                seg_hist["date"],
                seg_hist[feature_choice],
                color="purple",
                marker="o",
                label=f"{feature_choice}"
            )

            # Conflict event markers
            conflict_dates = seg_hist[seg_hist["conflict"] == 1]["date"]
            for d in conflict_dates:
                ax2.axvline(d, color="blue", linestyle=(0, (5, 10)), alpha=0.6)

            # Title + labels
            ax2.set_title(f"{feature_choice} vs Conflict — {segment}")
            ax2.set_xlabel("Date")
            ax2.set_ylabel(y_label, fontsize=10)
            ax2.grid(True, linestyle="--", alpha=0.4)

            # Legend box
            legend = ax2.legend(
                loc="upper left",
                bbox_to_anchor=(1.02, 1),
                frameon=True,
                facecolor="white",
                edgecolor="gray"
            )
            legend.get_frame().set_alpha(0.9)

            plt.xticks(rotation=45)
            st.pyplot(fig2)



        # # -------------------------------------------------
        # # 3️⃣ MULTI-SEGMENT COMPARISON (Optional but powerful)
        # # -------------------------------------------------
        # st.subheader("📌 Multi-Segment Comparison")

        # compare_feature = st.selectbox(
        #     "Choose a feature to compare across segments:",
        #     feature_cols
        # )

        # fig3, ax3 = plt.subplots(figsize=(10, 4))

        # for seg in segment_list:
        #     df_seg = history_df[history_df["segment_id"] == seg].sort_values("date")
        #     ax3.plot(df_seg["date"], df_seg[compare_feature], label=seg, alpha=0.6)

        # ax3.set_title(f"{compare_feature} Across All Segments")
        # ax3.set_xlabel("Date")
        # ax3.set_ylabel(compare_feature)
        # ax3.grid(True, linestyle="--", alpha=0.4)
        # ax3.legend(loc="center left", bbox_to_anchor=(1, 0.5))

        # plt.xticks(rotation=45)
        # st.pyplot(fig3)


    # -----------------------------------------------------
    # MODEL INSIGHTS TAB
    # -----------------------------------------------------
    with tab_insights:
        st.header("Model Insights")

        # Paths
        fi_csv = os.path.join(OUTPUTS_DIR, "feature_importance.csv")
        fi_png = os.path.join(OUTPUTS_DIR, "feature_importance.png")
        
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




if __name__ == "__main__":
    main()