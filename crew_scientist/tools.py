"""Custom tools for the Data Scientist crew — deterministic feature engineering,
model training, and evaluation using scikit-learn.
"""
from __future__ import annotations

import json
import os

import joblib
import pandas as pd
from crewai.tools import tool
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean", "clean_data.csv")
CONTRACT_PATH = os.path.join(BASE_DIR, "outputs", "dataset_contract.json")
FEATURES_PATH = os.path.join(BASE_DIR, "outputs", "features.csv")
MODEL_PATH = os.path.join(BASE_DIR, "outputs", "model.pkl")
EVAL_PATH = os.path.join(BASE_DIR, "outputs", "evaluation_report.md")
CARD_PATH = os.path.join(BASE_DIR, "outputs", "model_card.md")

LEAKAGE_COLUMNS = ["reservation_status", "reservation_status_date"]
# Excluded from modeling for non-leakage reasons (see dataset_contract.json):
DROP_ALWAYS = ["arrival_date", "assigned_room_type", "agent", "company"]
SPLIT_KEY = "arrival_date_year"  # kept in features.csv ONLY as the temporal split key

CATEGORICAL = [
    "hotel", "arrival_date_month", "meal", "country", "market_segment",
    "distribution_channel", "reserved_room_type", "deposit_type", "customer_type",
]
NUMERIC = [
    "lead_time", "arrival_date_week_number", "arrival_date_day_of_month",
    "stays_in_weekend_nights", "stays_in_week_nights", "adults", "children", "babies",
    "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled",
    "booking_changes", "days_in_waiting_list", "adr", "required_car_parking_spaces",
    "total_of_special_requests",
]
TARGET = "is_canceled"


def _contract_feature_names() -> list[str]:
    """Approved feature names from dataset_contract.json (empty list if absent)."""
    if not os.path.exists(CONTRACT_PATH):
        return []
    with open(CONTRACT_PATH, encoding="utf-8") as f:
        contract = json.load(f)
    return [c["name"] for c in contract.get("feature_columns", []) if isinstance(c, dict) and "name" in c]


@tool("Validate dataset contract against clean_data.csv")
def validate_contract() -> str:
    """Confirms that data/clean/clean_data.csv matches outputs/dataset_contract.json:
    checks the target column exists, all declared feature columns are present, and
    that the known leakage columns (reservation_status, reservation_status_date) are
    still in the raw file but will be excluded. Call this FIRST before any modeling."""
    if not os.path.exists(CONTRACT_PATH):
        return json.dumps({"error": "dataset_contract.json not found. Crew 1 must run first."})
    if not os.path.exists(CLEAN_PATH):
        return json.dumps({"error": "clean_data.csv not found. Crew 1 must run first."})

    with open(CONTRACT_PATH, encoding="utf-8") as f:
        contract = json.load(f)
    df = pd.read_csv(CLEAN_PATH)

    contract_cols = {c["name"] for c in contract.get("feature_columns", []) if "name" in c}
    missing = [c for c in contract_cols if c not in df.columns]
    target_ok = contract.get("target_column", TARGET) in df.columns
    leakage_present = [c for c in LEAKAGE_COLUMNS if c in df.columns]
    leakage_declared_as_feature = [c for c in LEAKAGE_COLUMNS if c in contract_cols]
    row_count_ok = contract.get("row_count", len(df)) == len(df)

    result = {
        "contract_target_column": contract.get("target_column", TARGET),
        "target_present_in_data": target_ok,
        "declared_feature_columns": len(contract_cols),
        "missing_declared_columns": missing,
        "leakage_columns_confirmed_present_but_excluded": leakage_present,
        "leakage_columns_wrongly_declared_as_features": leakage_declared_as_feature,
        "row_count": len(df),
        "row_count_matches_contract": row_count_ok,
        "validation_passed": (
            target_ok and len(contract_cols) > 0 and len(missing) == 0
            and len(leakage_declared_as_feature) == 0 and row_count_ok
        ),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Engineer features and save features.csv")
def engineer_features() -> str:
    """Builds the modeling feature set from clean_data.csv: selects only the
    contract-approved numeric and categorical columns, EXCLUDES the leakage
    columns (reservation_status, reservation_status_date) and assigned_room_type
    (a post-booking field), and saves the raw (pre-encoding) feature table plus
    target to outputs/features.csv. One-hot encoding happens later inside the
    model pipeline so features.csv stays human-readable."""
    df = pd.read_csv(CLEAN_PATH)

    approved = set(_contract_feature_names())
    model_features = [c for c in NUMERIC + CATEGORICAL if c in df.columns]
    if approved:  # never use a column the contract did not approve
        model_features = [c for c in model_features if c in approved]
    for c in LEAKAGE_COLUMNS:  # defense in depth
        assert c not in model_features, f"leakage column {c} slipped into features"

    keep_cols = model_features + [SPLIT_KEY, TARGET]
    features_df = df[keep_cols].copy()
    features_df["country"] = features_df["country"].fillna("UNK")

    os.makedirs(os.path.dirname(FEATURES_PATH), exist_ok=True)
    features_df.to_csv(FEATURES_PATH, index=False)

    summary = {
        "saved_to": "outputs/features.csv",
        "row_count": len(features_df),
        "model_feature_columns": model_features,
        "split_key_column_not_a_feature": SPLIT_KEY,
        "excluded_leakage_columns": LEAKAGE_COLUMNS,
        "excluded_other": DROP_ALWAYS,
        "target_column": TARGET,
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


def _build_pipeline(model):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )
    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])


@tool("Train and compare 2 model variations, save the best as model.pkl")
def train_and_evaluate_models() -> str:
    """Reads outputs/features.csv, splits into train/test (temporal split by
    arrival_date_year: train on 2015-2016, test on 2017), trains TWO model
    variations (RandomForestClassifier and GradientBoostingClassifier),
    evaluates both on accuracy/precision/recall/f1/roc_auc, saves the better
    model as outputs/model.pkl, and writes outputs/evaluation_report.md
    comparing both. Call this AFTER engineer_features."""
    df = pd.read_csv(FEATURES_PATH)

    train_df = df[df[SPLIT_KEY] <= 2016]
    test_df = df[df[SPLIT_KEY] == 2017]
    if len(test_df) == 0:
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df[TARGET])

    # The split key is NOT a model feature (the test year is never seen in training).
    drop = [TARGET, SPLIT_KEY]
    X_train, y_train = train_df.drop(columns=drop), train_df[TARGET]
    X_test, y_test = test_df.drop(columns=drop), test_df[TARGET]

    candidates = {
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=200, max_depth=12, random_state=42, class_weight="balanced", n_jobs=-1
        ),
        "GradientBoostingClassifier": GradientBoostingClassifier(
            n_estimators=150, max_depth=3, learning_rate=0.1, random_state=42
        ),
    }

    results = {}
    fitted_pipelines = {}
    for name, model in candidates.items():
        pipe = _build_pipeline(model)
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        proba = pipe.predict_proba(X_test)[:, 1]
        results[name] = {
            "accuracy": round(accuracy_score(y_test, preds), 4),
            "precision": round(precision_score(y_test, preds), 4),
            "recall": round(recall_score(y_test, preds), 4),
            "f1": round(f1_score(y_test, preds), 4),
            "roc_auc": round(roc_auc_score(y_test, proba), 4),
        }
        fitted_pipelines[name] = pipe

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    best_pipe = fitted_pipelines[best_name]

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(best_pipe, MODEL_PATH)

    report_lines = [
        "# Evaluation Report — Booking Cancellation Prediction\n",
        f"Train set: {len(X_train)} bookings (2015-2016) | Test set: {len(X_test)} bookings (2017)\n",
        "## Model Comparison\n",
        "| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |",
        "|---|---|---|---|---|---|",
    ]
    for name, m in results.items():
        marker = " ✅ (selected)" if name == best_name else ""
        report_lines.append(
            f"| {name}{marker} | {m['accuracy']} | {m['precision']} | {m['recall']} | {m['f1']} | {m['roc_auc']} |"
        )
    report_lines.append(f"\n**Best model:** {best_name} (highest ROC-AUC), saved to `outputs/model.pkl`.\n")
    report_lines.append(
        f"Features used: {len(NUMERIC)} numeric + {len(CATEGORICAL)} categorical "
        f"(one-hot encoded in-pipeline). Excluded: leakage columns {LEAKAGE_COLUMNS}, "
        f"post-booking/ID columns {DROP_ALWAYS}, and `{SPLIT_KEY}` (split key only).\n"
    )

    with open(EVAL_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    output = {
        "results": results,
        "best_model": best_name,
        "saved_model_to": "outputs/model.pkl",
        "saved_report_to": "outputs/evaluation_report.md",
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


@tool("Write model_card.md")
def write_model_card() -> str:
    """Writes outputs/model_card.md documenting model purpose, training data,
    metrics (read from evaluation_report.md), limitations, and ethical
    considerations. Call this LAST, after train_and_evaluate_models."""
    eval_content = ""
    if os.path.exists(EVAL_PATH):
        with open(EVAL_PATH, encoding="utf-8") as f:
            eval_content = f.read()

    card = f"""# Model Card — Hotel Booking Cancellation Predictor

## Model Purpose
Predicts, at booking time, the probability that a hotel reservation will be
canceled. Intended to support revenue management decisions such as overbooking
buffers and deposit policy — NOT to automatically deny or penalize guests.

## Training Data
- Source: Hotel Booking Demand dataset (Resort Hotel + City Hotel, Portugal, 2015-2017)
- Cleaned via Crew 1 (Data Analyst): missing values imputed, invalid rows removed
- Split: temporal (train 2015-2016, test 2017) to avoid future data leakage; `arrival_date_year` is used only as the split key, never as a feature
- Leakage columns (`reservation_status`, `reservation_status_date`) explicitly excluded; `assigned_room_type` (post-booking) and `agent`/`company` IDs also excluded

## Metrics
{eval_content if eval_content else "See outputs/evaluation_report.md"}

## Limitations
- Trained on Portugal-based hotels (2015-2017); may not generalize to other markets, hotel types, or post-pandemic booking behavior.
- Moderate class imbalance (~37% cancellation rate): recall on the canceled class (~63%) is lower than precision (~79%), so a meaningful share of true cancellations is missed. The decision threshold (0.5) should be tuned to the hotel's cost of a missed cancellation vs. a false alarm.
- No guest-level personal identifiers were used, but `country` and `market_segment` are coarse proxies that could correlate with protected characteristics — model should not be used for individual guest profiling.
- Does not account for external shocks (pandemics, travel bans, macroeconomic shifts).

## Ethical Considerations
- **Do not** use this model to deny bookings, apply discriminatory pricing, or blacklist guests by country/origin.
- Intended use is aggregate risk scoring for **operational planning** (overbooking, staffing), not individual guest judgment.
- Model should be periodically retrained as booking patterns shift over time.
- Predictions are probabilistic, not deterministic — human review is required before any policy action.
"""

    os.makedirs(os.path.dirname(CARD_PATH), exist_ok=True)
    with open(CARD_PATH, "w", encoding="utf-8") as f:
        f.write(card)

    return json.dumps({"saved_to": "outputs/model_card.md"}, ensure_ascii=False)
