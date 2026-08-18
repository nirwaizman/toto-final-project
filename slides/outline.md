# Toto — Industry-Simulated AI Product Workflow
- Final Project — AI Development & Collaboration Course
- Nir Waizman
- CrewAI · Python · GitHub · Streamlit

---
## Business Background
- A hospitality group operates multiple hotels (inspired by real operations: Hotel Eilat, Theodor Tel Aviv)
- Management needs two perspectives on booking data:
  - Descriptive: "What has happened in our bookings?"
  - Predictive: "Which bookings are likely to cancel?"
- This project simulates a real AI product team solving both, using two collaborating CrewAI crews

---
## The Concept — "Toto"
- Inspired by Toto: a real, daily-operating personal AI assistant
- Same core idea — an AI agent that ingests data, reasons, acts, and reports
- Reimagined here as a two-crew hospitality analytics pipeline
- Proves the multi-agent collaboration pattern on a real, high-value business problem

---
## High-Level Architecture
- Crew 1 — Data Analyst Crew (4 agents)
- CrewAI Flow — automated handoff + validation gate
- Crew 2 — Data Scientist Crew (3 agents)
- Streamlit UI — visualizes everything end to end

---
## Crew 1 — Data Analyst
- Data Ingestion Specialist — profiles the raw dataset
- Data Cleaning Engineer — produces clean_data.csv
- EDA Analyst — produces eda_report.html
- Insights & Contract Writer — produces insights.md + dataset_contract.json

---
## Dataset
- Hotel Booking Demand — 119,390 real hotel reservations
- Resort Hotel + City Hotel, Portugal, 2015-2017
- Target: is_canceled (37.3% cancellation rate)
- Chosen for direct relevance to hospitality revenue management

---
## Key Business Insights
- City Hotel cancels 41.8% of bookings vs 28.1% for Resort Hotel
- OTAs control ~68% of all bookings — high commission exposure
- Portugal dominates demand (47,784 bookings) — concentration risk
- Average lead time: 104.6 days — enables proactive revenue management
- 37.3% overall cancellation rate justifies a predictive model

---
## CrewAI Flow — The Handoff
- Automates Crew 1 -> Crew 2 handoff
- Validation gate: confirms dataset_contract.json matches clean_data.csv
- Confirms all required columns exist before modeling starts
- Fails gracefully with FlowValidationError if any check fails
- Full run log saved to outputs/flow_run_log.json

---
## Crew 2 — Data Scientist
- Contract Validator — confirms data matches the contract, flags leakage risk
- Feature Engineer — produces leakage-free features.csv
- ML Engineer — trains 2 models, compares them, saves model.pkl

---
## Model Results
- Compared RandomForest vs GradientBoosting
- Temporal train/test split (train 2015-2016, test 2017) — no data leakage
- GradientBoosting selected — ROC-AUC 0.876, F1 0.702
- reservation_status excluded as a leakage column — critical modeling discipline

---
## Model Card — Responsible AI
- Purpose: support overbooking/deposit decisions, not deny individual guests
- Limitations: Portugal-only data, ~63% recall, no pandemic-era patterns
- Ethical considerations: country feature flagged as a bias risk
- Predictions are advisory — human review required before policy action

---
## Streamlit Application
- Overview tab — explains the architecture
- Run Flow tab — triggers the full CrewAI Flow live
- EDA & Insights tab — interactive charts + business insights
- Model Results tab — live cancellation probability predictor

---
## Tech Stack & Reproducibility
- CrewAI, Python 3.12, GitHub, Streamlit
- Pandas, Scikit-Learn for data + modeling
- All artifacts version-controlled and reproducible from data/raw
- Deterministic tools (not LLM hallucination) for every data operation

---
## Conclusion
- A working, reproducible two-crew CrewAI Flow
- Solves a real hospitality business problem
- Same architecture pattern used by Toto in daily operations
- Repository: github.com/nirwaizman/toto-final-project
