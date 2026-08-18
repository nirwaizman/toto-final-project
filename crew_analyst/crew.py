"""Crew 1 — Data Analyst Crew.

4 agents (exceeds the "at least 3" requirement):
  1. Data Ingestion Specialist — loads & profiles the raw dataset
  2. Data Cleaning Engineer — cleans it, saves clean_data.csv
  3. EDA Analyst — runs exploratory analysis, saves eda_report.html
  4. Insights & Contract Writer — writes insights.md + dataset_contract.json
"""
from __future__ import annotations

import os

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from dotenv import load_dotenv

from crew_analyst.tools import (
    clean_dataset,
    load_and_profile_dataset,
    run_eda,
    write_dataset_contract,
    write_insights,
)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
INSIGHTS_PATH = os.path.join(OUTPUTS_DIR, "insights.md")


def build_llm() -> LLM:
    model = os.environ.get("MODEL", "claude-sonnet-4-6")
    return LLM(model=f"anthropic/{model}", temperature=0.3)


def build_analyst_crew() -> Crew:
    llm = build_llm()

    ingestion_agent = Agent(
        role="Data Ingestion Specialist",
        goal="Load the raw hotel booking dataset and produce an accurate profile "
             "of its structure, size, and data quality issues.",
        backstory="You are meticulous about understanding data before touching it. "
                   "You always profile a dataset first: shape, types, missing values.",
        tools=[load_and_profile_dataset],
        llm=llm,
        verbose=True,
    )

    cleaning_agent = Agent(
        role="Data Cleaning Engineer",
        goal="Clean the raw dataset into a reliable, well-documented clean_data.csv "
             "based on the ingestion profile.",
        backstory="You fix missing values, drop bad rows, and document every "
                   "transformation so downstream teams can trust the data.",
        tools=[clean_dataset],
        llm=llm,
        verbose=True,
    )

    eda_agent = Agent(
        role="EDA Analyst",
        goal="Explore the cleaned dataset and surface the business-relevant "
             "patterns: cancellation rates, pricing, guest origin, booking channels.",
        backstory="You are a hospitality data analyst who turns raw statistics "
                   "into a clear picture of what is happening in the business.",
        tools=[run_eda],
        llm=llm,
        verbose=True,
    )

    insights_agent = Agent(
        role="Insights & Contract Writer",
        goal="Summarize the EDA findings into business insights (insights.md) and "
             "define the formal dataset_contract.json for the Data Scientist crew.",
        backstory="You are the bridge between analysis and engineering — you write "
                   "clear insights for management and precise contracts for engineers.",
        tools=[write_insights, write_dataset_contract],
        llm=llm,
        verbose=True,
    )

    ingest_task = Task(
        description="Load data/raw/hotel_bookings.csv using the load_and_profile_dataset "
                     "tool. Report the shape, columns with missing values, and any data "
                     "quality concerns you notice.",
        expected_output="A short report of the dataset profile: shape, dtypes summary, "
                          "and which columns have missing values and why that matters.",
        agent=ingestion_agent,
    )

    clean_task = Task(
        description="Using the clean_dataset tool, clean the raw dataset. Then report "
                     "exactly how many rows were dropped and why, referencing the "
                     "ingestion profile's findings.",
        expected_output="A summary of the cleaning steps applied and before/after row counts.",
        agent=cleaning_agent,
        context=[ingest_task],
    )

    eda_task = Task(
        description="Using the run_eda tool on the cleaned dataset, compute cancellation "
                     "rates by hotel, average daily rate, top guest countries, and market "
                     "segment mix. Report the key numbers.",
        expected_output="The key EDA metrics: overall and per-hotel cancellation rate, "
                          "ADR by hotel, top countries, market segment mix.",
        agent=eda_agent,
        context=[clean_task],
    )

    insights_task = Task(
        description=(
            "Based on the EDA metrics, write a Markdown report with 5-8 bullet-point "
            "business insights (e.g. which hotel has higher cancellations and why that "
            "matters for overbooking policy, which segments/countries drive revenue), "
            "using the REAL numbers from the EDA. End the report with a short "
            "'Data Leakage Warning' section that explicitly flags reservation_status and "
            "reservation_status_date as columns that must NOT be used as model features. "
            "Save it by calling the write_insights tool with the full Markdown as `content`. "
            "Then call the write_dataset_contract tool to produce outputs/dataset_contract.json "
            "for the Data Scientist crew."
        ),
        expected_output=(
            "Confirmation that insights.md was written with business insights, and that "
            "dataset_contract.json was generated with the leakage warning included."
        ),
        agent=insights_agent,
        context=[eda_task],
    )

    return Crew(
        agents=[ingestion_agent, cleaning_agent, eda_agent, insights_agent],
        tasks=[ingest_task, clean_task, eda_task, insights_task],
        process=Process.sequential,
        verbose=True,
    )


def run() -> str:
    """Runs Crew 1 end to end. Also writes insights.md as a safety net in
    case the agent skipped the write_insights tool (should not happen)."""
    crew = build_analyst_crew()
    result = crew.kickoff()

    # Safety net: ensure insights.md exists even if the agent didn't call a
    # dedicated write tool for it (it writes prose, not JSON via a tool).
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    if not os.path.exists(INSIGHTS_PATH):
        with open(INSIGHTS_PATH, "w", encoding="utf-8") as f:
            f.write("# Insights — Hotel Booking Demand\n\n")
            f.write(str(result))

    return str(result)


if __name__ == "__main__":
    print(run())
