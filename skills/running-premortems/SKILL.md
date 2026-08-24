---
name: running-premortems
description: >
  Conducts rigorous prospective-hindsight premortems for projects, strategies,
  launches, decisions, implementations, technical systems, and AI workflows.
  Use when the user asks to run or facilitate a premortem, explicitly assumes
  an initiative has failed and asks you to explain why, or requests a
  prospective-hindsight analysis. Do not use this for generic risk reviews,
  pressure-testing, or postmortem root-cause analysis—this skill uses the
  specific premortem methodology.
---

# Running Premortems

## Goal

Produce decision-changing insight, not a risk register.

A strong premortem identifies where the plan is fragile, explains failure as a
causal chain rather than a category, challenges major hypotheses with
counterevidence, makes the failure observable early through leading indicators
and tripwires, and changes what the user will do—whether that's testing,
monitoring, preparing contingencies, accepting risk, or stopping.

## Route the task

Determine what is being premortemed (project, product, launch, strategy,
architecture, process, policy, AI system, etc.) and infer the mode:

- **Rapid**: Quick stress-test for time-sensitive decisions; still rigorous,
  just compressed
- **Standard**: Full methodology on well-scoped initiatives
- **Deep**: Complex, high-stakes, or ambiguous initiatives requiring extended
  analysis, outside view, and meta-premortem
- **Facilitator**: You are facilitating humans; protect their independent
  generation before adding model-generated risks
- **Review**: User has an existing risk register; premortem it for depth and
  decision consequence

Ask only questions whose answers could materially change the analysis. Otherwise
state assumptions and continue—do not turn this into an intake form.

## Core workflow

The sequence matters. Respect these ordering constraints:

1. **Model the plan** (objective, success/failure criteria, horizon, stakes,
   stakeholders, constraints, dependencies, key assumptions)

2. **Map epistemic status** (distinguish supplied facts, external evidence,
   estimates, assumptions, unknowns, speculative hypotheses)

3. **Construct a concrete failed future** using observable consequences and a
   specific horizon. Failure has already happened—this is prospective hindsight,
   not possibility.

4. **Diverge before converging** (no scoring, debate, or solutioning during
   generation; protect independent thinking)

5. **Protect independence**:
   - *Facilitator mode*: Participants generate silently first; you supply risks
     only after they contribute
   - *Solo mode*: Separate analytical passes before synthesis (different failure
     lenses, stakeholder perspectives)

6. **Expand coverage** using relevant failure lenses (read
   `references/failure-lenses.md` for general catalog; read
   `references/ai-agent-lenses.md` if the object is an AI system, workflow, or
   agent)

7. **Reconstruct causality** for material risks: underlying condition → trigger
   → propagation → control/detection failure → observable consequence

8. **Search interactions** (cascades, common-mode dependencies, correlated
   risks, delays that compress testing, risks that hide other risks)

9. **Surface uncomfortable and minority hypotheses** explicitly. Do not equate
   consensus with truth; preserve outlier concerns if they are high-impact,
   hard to detect, or informed by unique knowledge.

10. **Challenge each major hypothesis** with evidence for, evidence against,
    existing controls, hidden assumptions, and what would change the judgment

11. **Use outside-view evidence** only after generating inside view; never
    invent base rates. If research tools are unavailable, say so and keep that
    section explicitly incomplete (read `references/evidence-calibration.md`)

12. **Prioritize by decision relevance, impact, likelihood class, velocity,
    detectability, reversibility, controllability, evidence strength**—avoid
    fake numeric precision

13. **For Critical/High risks, engineer controls**: prevent → detect → respond
    → recover → exit

14. **Make the risk observable**: leading indicator → tripwire threshold →
    owner → predetermined action → last safe action time

15. **Force decision consequences**: change now / test before commitment /
    monitor / prepare contingency / accept / stop/no-go

16. **Stress-test the mitigation itself** (can it fail? shared dependencies?
    does it conceal rather than reduce risk?)

17. **Run a meta-premortem**: assume this analysis misled you—why?

18. **State when this should be rerun** (milestone, evidence, change that
    invalidates assumptions)

## Completion gate

Do not call the premortem complete if the top risks are only labels.

For each material risk, the output must include:

- A **causal mechanism** (not a category)
- **Evidence status and serious countercase** (what makes this risk less likely?)
- An **early observable signal** (leading indicator, not the final outcome)
- A **concrete decision consequence** (what changes in the plan?)

If you reach the end and top risks lack any of these, go back. The premortem is
incomplete.

## Team facilitation

When facilitating humans, follow these principles (see `references/facilitation.md`
for detailed scripts):

- **Ensure shared understanding of the plan** before generating failure stories
- **Construct and state the failed future** explicitly (concrete date,
  observable consequences)
- **Protect independent generation**: participants write silently before
  discussion; do not rebut during divergence
- **Collect and clarify without solving** during the generation phase
- **Preserve minority concerns** even if consensus disagrees
- **Add your own risks only after participants contribute** (this prevents
  anchoring)
- **Avoid letting the sponsor rebut** during divergence; sponsor can speak
  during synthesis

## Evidence discipline

Never present a plausible story as established fact.

Distinguish explicitly between:

- Supplied facts (user provided, observed)
- External evidence (cited, primary source preferred)
- Estimates (reasoned but not measured)
- Assumptions (things we are treating as true for planning purposes)
- Inferences (drawn from available data)
- Unknowns (explicitly unmeasured)
- Speculative hypotheses (consequential but unconfirmed)

For Deep mode or research-heavy analysis, read `references/evidence-calibration.md`.

## Output structure

Adapt length to stakes and mode. Default Standard output:

1. **Where the plan is most fragile** (executive framing)
2. **Failed future** (the prospective hindsight scenario)
3. **Critical failure mechanisms** (5–10 for Standard; more for Deep)
4. **Causal chains and countercases** (for top risks)
5. **Leading indicators and tripwires** (early detectability)
6. **Countermeasures and residual risk** (controls and what remains)
7. **What changes now** (decision consequences)
8. **Unknowns and gaps** (what we don't know and why it matters)
9. **Minority report** (uncomfortable or consensus-disagreed concerns, when
   relevant)
10. **Meta-premortem** (why this analysis might be wrong)
11. **Rerun trigger** (when to revisit)

See `references/output-contracts.md` for detailed risk-record schema and
mode-specific formats.

## Quality standard

Before finalizing, verify:

- **Surprise**: Did anything important emerge beyond what was already obvious?
- **Mechanism**: Do top risks explain *how* failure unfolds, not just *what*
  could fail?
- **Discomfort**: Did the analysis surface inconvenient, political, or
  capability-related hypotheses?
- **Signal**: Can failure be detected early, before the outcome becomes
  irreversible?
- **Decision**: Does the output change action (testing, monitoring, sequencing,
  contingency, acceptance, stop)?
- **Disconfirmation**: Were major hypotheses seriously challenged with
  counterevidence?
- **Epistemics**: Can the user distinguish evidence from inference from
  speculation?

Optimize for decision-changing insight per unit of attention. Short and potent
beats long and generic.

## When to read reference files

- **Failure lenses (general)**: Read `references/failure-lenses.md` when
  coverage feels incomplete; use the catalog to identify missing failure
  classes
- **AI/agent-specific lenses**: Read `references/ai-agent-lenses.md` when the
  object is an AI workflow, agent, model-enabled product, or LLM-powered
  system
- **Facilitation detail**: Read `references/facilitation.md` when you are
  facilitating humans; contains scripts for anonymous input, power-gradient
  handling, round-robin protocols
- **Evidence practices**: Read `references/evidence-calibration.md` for Deep
  mode or when research/external evidence is material
- **Output options**: Read `references/output-contracts.md` for detailed
  risk-record schema, compact vs. deep formatting, mode-specific templates
- **Examples**: Read `references/examples.md` to see how generic risks become
  causal mechanisms, how risks become signals/tripwires, how analysis drives
  decisions
