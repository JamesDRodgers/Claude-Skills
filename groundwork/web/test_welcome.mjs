/* Tests the welcome screen's upload path by actually firing the file-input
   handler with a real funder PDF — the one flow a user hit that had no
   coverage. Uses a DOM stub that records event listeners so handlers can be
   invoked, and the browser's own Blob/Response/DecompressionStream. */
import { readFileSync, existsSync } from "node:fs";

// Real funder forms are not redistributed here; see fixtures/pdf/README.md.
const FIX = new URL("../fixtures/pdf/", import.meta.url);
const REQUIRED = ["centerville-fillable.pdf", "scanned-no-text-layer.pdf"];
const absent = REQUIRED.filter(n => !existsSync(new URL(n, FIX)));
if (absent.length) {
  console.log(`SKIP: welcome-screen tests — missing fixtures: ${absent.join(", ")}`);
  console.log("      See groundwork/fixtures/pdf/README.md.");
  process.exit(0);
}

const html = readFileSync(new URL("./groundwork.html", import.meta.url), "utf8");
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];

const nodes = [];
class FakeNode {
  constructor(tag) {
    this.tag = tag; this.children = []; this.attrs = {}; this.handlers = {};
    this.textContent = ""; this.value = ""; this.files = null; this.hidden = false;
    this.className = ""; nodes.push(this);
  }
  append(...c) { for (const x of c) { this.children.push(x); if (x instanceof FakeNode) x.parent = this; } }
  replaceChildren() { this.children = []; }
  setAttribute(k, v) {
    this.attrs[k] = v;
    if (k === "placeholder") this.placeholder = v;
    if (k === "hidden") this.hidden = true;
    if (k === "type") this.type = v;
  }
  addEventListener(ev, fn) { (this.handlers[ev] ||= []).push(fn); }
  focus() {}
  fire(ev, arg) { return Promise.all((this.handlers[ev] || []).map(f => f(arg))); }
}
const storage = new Map();
const sandbox = {
  document: { getElementById: () => new FakeNode("div"), createElement: (t) => new FakeNode(t) },
  localStorage: {
    getItem: (k) => storage.get(k) ?? null,
    setItem: (k, v) => storage.set(k, v), removeItem: (k) => storage.delete(k),
  },
  window: {}, navigator: {}, location: { reload: () => {} },
  setTimeout: (fn) => fn(), console, TextDecoder,
  Blob, Response, DecompressionStream,
};
sandbox.window = sandbox;

const api = new Function(...Object.keys(sandbox), script + `
  return { state, renderWelcome, readApplicationFile };`)(...Object.values(sandbox));

let passed = 0;
const check = (name, cond) => {
  if (!cond) { console.error(`FAIL: ${name}`); process.exit(1); }
  console.log(`PASS: ${name}`); passed++;
};
const findAll = (pred) => nodes.filter(pred);

// --- render the welcome screen and locate its controls ---
nodes.length = 0;
api.renderWelcome();
const appBox = findAll(n => n.tag === "textarea" && /Paste the funder/.test(n.placeholder || ""))[0];
const fileInput = findAll(n => n.tag === "input" && n.type === "file")[0];
const prioBox = findAll(n => n.tag === "textarea" && /funder's priorities/.test(n.placeholder || ""))[0];
check("welcome renders an application box, a file input, and a priorities box",
  !!appBox && !!fileInput && !!prioBox);

const prioWrap = prioBox.parent;
const pulledNote = findAll(n => n.tag === "p" && /read from the application above/.test(n.textContent || String(n.children[0] || "")))[0]
  || prioWrap.parent.children.find(c => c instanceof FakeNode && c.hidden && c !== prioWrap);

check("with no application supplied, the priorities box is visible", prioWrap.hidden === false);

// --- upload a real funder PDF through the actual change handler ---
const pdf = readFileSync(new URL("../fixtures/pdf/centerville-fillable.pdf", import.meta.url));
fileInput.files = [{
  name: "centerville-fillable.pdf",
  arrayBuffer: async () => pdf.buffer.slice(pdf.byteOffset, pdf.byteOffset + pdf.length),
}];
await fileInput.fire("change");

check("uploading a PDF fills the application box with its text",
  appBox.value.includes("Grant Request Form") && appBox.value.includes("Centerville-Washington Foundation"));
check("the extracted text includes the questions the interview will be built from",
  appBox.value.includes("How does this request support the Foundation") &&
  appBox.value.includes("What other sources of funds"));
// Compare with whitespace normalized: the passage wraps across lines in the
// PDF, and the parse reads it as flowing text regardless.
const flat = appBox.value.replace(/\s+/g, " ");
check("the funder's stated priorities are present in the extracted text (for the parse to pull)",
  flat.includes("grant goals: To promote opportunities that benefit the citizens of Centerville/Washington Township") &&
  flat.includes("to generate matching funds"));
check("after upload the priorities box hides, since they come from the application",
  prioWrap.hidden === true);

// --- clearing the application text brings the manual box back ---
appBox.value = "";
await appBox.fire("input");
check("clearing the application text restores the manual priorities box", prioWrap.hidden === false);

// --- a scanned PDF reports rather than silently doing nothing ---
nodes.length = 0;
api.renderWelcome();
const appBox2 = findAll(n => n.tag === "textarea" && /Paste the funder/.test(n.placeholder || ""))[0];
const fileInput2 = findAll(n => n.tag === "input" && n.type === "file")[0];
const errLine = findAll(n => n.className === "errline")[0];
const scanned = readFileSync(new URL("../fixtures/pdf/scanned-no-text-layer.pdf", import.meta.url));
fileInput2.files = [{
  name: "scanned.pdf",
  arrayBuffer: async () => scanned.buffer.slice(scanned.byteOffset, scanned.byteOffset + scanned.length),
}];
await fileInput2.fire("change");
check("a scanned PDF leaves the application box empty", !appBox2.value);
check("a scanned PDF shows an actionable error instead of failing silently",
  errLine && errLine.hidden === false && /no readable text layer/.test(errLine.textContent));

console.log(`\nAll ${passed} welcome-screen tests passed.`);
