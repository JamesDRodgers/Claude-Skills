# AI & Agent System Failure Lenses

Use these lenses when the object of the premortem is an AI workflow, LLM-powered agent, ML system, or AI-enabled product.

## Triggering & Input Failures

- **Trigger too broad**: Agent activates on requests it shouldn't handle; produces out-of-scope output
- **Trigger too narrow**: Agent should activate but doesn't; misses opportunities
- **Ambiguous intent**: User query is ambiguous; agent misinterprets what to do
- **Context incomplete**: Agent lacks information needed to reason correctly
- **Edge case not recognized**: Agent encounters input it was not trained/designed for
- **Invalid input passes**: Malformed or hostile input reaches the agent without filtering

## Reasoning & Decision Failures

- **Hallucination**: Agent invents facts, citations, or evidence that don't exist
- **Shallow reasoning**: Agent stops at surface-level analysis instead of deeper reasoning
- **Logical error**: Agent makes an inference mistake or misapplies a rule
- **Preference reversal**: Agent's recommendation contradicts earlier guidance or user values
- **Overconfidence**: Agent states conclusions with certainty when uncertainty is warranted
- **Underconfidence**: Agent expresses doubt about things it should be confident about

## Tool & Integration Failures

- **Wrong tool choice**: Agent selects a tool that doesn't apply or is suboptimal
- **Tool execution fails**: Tool call syntax is wrong or the tool is unavailable
- **Incomplete tool use**: Agent doesn't use tools when it should; relies on memory instead
- **Tool chain breaks**: Sequence of tools fails partway through; agent doesn't recover
- **Data fetch failure**: Agent tries to retrieve external data but fails (API down, permission denied)
- **Integration mismatch**: Agent output doesn't integrate cleanly with downstream systems

## Evidence & Calibration Failures

- **Distinction lost**: Agent treats confident claims and speculations as equally certain
- **Sourcing weak**: Agent cites or invokes evidence that isn't primary or reliable
- **False precision**: Agent presents probability or percentage when it's really ordinal
- **Base rate ignored**: Agent forgets outside-view evidence in favor of inside-view story
- **Confirmation bias**: Agent seeks evidence that confirms its initial hypothesis
- **No disconfirmation**: Agent doesn't seriously challenge its own conclusions

## Composition & Orchestration Failures

- **Skill interference**: Two skills or agents in sequence work at cross-purposes
- **State not carried**: Information from one step is not available to the next
- **Precedence wrong**: Steps are ordered incorrectly; earlier steps should depend on later ones
- **Premature termination**: Agent exits before completion when it should continue
- **Runaway loop**: Agent keeps doing something without recognizing it's not productive
- **Deadlock**: Two agents or systems wait for each other; no progress

## Performance & Resource Failures

- **Latency too high**: Agent is too slow for the use case (interactive vs. batch expectations)
- **Token budget exceeded**: Agent generates too much output relative to available tokens
- **Cost per request too high**: Model calls and API usage make the system economically unviable
- **Memory limit**: Agent hits context window limit and loses information
- **Cascade effect**: One failure (e.g., one API call) cascades into repeated failures
- **Efficiency regression**: Agent performance was acceptable but degrades with model/config change

## Prompt & Instruction Failures

- **Instruction too vague**: Agent has latitude and makes inconsistent choices
- **Instruction too rigid**: Agent treats rules as absolute and fails on edge cases
- **Contradiction in instructions**: Agent is told to do two incompatible things
- **Instruction interpreted wrong**: Agent understands the instruction differently than intended
- **Instruction ignored**: Agent doesn't follow the instruction even though it's clear
- **Instruction creep**: Over time, instructions accumulate and become contradictory

## Model Behavior Failures

- **Model change breaks behavior**: New model version changes outputs (style, reasoning, risk tolerance)
- **Jailbreak/prompt injection**: User input tricks the agent into ignoring its guidelines
- **Bias or unfairness**: Agent's outputs reflect or amplify historical biases
- **Inconsistent personality**: Agent sounds different across calls or contradicts its own persona
- **Context pollution**: Earlier requests in the conversation influence later reasoning inappropriately
- **Refusal when it shouldn't**: Agent refuses a legitimate request due to overly broad safety rules

## Runtime & Deployment Failures

- **Cold start latency**: First invocation is much slower (model load, cache miss)
- **Availability**: Agent goes offline or becomes unavailable during critical periods
- **Rollback not possible**: Agent behavior change is unrecoverable; no fallback
- **Config drift**: Agent behavior differs from what was tested due to deployment or config changes
- **Monitoring gap**: Failures are not detected until they affect users
- **Graceful degradation missing**: When something breaks, the whole system fails instead of degrading

## Trust & Safety Failures

- **Adversarial prompt**: User crafts input specifically designed to elicit bad behavior
- **Trust boundary crossed**: Agent operates outside intended scope (e.g., accesses data it shouldn't)
- **Permission escalation**: Agent is given more capability than necessary for the task
- **Data leakage**: Agent reveals sensitive information in its output
- **Unintended side effect**: Agent's actions have consequences beyond the immediate task
- **Auditability lost**: It's unclear why the agent made a decision or took an action

## Evaluation & Testing Failures

- **Evals don't match reality**: Tests pass but users see failures
- **Coverage gap**: Evals don't test the failure mode
- **Measurement wrong**: Eval metric doesn't capture what matters
- **Benchmark gaming**: Agent is optimized for eval metrics, not actual performance
- **Flaky evals**: Test results vary randomly; hard to know if something is truly fixed
- **No longitudinal eval**: Performance is good on Day 1 but degrades over time (distribution shift)

## Maintenance & Evolution Failures

- **Technical debt accumulates**: Agent becomes harder to modify, debug, improve
- **Knowledge bottleneck**: Only one person understands the agent; turnover is catastrophic
- **Skill/component conflicts**: Two pieces of the system work independently but fail together
- **Incomplete documentation**: It's hard to understand what the agent is supposed to do
- **No rollback plan**: If the agent fails, there's no fallback or recovery procedure
- **Obsolescence**: The agent remains deployed but is no longer useful; blocking removal

---

## How to Apply These Lenses

1. **Route:** Identify what the AI system is supposed to do
2. **Model:** How does it orchestrate (user → intent detection → tools → reasoning → output)?
3. **Generate:** For each lens category, ask: Is this a plausible failure for this agent?
4. **Reconstruct:** For each plausible failure, explain the causal chain (not just the label)
5. **Challenge:** What evidence would change the judgment? What existing safeguards already address it?

## Example

**Lens:** "Shallow reasoning"

**For this AI agent:** "Agent is supposed to run premortems. Could it provide surface-level risk lists instead of causal mechanisms?"

**Causal chain:** Because the agent is optimized for token efficiency and the SKILL.md does not enforce mechanism reconstruction strongly enough, the agent generates many generic risks ("stakeholder risk", "technical risk") without explaining causality. The user sees a long list but gains little insight. The premortem fails its primary goal: decision-changing insight.

**Countercase:** The SKILL.md explicitly requires causal chains; the eval process filters for mechanisms. Shallow reasoning would be caught in testing.

**Leading indicator:** If early test runs produce mostly categories instead of mechanisms, the instruction isn't working.

**Control:** Tighten the SKILL.md to require causal skeleton for each material risk; test early against mechanisms not categories; score evals on whether top risks explain *how* failure happens.

---

This lens set is not exhaustive—AI systems evolve. Adapt these lenses to your specific architecture and model.
