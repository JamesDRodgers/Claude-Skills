"""CLI entry point. Ties together everything built in Phases 1-3: the
interview harness, the real Anthropic clients, the ProPublica client, the
Resolution Pass, and draft assembly. Run with:

    export ANTHROPIC_API_KEY=sk-ant-...
    python main.py

Auto-saves progress after every recorded fact, gap, and resolution to
SESSION_PATH, and offers to resume from it on the next run. Every persona in
the three-persona pressure test independently flagged the lack of this as
the top-priority gap -- an interruption mid-interview shouldn't erase
everything a leader already said.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

SESSION_PATH = ".grant_session.json"

ONBOARDING = """
Before we start: I'll structure this interview and draft only from what you tell me —
I won't invent claims. The more specific you are (numbers, names, dates), the stronger
the draft. I'll flag what's missing or inconsistent, but you make the final call on
every claim — including overruling a flag if you're confident I'm wrong. And check your
funder's policy on AI-assisted proposals before you submit this.
""".strip()


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. Export it first:\n  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    import requests

    from agent.consistency import run_document_checks
    from agent.documents import ProPublicaClient, parse_budget_csv
    from agent.draft import TABLE_DISCLAIMER, assemble_draft, build_criteria_table
    from agent.harness import InterviewHarness
    from agent.live_clients import AnthropicDraftClient, AnthropicEvalClient, AnthropicMetricMatcher
    from agent.models import ResolutionType
    from agent.persistence import load_session, save_session
    from agent.sections import SECTIONS

    print(ONBOARDING)
    print()

    filing = None
    budget_lines = None
    resumed = False

    if os.path.exists(SESSION_PATH):
        choice = input("A previous session was found. Resume it? (y/n): ").strip().lower()
        if choice == "y":
            payload = load_session(SESSION_PATH)
            harness = InterviewHarness(client=AnthropicEvalClient(), sections=SECTIONS,
                                        metric_matcher=AnthropicMetricMatcher())
            harness.state = payload["state"]
            harness.section_idx = payload["section_idx"]
            harness.probe_idx = payload["probe_idx"]
            harness.attempts = payload["attempts"]
            if payload.get("funder_fit_question"):
                SECTIONS[0].probes[0].question = payload["funder_fit_question"]
            budget_lines = payload.get("budget_lines")
            filing = payload.get("filing")
            resumed = True
            print("Resuming where you left off.\n")
        else:
            os.remove(SESSION_PATH)

    if not resumed:
        rfp_text = input("Paste the funder's stated priorities, or leave blank to skip: ").strip()
        if rfp_text:
            funder_fit_probe = SECTIONS[0].probes[0]
            funder_fit_probe.question = (
                f"The funder's stated priorities: \"{rfp_text}\"\n" + funder_fit_probe.question
            )

        ein = input("Organization EIN (for the public-record check), or leave blank to skip: ").strip()
        if ein:
            try:
                filing = ProPublicaClient().get_most_recent_filing(ein)
                if filing is None:
                    print("  No filing found for that EIN — the public-record check will be skipped (neutral, not a flag).")
                else:
                    print(f"  Found a filing for tax year {filing.tax_year}.")
            except ValueError as e:
                print(f"  {e} — skipping the public-record check for this run.")
            except requests.RequestException as e:
                print(f"  Couldn't reach the public-record service ({e}) — this check is unavailable this run, not neutral.")

        budget_path = input("Path to a budget CSV (category,amount), or leave blank to skip: ").strip()
        if budget_path:
            with open(budget_path) as f:
                budget_lines = parse_budget_csv(f.read())
            print(f"  Parsed {len(budget_lines)} budget line(s).")

        harness = InterviewHarness(client=AnthropicEvalClient(), metric_matcher=AnthropicMetricMatcher())

    def checkpoint() -> None:
        save_session(
            SESSION_PATH, harness,
            funder_fit_question=SECTIONS[0].probes[0].question,
            budget_lines=budget_lines, filing=filing,
        )

    print("\n--- Interview ---\n")
    result = harness.step()
    while result.role != "done":
        if result.role in ("question", "rephrase"):
            reply = input(f"[tutor] {result.text}\n[you] ")
            result = harness.step(reply)
        else:  # recorded / gap / warning already advanced the harness internally;
            # step() with no reply just returns the next probe's question, or "done"
            label = {"recorded": "[recorded]", "gap": "[gap]", "warning": "[WARNING]"}[result.role]
            print(f"{label} {result.text}\n")
            checkpoint()
            result = harness.step()
    print(result.text)

    state = harness.state
    run_document_checks(state, budget_lines, filing)
    checkpoint()

    open_flags = state.open_flags()
    if open_flags:
        print(f"\n--- Resolution Pass ({len(open_flags)} item(s) flagged) ---\n")
        for flag in open_flags:
            kind = "gap" if flag.id.startswith("gap") else "inconsistency"
            reason = getattr(flag, "reason", None) or getattr(flag, "description", "")
            print(f"[{kind}] {reason}")
            choice = input("  (c)orrect / (e)xplain / (a)ccept / (o)verride: ").strip().lower()
            if choice == "c":
                value = input("  Corrected value: ")
                apply_resolution_choice(state, flag.id, ResolutionType.CORRECTED, updated_value=value)
            elif choice == "e":
                note = input("  Explanation: ")
                apply_resolution_choice(state, flag.id, ResolutionType.EXPLAINED, note=note)
            elif choice == "o":
                apply_resolution_choice(state, flag.id, ResolutionType.OVERRIDDEN)
            else:
                apply_resolution_choice(state, flag.id, ResolutionType.ACCEPTED)
            checkpoint()

    print("\n--- Draft ---\n")
    section_drafts = assemble_draft(state, AnthropicDraftClient(), [s.key for s in SECTIONS])
    for sd in section_drafts:
        print(f"[{sd.section}]{'  (fell back to plain phrasing)' if sd.used_fallback else ''}")
        print(sd.text or "(no facts recorded for this section)")
        print()

    print("--- Criteria-Evidence Table ---")
    print(TABLE_DISCLAIMER)
    for row in build_criteria_table(state):
        print(f"  [{row['criterion']}] {row['summary']} — tier: {row['tier']}, status: {row['status']}")

    if os.path.exists(SESSION_PATH):
        os.remove(SESSION_PATH)  # session complete -- don't offer to "resume" a finished draft next time


def apply_resolution_choice(state, flag_id, resolution_type, updated_value=None, note=None):
    from agent.models import Resolution
    from agent.resolution import apply_resolution

    apply_resolution(state, Resolution(flag_id=flag_id, resolution=resolution_type, updated_value=updated_value, note=note))


if __name__ == "__main__":
    main()
