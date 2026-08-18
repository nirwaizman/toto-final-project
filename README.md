# 🐾 Toto — Industry-Simulated AI Product Workflow

**Final Project — AI Development & Collaboration Course**

## Project Concept

This project simulates how a real AI product team collaborates using **CrewAI**.
It is inspired by "Toto" — a real, daily-operating personal AI assistant — reimagined
as a two-crew hospitality analytics pipeline:

- **Crew 1 — Data Analyst Crew**: ingests, cleans, and explores a hotel/Airbnb dataset,
  producing descriptive insights and a dataset contract.
- **Crew 2 — Data Scientist Crew**: consumes the contract, engineers features, trains
  a predictive model, and evaluates it.
- **CrewAI Flow**: automates the handoff between the two crews with validation gates.

## Status

🚧 Work in progress — built step by step.

## Structure

```
final-project/
├── crew_analyst/       # Crew 1 — Data Analyst
├── crew_scientist/      # Crew 2 — Data Scientist
├── flow/                 # CrewAI Flow orchestration
├── data/                 # raw + clean datasets
├── outputs/               # generated artifacts
├── app/                   # Streamlit UI
├── slides/                # presentation
└── demo/                  # demo video
```

## Tech Stack

- CrewAI, Python
- Pandas, Scikit-Learn, Matplotlib/Seaborn
- Streamlit
- GitHub

## Author

Nir Waizman
