# Failure-Lens Catalog

After free-form generation, use these lenses to scan for missing failure classes. Don't force every lens into every premortem—use selectively to expand coverage.

## Execution & Delivery

- **Schedule slip**: Timeline compresses testing, review, or learning time
- **Resource shortage**: Key people leave, budget is cut, or competing priorities emerge
- **Dependency failure**: A vendor, partner, or upstream team misses their commitment
- **Quality/testing gap**: Insufficient time to find and fix defects before launch
- **Integration failure**: Components work independently but fail when combined
- **Communication breakdown**: Critical information doesn't reach the people who need it

## People & Incentives

- **Skill gap**: The team lacks expertise required; training is inadequate
- **Motivation misalignment**: What people are rewarded for points the wrong direction
- **Turnover**: Key people leave before the initiative is stable
- **Resistance/sabotage**: People actively work against the change
- **Overconfidence**: Team believes the risk is managed when it is not
- **Burnout**: Pace or scope exhausts the team; quality drops

## Adoption & Behavior Change

- **Habit formation fails**: Users comply during pilot but don't form new habit when pressure falls
- **Ease-of-use problem**: New way is harder than old way; people revert
- **Legacy system stronger**: Old system is faster, safer, more trusted; people stick with it
- **Incentive points wrong way**: Users (managers, staff) are rewarded for behavior that doesn't support adoption
- **Switching cost too high**: Effort to change exceeds perceived benefit
- **Peer effects**: Early adopters do not influence the broader population

## Market & External

- **Market conditions change**: Customer demand, competitive landscape, regulatory environment shifts
- **Customer needs different**: What we built doesn't match what customers actually want
- **Timing wrong**: Market is not ready; we launched too early or too late
- **Competitor response**: Someone else moves faster or better
- **Vendor viability**: Vendor is acquired, goes out of business, or changes terms

## Technical & System

- **Scalability failure**: System works at pilot scale but fails at full scale
- **Performance degradation**: System is too slow, too expensive, or too resource-intensive
- **Data quality**: Data is incomplete, inconsistent, or unreliable
- **Security/privacy**: Breach, compliance failure, or unintended exposure
- **Interoperability**: Integration with other systems is harder than expected
- **Maintainability**: System is difficult to update, patch, or extend

## Dependencies & Common-Mode Failures

- **Single point of failure**: Multiple defenses depend on the same assumption or resource
- **Correlated risks**: Multiple independent-seeming risks share a root cause
- **Vendor lock-in**: Plan depends on a single vendor; vendor risk is not mitigated
- **Decision-maker dependency**: Key approvals rest with one person; their absence blocks progress
- **Knowledge concentration**: Critical information lives with one person; turnover is catastrophic

## Organizational & Political

- **Leadership misalignment**: Sponsor and stakeholders have conflicting goals
- **Conflicting incentives**: What advances the initiative hurts other parts of the org
- **Cultural resistance**: Initiative conflicts with "how we do things here"
- **Bureaucracy/slow decisions**: Org processes block timely action
- **Scope creep**: Initial agreement expands; commitment and budget do not
- **Sponsor withdrawal**: Sponsor's attention/support fades before completion

## Safety, Compliance & External Risk

- **Regulatory surprise**: Unexpected regulatory requirement or policy change
- **Audit failure**: Internal or external review finds problems
- **Liability/legal**: Unintended legal or liability exposure
- **Reputational damage**: Public failure harms brand or trust
- **Safety incident**: Operation causes physical harm or creates safety risk
- **Data loss or corruption**: Unrecoverable loss of critical data

## Success-Caused Failures

- **Pilot overstates adoption**: Pilot success is artifacts of sponsorship; voluntary adoption is lower
- **Early visibility creates pressure**: Public commitment before readiness; can't scale back
- **Scope expands from success**: Initial win prompts requests for more; plan becomes unrealistic
- **Resources reallocated**: Early success causes org to pull resources for other initiatives
- **False confidence**: Early wins mask downstream risks

## Information & Feedback Gaps

- **Metrics hide truth**: KPIs look healthy but reflect what's measurable, not what matters
- **Feedback lag**: By the time the problem is visible, it's hard to reverse
- **Groupthink**: Team and leadership see only confirming evidence
- **No early warning**: No leading indicator of the failure mode
- **Surprises from field**: Problems emerge in operation that weren't visible in design/test

## Model-Specific Risks (AI/ML Systems)

See `ai-agent-lenses.md` for risks specific to AI workflows, agents, and LLM-powered systems.

---

## How to Use This Catalog

1. After free-form generation, read this list
2. For each lens, ask: "Did anyone mention this? Is it plausible for this initiative?"
3. If the answer is "no and yes," investigate: Add it to the risk list
4. Don't force-fit lenses that don't apply
5. Cluster the expanded list by mechanism, not by lens category

**Example:**
- Lens: "Habit formation fails"
- For this initiative: "Are there adoption habits to form?"
- Investigation: "Yes—users need to shift from manual reporting to system entry. What makes new habits stick?"
- Expanded risk: "Because the new system requires 5 extra clicks per entry and managers still reward speed-to-report, staff will optimize for legacy workflow even if the new system is officially mandated. The pilot looks good because corporate oversight enforces compliance, but voluntary adoption is lower. When oversight ends, usage collapses."

This is much richer than "adoption risk."
