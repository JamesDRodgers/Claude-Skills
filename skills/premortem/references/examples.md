# Examples: From Label to Mechanism to Decision

This file shows what excellent premortem analysis looks like at each stage.

## Example 1: Product Launch (SaaS)

### Starting Input (User's Vague Concern)

"We're launching a new analytics dashboard for our enterprise customers next month. I'm worried we're going to have adoption issues."

### Stage 1: From Label to Mechanism

**Poor version (label):**
"Adoption risk. Customers may not use the new dashboard. Recommendation: strong change management."

**Good version (mechanism):**
"Because enterprise customers have existing BI tools and analysts are trained on those workflows, the dashboard competes against established habits, not a vacuum. Adoption risk arises if the dashboard doesn't solve problems the analysts already face (speed, flexibility, integration with existing reports). Customers go back to legacy tools when they encounter friction. The team assumes 'if we build it, they will come,' but adoption is actually a choice customers make every day."

**Excellent version (with countercase and evidence status):**
"Because enterprise customers rely on existing BI tools and analysts have invested expertise in those workflows (OBSERVED from customer calls), the new dashboard competes against habit and switching cost, not a vacuum. The primary risk is not visibility but *value*: if the dashboard doesn't solve a problem the analysts currently face faster than their existing tools, they will revert. This is not a marketing problem (which would suggest 'educate them better'); it's a product-market fit problem.

Evidence status:
- Analysts have existing workflows: OBSERVED from 12 customer interviews
- Switching cost is real: ASSUMED (not quantified; interviews suggested it but not measured)
- Speed/flexibility/integration matter: INFERRED from problem statement in calls; not validated with measurement

Countercase:
If the new dashboard is demonstrably faster or enables analyses that legacy tools cannot, adoption could be high and sticky. Evidence: We would see >60% of pilot users voluntarily returning to the dashboard 2 weeks after pilot ends, even without corporate mandate.

What would change the judgment:
- If we measure pilot adoption against a matched cohort still using legacy tools and adoption is >70% sustained voluntary use
- If the dashboard's query speed is <1 second (vs. legacy tools' 5–10 seconds)
- If the dashboard solves a top-3 customer pain point that legacy tools don't"

### Stage 2: From Mechanism to Signal & Tripwire

**Poor version (generic):**
"Recommendation: Monitor adoption closely."

**Good version (observable signal):**
"The premortem should produce a leading indicator: 2-week voluntary return rate. After the pilot sponsorship period ends (Day 21), measure the percentage of analysts who voluntarily use the dashboard at least once per week. If that rate is <50%, adoption will likely not sustain through broader rollout."

**Excellent version (signal + tripwire + action):**
"Leading indicator: After pilot sponsorship pressure ends (Day 21), measure voluntary 14-day return rate. This is the percentage of analysts in the pilot who, in the 14 days after the pilot ends and corporate pressure is lifted, use the dashboard at least twice without prompting.

Tripwire: If voluntary 14-day return rate is below 50%, we have evidence that adoption is driven by mandates, not value. In that case:
- Pause Wave 2 rollout (scheduled for Month 4)
- Conduct root-cause interviews: Which analysts returned? Which didn't? Why?
- If root cause is performance or missing features: fix them before Wave 2
- If root cause is misalignment with workflow: reconsider the value prop or scope

Last safe moment: Adoption decision must be made by end of Month 3. Wave 2 procurement begins Month 3, and commitments become expensive to reverse after that."

### Stage 3: From Signal to Decision Consequence

**Poor version (no decision):**
"Recommendation: Monitor adoption; be ready to pivot if needed."

**Good version (decision tied to signal):**
"If voluntary 14-day return rate is >50%, proceed with Wave 2 as planned. If <50%, pause and investigate before committing to Wave 2."

**Excellent version (explicit decision tree):**
"Return rate >50%: Adoption is voluntary and sticky. Proceed with Wave 2 on schedule. Hypothesis: dashboard solves a real problem.

Return rate 30–50%: Adoption is moderate. Before Wave 2:
- Conduct 5–10 analyst interviews to understand barriers
- If barrier is UX/speed: allocate 2 weeks to performance and usability fixes
- If barrier is integration/data freshness: allocate 2 weeks to data layer fixes
- If barrier is workflow misalignment: reconsider product direction; consider a phased rollout instead of full Wave 2

Return rate <30%: Adoption is weak and likely mandate-driven. Decision options:
- Option A: Pause rollout; reassess whether the dashboard solves a real customer need
- Option B: Pivot to a 'power users first' rollout (analytics teams, not all analysts)
- Option C: Combine dashboard with training/incentives to drive habit formation
- Option D: Reduce scope; integrate dashboard features into existing BI tool instead

Pre-commitment: By end of Month 3, leadership chooses one of these paths. Proceeding with Wave 2 without resolving adoption weakness is not an option—it commits budget and customer attention to a weak value prop."

---

## Example 2: Technical Architecture Change (Internal System)

### Poor Version (Category Risk)

"Technical risk. Database migration is complex. Recommendation: extensive testing."

### Good Version (Mechanism)

"The database migration involves a 5-year-old system with 200+ undocumented stored procedures, inconsistent data schemas across tables, and 15+ downstream services that query the old system. The technical risk is not that we can't migrate the schema—it's that undocumented procedures and edge-case data patterns will break when we move. Existing controls (schema mapping doc, test coverage) don't account for:
- Stored procedures that rely on undocumented behavior (edge case behaviors we don't know about)
- Query performance assumptions (queries that work on old hardware may timeout on new)
- Implicit data constraints (data that 'should be' not NULL but actually sometimes is)

Production consequence: Services fail. Customer-facing queries time out or return wrong data. Revenue impact occurs within hours. Recovery requires reverting to old database, losing data written since migration, and explaining to customers why we're going backward."

### Excellent Version (With Controls & Tripwire)

**Risk:** Migration breaks downstream services due to undocumented procedures and edge-case data patterns.

**Mechanism:**
[As above]

**Evidence:**
- 200+ stored procedures: OBSERVED from code inventory
- 15+ downstream services: OBSERVED from dependency map
- Undocumented behavior: ASSUMED (common; specific procs not yet audited)
- Performance assumptions: INFERRED from current query patterns

**Countercase:**
If we audit all 200+ procedures before migration and update tests to cover observed edge cases, the risk is lower. Evidence: We would see zero procedure-related test failures in pre-prod migration if we've captured the real behavior.

**Controls:**
- Prevent: (1) Audit all 200+ stored procedures for undocumented behavior (2 weeks); (2) Add test cases for edge cases found in audit; (3) Performance-test queries on new hardware before migration
- Detect: Run pre-prod migration; run full regression suite; measure query performance vs. baseline
- Respond: If regression suite finds failures, fix them in pre-prod and re-test; do not proceed to production until regression suite passes 100%
- Recover: Keep old database available for 48 hours after production migration; practice rollback procedure; have full backup
- Exit: If pre-prod migration reveals more than 10% failure rate or more than 3 hours of recovery time, delay production migration by 1 quarter and conduct deeper audit

**Leading Indicator:**
Regression suite pass rate during pre-prod migration. If <99% on first run, we have evidence that edge cases are not fully captured. On second run (after fixes), if <99.9%, we still have hidden edge cases.

**Tripwire:**
If pre-prod regression suite pass rate is <98% after two fix iterations, do not proceed to production. This signals that the testing strategy is not capturing real system behavior.

**Decision:**
- Change now: Allocate time for stored procedure audit (don't assume behavior is what we think)
- Test before commitment: Run full pre-prod migration + regression + performance test before any production commitment
- Monitor: Regression suite pass rate; query performance metrics; downstream service error rates (first week post-migration)
- Contingency: Old database available; rollback playbook tested; practice run with data
- Rerun trigger: After pre-prod migration, if any significant edge case is discovered, rerun this premortem before production

---

## Example 3: Organizational Change (Difficult/Political)

### Poor Version (Label + Defensiveness)

"Change management risk. Employees might resist. Recommendation: communication plan and training."

### Good Version (Mechanism + Uncomfortable Truth)

"Because the new organizational structure consolidates Regional Sales into Central Operations, regional sales managers lose direct revenue authority and get moved to a dotted-line relationship. This is a demotion in status and compensation (commission structure changes). These managers have deep customer relationships and the power to leave. Existing control (communication plan) assumes the problem is information ('people don't understand why'); but the actual problem is incentives ('I lose money and status'). A better communication plan does not solve an incentive problem. Consequence: Key salespeople leave within 3 months. Customer relationships and pipeline are disrupted."

### Excellent Version (With Minority Report & Political Cover)

**Risk:** Sales leadership turnover due to incentive misalignment; loss of customer relationships.

**Mechanism:**
[As above]

**Evidence:**
- Regional managers have revenue authority now: OBSERVED from current org chart and compensation structure
- New structure eliminates that authority: OBSERVED from proposed org chart
- Compensation tied to regional revenue: OBSERVED from current sales comp plan
- New comp plan has lower leverage for regional managers: OBSERVED (preliminary draft)

Assumption: These managers will view this as a demotion. This is reasonable but not certain.

**Countercase:**
If the new structure increases total compensation (bonus structure compensates for lost revenue authority), or if new structure broadens their influence (e.g., they become CRO advisors), they might embrace the change. Evidence: We would know this if (a) compensation modeling shows total comp is stable or higher, and (b) managers' input shaped the design (vs. designed for them).

**Uncomfortable hypothesis (preserved explicitly):**
There is a political dynamic: the Executive Sponsor wants centralized control and is willing to accept some turnover to achieve it. The assumption is that "we can replace regional managers if they leave." This may or may not be true (market may be tight; customer relationships may be irreplaceable). But if the Sponsor's priority is control > retention, the premortem should name that. It changes the decision tree.

**Controls:**
- Prevent: (1) Redesign comp plan so total comp for regional managers is stable or increases; (2) Involve regional managers in org design before announcement (they have information about customers and risks)
- Detect: Month 1: Turnover among regional managers; Month 1: Retention interviews with top 20 salespeople
- Respond: If turnover >10% in first month, immediately engage departing managers (counter-offer if possible); conduct rapid interviews with flight risks
- Recover: Have a backlog plan for customer coverage if turnover exceeds 15%
- Exit: If turnover reaches 25%, pause expansion plans and focus on stabilization

**Leading Indicator:**
Within 2 weeks post-announcement, conduct pulse survey of regional managers: "On a scale of 1–10, how confident are you in your role and compensation in the new structure?" Responses <6 are a leading indicator of turnover risk.

**Tripwire:**
If >50% of regional managers rate confidence <6 in the pulse survey, or if any of the top 5 revenue-generating regions express major concerns, convene regional leadership within 48 hours to address specifics before resignations occur. Do not assume communication will solve an incentive problem.

**Decision:**
- Change now: Finalize new comp plan before announcement; ensure regional managers' input shaped the design
- Test before commitment: Present org design to top 10 regional managers; gather feedback on incentives and career path before public announcement
- Monitor: Turnover within first month; pulse survey; retention interviews
- Contingency: Have a transition plan for customer coverage if turnover is higher than expected; backfill resources
- Minority report: Name the political dynamic (control vs. retention trade-off); make explicit that some turnover may be acceptable to leadership; ensure Sponsor and HR agree on acceptable turnover threshold before announcement
- Rerun: After first month if turnover is >10% or if top-revenue regions express major concerns

---

## Example 4: AI Workflow Premortem

### Poor Version (AI Cliché)

"AI risk. Model might hallucinate. Recommendation: add guardrails."

### Good Version (Specific Failure Mode)

"Because the model is asked to synthesize research across 10+ complex papers and extract a policy recommendation, and because the evaluation set doesn't test for hallucination on novel combinations of concepts, the model will confidently state false causal relationships. Specifically: it will invent a study or misquote a finding to support a plausible-sounding narrative. Consequence: leadership makes policy decisions based on fabricated evidence. Reputational damage if the hallucination is discovered; policy harm if it's not."

### Excellent Version (With Evidence Tiers & Control Engineering)

**Risk:** Model hallucinates causal claims and attributes them to studies that don't support (or don't exist them).

**Mechanism:**
Because the model is operating at the edge of its training distribution (synthesis across 10+ papers on a novel policy question), it generates plausible-sounding but unsupported causal claims. The evaluation set used to assess the model does not test this specific failure mode (evals focused on factual extraction, not causal synthesis). Existing controls (instruction to 'cite sources') are insufficient—the model confidently cites sources even when its claim misrepresents the source. Consequence: Leadership implements policy based on hallucinated evidence. Reputational damage if discovered; policy harm if not.

**Evidence:**
- Model operating at edge of distribution: INFERRED from task complexity and training data
- Plausible-sounding fabrication is common: EXTERNAL EVIDENCE (see eval literature on hallucination)
- Evaluation set doesn't test causal synthesis: OBSERVED from test suite review
- Citation-following instruction is insufficient: OBSERVED from prior similar tasks

**Countercase:**
If we add a human expert step (senior researcher reviews causal claims and checks citations against actual papers) before findings reach leadership, the risk is mitigated. If we narrow the task scope (extract findings only, don't synthesize causality), the risk is lower. Evidence: We would see zero fabricated causal claims in a human expert review of 100 synthesis outputs.

**Disconfirmation:**
What controls already exist?
- Instruction to cite sources (insufficient alone)
- Model is state-of-the-art (better than earlier models, but not perfect)
- Researcher reviews outputs (but may not catch all misquotations if they're subtle)

What would make the risk less likely?
- Human expert review before output reaches leadership
- Explicit evidence tiers (observed vs. inferred vs. speculative) in output
- Automated citation-checking script
- Narrower task scope (findings only, no synthesis)

**Leading Indicator:**
In a test of 20 synthesis outputs, count how many causal claims are either (a) directly supported by the cited source, or (b) explicitly flagged as inference/speculation. If >10% of causal claims are unsupported or misquoted, the hallucination risk is active.

**Tripwire:**
If independent expert review of model outputs finds >5% unsupported causal claims, halt the workflow and add a human-expert-review gate before any output reaches leadership decision-makers.

**Controls:**
- Prevent: (1) Explicit instruction to distinguish observed findings from inferences; (2) Automated citation-check script that validates claim against actual paper; (3) Narrow task scope to findings extraction + metadata, not causal synthesis
- Detect: Expert review of 20 sample outputs; automated citation checking; tracking hallucination rate over time
- Respond: If hallucination rate exceeds threshold, route outputs to human expert for review before leadership sees them
- Recover: If hallucinated finding reaches leadership and policy decision is made, have a 48-hour reversal window (announcement: "We need to verify this finding before proceeding")
- Exit: If hallucination rate remains >5% despite interventions, do not use the model for policy-critical synthesis; revert to human-only research

**Decision:**
- Change now: Add explicit instruction for evidence tiers; build automated citation checker before deployment
- Test before commitment: Run model on 20 diverse synthesis tasks; have independent expert review for hallucinations
- Monitor: Hallucination rate per quarter; expert review sampling (ongoing 5% of outputs)
- Contingency: Human expert review gate in place before leadership decision; 48-hour reversal window if hallucination is discovered post-decision
- Rerun trigger: After first 100 uses of the workflow; if model is upgraded; if domain shifts (new papers, new policy questions)

---

## Key Patterns Across Examples

### From Poor to Excellent:

1. **Labels become mechanisms**: "Adoption risk" → "Users need new habits; legacy tools are faster; incentives point to legacy system; adoption collapses when pressure ends"

2. **Assumptions become evidence tiers**: "We assume X" → "X is OBSERVED / ASSUMED / INFERRED / SPECULATIVE; here's why"

3. **Generic mitigations become controls**: "Monitor closely" → "Leading indicator: [metric] measured at [frequency]; Tripwire: if [threshold], then [action]; Owner: [name]; Decision by [date]"

4. **Vague decisions become decision trees**: "Pivot if needed" → "If metric >X, do A. If metric X–Y, do B. If metric <Y, do C. Decision point: [date]."

5. **Uncomfortable truths get preserved**: Political dynamics, capability gaps, and incentive misalignment are named explicitly, not buried.

---

## Quality Checklist for Examples

- [ ] Does the risk explain *how* failure happens, not just what could fail?
- [ ] Are evidence categories clear (observed, assumed, inferred, speculative)?
- [ ] Is there a countercase that seriously challenges the risk?
- [ ] Is there a leading indicator that can be measured before the failure is obvious?
- [ ] Is there a tripwire with a specific threshold and predetermined action?
- [ ] Does the decision consequence change what the organization will do?
- [ ] Are uncomfortable/political dimensions named explicitly?
- [ ] Is there a decision point and a date by which it must be made?

If all yes, you have an excellent premortem risk. If no to any, go deeper.
