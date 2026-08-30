"""Real Anthropic clients, implementing the same interfaces the scripted
doubles in tests.py fake. harness.py and draft.py never change — only what
gets injected into them does."""

from __future__ import annotations

import json

import anthropic

MODEL = "claude-sonnet-5"

RECORD_FACT_TOOL = {
    "name": "record_fact",
    "description": "Call this when the leader's reply meets the stated concrete bar.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string", "description": "One sentence capturing the fact."},
            "verbatim_quote": {"type": "string", "description": "The leader's own wording, unedited."},
            "structured_fields": {
                "type": "object",
                "description": (
                    "Include metric_name and value (a number) if this is a quantifiable claim — "
                    "required for the internal consistency check to work. Include source_name if "
                    "the leader named where the number comes from. Include activity_name if the "
                    "leader names a specific program activity or line item (used to cross-check "
                    "against an uploaded budget). Use metric_name containing the word 'revenue' "
                    "for any claim about the organization's overall revenue (used to cross-check "
                    "against the organization's public tax filing, when available)."
                ),
            },
        },
        "required": ["summary", "verbatim_quote"],
    },
}

FLAG_GAP_TOOL = {
    "name": "flag_gap",
    "description": "Call this only if the leader explicitly gives up — says they don't know, have no data, or asks to move on.",
    "input_schema": {
        "type": "object",
        "properties": {"reason": {"type": "string"}},
        "required": ["reason"],
    },
}


class AnthropicEvalClient:
    """Implements .evaluate(section, probe, reply) -> dict, same contract
    ScriptedEvalClient fakes in tests.py."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def evaluate(self, *, section, probe, reply: str, known_metrics: set[str] | None = None) -> dict:
        reuse_instruction = ""
        if known_metrics:
            metrics_list = ", ".join(sorted(known_metrics))
            reuse_instruction = (
                f"\n\nMetric names already used elsewhere in this interview: {metrics_list}.\n"
                "If this reply is about one of those same quantities — even worded differently — "
                "reuse that EXACT metric_name string rather than inventing a new one. This is what "
                "lets the system catch it later if two answers about the same thing disagree. Only "
                "use a new metric_name if this is genuinely a different quantity."
            )
        system = (
            f"You are evaluating a nonprofit leader's answer during a structured grant-narrative "
            f"interview. Question asked: \"{probe.question}\"\n"
            f"What counts as concrete enough: {probe.concrete_bar}.\n\n"
            "If the reply meets that bar, call record_fact.\n"
            "If the reply does not meet the bar, do not call any tool — just respond with a short "
            "acknowledgment (no more than one sentence).\n"
            "If the leader explicitly gives up — says they don't know, have no data, or asks to "
            "move on — call flag_gap instead."
            f"{reuse_instruction}"
        )
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=system,
            tools=[RECORD_FACT_TOOL, FLAG_GAP_TOOL],
            messages=[{"role": "user", "content": reply}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "record_fact":
                inp = block.input
                # "required" in the tool schema is a hint to the model, not a
                # server-enforced guarantee without strict:true (not set here) --
                # a live model can still omit a field. Falling back to the leader's
                # raw reply for summary (same as verbatim_quote already did) means
                # a missing field degrades gracefully instead of crashing the CLI.
                return {
                    "type": "fact",
                    "summary": inp.get("summary", reply),
                    "verbatim_quote": inp.get("verbatim_quote", reply),
                    "structured_fields": inp.get("structured_fields", {}),
                }
            if block.type == "tool_use" and block.name == "flag_gap":
                return {"type": "flag_gap", "reason": block.input.get("reason", "Leader indicated no further detail.")}

        # No tool call = a miss. The system prompt already asks the model for a short
        # acknowledgment in this case -- previously that text was generated and then
        # discarded. Capturing it means attempt 1 can tell the leader WHY it fell short
        # instead of silently repeating the same question (see harness.py).
        note = "".join(block.text for block in response.content if block.type == "text").strip() or None
        return {"type": "miss", "note": note}


FIND_SAME_METRIC_TOOL = {
    "name": "same_metric",
    "description": "Call this if one candidate refers to the exact same underlying quantity as the new claim.",
    "input_schema": {
        "type": "object",
        "properties": {"metric_name": {"type": "string", "description": "The candidate's metric_name, copied exactly."}},
        "required": ["metric_name"],
    },
}


class AnthropicMetricMatcher:
    """Implements .find_same_metric(new_metric, new_value, candidates) -> str | None.
    A real judgment call, not a string comparison — this is exactly the kind
    of task worth spending a model call on: telling "162 enrolled" and "148
    completed" apart from "youth served" and "young people served" requires
    actually understanding what each label means, not just how it's spelled."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def find_same_metric(self, new_metric: str, new_value: float, candidates: list[tuple[str, float]]) -> str | None:
        if not candidates:
            return None
        candidates_text = "\n".join(f'- metric_name="{m}", value={v}' for m, v in candidates)
        system = (
            "You are checking whether a new claim from a grant-narrative interview refers to the "
            "SAME underlying quantity as any already-recorded claim below — not just a similar-sounding "
            "number. Different framings of the same thing should match (e.g. 'youth_served' and "
            "'young_people_served' if both mean the same count of the same population). Genuinely "
            "different quantities must NOT match even if they're related (e.g. 'students enrolled' and "
            "'students who completed' are different things, not the same metric under different names).\n\n"
            f"New claim: metric_name=\"{new_metric}\", value={new_value}\n\n"
            f"Already-recorded claims:\n{candidates_text}\n\n"
            "If exactly one candidate is clearly the same underlying quantity, call same_metric with its "
            "metric_name copied exactly. If none are, or you're not confident, don't call any tool."
        )
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=200,
            system=system,
            tools=[FIND_SAME_METRIC_TOOL],
            messages=[{"role": "user", "content": "Evaluate the claim above."}],
        )
        for block in response.content:
            if block.type == "tool_use" and block.name == "same_metric":
                return block.input.get("metric_name")
        return None


class AnthropicDraftClient:
    """Implements .transform(facts) -> str, same contract FakeDraftClient
    fakes in tests.py. Sees ONLY the resolved facts for one section — never
    the interview transcript, never facts from other sections."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def transform(self, facts: list) -> str:
        system = (
            "Transform the following resolved facts into 1-3 natural sentences of grant-narrative "
            "prose. Rules, strictly:\n"
            "- Do not add any number, date, or named entity that isn't in the facts below.\n"
            "- Do not alter or combine facts into a claim not directly stated.\n"
            "- Do not infer causation between facts unless it's already in a fact's summary.\n"
            "- Do not soften a precise number into vague language (never turn 118 into 'most').\n"
            "- Output only the prose. No preamble, no meta-commentary."
        )
        fact_lines = []
        for f in facts:
            line = f"- {f.summary}"
            if f.structured_fields:
                line += f" (fields: {json.dumps(f.structured_fields)})"
            fact_lines.append(line)

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=system,
            messages=[{"role": "user", "content": "\n".join(fact_lines)}],
        )
        return "".join(block.text for block in response.content if block.type == "text")
