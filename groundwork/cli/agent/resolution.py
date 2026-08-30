"""The Resolution Pass. Every flag from the interview surfaces once, at the
end, and the leader — never the model — decides what happens to it. This
module only applies a resolution the caller supplies; it does not itself
decide anything. That's deliberate: the AI proposes, the leader disposes.
"""

from __future__ import annotations

from .models import Fact, InterviewState, Resolution, ResolutionType, Tier


def apply_resolution(state: InterviewState, resolution: Resolution) -> None:
    state.resolutions[resolution.flag_id] = resolution

    gap = state.gaps.get(resolution.flag_id)
    if gap is not None:
        _apply_to_gap(state, gap, resolution)
        return

    fact = _related_fact(state, resolution.flag_id, resolution.target_fact_id)
    if fact is None:
        return
    _apply_to_fact(fact, resolution)


def _apply_to_gap(state: InterviewState, gap, resolution: Resolution) -> None:
    """A gap has no existing fact to correct — 'corrected' here means the
    leader is answering now, for the first time. That has to create a new
    fact, or the answer silently vanishes: no placeholder (a resolution now
    exists) and no fact (nothing was ever recorded). That's a worse failure
    than fabrication — it's the tool dropping real information."""
    if resolution.resolution == ResolutionType.CORRECTED and resolution.updated_value is not None:
        new_fact = Fact(
            id=state.next_id("fact"),
            section=gap.section,
            criterion=gap.criterion,
            probe_key=gap.probe_key,
            summary=resolution.updated_value,
            verbatim_quote=resolution.updated_value,
            structured_fields={},
            tier=Tier.ATTRIBUTED,
            source="resolution_pass",
        )
        state.facts[new_fact.id] = new_fact
    elif resolution.resolution == ResolutionType.EXPLAINED and resolution.note:
        gap.reason = f"{gap.reason} (leader note: {resolution.note})"
    # ACCEPTED, or OVERRIDDEN (meaningless for a gap — there's no original
    # claim to keep): the placeholder stands exactly as originally logged.


def _apply_to_fact(fact: Fact, resolution: Resolution) -> None:
    if resolution.resolution == ResolutionType.CORRECTED and resolution.updated_value is not None:
        # updated_value arrives as raw text from the CLI. Everywhere else
        # structured_fields["value"] is numeric, and downstream comparisons
        # (consistency checks, numeric_values) assume that -- so coerce when
        # the correction is a number ("118", "$45,000", "38%"), keep the
        # string only when it genuinely isn't one.
        raw = resolution.updated_value.strip()
        try:
            fact.structured_fields["value"] = float(raw.replace(",", "").lstrip("$").rstrip("%"))
        except ValueError:
            fact.structured_fields["value"] = resolution.updated_value
        fact.summary = resolution.updated_value
        fact.tier = Tier.ATTRIBUTED
    elif resolution.resolution == ResolutionType.EXPLAINED:
        fact.structured_fields["resolution_note"] = resolution.note
    elif resolution.resolution == ResolutionType.OVERRIDDEN:
        fact.structured_fields["overridden"] = True
        fact.structured_fields["override_note"] = "leader confirmed despite flag"
    # ACCEPTED: nothing to change on the fact.


def _related_fact(state: InterviewState, flag_id: str, target_fact_id: str | None = None):
    inc = state.inconsistencies.get(flag_id)
    if not inc or not inc.related_fact_ids:
        return None
    if target_fact_id is not None:
        if target_fact_id not in inc.related_fact_ids:
            raise ValueError(f"{target_fact_id} is not one of the facts involved in flag {flag_id}")
        return state.facts.get(target_fact_id)
    # No target named — default to the most recently recorded fact, but this
    # is a fallback for convenience, not a judgment about which one is
    # actually wrong. Callers resolving a two-fact inconsistency should
    # always pass target_fact_id explicitly.
    return state.facts.get(inc.related_fact_ids[-1])


def unresolved_summary(state: InterviewState) -> list[str]:
    """What's left to resolve — used to drive the Resolution Pass prompt."""
    return [f.id for f in state.open_flags()]
