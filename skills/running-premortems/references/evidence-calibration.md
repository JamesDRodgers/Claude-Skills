# Evidence Discipline & Calibration

Never present a plausible story as established fact. This document shows how to distinguish evidence quality and avoid overclaiming.

## Evidence Categories

### Observed / Supplied Facts

User provided it directly or it's observable in the supplied materials.

Example: "The pilot had 500 participants."

**How to reference:** State it as fact.

### External Evidence

Cited from a primary source, publication, or authoritative documentation.

Example: "According to the 2024 VHA field study of brainwriting premortems (Rabin et al.), implementation findings were immediately actionable."

**How to reference:** Cite with source. Do not invent citations.

### Estimate / Inference

Reasoned based on available data but not directly measured.

Example: "We estimate the integration testing window will be 3 weeks, based on complexity and team size."

**How to reference:** "We estimate..." or "Based on [data], we infer..."

### Assumption

Treated as true for planning purposes but unvalidated.

Example: "We assume the legacy system will remain available as a fallback during the transition."

**How to reference:** "Assuming [X]..." or "We treat [X] as true."

### Unknown

Explicitly unmeasured or unclear.

Example: "We don't know how the competitor's product announcement will affect market timing."

**How to reference:** "We don't know..." or "This is unmeasured."

### Speculative / Consequential Hypothesis

A plausible scenario that hasn't been validated but would matter if true.

Example: "If the vendor's API reliability degrades under load, both the primary and backup plans fail simultaneously."

**How to reference:** "If [condition], then [consequence]." or "Speculatively..."

---

## Overclaiming Patterns

### Pattern 1: Treating Plausibility as Certainty

**Overclaim:** "The team will resist the new system because legacy workflows are familiar."

**Better:** "There's a plausible risk that team adoption lags if legacy workflows remain faster and easier. We haven't yet measured voluntary adoption rates in pilots of similar complexity."

**Why it matters:** A vivid, coherent story feels true. But feeling true and being true are different. The second version signals uncertainty.

### Pattern 2: Inventing Evidence

**Overclaim:** "Studies show that 30% of system migrations fail due to adoption."

**Problem:** Where did this 30% come from? (Often this statistic is paraphrased or misremembered.)

**Better:** "A corpus of case studies suggests adoption is common failure mode in system migrations. We haven't gathered specific data on this initiative."

**Never:** Invent citations or specific percentages when you don't have them.

### Pattern 3: False Precision

**Overclaim:** "Probability of integration failure is 35%."

**Problem:** This appears scientific but is really ordinal (Low / Medium / High).

**Better:** "Integration risk is High because there are three untested dependencies and we have limited time to debug interactions."

**Use:** Tiers (Critical, High, Medium, Low) with narrative rationale instead of specific percentages.

### Pattern 4: Base Rate Ignorance

**Overclaim:** "This feature will succeed because our last feature succeeded."

**Problem:** You're ignoring how often launches in your industry fail.

**Better:** "Our last feature launch succeeded. Broader data suggests [X]% of features similar to this one achieve adoption targets. Given those base rates, what's different about our approach?"

### Pattern 5: Confirmation Bias

**Overclaim:** "Everyone agrees this is a low risk."

**Problem:** Did you ask people with opposing views? Silence ≠ agreement.

**Better:** "Most participants think this is low-risk. One participant flagged [concern]. That concern is plausible even if consensus disagrees."

---

## How to Structure Evidence in Premortems

### For Each Material Risk

**1. State the mechanism:**
"Because [underlying condition], [trigger] occurs, leading to [propagation]. Controls fail because [control failure], resulting in [consequence]."

**2. Evidence status for each claim:**

| Claim | Status | How to Reference |
|---|---|---|
| "Managers are rewarded on legacy metrics" | Observed in org structure | "According to the incentive plan..." |
| "Legacy workflow is faster" | Assumed (not measured) | "We assume the legacy system is faster..." |
| "Users will not form new habits" | Speculative, based on behavior theory | "Research on habit formation suggests that [mechanism]. Speculatively, this means..." |
| "Voluntary adoption in pilots of similar size is typically 40-60%" | External evidence if you have it; otherwise unknown | "Studies of [comparable initiatives] suggest [range]" or "We don't have data on comparable pilots" |

**3. Counterevidence:**

"What would make this risk less likely?
- What existing controls already reduce it?
- What evidence would change the judgment?"

**4. Outside view (if available):**

"Comparable initiatives [your company / industry] have had adoption rates of [range]. Our plan differs in [ways], which might improve or worsen that baseline."

### Example Risk Record

**Risk:** Pilot adoption overstates voluntary usage.

**Mechanism:** Because the legacy workflow remains faster and managers are still rewarded on legacy throughput (OBSERVED in incentive plan), staff comply during the pilot but do not form a new habit. Pilot metrics look good because corporate pressure enforces compliance, but voluntary usage is lower than reported (SPECULATIVE, based on incentive theory). When the mandate is relaxed, adoption collapses (SPECULATIVE, but supported by case studies of similar transitions). The team misreads this as a marketing problem rather than an incentive problem (INFERRED from organizational tendency to blame messaging).

**Countercase:** If the new system is genuinely faster or easier than the legacy system, and if manager incentives align with new-system usage, adoption could be voluntary and sustained even without corporate oversight. (This is the intended design, but we ASSUME it will work; we don't yet have pilot evidence.)

**Evidence gap:** We will know this risk is real (or not) when pilot participants voluntarily return to the new system at >70% rates for 4 consecutive weeks after corporate pressure is lifted.

**Controls:**
- Modify manager scorecards *before* pilot (DECISION: change now)
- Measure voluntary 14-day return rate after pilot (LEADING INDICATOR)
- If return rate <30%, pause Wave 2 and retest (TRIPWIRE)

---

## Research & Outside View

### When to Use Outside View

Use outside-view evidence (base rates, analogues, published research) *after* inside-view generation. This prevents external examples from anchoring the whole analysis prematurely.

### Standards for Outside View

**✓ Good:**
- Primary source (original research, not a summary)
- Comparable context (similar org size, industry, complexity)
- Recent data (within 5 years unless the domain is stable)
- Clear methodology (you understand how they reached the conclusion)

**✗ Bad:**
- Paraphrased statistics ("I heard that...")
- Cherry-picked examples (you found one success, ignored 10 failures)
- Unconfirmed claims ("Everyone knows that...")
- Outdated data applied to rapidly changing domains

### When to Say "We Don't Know"

If research tools are unavailable or the outside view data is weak, state it explicitly:

"We don't have access to research on comparable initiatives. Inside-view analysis suggests [mechanism]. Outside-view calibration would strengthen this, but we're proceeding without it."

This is honest and preserves epistemic discipline.

---

## Disconfirmation

For each major hypothesis, ask:

1. **What evidence would change the judgment?**
   - What would need to be observed?
   - How would we know the risk is less likely?

2. **What existing controls already reduce it?**
   - What is the organization already doing?
   - How effective is that control?

3. **What hidden assumptions underlie this risk?**
   - What would need to be true for the risk to NOT occur?
   - Are those assumptions realistic?

**Example:**

**Risk:** Integration testing window is too short.

**Evidence that would change the judgment:**
- If integration components have been tested at scale before and integration issues are typically minor (data: historical test results)
- If we allocate more time/people to integration testing than originally planned (decision)
- If the architecture simplifies integration requirements (external evidence from comparable architectures)

**Existing controls:**
- We have a dedicated integration team (resource)
- We planned 6 weeks of integration testing (schedule)
- We've done a dependency map (planning)

**Hidden assumptions:**
- We assume dependencies are well-understood (what if there are unknowns?)
- We assume the team has done similar integrations before (what if they haven't?)
- We assume tools will work as expected (what if a tool fails?)

This disconfirmation doesn't eliminate the risk, but it makes the judgment more nuanced.

---

## Epistemic Discipline Test

Before finalizing the premortem, verify:

- [ ] Can the user distinguish facts from estimates from assumptions?
- [ ] Are speculative claims labeled as such?
- [ ] Are no false statistics or invented citations present?
- [ ] Does each major risk have a countercase?
- [ ] Is outside view evidence, when present, sourced and comparable?
- [ ] Are unknowns explicitly named?
- [ ] Is the confidence level appropriate to the evidence?

This is the seventh test of excellence: Epistemic Discipline.
