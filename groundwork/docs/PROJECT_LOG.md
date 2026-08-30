# Grant Narrative Interview Agent — Project Log

A build log of everything designed, built, tested, broken, and fixed so far.
Written to be the single source of truth for the project's history — useful for
the eventual README, the blog post, and any future session picking this up cold.

---

## 1. Origin and goal

The project began as a search for blog topics for James's site (jamesdrodgers.ai),
pivoted to "let's actually build something and write about it," and settled on a
tool for nonprofit leaders — drawing on James's six years as a congregational
leader and the diocese planning-intelligence GPT on his resume.

**The tool:** an AI agent that interviews a nonprofit leader Socratically about
what actually happened in their program, refuses to invent numbers or outcomes
they didn't state, and assembles a grant-narrative first draft only from what
was said.

**The core architectural bet, held from day one:** guarantees live in code, not
in a prompt asking nicely. The model proposes; the harness enforces.

**The governing principle (sharpened over time):** *The AI may structure,
question, flag, compare, and draft from approved facts. The leader retains
authority over every claim the organization makes.*

**Distribution goal:** give it away — MIT-licensed public repo for technical
users, plus (still unbuilt) a hosted no-setup web version, because the target
user is a small-org ED with no grant writer, no terminal, and no API key.

---

## 2. Architecture (current)

```
main.py                      CLI: onboarding, uploads, interview loop,
                             Resolution Pass, draft + criteria table,
                             session auto-save/resume
agent/
  sections.py                8 interview sections as data (probe points with
                             mechanical concrete-bars + rephrase hints)
  harness.py                 interview state machine: follow-up ladder,
                             fact recording, role tagging, consistency hooks
  models.py                  Fact / Gap / Inconsistency / Resolution /
                             InterviewState; verification tiers
  consistency.py             deterministic checks (internal, budget, 990)
                             + semantic consistency via injectable matcher
  documents.py               budget CSV parser; ProPublica 990 client
  resolution.py              Resolution Pass: correct / explain / accept /
                             override — the leader decides, flags never erased
  draft.py                   fact-vs-language split: model transforms resolved
                             facts into prose; code validates every number
                             traces to a fact; per-section template fallback
  live_clients.py            real Anthropic clients: interview classifier,
                             draft transformer, semantic metric matcher
  persistence.py             session save/resume (checkpoint after every
                             fact, gap, and resolution)
tests.py                     30 deterministic tests, scripted doubles only
smoke_test.py                live classifier smoke test (real API)
smoke_test_metric_matcher.py live semantic-matcher smoke test (real API)
smoke_cli_backhalf.py        live resolution/draft/table smoke test (real API)
PHASE_0_DESIGN.md            the locked design spec
PHASE_3_CHECKLIST.md         the live-wiring checklist
```

**The 8 sections** (grounded in NIH/NSF/NEH/SAMHSA reviewer criteria research):
Funder Fit → Problem & Evidence → Objectives → Approach & Feasibility →
Team & Capacity → Measurable Outcomes (asked as 4 incremental probes) →
Budget Congruence → Impact.

**Follow-up ladder per probe:** miss 1 → re-ask, led by the model's own
one-line reason why the answer fell short; miss 2 → rephrase + example;
miss 3 → log a gap and move on. Never blocks. Funder Fit gaps render as
warnings (funders screen misaligned applications out before review).

**Verification tiers on every fact:** `document-verified`,
`public-record-checked`, `attributed`, `unattributed` — rendered in the
criteria-evidence table so "the leader said it" never looks like "confirmed."

**Resolution Pass:** every flag (gap, internal inconsistency, budget mismatch,
990 divergence) is deferred to one bounded end-of-interview review. Four
resolutions: correct (creates/updates a fact), explain (note attached),
accept (placeholder stands), override (leader's wording goes in verbatim,
untouched by the model; flag preserved as "confirmed despite flag," never
erased).

**Draft assembly (fact generation vs. language generation):** the model may
transform a section's resolved facts into prose but sees ONLY those facts —
never the transcript. Code then extracts every number from the prose and
confirms it traces to a fact; failure hard-falls that section back to plain
template phrasing. Overridden facts skip the model entirely.

---

## 3. Phase history

| Phase | Scope | Status |
|---|---|---|
| 0 | Interview design: sections, concrete bars, ladder, verification layer, Resolution Pass, draft-assembly rules | Done (locked in PHASE_0_DESIGN.md, revised twice by agreement) |
| 1 | Harness build + deterministic tests against scripted doubles | Done |
| 2 | Guardrail proof | Folded into Phase 1's tests |
| 3 | Real clients (Anthropic ×3, ProPublica), CLI, live test run | Done (all 5 checklist items) |
| — | Post-Phase-3 hardening: metric-matching fixes, session persistence, miss-1 coaching, Charlene-test fixes | Done |
| 4 | Repo packaging (MIT, ED-first README) | **Not started** — deliberately deferred until the hosted version exists |
| 5 | Ship + connect to site + blog post | **Not started** |
| — | Hosted no-setup web version (the "very low bar of entry" goal) | **Not started — agreed next major milestone** |

Key design evolutions along the way (each explicitly agreed, not drifted into):
- RFP/funder-priorities input and budget CSV upload added as fact sources.
- 990 public-record check moved from "v2 maybe" to v1 after research showed
  reviewers are literally instructed to check stated figures against the prior
  year's filing.
- Draft assembly loosened from "model never writes sentences containing facts"
  to "model may transform approved facts into prose, code-validated" — a
  quality gain with the guarantee preserved in the validator.
- Resolution Pass added after James's requirement: the writer, not the AI,
  makes the final call on every claim.
- Semantic metric matching added after James pushed back on my claim that the
  synonym problem was "not fixable" — he was right; it's a judgment call an
  LLM can make, wired as a proposal that only ever raises a flag.

---

## 4. Complete defect ledger

Every real bug found so far, in order, with how it was found. The "how found"
column is the story of the project: almost nothing was caught by writing code
carefully; nearly everything was caught by adversarial testing of some kind.

| # | Defect | Found by | Fix |
|---|---|---|---|
| 1 | Boolean-precedence bug in gap filtering let an accepted gap from another section bleed into the wrong draft | Self-review while writing Phase 1 | Rewrote filter as explicit loop |
| 2 | Correcting a Gap silently discarded the leader's answer (no fact created, placeholder gone) | Adversarial probe of the resolution path | Corrected gaps now create a real Fact |
| 3 | Two-fact inconsistency corrections always silently patched the newer fact | Adversarial probe | `target_fact_id` on Resolution; unknown ids raise |
| 4 | Malformed EIN crashed the CLI with a raw traceback | First live CLI run | Caught as `ValueError` with a friendly skip |
| 5 | `numeric_values()` read only `structured_fields`, so grounded prose was falsely rejected → unnecessary template fallback | Live back-half smoke run | Numbers also licensed from summary/verbatim text |
| 6 | Consistency check defeated by case/punctuation-only metric-name differences | 3-persona pressure test → edge-case tests | `_normalize_metric()` |
| 7 | Facts with no `metric_name` invisible to consistency checking | Edge-case tests | Harness derives `section:probe_key` fallback |
| 8 | Synonym metric names defeat the deterministic check entirely | Edge-case tests | Mitigated: `AnthropicMetricMatcher` (live-verified: matches youth_served/young_people_served, correctly refuses enrolled/completed) — flag-only, leader resolves |
| 9 | `_normalize_metric(None)` would stringify to "none" and falsely match another untagged fact | Self-review during fix #6 | Explicit None guard |
| 10 | Live model omitted `summary` from a tool call (schema "required" is a hint, not enforced without strict mode) → CLI crash | Live resume test | Graceful fallback to the leader's raw reply |
| 11 | **Resolved inconsistencies vanished from the criteria-evidence table** (only facts and gaps were iterated) | **Charlene persona test (Critical)** | Table now renders inconsistencies + resolution status |
| 12 | **Baseline vs. target false-positive on every honest Outcomes run** — my own metric-name-reuse fix (#8) made baseline and target share a name; the checker had no concept of role | **Charlene persona test (High)** | Deterministic `metric_role` tag from `probe.key`; role-aware skip in the checker; live-verified against the real classifier |
| 13 | Same false positive reachable through the **semantic** matcher when baseline/target get different names — the role guard only covered the deterministic path | Fresh code review (this session) | Same role guard in `check_semantic_consistency`; test written first, confirmed failing, then fixed |
| 14 | Corrected values stored as raw strings in a numeric field (latent TypeError for any future post-resolution comparison) | Fresh code review (this session) | Coerce to float when the correction parses as a number ($, %, commas handled) |

Also fixed along the way (UX, not defects): silent identical re-ask on miss 1
replaced with the model's one-line reason (the text was already being generated
and thrown away); session auto-save/resume added (checkpoint after every fact,
gap, and resolution; interruption simulated live and recovery verified).

**Known-open items from the Charlene test (deliberately not yet fixed):**
- *Defect C3 (Medium):* the CLI never asks which of two conflicting facts a
  correction/override targets — the `target_fact_id` capability exists in
  `resolution.py` but isn't surfaced in `main.py`'s prompt loop.
- *Defect C4 (High):* the draft grounding validator checks **numbers only**;
  PHASE_0_DESIGN.md promises numbers, dates, AND named entities. Dates and
  entities are currently unguarded in code.
- *Defect C5 (Low):* raw snake_case metric identifiers leak into leader-facing
  flag text.
- *UX:* most honest self-reported facts render as `unattributed`, which a
  skimming reader could misread as "unsupported."

---

## 5. Testing record

**Deterministic suite (`tests.py`): 30/30 passing.** Scripted doubles only —
no network, no model. Covers: the full follow-up ladder; fact recording and
advancement; warning-vs-gap severity; internal/budget/990 consistency checks
(hits, tolerance, neutrality of missing data); CSV parsing; ProPublica client
logic against the real captured response shape; all four resolution types on
both fact-flags and gap-flags; two-fact targeting; grounding validation pass,
fabrication catch, and fallback; override-bypasses-model; table disclosure of
overrides and inconsistencies; baseline/target role handling on both check
paths; save/resume continuation. One test remains deliberately labeled
CONFIRMED GAP: the deterministic layer alone still cannot catch synonyms —
that's the semantic matcher's job, and the label keeps the limit honest.

**Live verification (real API, real tokens):**
- Interview classifier smoke test — including the adversarial fluent-but-empty
  answer, correctly rejected; correctly refused a numbers-present answer that
  missed the actual bar (named roles).
- Draft transformer — grounded prose passes the validator cleanly.
- Semantic matcher — 3/3 judgment cases correct.
- Full CLI runs — interruption + resume verified end to end.
- Baseline/target fix — re-verified against the live classifier post-fix:
  same metric name reused, roles tagged, zero false flags.
- ProPublica — field names verified against a real response (fetched by James
  locally, since this sandbox's egress blocks the domain) and replayed through
  the actual client; correctly picks latest filing *with data* and ignores
  not-yet-extracted filings.

**Pressure tests run on the project itself:**
1. Initial concept pressure test — surfaced funder AI-skepticism, the
   non-technical-ED adoption barrier, and mission-drift-under-deadline risk.
2. Grant-research revision pass — locked funder-fit-first, the 5-part outcome
   structure, budget congruence as a code-level check.
3. Design-doc pressure test — flagged end-of-process batch-review
   rubber-stamping risk (mitigations planned; per-item timing to be measured
   in the eventual human pilot).
4. Three-persona test (new / intermediate / expert leader) — convergence on
   session persistence (built) and miss-1 coaching (built); fading-scaffold
   and EIN-context items deferred.
5. **Charlene Brooks QA test** (spec-driven persona subagent, live smoke run):
   PASS WITH ISSUES — 12/12 facts recorded from her wording, nothing
   fabricated in the draft, causal hedging preserved; found defects 11-12
   (fixed) and C3-C5 (open). Scaffold/resolution/agency/pressure modes not
   yet run.

---

## 6. Infrastructure notes

- API key: workspace-scoped throwaway in `.env` (gitignored). The first key
  James created was identity-linked ("all workspaces") and failed with a
  workspace-id error; scoping the key to one workspace in the Console fixed it.
  **Rotate/revoke this key when the project ships.**
- This sandbox's egress proxy blocks `projects.propublica.org`; live 990 calls
  must run locally or in an environment with a custom allowlist.
- Session model: cloud environment "Default"; everything lives in the session
  scratchpad — **nothing is committed to git yet.** The designated branch is
  `claude/blog-topic-ideas-cvu7qa` on JamesDRodgers/Claude-Skills.

---

## 7. Agreed next steps (in order)

1. **Hosted no-setup web version** — the "very low bar of entry" goal; key
   server-side (Netlify-function pattern from jamesdrodgers.ai), spend cap,
   no signup. The single highest-leverage remaining piece.
2. Close Charlene C4 (dates + named entities in the grounding validator) —
   it's a promised guarantee in the design doc, currently number-only.
3. Surface `target_fact_id` in the CLI Resolution Pass (C3); humanize flag
   labels (C5); revisit `unattributed` naming.
4. Charlene re-runs in `scaffold`, `resolution`, `agency`, and `pressure`
   modes — smoke mode never exercised the ladder or the override path live.
5. Phase 4: repo packaging (MIT, ED-first README covering both tracks) and
   the deferred small fixes (fading scaffold, EIN context line).
6. Phase 5: ship, link from the portfolio, write the blog post — the arc is
   the story: problem → build → self-critique → fix → give it away.
