"""Custom tools for the Data Analyst crew — pandas-backed, deterministic operations.

Agents call these tools instead of hallucinating data manipulation, which keeps
the pipeline reproducible (a hard requirement of the CrewAI Flow spec).
"""
from __future__ import annotations

import json
import os

import pandas as pd
from crewai.tools import tool

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "hotel_bookings.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "clean", "clean_data.csv")
CONTRACT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "dataset_contract.json")
EDA_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "eda_report.html")
INSIGHTS_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "insights.md")


@tool("Load and profile raw dataset")
def load_and_profile_dataset() -> str:
    """Loads the raw hotel_bookings.csv and returns a JSON profile:
    shape, dtypes, missing value counts per column, and the first 3 rows.
    Use this first to understand what needs cleaning."""
    df = pd.read_csv(RAW_PATH)
    profile = {
        "shape": list(df.shape),
        "columns": list(df.columns),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing_counts": {c: int(v) for c, v in df.isna().sum().items() if v > 0},
        "sample_rows": json.loads(df.head(3).to_json(orient="records")),
    }
    return json.dumps(profile, ensure_ascii=False, indent=2)


@tool("Clean dataset and save clean_data.csv")
def clean_dataset() -> str:
    """Cleans the raw hotel booking dataset with a deterministic, documented
    procedure: fills missing children/babies/agent/company with 0/'None',
    drops rows with missing country, removes the 'Undefined' meal category
    rows, casts date fields, and removes rows where adults+children+babies == 0
    (a known data-quality artifact in this dataset). Saves to data/clean/clean_data.csv.
    Returns a JSON summary of what changed."""
    df = pd.read_csv(RAW_PATH)
    before_rows = len(df)

    df["children"] = df["children"].fillna(0)
    df["agent"] = df["agent"].fillna(0)
    df["company"] = df["company"].fillna(0)
    df = df.dropna(subset=["country"])
    df = df[df["meal"] != "Undefined"]

    total_guests = df["adults"].fillna(0) + df["children"].fillna(0) + df["babies"].fillna(0)
    df = df[total_guests > 0]

    df["arrival_date"] = pd.to_datetime(
        df["arrival_date_year"].astype(str)
        + "-"
        + df["arrival_date_month"]
        + "-"
        + df["arrival_date_day_of_month"].astype(str),
        format="%Y-%B-%d",
        errors="coerce",
    )

    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)

    summary = {
        "rows_before": before_rows,
        "rows_after": len(df),
        "rows_dropped": before_rows - len(df),
        "steps": [
            "children/agent/company NaN -> 0",
            "dropped rows with missing country",
            "removed meal == 'Undefined'",
            "removed rows with 0 total guests",
            "parsed arrival_date from year/month/day",
        ],
        "saved_to": "data/clean/clean_data.csv",
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


@tool("Run exploratory data analysis and save eda_report.html")
def run_eda() -> str:
    """Reads data/clean/clean_data.csv, computes descriptive statistics and
    key business metrics (cancellation rate by hotel, ADR by month, lead time
    distribution, top guest countries, market segment mix), and writes a
    self-contained eda_report.html with tables. Returns a JSON of the key metrics."""
    df = pd.read_csv(CLEAN_PATH)

    cancel_by_hotel = df.groupby("hotel")["is_canceled"].mean().round(3).to_dict()
    adr_by_hotel = df.groupby("hotel")["adr"].mean().round(2).to_dict()
    top_countries = df["country"].value_counts().head(10).to_dict()
    segment_mix = df["market_segment"].value_counts().to_dict()
    avg_lead_time = round(df["lead_time"].mean(), 1)
    cancel_rate_overall = round(df["is_canceled"].mean(), 3)

    html_parts = [
        "<html><head><meta charset='utf-8'><title>EDA Report — Hotel Bookings</title>",
        "<style>body{font-family:sans-serif;margin:40px} table{border-collapse:collapse;margin-bottom:24px}",
        "td,th{border:1px solid #ccc;padding:6px 12px;text-align:left}</style></head><body>",
        "<h1>EDA Report — Hotel Booking Demand</h1>",
        f"<p>Rows analyzed: {len(df)} | Overall cancellation rate: {cancel_rate_overall*100:.1f}% | "
        f"Average lead time: {avg_lead_time} days</p>",
        "<h2>Cancellation Rate by Hotel</h2><table><tr><th>Hotel</th><th>Cancellation Rate</th></tr>",
    ]
    for k, v in cancel_by_hotel.items():
        html_parts.append(f"<tr><td>{k}</td><td>{v*100:.1f}%</td></tr>")
    html_parts.append("</table>")

    html_parts.append("<h2>Average Daily Rate (ADR) by Hotel</h2><table><tr><th>Hotel</th><th>Avg ADR</th></tr>")
    for k, v in adr_by_hotel.items():
        html_parts.append(f"<tr><td>{k}</td><td>€{v}</td></tr>")
    html_parts.append("</table>")

    html_parts.append("<h2>Top 10 Guest Countries</h2><table><tr><th>Country</th><th>Bookings</th></tr>")
    for k, v in top_countries.items():
        html_parts.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
    html_parts.append("</table>")

    html_parts.append("<h2>Market Segment Mix</h2><table><tr><th>Segment</th><th>Bookings</th></tr>")
    for k, v in segment_mix.items():
        html_parts.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
    html_parts.append("</table></body></html>")

    os.makedirs(os.path.dirname(EDA_PATH), exist_ok=True)
    with open(EDA_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    metrics = {
        "cancel_rate_overall": cancel_rate_overall,
        "cancel_by_hotel": cancel_by_hotel,
        "adr_by_hotel": adr_by_hotel,
        "avg_lead_time": avg_lead_time,
        "top_countries": top_countries,
        "segment_mix": segment_mix,
        "saved_to": "outputs/eda_report.html",
    }
    return json.dumps(metrics, ensure_ascii=False, indent=2)


@tool("Write dataset_contract.json")
def write_dataset_contract() -> str:
    """Writes outputs/dataset_contract.json — the schema, allowed values, and
    constraints the Data Scientist crew must respect when reading
    data/clean/clean_data.csv. Call this last, after cleaning and EDA."""
    df = pd.read_csv(CLEAN_PATH)

    contract = {
        "file": "data/clean/clean_data.csv",
        "target_column": "is_canceled",
        "target_type": "binary (0 = not canceled, 1 = canceled)",
        "row_count": len(df),
        "columns": {
            c: {
                "dtype": str(df[c].dtype),
                "nullable": bool(df[c].isna().any()),
            }
            for c in df.columns
        },
        "categorical_columns": [
            "hotel", "meal", "country", "market_segment", "distribution_channel",
            "reserved_room_type", "assigned_room_type", "deposit_type",
            "customer_type", "reservation_status",
        ],
        "numeric_columns": [
            "lead_time", "stays_in_weekend_nights", "stays_in_week_nights",
            "adults", "children", "babies", "previous_cancellations",
            "previous_bookings_not_canceled", "booking_changes",
            "days_in_waiting_list", "adr", "required_car_parking_spaces",
            "total_of_special_requests",
        ],
        "leakage_warning": (
            "reservation_status and reservation_status_date are recorded AFTER "
            "the cancellation outcome is known — they MUST be excluded from "
            "model features to avoid data leakage."
        ),
        "assumptions": [
            "children/agent/company missing values were imputed as 0",
            "rows with missing country were dropped",
            "rows with 0 total guests (data artifact) were dropped",
        ],
    }

    os.makedirs(os.path.dirname(CONTRACT_PATH), exist_ok=True)
    with open(CONTRACT_PATH, "w", encoding="utf-8") as f:
        json.dump(contract, f, ensure_ascii=False, indent=2)

    return json.dumps({"saved_to": "outputs/dataset_contract.json", "columns": len(contract["columns"])}, ensure_ascii=False)
