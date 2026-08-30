# Grant Narrative Interview Agent — Phase 0 Design

## Core guarantee

The AI can flag a concern. Only the leader decides what goes in the final draft.
The tool separates fact generation from language generation: the model never
introduces, alters, combines, or infers a factual claim — but once a fact is
resolved and approved, the model may transform it into readable prose. What the
tool verifies: internal consistency, budget-to-narrative alignment, alignment
with the org's own filed 990, and — at draft time — that every number, date, and
named entity the model writes traces back to a resolved fact record. What it does
NOT verify: whether an outcome or impact claim is true. That limit is stated to
the leader, not implied away.

## Draft assembly (fact generation vs. language generation)

Pure template concatenation risks producing prose too stilted to be useful —
reviewer-friendly writing is one of the ten characteristics an excellent proposal
needs. So the model is allowed to write sentences, but only from a narrow,
checked input, never from open recall of the conversation:

1. Once a section's facts are resolved (post Resolution Pass), the model drafts
   prose using **only the resolved fact records for that section** as input —
   not the transcript, not its own memory of the interview.
2. Instruction is strict: transform wording only. No new numbers, no altered
   values, no combining two approved facts into an unapproved implied claim
   (e.g. inferring causation), no softening a precise number into vague language.
3. **Deterministic post-generation check:** code extracts every number, date, and
   named entity from the drafted text and confirms each one matches a value in
   that section's resolved fact records. Anything that doesn't match is a hard
   fail for that section — not a warning, not a soft pass.
4. **Per-section fallback, never a blocked draft:** a section that fails
   validation falls back to plain structured phrasing built directly from the
   fact records, instead of the model's prose.
5. **Overridden facts are never prose-transformed.** A leader-overruled claim
   (see Resolution Pass) renders exactly as the leader wrote it — the one place
   where even a faithful paraphrase would add risk on top of an already-flagged
   claim.

The criteria-evidence table stays 100% code-generated, no model prose — it's an
audit reference, not a document meant to read well.

## Onboarding (runs once, before Section 1)

Plain-language framing of the AI Fluency framework (Delegation, Description,
Discernment, Diligence), specific to this tool, not generic advice:

> "I'll structure this interview and draft only from what you tell me — I won't
> invent claims. The more specific you are (numbers, names, dates), the stronger
> the draft. I'll flag what's missing or inconsistent, but you make the final
> call on every claim — including overruling a flag if you're confident I'm
> wrong. And check your funder's policy on AI-assisted proposals before you
> submit this."

## Interview sections

Each "concrete" bar is mechanical, not a holistic vibe check: a claim counts as
concrete if it contains a number, a named source, or a named specific example.
Anything else is vague and triggers the follow-up ladder below.

| # | Section | Seed question | Concrete bar | Tag |
|---|---|---|---|---|
| 1 | Funder Fit | If RFP uploaded: "This funder's stated priorities are X/Y/Z — which does your project advance, and how?" Else: "What funder, and what does their call say they're trying to accomplish?" | Names a specific stated priority + the mechanism connecting the project to it | FIT |
| 2 | Problem & Evidence | "What specific problem, for whom, and why does it need action now?" | Population + a number/data source/direct experience + a named barrier | SIGNIFICANCE |
| 3 | Objectives | "One sentence: what will you accomplish, for whom, doing what, producing what result?" | Specific, bounded, explainable after one read | OBJECTIVES |
| 4 | Approach & Feasibility | "Walk me through the activities in order, and why you believe they'll produce that outcome. What's most likely to go wrong?" | Sequenced activities + causal reasoning + one named risk with mitigation | APPROACH |
| 5 | Team & Capacity | "Who's doing this, and what's their actual track record?" | Named roles + a real number (sites, years, dollars managed, retention) | TEAM |
| 6 | Measurable Outcomes | Asked incrementally, one field per turn (see below) | Indicator + data source at minimum; missing fields logged individually | OUTCOMES |
| 7 | Budget Congruence | If CSV uploaded: "You allocated $X to [category] — does that match what you called central?" Else: "Roughly how does the ask map to these activities?" | Allocation is explainable against the narrative | BUDGET |
| 8 | Impact / So What | "If this succeeds, what changes beyond the outcome — and what's the path from here to there?" | Names a mechanism/next step, not just a magnitude claim | IMPACT |

**Section 6 is asked incrementally, not as one compound question** — this was a
deliberate fix, not an oversight: asking for indicator + baseline + target/timing
+ data source in a single free-text answer is a harder extraction task than the
model can be trusted to parse reliably. Four sequential turns instead:
1. "What's the main indicator you'll track?"
2. "What's the current baseline for that?"
3. "What's your target, and by when?"
4. "How will you measure it — what's the data source?"

**Section 1 (Funder Fit) is the one exception to the deferred-resolution rule**
below — a gap here surfaces immediately as a visible warning, not silently
deferred, because misalignment can mean the application gets screened out before
anyone reads the narrative (this is standard practice at some funders, not a
hypothetical).

**Section 7 stays scoped to a plain two-column CSV upload (category, amount)** —
deliberately not arbitrary PDF parsing. Real budgets vary too much in format for
that to be reliable, and getting it wrong (a phantom mismatch) is worse than not
checking at all.

## Follow-up ladder (per specific claim, harness-enforced even if the model forgets)

1. **Miss 1:** ask again, more specifically.
2. **Miss 2:** offer a rephrase + concrete example instead of asking the same way again — this was a deliberate fix for leaders who know the answer but are struggling to compress it, not just leaders with no answer.
3. **Miss 3:** log a gap (`flag_gap`), move on. Never blocks the interview.

## Verification layer

Every fact gets a tier, set automatically by how it was obtained:

| Tier | Meaning |
|---|---|
| `document-verified` | Extracted directly from the uploaded budget CSV |
| `public-record-checked` | Cross-referenced against the org's own filed 990 |
| `attributed` | Leader named a source; nothing checked against it |
| `unattributed` | Bare claim, no source named |

**Three active verification mechanisms, all in v1:**
- **Internal consistency checks** — every new numeric fact is compared against everything already logged in the session; contradictions (130 swimmers in Team, 80 in Outcomes) get flagged. Deterministic, free, zero added interview steps.
- **Budget CSV cross-check** — narrative claims compared against the uploaded budget. Not extra work for the leader; it's a document they already have to produce for the application itself.
- **990 public-record cross-check, scoped narrowly** — EIN requested as an optional pre-step field; pull the most recent filing via ProPublica's Nonprofit Explorer API; compare only aggregate revenue/expense figures against what was stated. Mirrors what reviewers are already told to check (alignment with the prior year's tax return) — not new scope, replication of standard practice. A missing 990 (new/small org) is neutral, never a red flag. Covers financials only — says nothing about outcomes or impact.

**Everywhere:** any numeric claim needs a named source to count as concrete — not verification, but it raises the cost of fabricating and gives a pointer to check.

**What this deliberately does not do:** verify that an outcome or impact claim is true. No engineering fixes that — only attribution and internal consistency apply there, and the tool says so.

## Resolution pass (before the draft is assembled)

Every flag raised during the interview — gaps, internal inconsistencies, budget
mismatches, 990 mismatches — is logged silently in the moment (no mid-section
interruptions) and presented as one bounded review at the end. The leader
resolves each flag with one of four actions:

- **Correct** — updates the fact, re-tiers it.
- **Explain** — logs the explanation; leader chooses whether it appears in the draft or stays as an internal note.
- **Accept** — the `[GAP: ...]` placeholder stands in the draft.
- **Override** — the leader's original claim goes into the draft exactly as stated. The tool never blocks, hedges, or rewrites it. The flag isn't erased — it's preserved as `leader confirmed despite flag` in the criteria-evidence table — but the narrative itself respects the leader's call, full stop.

New tool, used only in this pass: `resolve_flag(flag_id, resolution, updated_value, note)`.

## Assembled outputs

1. **Narrative draft** — per-section prose transformed from resolved facts (see
   Draft Assembly above; validated in code, falls back to structured phrasing on
   failure), with `[GAP: ...]` placeholders for accepted gaps and the leader's
   own unaltered wording for overrides.
2. **Criteria-evidence table** — grouped by tag (FIT, SIGNIFICANCE, OBJECTIVES, APPROACH, TEAM, OUTCOMES, BUDGET, IMPACT), each row showing verification tier and any flag/resolution history. Opens with a one-line disclaimer: *"This shows what's covered, not whether it's convincing."*

## Tool schema

- `record_fact(section, criterion, summary, verbatim_quote, structured_fields)`
- `flag_gap(section, criterion, reason, missing_fields)`
- `flag_inconsistency(criterion, description)`
- `resolve_flag(flag_id, resolution, updated_value, note)` — resolution pass only
