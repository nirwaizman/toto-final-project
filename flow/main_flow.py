"""CrewAI Flow — orchestrates the Data Analyst Crew -> Data Scientist Crew handoff.

Requirements satisfied:
  1. Automates handoff from Crew 1 -> Crew 2.
  2. Validation gates: confirms dataset_contract.json matches clean_data.csv,
     and confirms all required features/outputs exist before proceeding.
  3. Reproducibility: deterministic steps, clear logging, artifacts saved in repo.
  4. Fails gracefully when validations break (raises a clear FlowValidationError
     and halts before wasting an LLM call on broken input).
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone

from crewai.flow.flow import Flow, listen, start

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crew_analyst.crew import run as run_analyst_crew
from crew_scientist.crew import run as run_scientist_crew

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("toto-flow")

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean", "clean_data.csv")
CONTRACT_PATH = os.path.join(OUTPUTS_DIR, "dataset_contract.json")
LOG_PATH = os.path.join(OUTPUTS_DIR, "flow_run_log.json")

CREW1_REQUIRED_OUTPUTS = [
    os.path.join(BASE_DIR, "data", "clean", "clean_data.csv"),
    os.path.join(OUTPUTS_DIR, "eda_report.html"),
    os.path.join(OUTPUTS_DIR, "insights.md"),
    os.path.join(OUTPUTS_DIR, "dataset_contract.json"),
]
CREW2_REQUIRED_OUTPUTS = [
    os.path.join(OUTPUTS_DIR, "features.csv"),
    os.path.join(OUTPUTS_DIR, "model.pkl"),
    os.path.join(OUTPUTS_DIR, "evaluation_report.md"),
    os.path.join(OUTPUTS_DIR, "model_card.md"),
]


class FlowValidationError(Exception):
    """Raised when a validation gate fails — the Flow halts instead of proceeding."""


def _log_event(events: list[dict], stage: str, status: str, detail: str = "") -> None:
    entry = {
        "stage": stage,
        "status": status,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    events.append(entry)
    logger.info("[%s] %s — %s", stage, status, detail)


def _write_run_log(events: list[dict]) -> None:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump({"run_at": datetime.now(timezone.utc).isoformat(), "events": events}, f, indent=2)


class TotoFlow(Flow):
    """Two-crew CrewAI Flow: Data Analyst -> validation gate -> Data Scientist."""

    def __init__(self):
        super().__init__()
        self.events: list[dict] = []

    @start()
    def run_analyst_crew(self):
        _log_event(self.events, "crew1_analyst", "started")
        try:
            result = run_analyst_crew()
        except Exception as exc:  # fail gracefully
            _log_event(self.events, "crew1_analyst", "failed", str(exc))
            _write_run_log(self.events)
            raise FlowValidationError(f"Crew 1 (Data Analyst) failed: {exc}") from exc
        _log_event(self.events, "crew1_analyst", "completed")
        return result

    @listen(run_analyst_crew)
    def validate_handoff(self, _analyst_result):
        """Validation gate: confirm Crew 1's outputs exist AND the dataset
        contract matches the clean dataset before letting Crew 2 start."""
        missing = [p for p in CREW1_REQUIRED_OUTPUTS if not os.path.exists(p)]
        if missing:
            _log_event(
                self.events, "validation_gate", "failed",
                f"Missing Crew 1 outputs: {missing}",
            )
            _write_run_log(self.events)
            raise FlowValidationError(
                f"Validation gate failed — Crew 1 did not produce required outputs: {missing}"
            )

        with open(CONTRACT_PATH, encoding="utf-8") as f:
            contract = json.load(f)
        import pandas as pd

        df = pd.read_csv(CLEAN_PATH)
        target_col = contract.get("target_column", "is_canceled")
        if target_col not in df.columns:
            _log_event(
                self.events, "validation_gate", "failed",
                f"Target column '{target_col}' declared in contract but missing from clean_data.csv",
            )
            _write_run_log(self.events)
            raise FlowValidationError(
                f"Validation gate failed — contract target column '{target_col}' not in clean_data.csv"
            )

        declared_cols = {c["name"] for c in contract.get("feature_columns", [])}
        missing_cols = [c for c in declared_cols if c not in df.columns]
        if missing_cols:
            _log_event(
                self.events, "validation_gate", "failed",
                f"Contract declares columns not present in data: {missing_cols}",
            )
            _write_run_log(self.events)
            raise FlowValidationError(
                f"Validation gate failed — contract/data mismatch: {missing_cols}"
            )

        _log_event(
            self.events, "validation_gate", "passed",
            f"dataset_contract.json matches clean_data.csv ({len(df)} rows, "
            f"{len(declared_cols)} declared feature columns all present)",
        )
        return True

    @listen(validate_handoff)
    def run_scientist_crew(self, _validation_ok):
        _log_event(self.events, "crew2_scientist", "started")
        try:
            result = run_scientist_crew()
        except Exception as exc:
            _log_event(self.events, "crew2_scientist", "failed", str(exc))
            _write_run_log(self.events)
            raise FlowValidationError(f"Crew 2 (Data Scientist) failed: {exc}") from exc
        _log_event(self.events, "crew2_scientist", "completed")
        return result

    @listen(run_scientist_crew)
    def final_validation(self, _scientist_result):
        """Final gate: confirm all Crew 2 required artifacts exist before
        declaring the Flow successful."""
        missing = [p for p in CREW2_REQUIRED_OUTPUTS if not os.path.exists(p)]
        if missing:
            _log_event(
                self.events, "final_validation", "failed",
                f"Missing Crew 2 outputs: {missing}",
            )
            _write_run_log(self.events)
            raise FlowValidationError(
                f"Final validation failed — Crew 2 did not produce required outputs: {missing}"
            )

        _log_event(self.events, "final_validation", "passed", "All required artifacts present")
        _write_run_log(self.events)
        logger.info("✅ Flow completed successfully. All artifacts saved to outputs/")
        return {"status": "success", "events": self.events}


def run_flow():
    flow = TotoFlow()
    return flow.kickoff()


if __name__ == "__main__":
    result = run_flow()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
