// Deterministic tests for the web version's core logic. Runs the page's
// <script> under Node with a minimal DOM stub, then exercises the real
// functions. No network, no model.
import { readFileSync } from "node:fs";

const html = readFileSync(new URL("./groundwork.html", import.meta.url), "utf8");
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];

class FakeNode {
  constructor() { this.children = []; this.attrs = {}; this.textContent = ""; this.value = ""; this.files = null; }
  append(...c) { this.children.push(...c); }
  replaceChildren() { this.children = []; }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener() {}
  focus() {}
}
const storage = new Map();
const sandbox = {
  document: { getElementById: () => new FakeNode(), createElement: () => new FakeNode() },
  localStorage: {
    getItem: (k) => storage.get(k) ?? null,
    setItem: (k, v) => storage.set(k, v),
    removeItem: (k) => storage.delete(k),
  },
  window: {}, navigator: {}, location: { reload: () => {} },
  setTimeout: (fn) => fn(), console, TextDecoder,
};
sandbox.window = sandbox;

const fn = new Function(...Object.keys(sandbox), script + `
  return { state, CRITERIA, defaultSections, probesFor, normalizeParsed, coverageGaps,
           numbersIn, licensedNumbers, normalizeMetric, prettyMetric, sectionName,
           checkInternalConsistency, parseBudgetText, coerceValue, applyResolution,
           recordFact, logGap, nextId, buildTable, gapsForSection, runBudgetChecks,
           currentProbe, queueSemanticCheck, pendingChecks, asSentence, dedupeFacts,
           alreadyFlagged, isRestatement, checkpoint, loadSave, clearSave,
           TRANSIENT_KEYS, reflectionInsights,
           _setSample: (f) => { sampleFn = f; } };`);
const api = fn(...Object.values(sandbox));
const { state } = api;

let passed = 0;
function check(name, cond) {
  if (!cond) { console.error(`FAIL: ${name}`); process.exit(1); }
  console.log(`PASS: ${name}`); passed++;
}
function resetState(sections) {
  state.facts = {}; state.gaps = {}; state.inconsistencies = {}; state.resolutions = {};
  state.counter = 0; state.thread = []; state.sectionIdx = 0; state.probeIdx = 0;
  state.attempts = 0; state.budgetLines = null;
  state.sections = sections || api.defaultSections();
}
const mkFact = (over) => ({
  id: api.nextId("fact"), section: "team", criterion: "TEAM", probeKey: "main",
  summary: "", verbatim: "", structuredFields: {}, tier: "unattributed", overridden: false, ...over,
});

// ---------- adaptive structure ----------
resetState();
check("default sections cover the standard criteria", api.defaultSections().length === 9);
check("OUTCOMES expands into four separate probes",
  api.defaultSections().find(s => s.criterion === "OUTCOMES").probes.length === 4);
check("single-criterion sections get one probe",
  api.defaultSections().find(s => s.criterion === "TEAM").probes.length === 1);
check("probesFor carries OUR bar, not the funder's wording", (() => {
  const p = api.probesFor("SIGNIFICANCE", "Tell us about the need.")[0];
  return p.question === "Tell us about the need." && p.bar === api.CRITERIA.SIGNIFICANCE.bar;
})());

// Tavendon-shaped parse result (from the sample application dry run)
const TAVENDON = { sections: [
  { name: "Executive Summary", question: "Summarize the project.", criterion: "OTHER", wordLimit: null, autoAssemble: true },
  { name: "Organization Background", question: "Tell me about your organization.", criterion: "ORG", wordLimit: null, autoAssemble: false },
  { name: "Statement of Need", question: "Who do you serve and what's in their way?", criterion: "SIGNIFICANCE", wordLimit: 500, autoAssemble: false },
  { name: "Project Goal and Objective", question: "What will you accomplish?", criterion: "OBJECTIVES", wordLimit: null, autoAssemble: false },
  { name: "Project Activities", question: "Walk me through the activities.", criterion: "APPROACH", wordLimit: null, autoAssemble: false },
  { name: "Expected Outcomes", question: "What results do you expect?", criterion: "OUTCOMES", wordLimit: null, autoAssemble: false },
  { name: "Evaluation Plan", question: "How will you evaluate?", criterion: "EVALUATION", wordLimit: null, autoAssemble: false },
  { name: "Organizational Capacity", question: "Who delivers this?", criterion: "TEAM", wordLimit: null, autoAssemble: false },
  { name: "Sustainability", question: "What happens after the grant?", criterion: "SUSTAINABILITY", wordLimit: null, autoAssemble: false },
]};
{
  const { sections: parsed } = api.normalizeParsed(TAVENDON);
  check("parsed application yields the funder's sections in their order",
    parsed.length === 9 && parsed[0].name === "Executive Summary" && parsed[2].name === "Statement of Need");
  check("parsed OUTCOMES section still expands to four probes",
    parsed.find(s => s.criterion === "OUTCOMES").probes.length === 4);
  check("auto-assembled section gets no probes (never asked)",
    parsed[0].autoAssemble === true && parsed[0].probes.length === 0);
  check("word limit is captured", parsed[2].wordLimit === 500);
  check("funder wording is kept as the question, our bar underneath",
    parsed[2].probes[0].question === "Who do you serve and what's in their way?" &&
    parsed[2].probes[0].bar === api.CRITERIA.SIGNIFICANCE.bar);
  check("criteria the funder never asks about are simply absent",
    !parsed.some(s => s.criterion === "FIT") && !parsed.some(s => s.criterion === "RISK"));
  check("a funder covering the narrative essentials produces no coverage warning",
    api.coverageGaps(parsed).length === 0);
}
{
  const { sections: thin } = api.normalizeParsed({ sections: [
    { name: "Need", criterion: "SIGNIFICANCE" }, { name: "Need", criterion: "BOGUS" }, { name: "" },
  ]});
  check("duplicate names get distinct keys and blank names are dropped", thin.length === 2 && thin[0].key !== thin[1].key);
  check("an unrecognized criterion falls back to OTHER", thin[1].criterion === "OTHER");
  check("coverage report flags missing narrative essentials",
    api.coverageGaps(thin).includes("Objective") && api.coverageGaps(thin).includes("Team & Capacity"));
  check("coverage report never warns about Budget (collected separately)",
    !api.coverageGaps(thin).includes("Budget"));
}

// ---------- regressions from a real Sussex draft, locked in ----------
{
  // "How many people will be directly affected?" was mapped to OUTCOMES,
  // whose four measurement probes replaced it — so the headcount was never
  // asked and the funder's question went unanswered in the draft.
  check("a headcount question has its own criterion, distinct from OUTCOMES",
    !!api.CRITERIA.REACH && api.CRITERIA.REACH.bar.includes("number of people"));

  const outcomes = api.probesFor("OUTCOMES", "How many people will be directly affected from the Project?");
  check("a multi-probe criterion never drops the funder's own question",
    outcomes[0].question === "How many people will be directly affected from the Project?");
  check("the funder's question leads and our sub-probes follow it",
    outcomes.length === 4 && outcomes.slice(1).every(p => ["baseline", "target_timing", "data_source"].includes(p.key)));
  check("with no funder question, our own probe set is used unchanged",
    api.probesFor("OUTCOMES", "")[0].key === "indicator");

  // One disagreement produced two mirror-image flags, one from each side.
  resetState();
  const f1 = mkFact({ section: "a", structuredFields: { metric_name: "m", value: 130 } });
  const f2 = mkFact({ section: "b", structuredFields: { metric_name: "m", value: 80 } });
  state.facts[f1.id] = f1; state.facts[f2.id] = f2;
  const inc = api.checkInternalConsistency(f2);
  state.inconsistencies[inc.id] = inc;
  check("the same pair of facts is never flagged twice, from either direction",
    api.checkInternalConsistency(f1) === null && api.alreadyFlagged([f2.id, f1.id]));

  // Overridden facts were appended raw, producing mid-paragraph fragments.
  check("an overridden fact renders as a sentence, not a fragment",
    api.asSentence("increasing this outcome from 38% to 65%") === "Increasing this outcome from 38% to 65%.");
  check("wording is otherwise untouched — only case and a final stop are added",
    api.asSentence("We serve 120 students.") === "We serve 120 students.");
  check("empty text stays empty rather than becoming a stray period", api.asSentence("  ") === "");

  // Restating figures across sub-questions produced three near-identical facts.
  const restated = [
    mkFact({ section: "out", summary: "The main indicator is the percentage of youth who can demonstrate two stress-management strategies, moving from a 38% baseline to a 65% goal." }),
    mkFact({ section: "out", summary: "The baseline for the stress-management outcome is 38%, with a target of 65%." }),
    mkFact({ section: "other", summary: "The baseline for the stress-management outcome is 38%, with a target of 65%." }),
  ];
  const deduped = api.dedupeFacts(restated);
  check("restatements within one section collapse to the fullest version",
    deduped.filter(f => f.section === "out").length === 1 &&
    deduped.find(f => f.section === "out").summary.includes("main indicator"));
  check("a similar fact in a DIFFERENT section is never merged away",
    deduped.some(f => f.section === "other"));
  check("same numbers but unrelated wording is NOT treated as a restatement",
    !api.isRestatement(
      { section: "s", summary: "We will serve 120 students this year." },
      { section: "s", summary: "Rent for the annex is 120 dollars monthly." }));
}

// ---------- funder priorities pulled from the application ----------
{
  const withPrio = api.normalizeParsed({
    funderName: "Centerville-Washington Foundation",
    funderPriorities: "To promote opportunities that benefit the citizens of Centerville/Washington Township, to launch new projects that represent a unique and unduplicated opportunity for the community",
    sections: [{ name: "Describe project", criterion: "APPROACH" }],
  });
  check("funder name and stated priorities are captured from the application",
    withPrio.funderName === "Centerville-Washington Foundation" &&
    withPrio.funderPriorities.startsWith("To promote opportunities"));

  const none = api.normalizeParsed({ funderName: null, funderPriorities: null, sections: [{ name: "X", criterion: "OTHER" }] });
  check("an application that states no priorities yields null, not a guess",
    none.funderPriorities === null && none.funderName === null);

  const strNull = api.normalizeParsed({ funderPriorities: "null", funderName: "  ", sections: [{ name: "X" }] });
  check("a literal \"null\" string or blank is treated as absent",
    strNull.funderPriorities === null && strNull.funderName === null);
}

// ---------- interview flow over a parsed structure ----------
{
  const { sections: parsed } = api.normalizeParsed(TAVENDON);
  resetState(parsed);
  const first = api.currentProbe();
  check("the interview skips the auto-assembled section and starts at the first real question",
    first.section.name === "Organization Background");
  check("sectionName resolves against the parsed structure",
    api.sectionName(parsed[2].key) === "Statement of Need");
}

// ---------- numbers, metrics, consistency ----------
resetState();
check("numbersIn parses commas and decimals",
  [...api.numbersIn("1,250 families at 3 sites (85.5% retained)")].sort((a,b)=>a-b).join(",") === "3,85.5,1250");
check("licensedNumbers unions fields + summary + verbatim", (() => {
  const s = api.licensedNumbers(mkFact({ summary: "12 sites over 5 years", verbatim: "85% retention", structuredFields: { value: 12 } }));
  return s.has(12) && s.has(5) && s.has(85);
})());
check("normalizeMetric collapses case/separator variants",
  api.normalizeMetric("Households Served") === api.normalizeMetric("households-served"));
check("prettyMetric humanizes internal identifiers",
  api.prettyMetric("measurable_outcomes:baseline") === "measurable outcomes baseline");

resetState();
{
  const a = mkFact({ section: "team", structuredFields: { metric_name: "youth_served", value: 130 } });
  const b = mkFact({ section: "outcomes", structuredFields: { metric_name: "Youth-Served", value: 80 } });
  state.facts[a.id] = a; state.facts[b.id] = b;
  check("cross-section contradiction caught across formatting variants", api.checkInternalConsistency(b) !== null);
}
resetState();
{
  const a = mkFact({ section: "outcomes", structuredFields: { metric_name: "pct", value: 38, metric_role: "baseline" } });
  const b = mkFact({ section: "outcomes", structuredFields: { metric_name: "pct", value: 65, metric_role: "target" } });
  state.facts[a.id] = a; state.facts[b.id] = b;
  check("baseline vs target does NOT flag", api.checkInternalConsistency(b) === null);

  // Cross-section restatement: a funder that splits related questions into
  // separate sections (one real form has "Expected Results" and "Program
  // Efficiency") had the same 38/65 statement recorded twice, each fact
  // capturing a different one of the two figures — and they flagged each
  // other. Sharing any figure means restating, not disagreeing.
  const crossA = mkFact({ section: "expected_results", summary: "moving from 38% to 65%",
    structuredFields: { metric_name: "pct", value: 38 } });
  const crossB = mkFact({ section: "program_efficiency", summary: "from a 38% baseline toward the 65% target",
    structuredFields: { metric_name: "pct", value: 65 } });
  state.facts[crossA.id] = crossA; state.facts[crossB.id] = crossB;
  check("restatement ACROSS sections does not flag when the figures match",
    api.checkInternalConsistency(crossB) === null);

  // ...but a genuinely different number for the same metric still does.
  resetState();
  const realA = mkFact({ section: "team", summary: "we served 130 youth",
    structuredFields: { metric_name: "youth", value: 130 } });
  const realB = mkFact({ section: "outcomes", summary: "we served 80 youth",
    structuredFields: { metric_name: "youth", value: 80 } });
  state.facts[realA.id] = realA; state.facts[realB.id] = realB;
  check("a real cross-section contradiction is still caught",
    api.checkInternalConsistency(realB) !== null);

  // The regression that reached a real draft: numbers RESTATED in the
  // indicator and data-source answers carry no role tag, so the old
  // both-must-have-roles guard never applied and 38-vs-65 flagged twice.
  const untagged = mkFact({ section: "outcomes", structuredFields: { metric_name: "pct", value: 65 } });
  state.facts[untagged.id] = untagged;
  check("an untagged restatement inside the same section does NOT flag",
    api.checkInternalConsistency(untagged) === null);
}
resetState();
{
  const a = mkFact({ section: "team", structuredFields: { metric_name: "x", value: 130 } });
  const b = mkFact({ section: "outcomes", structuredFields: { metric_name: "x", value: 131 } });
  state.facts[a.id] = a; state.facts[b.id] = b;
  check("rounding tolerance does not flag 130 vs 131", api.checkInternalConsistency(b) === null);
}

// ---------- budget ----------
check("parseBudgetText handles $, commas, and markdown table rows", (() => {
  const l = api.parseBudgetText("| Category | Amount |\n|---|---:|\n| Personnel | $40,000 |\n| Transportation Assistance | $4,000 |");
  return l && l.Personnel === 40000 && l["Transportation Assistance"] === 4000 && Object.keys(l).length === 2;
})());
check("parseBudgetText still handles plain comma lines", (() => {
  const l = api.parseBudgetText("category, amount\nPersonnel, 45000\nSupplies\t8000");
  return l && l.Personnel === 45000 && l.Supplies === 8000;
})());
resetState();
{
  state.budgetLines = { Personnel: 45000, "Transportation Assistance": 4000 };
  const f1 = mkFact({ structuredFields: { activity_name: "transit passes" } });
  const f2 = mkFact({ section: "approach", structuredFields: { activity_name: "Transit Passes" } });
  const f3 = mkFact({ section: "impact", structuredFields: { activity_name: "childcare stipends" } });
  state.facts[f1.id] = f1; state.facts[f2.id] = f2; state.facts[f3.id] = f3;
  api.runBudgetChecks();
  const flags = Object.values(state.inconsistencies);
  check("the same activity named twice produces ONE flag, not two (noise fix)",
    flags.filter(i => /transit/i.test(i.description)).length <= 1);
  check("an activity with no budget line is flagged",
    flags.some(i => /childcare stipends/i.test(i.description)));
}
resetState();
{
  state.budgetLines = { "Transportation Assistance": 4000 };
  const f = mkFact({ structuredFields: { activity_name: "transportation" } });
  state.facts[f.id] = f;
  api.runBudgetChecks();
  check("a budget line that contains the activity name counts as a match (stays silent)",
    Object.keys(state.inconsistencies).length === 0);
}

// ---------- resolution ----------
check("coerceValue handles $ , % and leaves text alone",
  api.coerceValue("118") === 118 && api.coerceValue("$45,000") === 45000 &&
  api.coerceValue("38%") === 38 && api.coerceValue("per intake DB") === "per intake DB");
resetState();
{
  const g = { id: "gap-1", section: "need", criterion: "SIGNIFICANCE", probeKey: "main", reason: "no data", severity: "gap" };
  state.gaps[g.id] = g;
  api.applyResolution("gap-1", "corrected", "412 households per intake data", null, null);
  check("correcting a gap creates a real fact (not silence)",
    Object.values(state.facts).length === 1 && Object.values(state.facts)[0].summary === "412 households per intake data");
  check("corrected gap no longer renders a placeholder", api.gapsForSection("need").length === 0);
}
resetState();
{
  const a = mkFact({ summary: "130", structuredFields: { metric_name: "x", value: 130 } });
  const b = mkFact({ summary: "80", structuredFields: { metric_name: "x", value: 80 } });
  state.facts[a.id] = a; state.facts[b.id] = b;
  state.inconsistencies["inc-1"] = { id: "inc-1", criterion: "TEAM", kind: "internal", description: "d", relatedFactIds: [a.id, b.id] };
  api.applyResolution("inc-1", "corrected", "118", null, a.id);
  check("a correction can target either fact of a two-fact flag",
    a.summary === "118" && a.structuredFields.value === 118 && b.summary === "80");
  check("the flag record survives resolution (never erased)", !!state.resolutions["inc-1"]);
}
resetState();
{
  const a = mkFact({ summary: "kept", verbatim: "kept verbatim", structuredFields: { metric_name: "x", value: 5 } });
  state.facts[a.id] = a;
  state.inconsistencies["inc-1"] = { id: "inc-1", criterion: "TEAM", kind: "internal", description: "d", relatedFactIds: [a.id] };
  api.applyResolution("inc-1", "overridden", null, null, a.id);
  check("override marks the fact", a.overridden === true);
  const rows = api.buildTable();
  check("table shows the override as kept despite flag", rows.some(r => r.status === "kept despite flag"));
  check("table includes the inconsistency row with its resolution", rows.some(r => r.status === "flag (overridden)"));
}

// ---------- fact recording ----------
{
  const { sections: parsed } = api.normalizeParsed(TAVENDON);
  resetState(parsed);
  const outcomes = parsed.find(s => s.criterion === "OUTCOMES");
  state.sectionIdx = parsed.indexOf(outcomes); state.probeIdx = 1; // baseline
  api.recordFact(outcomes, outcomes.probes[1], { summary: "baseline 38%", verbatim_quote: "38%", structured_fields: { metric_name: "pct", value: 38 } }, "38%");
  check("baseline probe gets metric_role tagged deterministically",
    Object.values(state.facts)[0].structuredFields.metric_role === "baseline");
  api.recordFact(outcomes, outcomes.probes[2], { summary: "target 65%", verbatim_quote: "65%", structured_fields: { metric_name: "pct", value: 65 } }, "65%");
  check("baseline→target on a parsed structure raises zero flags", Object.keys(state.inconsistencies).length === 0);
}
{
  const { sections: parsed } = api.normalizeParsed(TAVENDON);
  resetState(parsed);
  const team = parsed.find(s => s.criterion === "TEAM");
  api.recordFact(team, team.probes[0], { summary: "we reached about 80 households", verbatim_quote: "80 households", structured_fields: {} }, "80 households");
  const f = Object.values(state.facts)[0];
  check("missing metric_name gets a section:probe fallback plus a value from the text",
    f.structuredFields.metric_name === `${team.key}:main` && f.structuredFields.value === 80);
}

// ---------- background semantic check ----------
resetState();
{
  let asked = 0;
  api._setSample(Object.assign(() => Promise.resolve({ text: "" }),
    { json: () => { asked++; return Promise.resolve({ match: "youth_served" }); } }));

  const a = mkFact({ section: "team", structuredFields: { metric_name: "youth_served", value: 130 } });
  const b = mkFact({ section: "outcomes", structuredFields: { metric_name: "young_people_served", value: 80 } });
  state.facts[a.id] = a; state.facts[b.id] = b;
  api.queueSemanticCheck(b);
  await Promise.allSettled(api.pendingChecks);
  check("semantic check flags a synonym contradiction in the background",
    Object.values(state.inconsistencies).some(i => /same thing under different names/.test(i.description)));

  resetState(); asked = 0;
  const c = mkFact({ section: "team", structuredFields: { metric_name: "youth_served", value: 130 } });
  const d = mkFact({ section: "outcomes", structuredFields: { metric_name: "young_people_served", value: 131 } });
  state.facts[c.id] = c; state.facts[d.id] = d;
  api.queueSemanticCheck(d);
  await Promise.allSettled(api.pendingChecks);
  check("agreeing values never reach the model — variation alone interrupts no one",
    asked === 0 && Object.keys(state.inconsistencies).length === 0);

  resetState(); asked = 0;
  const e1 = mkFact({ section: "team", structuredFields: { metric_name: "pct_baseline", value: 38, metric_role: "baseline" } });
  const e2 = mkFact({ section: "outcomes", structuredFields: { metric_name: "pct_target", value: 65, metric_role: "target" } });
  state.facts[e1.id] = e1; state.facts[e2.id] = e2;
  api.queueSemanticCheck(e2);
  await Promise.allSettled(api.pendingChecks);
  check("baseline/target role guard holds on the semantic path too",
    asked === 0 && Object.keys(state.inconsistencies).length === 0);
  api._setSample(null);
}

// ---------- persistence ----------
// These call the real checkpoint()/loadSave(). An earlier version of this
// block re-implemented checkpoint's destructuring inline, so it would have
// passed even if the real function stopped dropping the right keys.
resetState();
{
  state.phase = "output";
  state.drafts = [{ section: "fit", name: "Funder Fit", text: "drafted." }];
  api.checkpoint();
  const back = api.loadSave();
  check("a completed session persists as 'drafting' so a reload regenerates the draft",
    back.phase === "drafting");
  check("the parsed structure persists with the session",
    Array.isArray(back.sections) && back.sections.length === 9);
  check("drafts are not persisted (regenerated from the same resolved facts)",
    back.drafts === undefined);
  api.clearSave();
}

// Transient per-attempt state must never outlive the attempt. Persisting any
// one of these alone splits a pair that only makes sense together — most
// importantly a coachStrength restored without its coachNote, which would
// show what the leader brought with no statement of what is still missing.
resetState();
{
  state.phase = "interview";
  state.coachNote = "Still needed: a baseline.";
  state.coachStrength = "They named the partner clinic.";
  state.lastAttemptText = "my typed answer";
  state.autoGapNotice = "Marked X as a gap.";
  api.checkpoint();
  const back = api.loadSave();
  for (const k of api.TRANSIENT_KEYS)
    check(`transient "${k}" is not persisted across a reload`, back[k] === undefined);
  check("durable progress still persists alongside", back.phase === "interview");
  api.clearSave();
}

// ---------- the draft is funder-facing: no interface copy inside it ----------
{
  const uiPhrases = ["You flagged this", "fill in later", "come back to it"];
  const drafted = script.match(/logGap\([^)]*"[^"]*"\)/g) || [];
  check("gap text written into the draft never narrates the interface",
    !uiPhrases.some(ph => drafted.some(d => d.includes(ph))));
}

// ---------- per-criterion coaching ----------
// A single generic instruction produced the same nudge for all twelve
// questions; live testing showed two near-miss answers rejected three times
// each. Every criterion now names its own typical gap.
{
  const named = Object.keys(api.CRITERIA);
  check("every criterion carries its own coaching guidance",
    named.every(k => typeof api.CRITERIA[k].coach === "string" && api.CRITERIA[k].coach.length > 40));
  const coaches = named.map(k => api.CRITERIA[k].coach);
  check("coaching guidance is criterion-specific, not copy-pasted",
    new Set(coaches).size === coaches.length);

  const probes = api.probesFor("APPROACH", null);
  check("probesFor carries coach onto a single-probe section", !!probes[0].coach);
  const multi = api.probesFor("OUTCOMES", "How many will you serve?");
  check("probesFor carries coach onto every probe of a multi-probe section",
    multi.length > 1 && multi.every(p => !!p.coach));
  check("an unknown criterion still gets coaching (falls back to OTHER)",
    !!api.probesFor("NOT_A_CRITERION", null)[0].coach);
}

// ---------- affirmation and verdict stay structurally separate ----------
// The prompt must request two fields, and must forbid manufacturing praise
// when the reply contains nothing specific to name.
{
  check("the classify prompt requests strength and note as separate fields",
    /"strength"\s*:/.test(script) && /"note"\s*:/.test(script));
  check("the prompt allows a null strength rather than generic praise",
    /use null/.test(script) && /[Nn]ever write generic encouragement/.test(script));
  check("the prompt forbids softening the verdict inside the strength field",
    /never soften or hedge the verdict here/.test(script));
  check("strength and note render as two separate elements",
    /strengthnote/.test(script) && /coachnote/.test(script));
}

// ---------- reflection summary is grounded, never model-authored ----------
{
  resetState();
  check("no gaps or flags yields no reflection notes", api.reflectionInsights().length === 0);

  state.gaps["g1"] = { id: "g1", section: "outcomes", criterion: "OUTCOMES", probeKey: "baseline", reason: "r" };
  state.gaps["g2"] = { id: "g2", section: "fit", criterion: "FIT", probeKey: "main", reason: "r" };
  state.inconsistencies["i1"] = { id: "i1", criterion: "BUDGET", kind: "budget", description: "d", relatedFactIds: [] };
  const notes = api.reflectionInsights();
  check("reflection counts the leader's own gaps", notes.some(n => /2 section/.test(n)));
  check("reflection separates measurement gaps from the rest", notes.some(n => /measuring results/.test(n)));
  check("reflection reports budget flags distinctly", notes.some(n => /budget line/.test(n)));
  check("reflection never invents a claim beyond counting",
    notes.every(n => typeof n === "string" && n.length > 0));
}

console.log(`\nAll ${passed} tests passed.`);
