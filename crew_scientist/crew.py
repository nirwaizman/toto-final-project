"""Crew 2 — Data Scientist Crew.

3 agents (meets the "at least 3" requirement):
  1. Contract Validator — confirms clean_data.csv matches dataset_contract.json
  2. Feature Engineer — builds features.csv (leakage-safe)
  3. ML Engineer — trains/compares 2 models, saves model.pkl, evaluation_report.md, model_card.md
"""
from __future__ import annotations

import os

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from dotenv import load_dotenv

from crew_scientist.tools import (
    engineer_features,
    train_and_evaluate_models,
    validate_contract,
    write_model_card,
)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def build_llm() -> LLM:
    model = os.environ.get("MODEL", "claude-sonnet-4-6")
    return LLM(model=f"anthropic/{model}", temperature=0.3)


def build_scientist_crew() -> Crew:
    llm = build_llm()

    validator_agent = Agent(
        role="Contract Validator",
        goal="Confirm the cleaned dataset from Crew 1 matches the dataset_contract.json "
             "before any modeling begins, and explicitly flag leakage risks.",
        backstory="You are the gatekeeper between the analyst and modeling teams. You "
                   "never let modeling start on unvalidated or leaking data.",
        tools=[validate_contract],
        llm=llm,
        verbose=True,
    )

    feature_agent = Agent(
        role="Feature Engineer",
        goal="Build a clean, leakage-free feature table (features.csv) from the "
             "validated dataset, strictly following the dataset contract.",
        backstory="You translate raw cleaned data into model-ready features, always "
                   "respecting the contract's leakage warnings.",
        tools=[engineer_features],
        llm=llm,
        verbose=True,
    )

    ml_agent = Agent(
        role="ML Engineer",
        goal="Train and compare at least 2 model variations to predict booking "
             "cancellations, select the best one by ROC-AUC, and document results.",
        backstory="You are a pragmatic ML engineer who always compares multiple "
                   "models and documents metrics transparently before shipping.",
        tools=[train_and_evaluate_models, write_model_card],
        llm=llm,
        verbose=True,
    )

    validate_task = Task(
        description="Call validate_contract to confirm clean_data.csv matches "
                     "dataset_contract.json. Report whether validation passed and "
                     "list any leakage columns confirmed present (that must stay excluded).",
        expected_output="A pass/fail validation report including confirmed leakage columns.",
        agent=validator_agent,
    )

    feature_task = Task(
        description="Call engineer_features to build outputs/features.csv from the "
                     "validated clean dataset, excluding all leakage columns per the contract.",
        expected_output="Confirmation of features.csv creation with row/column counts "
                          "and the list of excluded leakage columns.",
        agent=feature_agent,
        context=[validate_task],
    )

    model_task = Task(
        description=(
            "Call train_and_evaluate_models to train and compare RandomForest and "
            "GradientBoosting models on outputs/features.csv, using a temporal train/test "
            "split. Report the comparison metrics and which model was selected. Then call "
            "write_model_card to produce outputs/model_card.md documenting purpose, "
            "training data, metrics, limitations, and ethical considerations."
        ),
        expected_output=(
            "The model comparison table with metrics, the selected best model, and "
            "confirmation that model.pkl, evaluation_report.md, and model_card.md were saved."
        ),
        agent=ml_agent,
        context=[feature_task],
    )

    return Crew(
        agents=[validator_agent, feature_agent, ml_agent],
        tasks=[validate_task, feature_task, model_task],
        process=Process.sequential,
        verbose=True,
    )


def run() -> str:
    crew = build_scientist_crew()
    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    print(run())
