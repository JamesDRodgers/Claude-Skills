"""The interview loop. Follow-up ladder per probe point:
  miss 1 -> ask again
  miss 2 -> harness forces a rephrase + example (regardless of the model)
  miss 3 -> harness forces a gap (regardless of the model)
Never blocks. The model can also give up early (leader says "I don't know") or
record a fact at any attempt; the harness's floor is a backstop, not the only path.
"""

from __future__ import annotations

from dataclasses import dataclass

from .consistency import check_internal_consistency, check_semantic_consistency
from .models import Fact, Gap, InterviewState, Tier
from .sections import SECTIONS, ProbePoint, Section

MAX_ATTEMPTS_BEFORE_GAP = 3
REPHRASE_AT_ATTEMPT = 2


@dataclass
class TurnResult:
    role: str  # "question" | "rephrase" | "recorded" | "gap" | "warning" | "done"
    text: str
    fact: Fact | None = None
    gap: Gap | None = None


class InterviewHarness:
    def __init__(self, client, state: InterviewState | None = None, sections: list[Section] | None = None,
                 metric_matcher=None):
        self.client = client
        self.state = state or InterviewState()
        self.sections = sections or SECTIONS
        self.metric_matcher = metric_matcher  # None (default) = deterministic-only, no live model dependency
        self.section_idx = 0
        self.probe_idx = 0
        self.attempts = 0

    def _current(self) -> tuple[Section, ProbePoint] | None:
        if self.section_idx >= len(self.sections):
            return None
        section = self.sections[self.section_idx]
        if self.probe_idx >= len(section.probes):
            return None
        return section, section.probes[self.probe_idx]

    def _advance(self) -> None:
        section = self.sections[self.section_idx]
        self.probe_idx += 1
        self.attempts = 0
        if self.probe_idx >= len(section.probes):
            self.probe_idx = 0
            self.section_idx += 1

    def step(self, leader_reply: str | None = None) -> TurnResult:
        current = self._current()
        if current is None:
            return TurnResult(role="done", text="Interview complete.")
        section, probe = current

        if leader_reply is None:
            return TurnResult(role="question", text=probe.question)

        known_metrics = {
            f.structured_fields["metric_name"]
            for f in self.state.facts.values()
            if f.structured_fields.get("metric_name")
        }
        action = self.client.evaluate(section=section, probe=probe, reply=leader_reply, known_metrics=known_metrics)

        if action["type"] == "fact":
            fact = Fact(
                id=self.state.next_id("fact"),
                section=section.key,
                criterion=section.criterion,
                probe_key=probe.key,
                summary=action["summary"],
                verbatim_quote=action.get("verbatim_quote", leader_reply),
                structured_fields=action.get("structured_fields", {}),
                tier=Tier.ATTRIBUTED if action.get("structured_fields", {}).get("source_name") else Tier.UNATTRIBUTED,
                source="interview",
            )
            if section.key == "measurable_outcomes" and probe.key in ("baseline", "target_timing"):
                # Deterministic, code-level role tag -- not left to the model. Without
                # this, the "reuse an existing metric_name for the same quantity"
                # instruction (added to catch synonym contradictions) correctly makes
                # a baseline and its target share one metric_name, and
                # check_internal_consistency then flags them as contradictory --
                # a false positive on the intended, correctly-answered shape of this
                # section's own core question, every time. Charlene test, Defect 2.
                fact.structured_fields.setdefault("metric_role", "baseline" if probe.key == "baseline" else "target")

            if fact.structured_fields.get("metric_name") is None:
                # The model didn't populate metric_name — without a fallback, this
                # fact would be entirely invisible to check_internal_consistency
                # even though numeric_values() (fed by summary/verbatim text) can
                # already see numbers in it. Best-effort, not precise: probe_key
                # scoping only groups facts asked by the exact same question, so
                # this catches "forgot to tag it" but not "used a different word
                # for the same thing across two different probes" — that's the
                # synonym problem, and no code-level fix reaches it.
                numbers = fact.numeric_values()
                if numbers:
                    fact.structured_fields.setdefault("metric_name", f"{section.key}:{probe.key}")
                    fact.structured_fields.setdefault("value", next(iter(numbers)))

            self.state.facts[fact.id] = fact
            inconsistency = check_internal_consistency(fact, self.state)
            if inconsistency is None and self.metric_matcher is not None:
                inconsistency = check_semantic_consistency(fact, self.state, self.metric_matcher)
            if inconsistency:
                self.state.inconsistencies[inconsistency.id] = inconsistency
            self._advance()
            return TurnResult(role="recorded", text=fact.summary, fact=fact)

        if action["type"] == "flag_gap":
            return self._log_gap(section, probe, action.get("reason", "Leader indicated no further detail available."))

        # action["type"] == "miss"
        self.attempts += 1
        if self.attempts >= MAX_ATTEMPTS_BEFORE_GAP:
            return self._log_gap(section, probe, "No sufficiently specific answer after three attempts.")
        if self.attempts == REPHRASE_AT_ATTEMPT:
            return TurnResult(role="rephrase", text=probe.rephrase_hint)
        # First miss: lead with the model's own acknowledgment of what fell short,
        # when the client supplies one, instead of silently repeating the same
        # question -- silence here reads as failure, not guidance, especially for
        # a first-time user. Scripted/fake clients that don't supply "note" fall
        # back to the original plain re-ask, so existing tests are unaffected.
        note = action.get("note")
        text = f"{note}\n\n{probe.question}" if note else probe.question
        return TurnResult(role="question", text=text)

    def _log_gap(self, section: Section, probe: ProbePoint, reason: str) -> TurnResult:
        gap = Gap(
            id=self.state.next_id("gap"),
            section=section.key,
            criterion=section.criterion,
            probe_key=probe.key,
            reason=reason,
            severity="warning" if section.immediate_warning else "gap",
        )
        self.state.gaps[gap.id] = gap
        self._advance()
        role = "warning" if section.immediate_warning else "gap"
        return TurnResult(role=role, text=reason, gap=gap)
