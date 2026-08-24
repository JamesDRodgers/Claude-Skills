# Full Premortem Methodology

This document details the 18-step state machine and the reasoning behind each phase.

## Table of Contents

1. [Core Principles](#core-principles)
2. [The 18-Step State Machine](#the-18-step-state-machine)
3. [Phase-by-Phase Guidance](#phase-by-phase-guidance)
4. [Causal Reconstruction](#causal-reconstruction)
5. [Interaction Analysis](#interaction-analysis)
6. [Control Design](#control-design)
7. [Tripwires and Leading Indicators](#tripwires-and-leading-indicators)
8. [Meta-Premortem](#meta-premortem)

---

## Core Principles

### 1. Failure Is Certain During Divergence

Use *certainty* framing: "It is 18 months from now. The initiative has failed."

This is the prospective-hindsight mechanism discovered by Mitchell, Russo, and Pennington. Certainty prompts longer, more episodic explanations—participants imagine *how* failure unfolded, not just *whether* it could.

Weak: "Imagine the project might fail. What could go wrong?"

Better: "It is 18 months from now. The initiative has failed."

Excellent: "It is 18 months from now. The initiative launched, but voluntary adoption is below 20%, cost is 35% above the approved plan, the second rollout wave has been cancelled, and leadership has decided not to expand it. Explain how we got here."

### 2. Understand the Plan Before Attacking It

The skill should not critique a strawman. Normalize:

- Objectives
- Success and failure criteria
- Time horizon
- Key stakeholders
- Current plan (what is being done)
- Constraints (time, budget, people, regulatory)
- Dependencies (vendor, team, technology, decision-maker)
- Key assumptions
- Evidence confidence levels

If the user provides vague input, ask targeted questions that could materially change the analysis. Otherwise state assumptions and continue.

### 3. Separate Generation From Evaluation

Do not immediately debate, score, or solve each risk. This is the divergence principle. Early convergence narrows the search space and anchors the analysis.

In team mode, collect all human input before adding model-generated risks. In solo mode, run separate analytical passes before synthesis.

### 4. Protect Independent Generation

In team settings, human participants should generate silently before discussion. If power gradients are steep, collect concerns anonymously or have the sponsor speak last.

In solo analysis, use procedurally separate passes (different failure lenses, stakeholder perspectives, domains) without letting one pass seed the next.

### 5. Generate Mechanisms, Not Labels

"Low adoption" is not a risk diagnosis. "Stakeholder resistance" is a category, not an explanation.

Top risks must articulate causal chains:

**Weak:** Low adoption.

**Mechanism:** Because the legacy workflow remains easier and managers are still rewarded on legacy metrics, staff comply during the sponsored pilot but do not form a new habit. Pilot usage therefore overstates voluntary adoption. When sponsor pressure falls, repeat usage collapses and the team misreads the problem as a marketing shortfall rather than an incentive-design failure.

### 6. Preserve Minority Information

Consensus is not evidence. A one-off concern can be critical if it is well-supported, hard to detect, or informed by unique knowledge. Preserve minority reports explicitly; do not cluster them away.

### 7. Search for Interactions

Individual risks often look manageable. Projects fail when risks reinforce one another. Ask:

- Which single risk can trigger two or more others?
- Which pair of moderate risks becomes severe together?
- Which "independent" mitigations share the same vendor, team, dataset, or assumption?
- Which delay compresses testing/review/learning and changes the severity of another risk?
- Which risk hides another by making metrics look temporarily healthy?

### 8. Distinguish Evidence From Imagination

Tag claims as observed, externally evidenced, inferred, assumed, unknown, or speculative. A polished causal story is not evidence.

### 9. Disconfirm Before Prioritizing

Every major risk deserves a countercase. Ask:

- What makes this risk less likely?
- What existing controls already reduce it?
- What evidence would change the judgment?

### 10. Make the Future Observable

Every critical risk should have an earliest signal—a leading indicator that appears before the outcome is obvious. Include a tripwire: "If [signal] reaches [threshold], then [predetermined action]."

### 11. Force Decision Consequences

Identifying risks is not enough. Every material risk must produce a change in the plan: change now, test before commitment, monitor, prepare contingency, accept the risk, or stop/no-go.

### 12. Stress-Test Mitigations

Controls can fail, conceal risk, create new risk, or share dependencies with the original failure. Ask:

- How could this mitigation fail?
- Does the control depend on the same assumption as the original plan?
- Does it conceal the risk rather than reduce it?
- What new risk does it create?
- Will the owner actually have authority, information, and time to act?

### 13. End With a Meta-Premortem

Assume this analysis itself was misleading. Why might that be?

- The most vivid stories were mistaken for the most likely
- The team imagined familiar failures, not novel ones
- Sponsor framing constrained what people considered
- A critical stakeholder or expertise was missing
- External analogues were not actually comparable
- The model invented or overstated evidence
- Risk scoring created false precision
- Mitigations were assumed to work without testing

---

## The 18-Step State Machine

This is the canonical sequence. Each step builds on the previous.

### 0. Route

Determine:
- Object being premortemed (project, product, launch, strategy, etc.)
- Stakes and reversibility
- Which mode (Rapid, Standard, Deep, Facilitator, Review)
- Whether sufficient plan context exists

### 1. Model the Plan

Objective → success/failure criteria → horizon → stakeholders → plan →
constraints → dependencies → assumptions → unknowns.

Output: A compact model that you and the user both understand.

### 2. Map Epistemics

Facts → estimates → assumptions → unknowns → evidence confidence.

Output: A clear distinction between what is known and what is assumed.

### 3. Lock the Failed Future

Concrete date + observable consequences. Failure has occurred.

Output: A prospective-hindsight scenario that guides generation.

### 4. Diverge

Independent free generation. No scoring, debate, or solutioning. Maximize the
chance of discovering different hypotheses before the first compelling story
anchors the rest.

Output: Raw material (risks, failure modes, concerns) without filtering.

### 5. Expand Coverage

Run relevant failure lenses and search for missing classes. Use the general
catalog or domain-specific lenses.

Output: Broader coverage; identification of gaps.

### 6. Reconstruct Causality

Root condition → trigger → propagation → control failure → consequence.

Output: Causal chains instead of categories.

### 7. Search Interactions

Cascades → common-mode dependencies → risk combinations → success-caused
failures.

Output: Identification of reinforcing risks and hidden dependencies.

### 8. Surface the Uncomfortable

Minority report → taboo hypothesis → sponsor/incentive/capability risks.

Output: Explicitly preserved concerns that ordinary planning avoids.

### 9. Calibrate

Counterevidence → existing controls → outside view / base rates if available.

Output: Challenge to each major hypothesis.

### 10. Consolidate

Deduplicate without erasing distinct mechanisms or minority concerns. Cluster
by underlying mechanism, not generic category.

Output: A working risk list without loss of causal detail.

### 11. Prioritize

Decision relevance, impact, likelihood class, velocity, detectability,
reversibility, controllability, evidence strength, uncertainty.

Output: A ranked list optimized for decision-making, not fake precision.

### 12. Engineer Controls

For Critical/High risks: Prevent → Detect → Respond → Recover → Exit.

Output: A small control system for each material risk.

### 13. Instrument & Precommit

Leading signal → threshold → owner → predetermined response → last safe action
time.

Output: Observable tripwires; pre-commitment to action.

### 14. Change the Plan

Change now → test → monitor → contingency → accept → stop/no-go.

Output: Concrete decision consequences.

### 15. Stress-Test the Response

How can the mitigation fail? What new/common-mode risk does it create?

Output: Refined mitigations; residual risk quantified.

### 16. Meta-Premortem

Assume this analysis misled us. Why?

Output: Explicit uncertainty; identified blind spots.

### 17. (Optional) Success Inversion

Assume it exceeded expectations. What variables explain both futures?

Output: Identification of pivotal control variables.

### 18. Review Trigger

State what event, milestone, or evidence should trigger a rerun.

Output: Commitment to revisit when reality changes.

---

## Phase-by-Phase Guidance

### Phase 1: Route & Model (Steps 0–2)

**Goal:** Understand the object and the landscape before generating failure stories.

**Key discipline:** Ask only questions that could materially change the analysis. State assumptions for the rest.

**Output:**
- Object clearly defined
- Success/failure criteria explicit
- Horizon (3 months? 18 months? 5 years?)
- Key stakeholders identified
- Constraints known
- Major dependencies mapped
- Assumptions listed with confidence levels

**Common failures:**
- Turning this into a 20-question intake; instead, ask 2–3 key questions and assume the rest
- Accepting vague success criteria ("successful adoption"); force concreteness
- Missing dependencies because the user didn't think to mention them; ask about integrations, vendors, decision-maker alignment

### Phase 2: Construct the Failed Future (Step 3)

**Goal:** Create a prospective-hindsight scenario that anchors generation.

**Key discipline:** Failure must be certain and observable, not hypothetical.

**Weak framing:**
"Imagine the project might fail. What could go wrong?"

**Excellent framing:**
"It is 18 months from now. The initiative launched, but voluntary adoption
among the target users is below 20%. The second rollout wave has been
cancelled. Cost overran by 35%. Leadership has decided not to expand it.
Explain how we got here."

For Deep mode, construct 2–4 distinct failure futures if failure can take
materially different forms (execution failure, adoption failure, economic
failure, trust failure, strategic irrelevance, etc.).

**Output:** A concrete scenario that participants will use to generate
explanations.

### Phase 3: Generate & Expand (Steps 4–5)

**Goal:** Maximize hypothesis diversity before convergence.

**Team protocol:**
- Participants write independently first (silent generation)
- If power dynamics are steep, collect anonymously or have sponsor speak last
- Collect without debating or solving
- Clarify for understanding; do not rebut

**Solo protocol:**
- Run separate analytical passes:
  - Pass 1: Free-form generation (what immediately comes to mind)
  - Pass 2: Failure lens 1 (execution, people, dependencies)
  - Pass 3: Failure lens 2 (market, adoption, incentives)
  - Pass 4: Uncomfortable/political (sponsor capability, incentive misalignment)
- Do not let one pass seed the next; treat them independently

**Output:** Raw material without early filtering. Likely 20–50 raw hypotheses
for Standard mode; more for Deep.

### Phase 4: Reconstruct & Challenge (Steps 6–9)

**Goal:** Convert labels into mechanisms; challenge each with counterevidence.

**For each material risk:**

1. **Causal skeleton:**
   - Underlying condition (what state allows this failure?)
   - Initiating event (what happens first?)
   - Propagation mechanism (how does it spread?)
   - Control/detection failure (why didn't we catch it?)
   - Observable consequence (what made it visible?)

2. **Evidence status:**
   - Is this observed, externally evidenced, inferred, assumed, or speculative?
   - What evidence would change the judgment?

3. **Countercase:**
   - What makes this risk less likely?
   - What existing controls already address it?
   - What would need to be false for this to not happen?

**Output:** 5–10 Critical/High risks with explicit causal chains and
countercases.

### Phase 5: Prioritize & Control Design (Steps 10–13)

**Prioritization dimensions** (in order of importance):

1. **Decision relevance**: Would this risk change what we decide to do?
2. **Impact**: If it occurs, how much damage?
3. **Likelihood class**: Is this in the 10% tail or 50% probability range?
4. **Velocity**: How fast does failure cascade once it starts?
5. **Detectability**: How early can we see it coming?
6. **Reversibility**: Can we recover if it happens?
7. **Controllability**: Do we have levers?
8. **Evidence strength**: How confident are we in this diagnosis?
9. **Uncertainty**: How much do we not know?

**Do not multiply ordinal scores.** Avoid producing a single "risk score"
that presents false precision. Use tiers (Critical, High, Medium, Low) with
narrative rationale.

**Control engineering** (for each Critical/High risk):

- **Prevent**: Reduce the probability that the initiating condition or event occurs
- **Detect**: What leading signal shows the chain has begun?
- **Respond**: What action is taken when the trigger fires?
- **Recover**: How is damage limited or reversed?
- **Exit**: When should the organization stop, pivot, or abandon the approach?

**Output:** Prioritized risk list; control systems for material risks.

### Phase 6: Make the Future Observable (Step 13 continued)

**Goal:** Every critical risk should have an earliest signal and a tripwire.

**Lagging indicator (too late):**
"Revenue missed the annual target."

**Leading indicator (in time to act):**
"Pilot users complete onboarding but fewer than 30% return voluntarily within 14 days."

**Tripwire (pre-commitment):**
"If voluntary 14-day return is below 30% after two onboarding variants, pause
rollout and retest the adoption thesis before committing procurement for Wave 2."

**Last safe moment:**
"The decision must be made before Wave 2 procurement becomes non-cancellable (date: Q3 EOY)."

**Output:** For each Critical/High risk, at least one leading indicator and one
tripwire with an owner and predetermined response.

### Phase 7: Force Decision Consequences (Step 14)

**This is the key upgrade from good to excellent.** Identifying risks is not
enough.

For each Critical/High risk, force a decision consequence:

- **Change now**: Modify the plan, timeline, scope, team, or approach before execution
- **Test before commitment**: Pilot, prototype, or experiment to reduce uncertainty
- **Monitor**: Establish ongoing surveillance with tripwires and predetermined actions
- **Contingency**: Prepare a backup plan, team, or resource
- **Accept**: Consciously accept the risk and the residual consequence
- **Stop/no-go**: Do not proceed unless/until the risk is resolved

**Output:** Explicit decisions tied to each material risk.

### Phase 8: Stress-Test & Meta-Premortem (Steps 15–18)

**Stress-test mitigations:**
- How could this mitigation fail in practice?
- Does the control depend on the same assumption as the original plan?
- Could the control conceal the risk rather than reduce it?
- What new risk does the control create?
- Are multiple backups exposed to the same common-mode dependency?
- Will the owner actually have authority, information, and time to act when the tripwire fires?

**Meta-premortem:**
Assume this entire analysis was misleading. Why might that be?

- The most vivid stories were mistaken for the most likely
- Only familiar failure modes were imagined
- Sponsor framing constrained consideration
- Critical expertise was missing
- External analogues were not comparable
- The model invented evidence
- Risk scoring created false precision
- Mitigations were assumed to work without testing
- Minority concerns were clustered away
- The analysis produced pessimism without success-side calibration

**Which major risk would a smart critic remove or downgrade?**
**Which important failure mechanism might still be missing?**

**Output:** Refined confidence in the analysis; identified blind spots.

---

## Causal Reconstruction

The core skill is converting labels into mechanisms.

### Template

```
Because [underlying condition],
[initiating event] occurs,
which causes [propagation mechanism].
Existing controls fail because [control/detection failure],
leading to [observable consequence].

We would expect to see [leading indicator] first.
If [tripwire threshold], then [predetermined response].
```

### Example: From Label to Mechanism

**Label:**
"Stakeholder resistance"

**Mechanism:**
"Because legacy system customers are rewarded for quarterly efficiency metrics
and the new system requires a 3-month ramp with reduced throughput, mid-level
managers actively discourage their teams from adopting it during the pilot.
Pilot metrics look good because corporate pressure enforces compliance, but
voluntary usage is lower than reported. When the mandate is relaxed, adoption
collapses. The team misreads this as a change-management problem ('we need
better training') rather than an incentive-design problem ('the old metrics
still drive behavior').

We would expect to see pilot users checking back into the legacy system
within 2 weeks after the sponsorship pressure falls.

If legacy system usage is above 40% in any pilot cohort 6 weeks after go-live,
pause the next region and rerun the incentive analysis before proceeding.

The current plan should therefore modify manager scorecards *before* the pilot,
not after, and build in a 1-month holdback before Wave 2 to test sustained adoption."

---

## Interaction Analysis

Risks interact when one amplifies another or shares a root cause.

### Types of Interactions

**Cascade:** Risk A triggers Risk B triggers Risk C

Example: Poor onboarding → low pilot engagement → misinterpreted as marketing
problem → wrong fix applied → Wave 2 launch proceeds with same issue.

**Common-mode dependency:** Multiple "independent" risks share the same
failure point

Example: Both the primary adoption strategy and the contingency plan depend on
the same vendor's API. If the vendor has an outage or changes their terms,
both fail together.

**Risk combination:** Two moderate risks become severe when they occur together

Example: Modest cost overrun (20%) + modest timeline slip (4 weeks) = 30% of
Wave 2 testing time lost = High risk failures make it through.

**Success-caused failure:** Meeting one objective creates conditions for
failure

Example: If the pilot is *too* successful, it becomes a showcase; corporate
announces public commitments before full rollout readiness; second-mover
problems compound pressure.

**Delay compression:** Timing pressure changes the severity of another risk

Example: If onboarding is delayed 3 weeks, the rollout window shrinks and
testing time for Wave 2 is cut in half.

### Analysis Method

For each material risk, ask:

- Does this risk trigger or amplify another?
- Do any of my mitigations share a common-mode dependency?
- If this risk occurs late (close to irreversibility), does it change the
  severity of another risk?

Document the interactions explicitly. Prioritize not just individual risks but
the combinations.

---

## Control Design

Every Critical/High risk needs a small control system.

### Five Layers

1. **Prevent**: Reduce probability of the initiating condition
2. **Detect**: Identify the chain is active (leading indicator + tripwire)
3. **Respond**: Predetermined action when tripwire fires
4. **Recover**: Damage limitation or reversal after occurrence
5. **Exit**: Stop/pivot/de-scope decision

### Documentation

For each control:

- Owner (who has authority to act)
- Trigger (what signal fires this control?)
- Threshold (numerical, if applicable)
- Action (what specifically happens)
- Residual risk (what risk remains even if the control works?)
- Dependencies (what else must be true for the control to work?)

### Example

**Risk:** Pilot adoption overstates voluntary usage because managers enforce
compliance during sponsorship but adoption collapses when pressure falls.

**Control System:**

1. **Prevent**: Change manager scorecards *before* pilot to reinforce new-system
   usage (not legacy throughput)

2. **Detect**: After pilot ends, measure voluntary return rate at Day 3, Day 7,
   Day 14. Leading indicator: <30% return by Day 14.

3. **Respond**: If return rate <30%, pause Wave 2 procurement and retest
   adoption thesis before proceeding.

4. **Recover**: If adoption does collapse, revert to legacy-system-primary
   approach with new system as optional tool (limited damage).

5. **Exit**: If adoption is <15% after two scorecard variants, cancel Wave 2
   expansion and reallocate resources.

**Residual risk**: Even with corrected incentives, adoption could still be low
if the UX is poor or the new workflow is genuinely less efficient than legacy.

**Dependencies**: Managers must have authority to change scorecards; finance
must support pre-pilot change.

---

## Tripwires and Leading Indicators

### Leading Indicator Design

A leading indicator appears *before* the final outcome is obvious.

**Timeline example:**
- Day 0: Launch
- Week 2: Users onboard; leading indicator is measured
- Week 6: Tripwire threshold is evaluated
- Month 3: If tripwire fires, decision is made
- Month 6: Final outcome becomes obvious (too late to act)

### Format

**Leading Indicator:**
"[Metric/observation] will show [signal] before [final outcome]."

Example:
"Voluntary 14-day return rate will show low adoption before we commit Wave 2 budget."

**Tripwire Threshold:**
"If [metric] reaches [value] by [date], then [action]."

Example:
"If voluntary 14-day return is below 30% by Week 6 after pilot launch, pause Wave 2 procurement."

**Last Safe Moment:**
"[Decision] must be made by [date/milestone] before [irreversible commitment]."

Example:
"Adoption decision must be made by Q3 EOY before Wave 2 procurement orders become non-cancellable."

### Coverage

For Deep mode, every Critical/High risk should have at least one leading
indicator. For Standard mode, the top 3–5 risks need leading indicators.

---

## Meta-Premortem

The analysis itself can be wrong. Use the meta-premortem to expose why.

### Questions

1. **Were the most vivid stories mistaken for the most likely?**
   - Did a memorable example anchor the analysis toward one failure mode?
   - What other failure modes are possible but less dramatic?

2. **Did the team imagine only familiar failures?**
   - What happened last time and what could be different?
   - What would a newcomer to this domain see that we miss?

3. **Did the sponsor's framing constrain what was considered?**
   - What would be too uncomfortable to discuss in the kickoff?
   - What would people say privately but not publicly?

4. **Was a critical stakeholder or expertise missing?**
   - Who would have raised a concern we missed?
   - What domain knowledge would change the diagnosis?

5. **Were external analogues actually comparable?**
   - Did we cherry-pick examples that matched our narrative?
   - What do the failures of similar initiatives tell us?

6. **Did the model invent or overstate evidence?**
   - Which claims were made based on research vs. plausibility?
   - Did I confuse a well-told story with a well-grounded one?

7. **Did risk scoring create false precision?**
   - Am I more confident in the rank order than I should be?
   - Which risks have actual numerical estimates vs. ordinal guesses?

8. **Were mitigations assumed to work without testing?**
   - Have these controls been proven in similar contexts?
   - What could break the mitigation?

9. **Were minority concerns clustered away?**
   - Did one-off concerns get deleted because nobody agreed?
   - Should any outlier hypothesis be preserved?

10. **Did the exercise produce only pessimism?**
    - Was there a success-side analysis to calibrate?
    - What pivotal variables explain both the success and failure futures?

### Output

State explicitly:

- **Which major risk would a smart critic remove or downgrade?**
- **Which important failure mechanism might still be missing?**

This is not meant to destroy confidence in the analysis, but to preserve
humility and identify the thin places where the analysis is most vulnerable.

---

## Mode-Specific Guidance

### Rapid Mode

- Time constraint: 30–60 minutes
- Depth: Identify the top 2–3 vulnerabilities and 1–2 tripwires
- Skip: Extended outside-view analysis, deep meta-premortem
- Keep: Causal chains, disconfirmation, decision consequences

### Standard Mode

- Time: 1–3 hours
- Depth: Full state machine, 5–10 Critical/High risks, leading indicators for top 3–5
- Skip: Exhaustive outside view unless material
- Keep: All core steps; optional success inversion

### Deep Mode

- Time: Multiple sessions possible
- Depth: Extended analysis, 2–4 failed futures, outside-view research, meta-premortem, success inversion
- Include: Interaction analysis, minority report, stress-test of mitigations
- May include: Expert consultation, scenario modeling

### Facilitator Mode

- Protect independent generation before adding model-generated risks
- Use documented scripts for team dynamics
- Preserve anonymity if power gradients are steep
- Explicitly avoid anchoring with your own ideas

### Review Mode

- User brings an existing risk register
- Job is to assess: Are risks mechanisms or labels? Are there disconfirmations? Do they connect to decisions? Are interactions identified?
- Output: Strengths and gaps; recommendations for depth

