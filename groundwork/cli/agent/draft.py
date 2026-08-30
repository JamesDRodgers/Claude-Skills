"""Draft assembly: fact generation vs. language generation, kept separate.

The model may transform a section's resolved, non-overridden facts into
prose. It is never shown the transcript, only the facts. Every number in
what it writes is checked, in code, against the numbers those facts actually
license. Anything that doesn't match fails the section back to plain
template phrasing instead of ever reaching the leader unchecked.

Overridden facts skip the model entirely and render exactly as the leader
wrote them — the one place a faithful paraphrase would still add risk on
top of an already-flagged claim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Fact, Gap, InterviewState

NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def _numbers_in(text: str) -> set[float]:
    found = set()
    for match in NUMBER_RE.findall(text):
        try:
            found.add(float(match.replace(",", "")))
        except ValueError:
            continue
    return found


def _template_sentence(fact: Fact) -> str:
    return fact.summary.rstrip(".") + "."


@dataclass
class SectionDraft:
    section: str
    text: str
    used_fallback: bool


def _resolved_gaps_for_section(state: InterviewState, section_key: str) -> list[Gap]:
    """Gaps that should still render as [GAP: ...] in the draft: never
    resolved, accepted, explained (reason text already carries the note —
    see resolution.py), or overridden (meaningless for a gap, treated like
    accepted). A *corrected* gap is excluded here on purpose — its content
    now lives in a real Fact record instead, which assemble_section already
    picks up separately, so leaving it in this list would show the same
    information twice."""
    result = []
    for g in state.gaps.values():
        if g.section != section_key:
            continue
        resolution = state.resolutions.get(g.id)
        if resolution is None or resolution.resolution.value != "corrected":
            result.append(g)
    return result


def assemble_section(section_key: str, state: InterviewState, llm_client) -> SectionDraft:
    section_facts = [f for f in state.facts.values() if f.section == section_key]
    clean_facts = [f for f in section_facts if not f.structured_fields.get("overridden")]
    overridden_facts = [f for f in section_facts if f.structured_fields.get("overridden")]
    gaps = _resolved_gaps_for_section(state, section_key)

    used_fallback = False
    if clean_facts:
        allowed_numbers = set()
        for f in clean_facts:
            allowed_numbers |= set(f.numeric_values())

        prose = llm_client.transform(clean_facts)
        drafted_numbers = _numbers_in(prose)
        if drafted_numbers.issubset(allowed_numbers) or not drafted_numbers:
            body = prose
        else:
            used_fallback = True
            body = " ".join(_template_sentence(f) for f in clean_facts)
    else:
        body = ""

    parts = [body] if body else []
    for f in overridden_facts:
        parts.append(f.verbatim_quote)
    for g in gaps:
        parts.append(f"[GAP: {g.reason}]")

    return SectionDraft(section=section_key, text=" ".join(p for p in parts if p), used_fallback=used_fallback)


def assemble_draft(state: InterviewState, llm_client, section_keys: list[str]) -> list[SectionDraft]:
    return [assemble_section(key, state, llm_client) for key in section_keys]


def build_criteria_table(state: InterviewState) -> list[dict]:
    rows = []
    for fact in state.facts.values():
        override = fact.structured_fields.get("overridden", False)
        rows.append(
            {
                "criterion": fact.criterion,
                "section": fact.section,
                "summary": fact.summary,
                "tier": fact.tier.value,
                "status": "confirmed despite flag" if override else "resolved",
            }
        )
    for gap in state.gaps.values():
        resolution = state.resolutions.get(gap.id)
        rows.append(
            {
                "criterion": gap.criterion,
                "section": gap.section,
                "summary": gap.reason,
                "tier": "n/a",
                "status": f"gap ({resolution.resolution.value})" if resolution else "gap (unresolved)",
            }
        )
    for inc in state.inconsistencies.values():
        # Charlene test, Defect 1: this loop was missing entirely -- a resolved
        # inconsistency vanished from the table with no trace, contradicting the
        # table's own stated purpose ("shows what's covered"). related_fact_ids
        # gives a real section context even though Inconsistency itself has none.
        resolution = state.resolutions.get(inc.id)
        related_sections = {state.facts[fid].section for fid in inc.related_fact_ids if fid in state.facts}
        section = "/".join(sorted(related_sections)) if related_sections else inc.kind
        rows.append(
            {
                "criterion": inc.criterion,
                "section": section,
                "summary": inc.description,
                "tier": "n/a",
                "status": f"inconsistency ({resolution.resolution.value})" if resolution else "inconsistency (unresolved)",
            }
        )
    return rows


TABLE_DISCLAIMER = "This shows what's covered, not whether it's convincing."
