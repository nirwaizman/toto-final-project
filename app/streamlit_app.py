"""Streamlit UI — Toto: Industry-Simulated AI Product Workflow.

Shows the two-crew CrewAI pipeline (Data Analyst -> Data Scientist), lets the
user trigger a full Flow run, and visualizes the generated outputs.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean", "clean_data.csv")

st.set_page_config(page_title="🐾 Toto — AI Product Workflow", layout="wide")

st.title("🐾 Toto — Industry-Simulated AI Product Workflow")
st.caption(
    "A CrewAI Flow that coordinates a Data Analyst Crew and a Data Scientist "
    "Crew to turn hotel booking data into a cancellation-prediction model."
)

tab_overview, tab_flow, tab_eda, tab_model = st.tabs(
    ["📋 Overview", "▶️ Run Flow", "📊 EDA & Insights", "🤖 Model Results"]
)

# ---------------------------------------------------------------- Overview
with tab_overview:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👥 Crew 1 — Data Analyst")
        st.markdown(
            "- **Ingestion Specialist** — profiles raw data\n"
            "- **Cleaning Engineer** — produces `clean_data.csv`\n"
            "- **EDA Analyst** — produces `eda_report.html`\n"
            "- **Insights & Contract Writer** — produces `insights.md` + `dataset_contract.json`"
        )
    with col2:
        st.subheader("👥 Crew 2 — Data Scientist")
        st.markdown(
            "- **Contract Validator** — checks data matches the contract\n"
            "- **Feature Engineer** — produces `features.csv`\n"
            "- **ML Engineer** — trains 2 models, produces `model.pkl`, "
            "`evaluation_report.md`, `model_card.md`"
        )

    st.subheader("🔗 CrewAI Flow")
    st.markdown(
        "`Crew 1` → **validation gate** (contract vs. data match) → `Crew 2` → "
        "**final validation** (all artifacts present). Fails gracefully with a "
        "`FlowValidationError` if any gate fails."
    )

    st.subheader("🎯 Business Question")
    st.info(
        "Can we predict, at booking time, whether a hotel reservation will be "
        "canceled — to help revenue management with overbooking strategy?"
    )

# ---------------------------------------------------------------- Run Flow
with tab_flow:
    st.subheader("Run the full CrewAI Flow")
    st.warning(
        "This triggers real LLM calls (Anthropic Claude) for both crews. "
        "It can take a few minutes and will overwrite files in `outputs/`."
    )
    if st.button("▶️ Run Flow now", type="primary"):
        with st.spinner("Running Crew 1 → validation → Crew 2 ... this takes a few minutes"):
            env = os.environ.copy()
            proc = subprocess.run(
                [sys.executable, "-m", "flow.main_flow"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                env=env,
            )
        if proc.returncode == 0:
            st.success("✅ Flow completed successfully!")
        else:
            st.error("❌ Flow failed — see log below")
        st.code(proc.stdout[-4000:] + "\n" + proc.stderr[-2000:], language="text")

    log_path = os.path.join(OUTPUTS_DIR, "flow_run_log.json")
    if os.path.exists(log_path):
        st.subheader("Last Flow Run Log")
        with open(log_path, encoding="utf-8") as f:
            log = json.load(f)
        st.json(log)

# ---------------------------------------------------------------- EDA
with tab_eda:
    insights_path = os.path.join(OUTPUTS_DIR, "insights.md")
    eda_path = os.path.join(OUTPUTS_DIR, "eda_report.html")
    contract_path = os.path.join(OUTPUTS_DIR, "dataset_contract.json")

    if os.path.exists(insights_path):
        st.subheader("💡 Business Insights")
        with open(insights_path, encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("Run the Flow first to generate insights.")

    if os.path.exists(CLEAN_PATH):
        st.subheader("📈 Live Charts (from clean_data.csv)")
        df = pd.read_csv(CLEAN_PATH)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Cancellation rate by hotel**")
            st.bar_chart(df.groupby("hotel")["is_canceled"].mean())
        with c2:
            st.markdown("**Average Daily Rate by hotel**")
            st.bar_chart(df.groupby("hotel")["adr"].mean())

        st.markdown("**Top 10 guest countries**")
        st.bar_chart(df["country"].value_counts().head(10))

    if os.path.exists(eda_path):
        with st.expander("📄 Full EDA HTML report"):
            with open(eda_path, encoding="utf-8") as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)

    if os.path.exists(contract_path):
        with st.expander("📜 Dataset Contract (JSON)"):
            with open(contract_path, encoding="utf-8") as f:
                st.json(json.load(f))

# ---------------------------------------------------------------- Model
with tab_model:
    eval_path = os.path.join(OUTPUTS_DIR, "evaluation_report.md")
    card_path = os.path.join(OUTPUTS_DIR, "model_card.md")
    model_path = os.path.join(OUTPUTS_DIR, "model.pkl")

    if os.path.exists(eval_path):
        st.subheader("📊 Evaluation Report")
        with open(eval_path, encoding="utf-8") as f:
            st.markdown(f.read())

    if os.path.exists(card_path):
        st.subheader("🗂️ Model Card")
        with open(card_path, encoding="utf-8") as f:
            st.markdown(f.read())

    if os.path.exists(model_path):
        st.subheader("🔮 Try a Prediction")
        st.caption("Enter booking details to get a live cancellation probability.")
        model = joblib.load(model_path)

        c1, c2, c3 = st.columns(3)
        with c1:
            hotel = st.selectbox("Hotel", ["City Hotel", "Resort Hotel"])
            lead_time = st.number_input("Lead time (days)", 0, 700, 30)
            adr = st.number_input("ADR (€)", 0.0, 1000.0, 100.0)
        with c2:
            market_segment = st.selectbox(
                "Market segment",
                ["Online TA", "Offline TA/TO", "Direct", "Corporate", "Groups", "Complementary", "Aviation"],
            )
            deposit_type = st.selectbox("Deposit type", ["No Deposit", "Non Refund", "Refundable"])
            customer_type = st.selectbox(
                "Customer type", ["Transient", "Transient-Party", "Contract", "Group"]
            )
        with c3:
            total_special_requests = st.slider("Special requests", 0, 5, 0)
            previous_cancellations = st.slider("Previous cancellations", 0, 10, 0)
            is_repeated_guest = st.checkbox("Repeated guest")

        if st.button("Predict cancellation probability"):
            row = pd.DataFrame([{
                "hotel": hotel,
                "arrival_date_month": "July",
                "meal": "BB",
                "country": "PRT",
                "market_segment": market_segment,
                "distribution_channel": "TA/TO",
                "reserved_room_type": "A",
                "deposit_type": deposit_type,
                "customer_type": customer_type,
                "lead_time": lead_time,
                "arrival_date_year": 2017,
                "arrival_date_week_number": 27,
                "arrival_date_day_of_month": 15,
                "stays_in_weekend_nights": 1,
                "stays_in_week_nights": 2,
                "adults": 2,
                "children": 0,
                "babies": 0,
                "is_repeated_guest": int(is_repeated_guest),
                "previous_cancellations": previous_cancellations,
                "previous_bookings_not_canceled": 0,
                "booking_changes": 0,
                "days_in_waiting_list": 0,
                "adr": adr,
                "required_car_parking_spaces": 0,
                "total_of_special_requests": total_special_requests,
            }])
            proba = model.predict_proba(row)[0][1]
            st.metric("Cancellation probability", f"{proba*100:.1f}%")
            if proba > 0.5:
                st.error("⚠️ High cancellation risk — consider overbooking buffer / stricter deposit policy")
            else:
                st.success("✅ Low cancellation risk")
    else:
        st.info("Run the Flow first to train a model.")
