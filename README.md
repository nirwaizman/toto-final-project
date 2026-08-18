# 🐾 Toto — Industry-Simulated AI Product Workflow

**Final Project — AI Development & Collaboration Course**
**Author:** Nir Waizman

---

## 🎯 What this is

A two-crew **CrewAI** pipeline that simulates how a real AI product team turns
raw hotel booking data into a deployable cancellation-prediction model —
inspired by *Toto*, a real personal AI assistant the author operates daily.

- **Crew 1 — Data Analyst** (4 agents): ingest → clean → EDA → insights + dataset contract
- **CrewAI Flow**: automated handoff with validation gates, fails gracefully
- **Crew 2 — Data Scientist** (3 agents): validate → feature engineering → train/compare models
- **Streamlit app**: interactive UI to run the flow and explore results live

## 📊 Results

- Dataset: [Hotel Booking Demand](data/DATASET_INFO.md) — 119,390 real reservations (Portugal, 2015-2017)
- Best model: **GradientBoostingClassifier** — ROC-AUC **0.875**, F1 **0.693** (temporal split: train 2015-16, test 2017)
- Full comparison: [`outputs/evaluation_report.md`](outputs/evaluation_report.md)
- Model card (purpose, limitations, ethics): [`outputs/model_card.md`](outputs/model_card.md)
- Business insights: [`outputs/insights.md`](outputs/insights.md)

## 📁 Key Files

| File | What it is |
|---|---|
| [`slides/toto-final-project-he.pptx`](slides/toto-final-project-he.pptx) | 16-slide presentation (Hebrew, RTL) — built by `slides/build_deck_he.py` |
| [`slides/toto-final-project.pptx`](slides/toto-final-project.pptx) | 15-slide presentation (English) |
| [`demo/toto-demo.mp4`](demo/toto-demo.mp4) | 40s demo video of the running app |
| [`outputs/flow_run_log.json`](outputs/flow_run_log.json) | Log of the last full Flow run (both gates passed) |
| [`flow/main_flow.py`](flow/main_flow.py) | CrewAI Flow orchestration |
| [`crew_analyst/`](crew_analyst/) | Crew 1 — Data Analyst agents & tools |
| [`crew_scientist/`](crew_scientist/) | Crew 2 — Data Scientist agents & tools |
| [`app/streamlit_app.py`](app/streamlit_app.py) | Streamlit UI |
| [`outputs/`](outputs/) | All generated artifacts (contract, EDA, model, reports) |

## 🚀 Run it yourself

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "ANTHROPIC_API_KEY=your_key_here" > .env
echo "MODEL=claude-sonnet-4-6" >> .env

# Run the full CrewAI Flow (Crew 1 -> validation -> Crew 2)
python3 -m flow.main_flow

# Or launch the interactive UI
streamlit run app/streamlit_app.py
```

## 🏗️ Architecture

```
data/raw/hotel_bookings.csv
        │
        ▼
┌───────────────────────┐
│  Crew 1 — Data Analyst │  4 agents: Ingestion → Cleaning → EDA → Insights/Contract
└───────────┬───────────┘
            │  outputs: clean_data.csv, eda_report.html,
            │           insights.md, dataset_contract.json
            ▼
   ✅ Validation Gate (CrewAI Flow)
   confirms contract matches cleaned data
            │
            ▼
┌─────────────────────────┐
│ Crew 2 — Data Scientist  │  3 agents: Validate → Features → Train/Evaluate
└───────────┬──────────────┘
            │  outputs: features.csv, model.pkl,
            │           evaluation_report.md, model_card.md
            ▼
   ✅ Final Validation Gate
            │
            ▼
      Streamlit App (live predictions)
```

## 🛠️ Tech Stack

CrewAI · Python 3.12 · Anthropic Claude · Pandas · Scikit-Learn · Streamlit · GitHub

## ⚠️ Data Leakage Discipline

`reservation_status` and `reservation_status_date` are recorded **after** the
booking outcome is known. Both crews explicitly exclude them from model
features — flagged in the dataset contract, the model card, and enforced in
code (`crew_scientist/tools.py`). Also excluded: `assigned_room_type`
(post-booking), `agent`/`company` IDs, and `arrival_date_year` (used only as
the temporal split key, so the test year is never a training feature).

## ✅ Validation Gate — what it actually checks

Before Crew 2 starts, `flow/main_flow.py` verifies that `dataset_contract.json`
(written by Crew 1's `write_dataset_contract` tool) matches `clean_data.csv`:

1. all four Crew 1 artifacts exist;
2. the target column exists in the data;
3. the contract declares a **non-empty** `feature_columns` list and every one is present in the CSV;
4. no leakage column is declared as a feature;
5. the contract's `row_count` equals the actual row count.

Any failure raises `FlowValidationError`, writes `outputs/flow_run_log.json`, and
Crew 2 never runs. Negative cases (empty contract, ghost column, leakage column
declared as feature) were tested and all halt the Flow.

## 🔁 Reproducibility

Re-running the deterministic tools on `data/raw/hotel_bookings.csv` reproduces
the exact metrics in `outputs/evaluation_report.md` (fixed `random_state=42`,
fixed temporal split). The full Flow (with LLM calls) was run end-to-end and its
log is committed in `outputs/flow_run_log.json`.
