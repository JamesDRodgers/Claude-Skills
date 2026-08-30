"""Session save/resume. Every persona in the last pressure test converged on
this being the highest-priority gap: an 8-section interview held entirely in
memory, with nothing written until the very end, means one interruption --
a phone call, a closed laptop, a crashed terminal -- throws away everything
a leader already said. A scaffold that only works in one unbroken sitting
isn't scaffolding; it's a timed exam.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from .documents import Filing
from .models import Fact, Gap, Inconsistency, InterviewState, Resolution, ResolutionType, Tier


def _state_to_dict(state: InterviewState) -> dict:
    return {
        "facts": {k: dataclasses.asdict(v) for k, v in state.facts.items()},
        "gaps": {k: dataclasses.asdict(v) for k, v in state.gaps.items()},
        "inconsistencies": {k: dataclasses.asdict(v) for k, v in state.inconsistencies.items()},
        "resolutions": {k: dataclasses.asdict(v) for k, v in state.resolutions.items()},
        "_counter": state._counter,
    }


def _state_from_dict(d: dict) -> InterviewState:
    state = InterviewState()
    state._counter = d.get("_counter", 0)
    for k, v in d.get("facts", {}).items():
        v = dict(v)
        v["tier"] = Tier(v["tier"])
        state.facts[k] = Fact(**v)
    for k, v in d.get("gaps", {}).items():
        state.gaps[k] = Gap(**v)
    for k, v in d.get("inconsistencies", {}).items():
        state.inconsistencies[k] = Inconsistency(**v)
    for k, v in d.get("resolutions", {}).items():
        v = dict(v)
        v["resolution"] = ResolutionType(v["resolution"])
        state.resolutions[k] = Resolution(**v)
    return state


def save_session(
    path: str,
    harness,
    *,
    funder_fit_question: str | None = None,
    budget_lines: dict[str, float] | None = None,
    filing: Filing | None = None,
) -> None:
    payload = {
        "state": _state_to_dict(harness.state),
        "section_idx": harness.section_idx,
        "probe_idx": harness.probe_idx,
        "attempts": harness.attempts,
        "funder_fit_question": funder_fit_question,
        "budget_lines": budget_lines,
        "filing": dataclasses.asdict(filing) if filing else None,
    }
    Path(path).write_text(json.dumps(payload, indent=2))


def load_session(path: str) -> dict:
    """Returns the raw payload; main.py applies it to a freshly constructed
    harness rather than this module owning harness construction, since the
    harness needs a real client/sections/metric_matcher wired in by the caller."""
    payload = json.loads(Path(path).read_text())
    payload["state"] = _state_from_dict(payload["state"])
    if payload.get("filing"):
        payload["filing"] = Filing(**payload["filing"])
    return payload
