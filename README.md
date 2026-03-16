# forecast_v2
*AI Prompted Code and Assisted Debugging for Model Testing and Simulation*

📘 Thailand–Cambodia Conflict Forecasting System
📌 Overview
This repository contains a complete, end‑to‑end forecasting system for weekly conflict risk along the Thailand–Cambodia border. It integrates:

Data ingestion & cleaning

Feature engineering (lags, rolling windows, categorical encoding)

Model training (Random Forest classifier)

Weekly forecasting

Interactive Streamlit dashboard for visualization and analysis

The system is designed for operational early‑warning workflows, enabling analysts to explore historical patterns, inspect feature behavior, and monitor forecasted conflict probabilities.


🚀 Running the Full Pipeline
Run the entire workflow with:

python run_pipeline.py

This executes:

STEP 1 — Generate synthetic data for model testing, or load proccessed data

STEP 2 — Merge & clean

STEP 3 — Feature engineering

STEP 4 — Save feature matrix

STEP 5 — Train model

STEP 6 — Forecast next week

STEP 7 — Save forecast output

All artifacts are written to the outputs/ directory.


🧠 Model Training
Training is handled by:

src/model_training.py

Key details:

Model: RandomForestClassifier

Handles class imbalance via class_weight="balanced"

Automatically encodes categorical variables:

event_type

source

Saves:

model_latest.pkl

model_input_latest.csv

The pipeline calls:

from src.model_training import train
train(features_df)


🔮 Forecasting
Forecasting is handled by:

src/forecast.py

The forecast step:

Loads the trained model

Encodes features exactly the same way as training

Drops non-feature columns

Predicts conflict probability

Saves:

outputs/forecast_latest.csv

This file powers the dashboard.


📊 Streamlit Dashboard
Launch the dashboard with:

streamlit run dashboard.py


The dashboard includes:

1. Interactive Map
Displays conflict probability by segment

Supports satellite view, zoom, and layer toggles

2. Timeline View
Historical conflict events

Forecast probabilities

Clean labels and annotations

3. Feature Explorer
Select any feature

View its weekly trend

Conflict events marked with blue dashed lines

Clear human-readable scale labels

Legend box for interpretability


📈 Feature Scale Dictionary
The dashboard uses a comprehensive dictionary to label features clearly:

Counts (e.g., troop_movements, fatalities)

Sentiment (−1 to +1)

Trade values

Lagged features (_lag1, _lag2, _lag4)

Event type flags (event_type_*)

Source flags (source_*)

This ensures analysts always understand the meaning and scale of each feature.


📦 Requirements
Install dependencies:

pip install -r requirements.txt

Typical dependencies include:

pandas

numpy

scikit-learn

joblib

streamlit

folium

matplotlib


🧪 Adding New Data
To update the system with new weekly data:

Add the new raw CSV to your data directory

Run:

python run_pipeline.py


Refresh the Streamlit dashboard

The map + analytics update automatically


🛠️ Troubleshooting
ImportError: cannot import name 'train'
Ensure model_training.py defines:

def train(features_df):

Feature mismatch errors
Occurs when training and forecasting use different encodings.
Fix: ensure encode_features() is used in both training and forecasting.

Model not loading
Verify:

outputs/model_latest.pkl

exists and is readable.


📄 License
This project is for analytical and research purposes.
No warranty or guarantee of predictive accuracy.
