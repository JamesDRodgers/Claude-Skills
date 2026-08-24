# Output Contracts & Risk Record Schema

The skill should have a flexible presentation layer but a stable internal information model.

## Standard Output Structure

Adapt the length to stakes and mode. Default for Standard mode:

1. **Where the plan is most fragile** (executive-level framing)
2. **Failed future** (the prospective-hindsight scenario)
3. **Critical failure mechanisms** (5–10 for Standard; more for Deep)
4. **Causal chains and countercases** (for top 3–5 risks)
5. **Leading indicators and tripwires** (early detectability and predetermined action)
6. **Countermeasures and residual risk** (controls and what risk remains)
7. **What changes now** (decision consequences: change, test, monitor, contingency, accept, stop)
8. **Unknowns and evidence gaps** (what we don't know and why it matters)
9. **Minority report** (uncomfortable or consensus-disagreed concerns, when relevant)
10. **Meta-premortem** (why this analysis might be wrong)
11. **Rerun trigger** (when to revisit the analysis)

**Do not mechanically print every section if it adds no value.** The contract is about information, not ceremonial headings. If there are no unknowns worth naming, skip that section. If there's no minority concern, don't force one.

## Risk Record Schema

Each material risk should follow this structure:

```
RISK TITLE
[Ordinal tier: Critical / High / Medium / Low]

MECHANISM:
Because [underlying condition],
[initiating event] occurs,
which causes [propagation mechanism].
Existing controls fail because [control/detection failure],
leading to [observable consequence].

EVIDENCE STATUS:
- [Claim 1] is [observed / externally evidenced / estimated / assumed / unknown / speculative]
- [Claim 2] is...

COUNTERCASE:
What would make this risk less likely?
- [Existing control]: [How it reduces the risk]
- [Evidence that would change judgment]: [What we'd need to see]

LEADING INDICATOR:
[Metric/observation] will show [signal] before [final outcome].
Example: "Voluntary 14-day return rate will show low adoption before Wave 2 commitment."

TRIPWIRE:
If [metric] reaches [value] by [date], then [predetermined action].
Example: "If voluntary 14-day return is below 30% by Week 6, pause Wave 2 procurement."

LAST SAFE MOMENT:
[Decision] must be made by [date/milestone] before [irreversible commitment].
Example: "Adoption decision must be made by Q3 EOY before Wave 2 orders become non-cancellable."

CONTROLS:
- Prevent: [What reduces probability of initiating condition]
- Detect: [Leading signal / tripwire]
- Respond: [Action when tripwire fires]
- Recover: [Damage limitation]
- Exit: [Stop/pivot/de-scope decision]

RESIDUAL RISK:
[What risk remains even if all controls work as designed]

DECISION CONSEQUENCE:
The current plan should therefore:
[ ] Change now (modify scope, timeline, team, approach)
[ ] Test before commitment (pilot, prototype, experiment)
[ ] Monitor with tripwires (ongoing surveillance + predetermined action)
[ ] Prepare contingency (backup plan or team)
[ ] Accept consciously (name the risk; accept the consequence)
[ ] Stop/no-go if [condition is met]
```

## Mode-Specific Output

### Rapid Mode (30–60 minutes)

Keep it tight. Focus on top 2–3 vulnerabilities and the tripwires that matter most.

**Output:**
1. Where the plan is most fragile
2. Failed future (brief)
3. Top 2–3 Critical risks (mechanism + countercase only)
4. Leading indicators/tripwires for those risks
5. What changes in the plan
6. Meta-premortem (one paragraph)

Expect 1–3 pages of dense, high-signal content.

### Standard Mode (1–3 hours)

Full state machine. 5–10 Critical/High risks with mechanisms, countercases, and controls.

**Output:**
1. Where the plan is most fragile
2. Failed future
3. Critical failure mechanisms (5–10)
4. Causal chains and countercases (top 3–5)
5. Leading indicators and tripwires (top 3–5)
6. Countermeasures and residual risk
7. What changes now
8. Unknowns and evidence gaps
9. Meta-premortem
10. Rerun trigger

Expect 4–8 pages.

### Deep Mode (3+ hours, possibly multiple sessions)

Extended analysis. 2–4 failed futures. Outside-view research. Interaction analysis. Minority report. Success inversion. Extensive meta-premortem.

**Output:**
1. Executive summary
2. Multiple failed futures (2–4 distinct failure modes)
3. Critical and High risks (10–20)
4. Causal chains, countercases, external evidence (detailed)
5. Interaction analysis (how risks reinforce each other)
6. Leading indicators, tripwires, and controls (comprehensive)
7. What changes now (extensive decision consequences)
8. Unknowns, gaps, and research needs
9. Minority report (with explicit reasoning about why concerns are preserved)
10. Meta-premortem (detailed)
11. Success inversion (what variables explain both success and failure?)
12. Rerun trigger and review schedule

Expect 10–20 pages or a detailed document for team consumption.

### Facilitator Mode

Same structure as Standard or Deep, but emphasize:
- Human-generated input (what participants surfaced)
- Model-added risks (what you contributed; explicitly labeled)
- Preserved minority concerns (dissenting views and why they matter)
- Team alignment (where consensus exists vs. disagreement)

### Review Mode

User brings an existing risk register. Assess depth and completeness.

**Output:**
1. Strengths (what the register captures well)
2. Gaps (what failure classes or interactions are missing)
3. Depth assessment (labels vs. mechanisms; mechanisms vs. countercases)
4. Decision consequence analysis (do risks connect to changes in the plan?)
5. Recommendations for improvement

---

## Example: Short Risk Record (Standard Mode)

**Adopting users don't form new habits; adoption collapses when sponsorship ends**
[High]

**Mechanism:**
Because the legacy system is faster and managers are still rewarded for legacy throughput, staff comply during the pilot but don't form a new habit. Pilot usage therefore overstates voluntary adoption. When sponsor pressure falls, repeat usage collapses. The team misreads the problem as marketing/training rather than incentive-design failure and repeats the same approach in Wave 2.

**Evidence:**
- Legacy system faster: ASSUMED (not measured)
- Managers rewarded on legacy throughput: OBSERVED in current incentive structure
- Pilot compliance under pressure: EXPECTED based on prior org behavior
- Voluntary adoption collapse: SPECULATIVE, supported by behavior change literature

**Countercase:**
If the new system becomes faster than legacy (design goal), and if manager scorecards change before the pilot (decision pending), adoption could be voluntary and sustained.

**Leading Indicator:**
Voluntary 14-day return rate after pilot sponsorship pressure is lifted will show whether adoption is sustained.

**Tripwire:**
If voluntary 14-day return rate is below 30% in any pilot cohort 2 weeks after pilot ends, pause Wave 2 and retest the adoption thesis before committing procurement.

**Controls:**
- Prevent: Modify manager scorecards *before* pilot; tie compensation to new-system usage
- Detect: Measure voluntary 14-day return rate; measure manager scorecard alignment
- Respond: If tripwire fires, conduct sprint to identify adoption barriers; test UX/workflow changes
- Recover: Pivot to phased approach; scale adoption learning before full rollout
- Exit: If adoption remains <20% after two scorecard iterations, reassess strategy viability

**Decision:**
- Change now: Modify incentives before pilot
- Test before commitment: Run scorecard change pilot if adoption is uncertain
- Monitor: 14-day return rate; manager usage patterns
- Contingency: Phased rollout; fallback to legacy-primary + new-system-optional
- Rerun: After pilot completes and sponsorship pressure is removed

---

## Example: Deep Risk Record (Deep Mode, with Outside View)

**Integration complexity exceeds testing capacity; defects reach production**
[Critical]

**Mechanism:**
Because the new system integrates with Finance (GL posting), HR (employee records), and Operations (scheduling) and there are three separate vendor dependencies (API, database, middleware), the interaction surface is large. Testing time is 6 weeks; that is insufficient to systematically test all failure modes. Control breakdown: The team assumes dependencies will behave as documented, but undocumented behavior or edge-case interactions are common. Production issues cascade: A Finance GL posting bug affects time-and-attendance, affecting payroll, affecting HR compliance. Existing controls (code review, UAT) do not catch complex interactions.

**Evidence:**
- Three vendor dependencies: OBSERVED from system architecture
- Integration surface large: INFERRED from integration requirements doc
- 6 weeks testing time: OBSERVED from project plan
- Integration issues common in migrations: EXTERNAL EVIDENCE (see below)
- Undocumented API behavior: ASSUMED (common but not measured for these vendors)

**Outside View:**
- A 2023 survey of 200+ enterprise system migrations found 45% of projects experienced integration defects in production. The median time to resolve was 4 weeks.
- Of those 45%, the modal cause was undocumented API behavior or edge-case interactions discovered in production rather than test.
- Comparable systems with 3+ vendor integrations reported higher failure rates (61%) than 1–2 vendor systems (38%).

**Countercase:**
If the vendor APIs are well-documented and well-tested, if the team has integration experience, and if we allocate more than 6 weeks to testing, the risk is lower. Evidence that would change the judgment: (1) Full vendor API documentation + prior successful integrations by this team, (2) allocation of 10+ weeks to integration testing, (3) pilot testing with live Finance data.

**Interactions:**
This risk intersects with Timeline Risk (if testing is compressed by schedule slip, integration risk increases). It also intersects with Dependency Risk (if vendors change terms mid-project, integration scope increases).

**Leading Indicator:**
Integration defect density in Week 3 testing (before production) will predict severity. High defect density (>10 defects per 1000 LOC of integration code) by Week 3 suggests we haven't achieved sufficient understanding of interaction behavior.

**Tripwire:**
If integration defect density at Week 3 exceeds 10 per KLOC, extend testing by 2 weeks and reassess vendor API documentation before production go-live. If defects remain high, consider phased go-live (Finance only, then HR, then Operations) to limit blast radius.

**Controls:**
- Prevent: Require vendor API documentation; run sandbox tests with live vendor APIs before project starts
- Detect: Weekly integration test reporting; defect density by vendor/interface
- Respond: If high defect density: extend testing, vendor escalations, additional integration sprint
- Recover: Phased go-live; keep legacy system available during transition
- Exit: If integration defect density exceeds 15 per KLOC and we're unable to resolve, delay production go-live by 1 quarter

**Residual Risk:**
Even with extended testing, complex systems occasionally reveal edge-case interactions in production. Residual risk: a single high-severity defect in production (e.g., GL posting failure) during the first week. Mitigation: have a Finance team lead on-call and pre-coordinate escalation with each vendor for rapid support.

**Decision:**
- Change now: Allocate 10 weeks to integration testing (vs. 6 planned); require vendor API documentation before project kick-off
- Test before commitment: Run sandbox integration tests with live vendor APIs; don't wait for dev environment
- Monitor: Weekly integration test results; defect density by vendor; vendor API change logs
- Contingency: Phased go-live; legacy system remains available; Finance team lead on-call
- Rerun: After sandbox testing is complete and before UAT kicks off

---

## Completion Checklist

Before finalizing the premortem output:

- [ ] Are top risks mechanisms, not labels?
- [ ] Does each material risk have a countercase?
- [ ] Is evidence status clear (observed vs. inferred vs. speculative)?
- [ ] Does each Critical/High risk have a leading indicator?
- [ ] Does each Critical/High risk have a tripwire with predetermined action?
- [ ] Is there a decision consequence for each material risk?
- [ ] Is the meta-premortem present and specific?
- [ ] Is the rerun trigger stated?
- [ ] Have minority concerns been preserved (if any)?
- [ ] Is the length appropriate to stakes and mode?

If any "no," go back and fill the gap before calling the premortem complete.
