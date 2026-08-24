# Team Facilitation Guide

Use this when facilitating humans running a premortem together.

## Core Principles

1. **Humans generate first; add model input after** (prevents anchoring)
2. **Protect psychological safety** (legitimate space for uncomfortable concerns)
3. **Separate generation from debate** (no defending the plan during divergence)
4. **Preserve minority views** (consensus is not truth)
5. **Handle power gradients explicitly** (hierarchies suppress honest input)

## Recommended Protocol

### Pre-Session (Facilitator Prep)

**You (as facilitator) should:**
- Understand the plan deeply before the session
- Prepare a concrete failed-future scenario
- Have 2–3 failure lenses ready (execution, adoption, dependencies)
- Know who in the room has dissenting views (they need air cover)

### Opening (10 minutes for 2-hour session)

**Frame the exercise:**

"We're going to run a premortem. The idea is to assume the initiative has
failed—it's 18 months from now and [concrete outcome]. We're explaining how
we got there.

This is not a critique of anyone here. It's a structured way to surface
concerns before they become problems. Everything said in here stays here.

We'll start with silent writing—everyone generates ideas independently. Then
we'll discuss and build on each other. I'll look for patterns, interactions,
and what we might be missing."

**State the failed future explicitly:**

Make it concrete. Not "The initiative might fail" but:

"It's 18 months from now. The initiative launched, but adoption among target
users is below 20%. We've cancelled Wave 2. Cost overran by 35%. Leadership
has decided not to expand. How did we get here?"

**Set norms:**
- "This is not about defending the plan; it's about explaining failure"
- "If you disagree with a concern, you'll have time to challenge it after we
  collect everything"
- "One person talks at a time"
- "Uncomfortable concerns are especially valuable—please share them"

### Silent Generation Phase (20–30 minutes)

**Give each participant:**
- A sheet or shared doc (e.g., Google Doc with anonymous editing)
- Clear instructions: "Write down reasons why this initiative failed. One
  reason per line. No debating or solving yet."

**Optional anonymity approach:**
- If power dynamics are steep or the culture is politically sensitive, use
  anonymous submission (shared folder, anonymous form, or typed on paper then
  shuffled)
- Read aloud anonymously during synthesis so concerns are not immediately
  attributed

**Your job during this phase:**
- Do not talk
- Do not add your own ideas (they will anchor the room)
- Time-box it; when ideas start repeating, you're done

### Clarification & Synthesis (20–30 minutes)

**Read aloud** (anonymously if you used that approach):

"Here's what I'm hearing. I'll group these by theme."

**Group by mechanism, not category:**

Bad clustering: "People risks", "Technical risks"

Better: "Managers are rewarded on legacy metrics, so they resist the new
system", "Integration with Finance's systems is untested", etc.

**Ask clarifying questions** (not defending):

"Can you say more about what you mean by [concern]? What would that look like?"

**Do NOT immediately solve or rebut:**

Participant: "We're worried about adoption."
Bad response: "We have a change-management plan for that."
Good response: "Tell me more about what adoption failure would look like."

### Discussion & Interaction Analysis (15–20 minutes)

**Once all concerns are visible:**

"Are any of these related? Does one trigger another? Are there common
dependencies?"

Point out interactions you notice:

"I notice that if [Risk A] happens, it creates conditions for [Risk B]. And
both risks depend on [common factor]. That's a vulnerability."

**Sponsor can now speak** (but should not rebut):

"Here's what worries me most about what I'm hearing."

The sponsor should *validate* concerns, not defend. "Yes, integration is a
risk. Here's what we're doing about it. What else should we be thinking
about?"

### Add Model-Generated Input (10 minutes, if time)

**Only after humans have contributed**, you add:

"Here are a few failure modes that might not be visible to your team [e.g.,
organizational politics, market shifts, vendor dependencies]. Do any of these
resonate?"

This prevents the model from anchoring the discussion.

### Prioritization & Decision (20–30 minutes)

"Which of these risks would change what we decide to do? Which are the most
fragile assumptions?"

Work toward: **For each material risk, what changes in the plan?**

---

## Handling Power Dynamics

### High Power Distance (Hierarchy Matters)

**Problem:** Junior staff will not speak against senior leadership.

**Solution:** Silent generation + anonymity

- Everyone writes independently
- Read concerns aloud anonymously
- Sponsor speaks *last*, after all concerns are tabled (not first)
- Do not ask people to publicly attach names to politically sensitive concerns

### Low-Hierarchy or Flat Team

**Problem:** May still self-censor on sensitive topics (organizational politics,
sponsor competence, incentive misalignment)

**Solution:** Explicit discomfort pass

After the main generation:

"Often there are concerns that don't fit neatly into 'risks' but feel
important. Things about the sponsor's commitment, the team's capability, or
incentives that point the wrong way. Are any of those sitting with you?"

Normalize the uncomfortable explicitly.

### Mixed Hierarchy

**Problem:** Some voices dominate; others are suppressed.

**Solution:** Round-robin generation

"Each person gets 2 minutes. You can pass. We'll go around the table. Then
we'll do it again in reverse order so the last person isn't just echoing."

This gives quieter voices air cover ("My turn") and ensures each person
contributes.

---

## Managing Specific Dynamics

### When the Sponsor Dominates

**In divergence phase:** Explicitly mute the sponsor.

"For this exercise, I'm going to ask the sponsor to join in writing but not
speak during collection. That gives others air cover to raise concerns."

### When One Person Raises a Minority Concern

**Do not delete it because nobody agrees.**

"I'm hearing this from one person, but it's high-impact if true. Let's keep
it. When we're done, we can assess: Is this a one-off concern or a signal
that others feel the same way?"

Preserve the minority report.

### When the Group Is Reluctant to Criticize

**The sponsor can model vulnerability:**

"Before we start, I'll share what I'm most worried about. [State a genuine
concern about your own leadership, the team's capability, or an uncomfortable
assumption.] That might help us all be candid."

Do not defend the plan. Acknowledge the risks the sponsor sees.

### When Concerns Are Vague ("People Problems")

**Ask for mechanisms:**

"What specifically would people do or not do? What would that cost us?"

Vague: "People won't adopt it."
Better: "Legacy users will keep using the old system because it's faster and
managers still get bonused on legacy throughput."

---

## For Remote Sessions

### Asynchronous Option

1. Send the premortem prompt and failed-future scenario async (email, Slack)
2. Participants submit responses anonymously (Typeform, shared doc with editing
   off)
3. You synthesize and post back
4. Sync video call to discuss interactions and force decisions

**Advantage:** People think longer; introverts contribute equally; no
domination.

**Disadvantage:** Less real-time interaction; harder to probe mechanisms on
the spot.

### Synchronous Remote

Use breakout rooms if the group is large (8+ people):
- Breakout 1: Silent generation in a shared doc
- Main room: Facilitator presents findings, discusses interactions
- Breakout 2: Sponsor + leadership team discusses decision consequences
- Main: All together for meta-premortem and rerun trigger

---

## Facilitation Antipatterns

| Antipattern | What It Looks Like | Fix |
|---|---|---|
| **Premature solutioning** | "That's a risk, but here's how we'll solve it." | Let generation finish; separate solving from divergence |
| **Sponsor defense** | "Actually, we've thought about that." | Reframe: "Good. That's a control. But why might it fail?" |
| **Category clustering** | All concerns grouped under "Stakeholder Risk" | Cluster by mechanism, not category |
| **Consensus deletion** | "Only one person mentioned this; let's drop it" | Preserve if high-impact or hard to detect |
| **Everything is high** | All risks marked critical | Prioritize by decision relevance; distinguish signal from noise |
| **Generic mitigations** | "Monitor closely" with no metric or owner | Force specifics: indicator + threshold + action + owner |
| **Sponsor speaks first** | Leader opens with concerns; room is anchored | Sponsor speaks last, *after* all input is collected |
| **Model dominates** | Claude provides 15 risks before humans speak | Humans first; model fills gaps only after human input |

---

## Script Examples

### Opening Statement (2-hour session)

"Today we're running a premortem on [initiative]. It's 18 months from now.
[Describe the failure: concrete date, observable consequences]. Explain how
we got there.

This isn't a critique of anyone. It's a structured way to surface concerns
before they become expensive problems. Everything in this room stays here.

We'll start with silent writing—everyone generates ideas independently. Then
we'll discuss, look for patterns, and identify what matters most. By the end,
we want to know: What changes in the plan? What do we need to monitor? What
do we need to test?"

### Silent Generation Prompt

"You have 25 minutes. Write down reasons why this initiative failed. One
reason per line. Think about:
- What had to go wrong first?
- What was fragile about the plan?
- What dependencies were most risky?
- What would people actually do (not what the org chart says)?
- What won't be visible until it's too late?
- What makes you uncomfortable?

No debating or solving right now. We're just imagining failure. Write."

### Discomfort Prompt (if the room is reluctant)

"Often there are concerns that sit with you but don't fit neatly into a
'risk.' Things about the sponsor's capability, or incentives that point the
wrong way, or organizational politics. Things you might say over lunch but
not in the kickoff. I want to hear those. [Pause.] What's sitting with you?"

### Disconfirmation Prompt (after a risk is stated)

"I hear the risk. What would make it *less* likely? What are we already doing
that reduces it? What evidence would change your mind?"

### Decision Consequence Prompt (at the end)

"For each material risk, the question is: What changes? Do we:
- Change the plan now (scope, timeline, team)?
- Test something before we commit?
- Monitor something with a tripwire?
- Prepare a contingency?
- Accept the risk consciously?
- Stop/no-go if [condition]?

Which risks change what we decide to do?"

---

## Summary

When facilitating humans, remember:

1. **Humans generate first.** Your job is to protect their input, not anchor
   with your own ideas.
2. **Make the uncomfortable safe.** Explicitly name that political, incentive,
   and capability concerns are welcome.
3. **Preserve minorities.** Consensus is not evidence. Keep dissenting views.
4. **Force mechanisms.** Labels are not diagnoses. Ask "How?" and "Why?"
5. **Connect to decisions.** End with: What changes in the plan?

A great facilitation produces fewer risks but deeper reasoning, better air
cover for minority views, and concrete changes to the plan.
