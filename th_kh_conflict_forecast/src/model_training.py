# import pandas as pd
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import roc_auc_score
# from joblib import dump


# # from sklearn.ensemble import RandomForestClassifier
# # from sklearn.metrics import roc_auc_score
# # from joblib import dump

# # def train(df):
# #     train = df[df["date"] < "2025-01-01"]
# #     test  = df[df["date"] >= "2025-01-01"]

# #     X_train = train.drop(columns=["conflict", "date"])
# #     y_train = train["conflict"]

# #     X_test = test.drop(columns=["conflict", "date"])
# #     y_test = test["conflict"]

# #     model = RandomForestClassifier(
# #         n_estimators=300,
# #         class_weight="balanced",
# #         random_state=42
# #     )
# #     model.fit(X_train, y_train)

# #     preds = model.predict_proba(X_test)[:, 1]
# #     print("AUC:", roc_auc_score(y_test, preds))

# #     dump(model, "models/border_rf.joblib")

# def train(df):
#     train = df[df["date"] < "2025-01-01"]
#     test  = df[df["date"] >= "2025-01-01"]

#     # FIX: remove segment_id so model doesn't see strings
#     X_train = train.drop(columns=["conflict", "date", "segment_id"])
#     y_train = train["conflict"]

#     X_test = test.drop(columns=["conflict", "date", "segment_id"])
#     y_test = test["conflict"]

#     model = RandomForestClassifier(
#         n_estimators=300,
#         class_weight="balanced",
#         random_state=42
#     )
#     model.fit(X_train, y_train)

#     preds = model.predict_proba(X_test)[:, 1]
#     print("AUC:", roc_auc_score(y_test, preds))

#     dump(model, "models/border_rf.joblib")

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from joblib import dump

def train(df):
    train = df[df["date"] < "2025-01-01"]
    test  = df[df["date"] >= "2025-01-01"]

    drop_cols = ["conflict", "date", "segment_id", "event_type", "source"]

    X_train = train.drop(columns=drop_cols)
    y_train = train["conflict"]

    X_test = test.drop(columns=drop_cols)
    y_test = test["conflict"]

    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict_proba(X_test)[:, 1]
    print("AUC:", roc_auc_score(y_test, preds))

    dump(model, "models/border_rf.joblib")
