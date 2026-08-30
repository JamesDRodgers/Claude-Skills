"""Validates the back half of main.py's flow (document checks, Resolution
Pass, real draft assembly, table printing) directly, sidestepping the live
interview classifier's turn-count variability which makes scripted stdin
fragile against an adaptive multi-turn conversation."""

from dotenv import load_dotenv
load_dotenv()

from agent.consistency import run_document_checks
from agent.documents import Filing
from agent.draft import TABLE_DISCLAIMER, assemble_draft, build_criteria_table
from agent.live_clients import AnthropicDraftClient
from agent.models import Fact, Gap, InterviewState, Resolution, ResolutionType, Tier
from agent.resolution import apply_resolution

state = InterviewState()

state.facts["fact-1"] = Fact(
    id="fact-1", section="team_capacity", criterion="TEAM", probe_key="track_record",
    summary="delivered at 12 sites over 5 years with 85% retention", verbatim_quote="12 sites, 5 years, 85% retention",
    structured_fields={"metric_name": "sites", "value": 12, "source_name": "program records"}, tier=Tier.ATTRIBUTED,
)
state.facts["fact-2"] = Fact(
    id="fact-2", section="budget_congruence", criterion="BUDGET", probe_key="allocation",
    summary="community engagement work is central to the project", verbatim_quote="community engagement is central to this",
    structured_fields={"activity_name": "Community Engagement"}, tier=Tier.ATTRIBUTED,
)
state.facts["fact-3"] = Fact(
    id="fact-3", section="problem_evidence", criterion="SIGNIFICANCE", probe_key="problem_scale",
    summary="annual revenue is $2,000,000", verbatim_quote="our annual revenue is about $2 million",
    structured_fields={"metric_name": "revenue", "value": 2_000_000}, tier=Tier.ATTRIBUTED,
)
state.gaps["gap-1"] = Gap(
    id="gap-1", section="impact", criterion="IMPACT", probe_key="pathway",
    reason="No sufficiently specific answer after three attempts.",
)

budget_lines = {"Personnel": 40000, "Supplies": 5000}  # no "Community Engagement" line -> should flag
filing = Filing(ein="142007220", tax_year=2023, total_revenue=57_970_562)  # real filing from earlier -> stated $2M should flag divergence

run_document_checks(state, budget_lines, filing)
print(f"Inconsistencies found by document checks: {len(state.inconsistencies)}")
for inc in state.inconsistencies.values():
    print(f"  [{inc.kind}] {inc.description}")

print("\n--- Resolution Pass (scripted) ---")
for flag in state.open_flags():
    kind = "gap" if flag.id.startswith("gap") else "inconsistency"
    reason = getattr(flag, "reason", None) or getattr(flag, "description", "")
    print(f"[{kind}] {reason}")
    if kind == "gap":
        apply_resolution(state, Resolution(flag_id=flag.id, resolution=ResolutionType.EXPLAINED,
                                            note="not yet defined at this stage of planning"))
        print("  -> explained")
    else:
        apply_resolution(state, Resolution(flag_id=flag.id, resolution=ResolutionType.OVERRIDDEN))
        print("  -> overridden (leader keeps original figures)")

print("\n--- Draft (real Anthropic draft client) ---")
section_drafts = assemble_draft(state, AnthropicDraftClient(), ["team_capacity", "budget_congruence", "problem_evidence", "impact"])
for sd in section_drafts:
    print(f"[{sd.section}]{'  (fell back to plain phrasing)' if sd.used_fallback else ''}")
    print(sd.text)
    print()

print("--- Criteria-Evidence Table ---")
print(TABLE_DISCLAIMER)
for row in build_criteria_table(state):
    print(f"  [{row['criterion']}] {row['summary']} — tier: {row['tier']}, status: {row['status']}")
