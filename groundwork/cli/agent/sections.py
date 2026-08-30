"""The 8-section interview, expressed as data so the harness has no hardcoded
per-section logic. Each section is one or more probe points; each probe point
runs the same follow-up ladder (see harness.py) independently.

Sections are collapsed here to their control-flow-relevant shape. The exact
wording of questions is close to Phase 0 but not sacred — it's a prompt, not
a contract; the ladder and the flags are the contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProbePoint:
    key: str
    question: str
    concrete_bar: str
    rephrase_hint: str


@dataclass
class Section:
    key: str
    criterion: str
    probes: list[ProbePoint]
    immediate_warning: bool = False  # Funder Fit only


SECTIONS: list[Section] = [
    Section(
        key="funder_fit",
        criterion="FIT",
        immediate_warning=True,
        probes=[
            ProbePoint(
                key="priority_match",
                question="Which of this funder's stated priorities does your project advance, and how?",
                concrete_bar="names a specific stated priority plus the mechanism connecting the project to it",
                rephrase_hint="Pick one priority from the funder's own language and say the one sentence that connects it to what you're doing.",
            )
        ],
    ),
    Section(
        key="problem_evidence",
        criterion="SIGNIFICANCE",
        probes=[
            ProbePoint(
                key="problem_scale",
                question="What specific problem, for whom, and why does it need action now?",
                concrete_bar="population + a number/data source/direct experience + a named barrier",
                rephrase_hint="Do you have a number, a data source, or specific experience showing the scale? What's actually stopping people from getting help now?",
            )
        ],
    ),
    Section(
        key="objectives",
        criterion="OBJECTIVES",
        probes=[
            ProbePoint(
                key="one_sentence",
                question="One sentence: what will you accomplish, for whom, doing what, producing what result?",
                concrete_bar="specific, bounded, explainable after one read",
                rephrase_hint="If I could remember only one sentence about this project, what should it be?",
            )
        ],
    ),
    Section(
        key="approach_feasibility",
        criterion="APPROACH",
        probes=[
            ProbePoint(
                key="causal_logic",
                question="Walk me through the activities in order, and why you believe they'll produce that outcome.",
                concrete_bar="sequenced activities plus explicit causal reasoning",
                rephrase_hint="Why do you expect that specific activity to lead to that specific result?",
            ),
            ProbePoint(
                key="risk_mitigation",
                question="What's most likely to go wrong, and what would you do about it?",
                concrete_bar="one named risk with a stated mitigation or fallback",
                rephrase_hint="If your best-case assumption doesn't hold, what's the fallback?",
            ),
        ],
    ),
    Section(
        key="team_capacity",
        criterion="TEAM",
        probes=[
            ProbePoint(
                key="track_record",
                question="Who's doing this, and what's their actual track record?",
                concrete_bar="named roles plus a real number (sites, years, dollars managed, retention)",
                rephrase_hint="Can you give me a number that backs that up?",
            )
        ],
    ),
    Section(
        key="measurable_outcomes",
        criterion="OUTCOMES",
        probes=[
            ProbePoint(
                key="indicator",
                question="What's the main indicator you'll track?",
                concrete_bar="a named, trackable indicator",
                rephrase_hint="What number would tell you this worked?",
            ),
            ProbePoint(
                key="baseline",
                question="What's the current baseline for that?",
                concrete_bar="a starting value or explicit 'no baseline yet'",
                rephrase_hint="Even a rough starting point helps — what's it at today?",
            ),
            ProbePoint(
                key="target_timing",
                question="What's your target, and by when?",
                concrete_bar="a target value with a date or period",
                rephrase_hint="By the end of the grant period, what number are you aiming for?",
            ),
            ProbePoint(
                key="data_source",
                question="How will you measure it — what's the data source?",
                concrete_bar="a named data source or measurement method",
                rephrase_hint="What record or system will you pull that number from?",
            ),
        ],
    ),
    Section(
        key="budget_congruence",
        criterion="BUDGET",
        probes=[
            ProbePoint(
                key="allocation",
                question="Roughly how does the ask map to the activities you described?",
                concrete_bar="allocation explainable against the narrative",
                rephrase_hint="Which line item covers the activity you called central?",
            )
        ],
    ),
    Section(
        key="impact",
        criterion="IMPACT",
        probes=[
            ProbePoint(
                key="pathway",
                question="If this succeeds, what changes beyond the outcome — and what's the path from here to there?",
                concrete_bar="names a mechanism or next step, not just a magnitude claim",
                rephrase_hint="What's the next step after this grant period that gets you from the outcome to that bigger change?",
            )
        ],
    ),
]
