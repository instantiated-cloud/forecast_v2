import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib


# ---------------------------------------------------------
# Resolve absolute paths safely
# ---------------------------------------------------------
def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


# ---------------------------------------------------------
# Save feature importance
# ---------------------------------------------------------
def save_feature_importance(model, feature_names):
    fi = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    fi_path = os.path.join(OUTPUTS_DIR, "feature_importance.csv")
    fi.to_csv(fi_path, index=False)
    print(f"[model_training] Saved feature importance → {fi_path}")


# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------
def train_model(df):
    print("[model_training] Starting model training...")

    # Drop non-feature columns
    drop_cols = ["segment_id", "date", "conflict"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    y = df["conflict_next_week"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Model
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred)
    print(f"[model_training] Validation AUC: {auc:.4f}")

    # Save model
    model_path = os.path.join(OUTPUTS_DIR, "model_latest.pkl")
    joblib.dump(model, model_path)
    print(f"[model_training] Saved model → {model_path}")

    # Save feature importance
    save_feature_importance(model, X_train.columns)

    return model