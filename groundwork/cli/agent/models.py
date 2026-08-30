"""Structured records for the Grant Narrative Interview Agent.

Everything downstream (consistency checks, resolution, draft assembly) reads
and writes these records instead of raw model text. That's the whole
architectural bet: state lives in typed data, not in a transcript.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

_NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def _numbers_in_text(text: str) -> set[float]:
    found = set()
    for match in _NUMBER_RE.findall(text):
        try:
            found.add(float(match.replace(",", "")))
        except ValueError:
            continue
    return found


class Tier(str, Enum):
    DOCUMENT_VERIFIED = "document-verified"
    PUBLIC_RECORD_CHECKED = "public-record-checked"
    ATTRIBUTED = "attributed"
    UNATTRIBUTED = "unattributed"


class ResolutionType(str, Enum):
    CORRECTED = "corrected"
    EXPLAINED = "explained"
    ACCEPTED = "accepted"
    OVERRIDDEN = "overridden"


@dataclass
class Fact:
    id: str
    section: str
    criterion: str
    probe_key: str
    summary: str
    verbatim_quote: str
    structured_fields: dict = field(default_factory=dict)
    tier: Tier = Tier.UNATTRIBUTED
    source: str = "interview"  # interview | budget_csv | public_record

    def numeric_values(self) -> set[float]:
        """Every number this fact is allowed to license in a drafted sentence —
        from structured_fields AND from the fact's own summary/verbatim_quote
        text. Reading structured_fields alone was too strict: a classifier can
        legitimately capture only one field (e.g. metric_name/value) while the
        summary it wrote still contains other real numbers from what the
        leader said (e.g. "5 years" in "delivered at 12 sites over 5 years").
        Those numbers are already part of the approved fact, not something the
        draft model is introducing — excluding them caused false-positive
        fallbacks to plain template phrasing."""
        values: set[float] = set()
        for v in self.structured_fields.values():
            if isinstance(v, (int, float)):
                values.add(float(v))
        values |= _numbers_in_text(self.summary)
        values |= _numbers_in_text(self.verbatim_quote)
        return values


@dataclass
class Gap:
    id: str
    section: str
    criterion: str
    probe_key: str
    reason: str
    missing_fields: list[str] = field(default_factory=list)
    severity: str = "gap"  # "gap" | "warning" (Funder Fit uses warning)


@dataclass
class Inconsistency:
    id: str
    criterion: str
    description: str
    related_fact_ids: list[str] = field(default_factory=list)
    kind: str = "internal"  # internal | budget | public_record


@dataclass
class Resolution:
    flag_id: str
    resolution: ResolutionType
    updated_value: str | None = None
    note: str | None = None
    target_fact_id: str | None = None
    """Which fact this resolution applies to, when a flag involves more than
    one (an internal-consistency inconsistency has two). Defaults to the
    most recently recorded related fact if not given — but the leader
    should always be able to say "the OTHER one was wrong," not just accept
    a silent default."""


@dataclass
class InterviewState:
    facts: dict = field(default_factory=dict)          # id -> Fact
    gaps: dict = field(default_factory=dict)            # id -> Gap
    inconsistencies: dict = field(default_factory=dict)  # id -> Inconsistency
    resolutions: dict = field(default_factory=dict)     # flag_id -> Resolution
    _counter: int = 0

    def next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}-{self._counter}"

    def open_flags(self) -> list:
        """Every gap/inconsistency that hasn't been through the Resolution Pass yet."""
        flags = list(self.gaps.values()) + list(self.inconsistencies.values())
        return [f for f in flags if f.id not in self.resolutions]
