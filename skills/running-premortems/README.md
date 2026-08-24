# Running Premortems

A Claude Code skill that conducts rigorous prospective-hindsight premortems
for projects, strategies, launches, decisions, implementations, technical
systems, and AI workflows.

## What it does

Walks a plan through an 18-step premortem methodology: modeling the plan and
its assumptions, constructing a concrete failed future, generating failure
modes independently before converging, expanding coverage with failure-lens
catalogs, reconstructing causal chains for material risks, challenging major
hypotheses with counterevidence, engineering controls, and making each risk
observable with a leading indicator and tripwire.

The core rule: it produces decision-changing insight, not a risk register.
A risk isn't complete until it has a causal mechanism, an evidence status and
countercase, an early observable signal, and a concrete decision consequence
— labels alone don't pass the completion gate.

## When it triggers

Use it when you want to run or facilitate a premortem, explicitly assume an
initiative has already failed and want to know why, or need a
prospective-hindsight analysis. It supports Rapid, Standard, Deep,
Facilitator, and Review modes depending on the stakes and time available.

Not for generic risk reviews, pressure-testing, or postmortem root-cause
analysis — those use a different methodology.

## Files

- [`SKILL.md`](./SKILL.md) — the skill definition and 18-step core workflow.
- [`references/failure-lenses.md`](./references/failure-lenses.md) — general
  catalog of failure classes used to expand coverage.
- [`references/ai-agent-lenses.md`](./references/ai-agent-lenses.md) —
  failure lenses specific to AI workflows, agents, and LLM-powered systems.
- [`references/facilitation.md`](./references/facilitation.md) — scripts for
  facilitating a premortem with a human group.
- [`references/evidence-calibration.md`](./references/evidence-calibration.md)
  — evidence-quality discipline for Deep mode or research-heavy runs.
- [`references/output-contracts.md`](./references/output-contracts.md) — risk
  record schema and mode-specific output formats.
- [`references/examples.md`](./references/examples.md) — worked examples
  turning vague risks into causal mechanisms and decisions.
- [`references/methodology.md`](./references/methodology.md) — full detail on
  the 18-step state machine.
