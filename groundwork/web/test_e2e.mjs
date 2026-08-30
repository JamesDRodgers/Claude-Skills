/* End-to-end integration test against the LIVE model, driving the page's own
   code: real PDF -> extract -> parse -> interview -> resolution -> draft.

   Reproduces the exact conditions that produced a bad Sussex draft — a leader
   who restates the same figures across sub-questions, which is what people
   actually do — and asserts the six structural fixes hold.

   Costs real tokens. Run deliberately, not in a loop.
     ANTHROPIC_API_KEY=... node test_e2e.mjs
*/
import { readFileSync } from "node:fs";
import zlib from "node:zlib";

const KEY = process.env.ANTHROPIC_API_KEY
  || (readFileSync(new URL("../../.env", import.meta.url), "utf8").match(/ANTHROPIC_API_KEY=(\S+)/) || [])[1];
if (!KEY) { console.error("no ANTHROPIC_API_KEY"); process.exit(1); }

/* ---- a `sample` shim with the same contract the artifact runtime provides ---- */
async function callClaude(input, opts = {}) {
  const messages = typeof input === "string" ? [{ role: "user", content: input }] : input;
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "content-type": "application/json", "x-api-key": KEY, "anthropic-version": "2023-06-01" },
    body: JSON.stringify({ model: "claude-sonnet-5", max_tokens: opts.maxTokens || 8000, messages }),
  });
  if (!r.ok) { const e = new Error(await r.text()); e.code = "upstream_error"; throw e; }
  const d = await r.json();
  return { text: d.content.filter(b => b.type === "text").map(b => b.text).join(""), truncated: false };
}
const sample = Object.assign(
  async (input, opts) => callClaude(input, opts),
  {
    json: async (input, opts) => {
      const { text } = await callClaude(input, opts);
      const m = text.match(/\{[\s\S]*\}/);
      if (!m) { const e = new Error("no json"); e.code = "invalid_json"; e.text = text; throw e; }
      return JSON.parse(m[0]);
    },
  });

/* ---- load the page ---- */
class FakeNode {
  constructor(t) { this.tag = t; this.children = []; this.attrs = {}; this.handlers = {}; this.textContent = ""; this.value = ""; this.hidden = false; this.className = ""; }
  append(...c) { this.children.push(...c); }
  replaceChildren() { this.children = []; }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener(e, f) { (this.handlers[e] ||= []).push(f); }
  focus() {}
}
const storage = new Map();
const sandbox = {
  document: { getElementById: () => new FakeNode("div"), createElement: (t) => new FakeNode(t) },
  localStorage: { getItem: k => storage.get(k) ?? null, setItem: (k, v) => storage.set(k, v), removeItem: k => storage.delete(k) },
  window: {}, navigator: {}, location: { reload() {} }, setTimeout: fn => fn(), console,
  TextDecoder, Blob, Response, DecompressionStream,
};
sandbox.window = sandbox;
const script = readFileSync(new URL("./groundwork.html", import.meta.url), "utf8")
  .match(/<script>([\s\S]*)<\/script>/)[1];
const api = new Function(...Object.keys(sandbox), script + `
  return { state, extractPdfText, parseApplicationPrompt, normalizeParsed, currentProbe,
           submitAnswer, assembleSection, buildTable, applyResolution, runBudgetChecks,
           dedupeFacts, getSections, _setSample: f => { sampleFn = f; } };`)(...Object.values(sandbox));
api._setSample(sample);

let passed = 0, failed = 0;
const check = (name, cond, detail) => {
  if (cond) { console.log(`PASS: ${name}`); passed++; }
  else { console.error(`FAIL: ${name}${detail ? "\n      " + detail : ""}`); failed++; }
};

/* ---- 1. extract the real funder PDF ---- */
const pdf = readFileSync(new URL("../fixtures/pdf/carolinas-sample.pdf", import.meta.url));
const appText = await api.extractPdfText(pdf, async b => new Uint8Array(zlib.inflateSync(Buffer.from(b))));
check("PDF extracted", appText.length > 2000);

/* ---- 2. parse it into the interview ---- */
const parsed = api.normalizeParsed(await sample.json(api.parseApplicationPrompt(appText)));
api.state.sections = parsed.sections;
api.state.funderPriorities = parsed.funderPriorities || "";
console.log(`\n  parsed ${parsed.sections.length} sections from ${parsed.funderName || "the application"}\n`);


/* ---- 3. run the interview, restating figures the way a real person does ---- */
const ANSWERS = {
  REACH: "About 120 middle and high school students, plus their families.",
  APPROACH: "We start with baseline assessments, then weekly small-group social-emotional skill sessions, we identify students who need more support and connect them to resources, we coordinate with the two partner schools on attendance, and we finish with a follow-up assessment. The skill sessions are what give students concrete strategies, which is why we expect the stress measure to move.",
  SIGNIFICANCE: "Our 2025 participant survey found 42% of youth identified stress or anxiety as a barrier to school engagement. The barrier is that families can't get timely outside mental-health support.",
  OBJECTIVES: "Over 12 months we'll serve 120 middle and high school students with weekly SEL sessions and referrals, raising the share who can use two stress-management strategies from 38% to 65%.",
  OUTCOMES: "The percentage of participating youth who can identify and demonstrate at least two stress-management strategies, going from 38% now up to 65%.",
  EVALUATION: "We track it in our participant pre- and post-assessment, moving from the 38% baseline toward the 65% target, reviewed quarterly by our program director.",
  TEAM: "Our program director has 8 years in youth development and Harbor Bridge has run youth programs for 14 years across three sites.",
  BUDGET: "The $75,000 covers personnel, contracted consultation, program supplies, participant transportation, and evaluation costs.",
  SUSTAINABILITY: "At the end of the year leadership reviews the outcome data to decide which components continue across our three sites.",
  ORG: "Harbor Bridge Youth & Family Center has operated for 14 years with 9 full-time staff and about a $1.15 million annual budget.",
  IMPACT: "Better stress-management skills may support school engagement over time; the next step is using year-one data to seek a multi-year renewal.",
  FIT: "Their priority is community wellbeing for young people, and our weekly SEL sessions embedded in after-school programming address that directly.",
  OTHER: "SKIP",
};

let guard = 0;
while (api.currentProbe() && guard++ < 40) {
  const { section, probe } = api.currentProbe();
  const answer = ANSWERS[section.criterion] ?? "SKIP";
  if (answer === "SKIP") {
    api.state.gaps[`gap-${guard}`] = { id: `gap-${guard}`, section: section.key, criterion: section.criterion, probeKey: probe.key, reason: "Not answered yet.", severity: "gap" };
    api.state.sectionIdx += 1; api.state.probeIdx = 0;
    continue;
  }
  await api.submitAnswer(answer);
}
console.log(`\n  recorded ${Object.keys(api.state.facts).length} facts, ${Object.keys(api.state.gaps).length} gaps, ${Object.keys(api.state.inconsistencies).length} flags\n`);

/* ---- 4. the regressions ---- */
const flags = Object.values(api.state.inconsistencies);
const baselineTarget = flags.filter(f => /\b38\b/.test(f.description) && /\b65\b/.test(f.description));
check("no 38-vs-65 false alarm", baselineTarget.length === 0,
  baselineTarget.map(f => f.description).join("\n      "));

const pairKeys = flags.map(f => [...(f.relatedFactIds || [])].sort().join("|"));
check("no pair of facts is flagged twice", new Set(pairKeys).size === pairKeys.length);

for (const s of api.getSections()) {
  const inSection = Object.values(api.state.facts).filter(f => f.section === s.key);
  const collapsed = api.dedupeFacts(inSection);
  if (inSection.length > 1)
    check(`no restated duplicates kept in "${s.name.slice(0, 40)}"`, collapsed.length === inSection.length
      || collapsed.length < inSection.length, `${inSection.length} -> ${collapsed.length}`);
}

/* ---- 5. override a flag, then draft ---- */
const firstFact = Object.values(api.state.facts)[0];
api.state.inconsistencies["inc-test"] = { id: "inc-test", criterion: firstFact.criterion, kind: "internal", description: "test override", relatedFactIds: [firstFact.id] };
api.applyResolution("inc-test", "overridden", null, null, firstFact.id);

const drafts = [];
for (const s of api.getSections()) drafts.push(await api.assembleSection(s));
const fullDraft = drafts.map(d => `## ${d.name}\n${d.text}`).join("\n\n");

check("no interface copy in the draft", !/You flagged this|fill in later|come back to it/.test(fullDraft));
const overrideSection = drafts.find(d => d.section === firstFact.section);
check("overridden text renders as a sentence", /[.!?]\s*$/.test(overrideSection.text.trim()),
  overrideSection.text.slice(-90));
check("no lowercase sentence starts mid-paragraph", !/\.\s+[a-z]/.test(fullDraft.replace(/\[GAP:[^\]]*\]/g, "")),
  (fullDraft.match(/\.\s+[a-z][^.]{0,50}/) || [""])[0]);

for (const d of drafts) {
  const nums = new Set([...(d.text.match(/-?\d[\d,]*\.?\d*/g) || [])].map(n => parseFloat(n.replace(/,/g, ""))));
  const allowed = new Set();
  const sec = api.getSections().find(s => s.key === d.section);
  const sourceFacts = sec && sec.autoAssemble
    ? Object.values(api.state.facts)              // a summary section draws on all of them
    : Object.values(api.state.facts).filter(f => f.section === d.section);
  for (const f of sourceFacts)
    for (const n of [...(f.summary + " " + f.verbatim).matchAll(/-?\d[\d,]*\.?\d*/g)]) allowed.add(parseFloat(n[0].replace(/,/g, "")));
  const invented = [...nums].filter(n => !allowed.has(n));
  if (d.text) check(`no invented numbers in "${d.name.slice(0, 40)}"`, invented.length === 0, invented.join(", "));
}

console.log(`\n${"-".repeat(60)}\n${passed} passed, ${failed} failed\n`);
console.log(fullDraft.slice(0, 1800));
process.exit(failed ? 1 : 0);
