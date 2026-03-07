import folium
import matplotlib.pyplot as plt
import numpy as np

def map_forecast(df, segments_df):
    m = folium.Map(location=[14.3, 104.8], zoom_start=7)

    merged = df.merge(segments_df, on="segment_id", how="left")

    for _, row in merged.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=8,
            color="red",
            fill=True,
            fill_opacity=row["conflict_prob"],
            popup=f"{row['segment_id']}: {row['conflict_prob']:.2f}"
        ).add_to(m)

    m.save("outputs/forecast_map.html")
    print("Map saved to outputs/forecast_map.html")

def bar_forecast(df):
    latest = df.groupby("segment_id")["conflict_prob"].mean().sort_values()

    plt.figure(figsize=(10,6))
    latest.plot(kind="barh", color="firebrick")
    plt.title("Predicted Conflict Probability by Segment")
    plt.xlabel("Probability")
    plt.tight_layout()
    plt.savefig("outputs/forecast_bar.png")
    plt.close()
    print("Bar chart saved to outputs/forecast_bar.png")

def feature_importance(model, X):
    importances = model.feature_importances_
    idx = np.argsort(importances)

    plt.figure(figsize=(10,8))
    plt.barh(X.columns[idx], importances[idx], color="steelblue")
    plt.title("Feature Importance")
    plt.tight_layout()
    plt.savefig("outputs/feature_importance.png")
    plt.close()
    print("Feature importance saved to outputs/feature_importance.png")
