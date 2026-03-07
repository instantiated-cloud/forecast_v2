import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# ---------------------------------------------------------
# Resolve absolute paths
# ---------------------------------------------------------
def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ---------------------------------------------------------
# Load your full dataset (the one you used to train)
# ---------------------------------------------------------
def load_dataset():
    data_path = os.path.join(OUTPUTS_DIR, "forecast_latest.csv")
    df = pd.read_csv(data_path, parse_dates=["date"])
    print(f"[training] Loaded dataset → {data_path}")
    print(f"[training] Rows: {len(df)}")
    return df

# ---------------------------------------------------------
# Encode categorical columns
# ---------------------------------------------------------
def encode_features(df):
    categorical_cols = ["event_type", "source"]

    print(f"[training] Encoding categorical columns: {categorical_cols}")

    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    print(f"[training] Encoded feature count: {df_encoded.shape[1]}")
    return df_encoded

# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------
def train_model(df):

    # Columns we do NOT use as features
    drop_cols = [
        "segment_id",
        "date",
        "conflict_prob",  # from previous runs
        "conflict"        # label
    ]

    feature_cols = [c for c in df.columns if c not in drop_cols]

    X = df[feature_cols]
    y = df["conflict"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("[training] Training RandomForest model...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)
    print("[training] Model training complete.")

    return model, feature_cols

# ---------------------------------------------------------
# Save model + encoded dataset
# ---------------------------------------------------------
def save_outputs(model, df):
    # Save model
    model_path = os.path.join(OUTPUTS_DIR, "model_latest.pkl")
    joblib.dump(model, model_path)
    print(f"[training] Saved model → {model_path}")

    # Save encoded dataset
    feature_path = os.path.join(OUTPUTS_DIR, "model_input_latest.csv")
    df.to_csv(feature_path, index=False)
    print(f"[training] Saved feature dataset → {feature_path}")

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def run_training():
    df = load_dataset()
    df_encoded = encode_features(df)
    model, feature_cols = train_model(df_encoded)
    save_outputs(model, df_encoded)
    print("[training] Training pipeline complete.")
    return model


if __name__ == "__main__":
    run_training()
