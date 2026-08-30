"""Deterministic checks — no model call. Explicitly a heuristic, not a full
audit: it compares numbers/amounts the harness already knows about, tagged
with the same metric name, and flags disagreement. It does not understand
language, so it stays honest about that limit rather than pretending to."""

from __future__ import annotations

import re

from .models import Fact, Inconsistency, InterviewState

TOLERANCE = 0.02  # 2% — treat trivial rounding as agreement, not a flag


def _normalize_metric(name) -> str:
    """Case/whitespace/punctuation-insensitive comparison key. Fixes the
    formatting-only edge case ('Households Served' vs 'households-served')
    with zero model dependency. Does NOT fix genuine synonyms ('youth_served'
    vs 'young_people_served') — that's a different word, not a different
    format, and no amount of normalization makes those the same string."""
    return re.sub(r"[\s\-_]+", " ", str(name).strip().lower()).strip()


def check_internal_consistency(new_fact: Fact, state: InterviewState) -> Inconsistency | None:
    """Compare a newly recorded fact's numeric fields against every existing
    fact that claims the same metric_name (normalized). Flags disagreement
    beyond rounding tolerance."""
    new_metric = new_fact.structured_fields.get("metric_name")
    new_value = new_fact.structured_fields.get("value")
    if new_metric is None or new_value is None:
        return None

    for existing in state.facts.values():
        if existing.id == new_fact.id:
            continue
        existing_metric = existing.structured_fields.get("metric_name")
        if existing_metric is None:
            continue  # guard: _normalize_metric(None) would stringify to "none" and falsely match another None
        if _normalize_metric(existing_metric) != _normalize_metric(new_metric):
            continue
        existing_value = existing.structured_fields.get("value")
        if existing_value is None:
            continue
        existing_role = existing.structured_fields.get("metric_role")
        new_role = new_fact.structured_fields.get("metric_role")
        if existing_role and new_role and existing_role != new_role:
            continue  # e.g. baseline vs target for the same indicator -- expected to differ, not a contradiction
        if existing_value == 0:
            continue
        if abs(new_value - existing_value) / abs(existing_value) > TOLERANCE:
            return Inconsistency(
                id=state.next_id("inc"),
                criterion=new_fact.criterion,
                description=(
                    f"'{new_metric}' stated as {existing_value} in {existing.section} "
                    f"but {new_value} in {new_fact.section}."
                ),
                related_fact_ids=[existing.id, new_fact.id],
                kind="internal",
            )
    return None


def check_semantic_consistency(new_fact: Fact, state: InterviewState, matcher) -> Inconsistency | None:
    """Second pass, only runs when a matcher is configured (live use — see
    AnthropicMetricMatcher in live_clients.py). Deliberately separate from
    check_internal_consistency, not a replacement for it: the deterministic
    string check stays free and always-on; this one costs a real model call
    and only runs against facts the deterministic pass didn't already match,
    to avoid redundant work.

    The matcher's job is narrow and specific: given a new (metric, value) and
    a list of existing (metric, value) candidates, decide which candidate (if
    any) refers to the SAME underlying quantity — not just a similar-looking
    number. "162 enrolled" and "148 completed" must NOT match each other even
    though they're both about program participation; "youth served" and
    "young people served" SHOULD match. That distinction is exactly the kind
    of judgment call worth spending a model call on, and it's still only a
    proposal — if it finds a match whose values disagree, that becomes a
    flag the leader resolves, same as any other inconsistency. It never
    silently changes anything on its own."""
    new_metric = new_fact.structured_fields.get("metric_name")
    new_value = new_fact.structured_fields.get("value")
    if new_metric is None or new_value is None or matcher is None:
        return None

    candidates = []
    for existing in state.facts.values():
        if existing.id == new_fact.id:
            continue
        existing_metric = existing.structured_fields.get("metric_name")
        existing_value = existing.structured_fields.get("value")
        if existing_metric is None or existing_value is None:
            continue
        if _normalize_metric(existing_metric) == _normalize_metric(new_metric):
            continue  # already covered by the deterministic pass
        candidates.append((existing_metric, existing_value, existing))

    if not candidates:
        return None

    matched_name = matcher.find_same_metric(
        new_metric, new_value, [(m, v) for m, v, _ in candidates]
    )
    if matched_name is None:
        return None

    matched = next((existing for m, v, existing in candidates if m == matched_name), None)
    if matched is None:
        return None  # matcher returned something that wasn't actually offered — ignore rather than guess

    matched_role = matched.structured_fields.get("metric_role")
    new_role = new_fact.structured_fields.get("metric_role")
    if matched_role and new_role and matched_role != new_role:
        # Same guard as the deterministic pass, and it matters just as much here:
        # a baseline and its target ARE the same underlying quantity (so a good
        # matcher SHOULD link them), but they're supposed to differ. Without this,
        # the Charlene Defect-2 false positive comes back through the semantic
        # door whenever the classifier gives the two probes different metric names.
        return None

    existing_value = matched.structured_fields.get("value")
    if existing_value == 0:
        return None
    if abs(new_value - existing_value) / abs(existing_value) <= TOLERANCE:
        return None  # matcher says same quantity, values agree -- no friction, nothing to flag

    return Inconsistency(
        id=state.next_id("inc"),
        criterion=new_fact.criterion,
        description=(
            f"'{matched_name}' ({existing_value}, in {matched.section}) and '{new_metric}' "
            f"({new_value}, in {new_fact.section}) appear to describe the same thing but disagree — "
            f"flagged by semantic match, not an exact metric_name match."
        ),
        related_fact_ids=[matched.id, new_fact.id],
        kind="internal",
    )


def check_budget_alignment(central_activity: str, budget_lines: dict[str, float]) -> Inconsistency | None:
    """budget_lines: {category: amount}. A 'central' activity with no
    matching category, or a near-zero one, is flagged — not proven wrong,
    just worth the leader's attention in the Resolution Pass."""
    match = next((amt for cat, amt in budget_lines.items() if central_activity.lower() in cat.lower()), None)
    if match is None:
        return Inconsistency(
            id="",  # caller assigns via state.next_id so ids stay sequential
            criterion="BUDGET",
            description=f"'{central_activity}' was described as central, but no budget line matches it.",
            kind="budget",
        )
    if match <= 0:
        return Inconsistency(
            id="",
            criterion="BUDGET",
            description=f"'{central_activity}' was described as central, but its budget line is ${match:.2f}.",
            kind="budget",
        )
    return None


def run_document_checks(state: InterviewState, budget_lines: dict[str, float] | None, filing) -> None:
    """Orchestrates the two document-grounded checks against whatever facts
    the interview already recorded. Heuristic on purpose: it looks for
    structured_fields the classifier was asked to populate (activity_name
    for budget matching, a metric_name containing "revenue" for the 990
    check) rather than trying to parse arbitrary prose. Adds any resulting
    Inconsistency straight into state — the Resolution Pass picks it up the
    same as an internally-detected one."""
    for fact in list(state.facts.values()):
        activity = fact.structured_fields.get("activity_name")
        if activity and budget_lines:
            inc = check_budget_alignment(activity, budget_lines)
            if inc:
                inc.id = state.next_id("inc")
                inc.related_fact_ids = [fact.id]
                state.inconsistencies[inc.id] = inc

        metric = fact.structured_fields.get("metric_name", "")
        value = fact.structured_fields.get("value")
        if filing is not None and value is not None and "revenue" in str(metric).lower():
            inc = check_public_record_alignment(float(value), filing.total_revenue)
            if inc:
                inc.id = state.next_id("inc")
                inc.related_fact_ids = [fact.id]
                state.inconsistencies[inc.id] = inc


def check_public_record_alignment(stated_revenue: float, filing_revenue: float | None) -> Inconsistency | None:
    """filing_revenue is None when no 990 was found — that's neutral, not a flag."""
    if filing_revenue is None:
        return None
    if filing_revenue == 0:
        return None
    ratio = stated_revenue / filing_revenue
    if ratio > 3 or ratio < (1 / 3):
        return Inconsistency(
            id="",
            criterion="BUDGET",
            description=(
                f"Stated figure (${stated_revenue:,.0f}) diverges sharply from the "
                f"org's most recent filed 990 (${filing_revenue:,.0f})."
            ),
            kind="public_record",
        )
    return None
