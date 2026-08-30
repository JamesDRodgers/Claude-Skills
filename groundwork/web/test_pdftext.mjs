/* PDF extraction tests, run against the extractor as INLINED IN THE ARTIFACT
   (not the standalone pdftext.js copy) so these cover what actually ships.

   Fixtures are real funder application forms, which are not redistributed in
   this repository — see fixtures/pdf/README.md for what to drop in. Without
   them this suite skips rather than fails. */
import { readFileSync, existsSync } from "node:fs";
import zlib from "node:zlib";

const HTML = new URL("./groundwork.html", import.meta.url);
const FIX = new URL("../fixtures/pdf/", import.meta.url);

const REQUIRED = ["centerville-fillable.pdf", "carolinas-sample.pdf",
                  "sussex-online.pdf", "scanned-no-text-layer.pdf"];
const absent = REQUIRED.filter(n => !existsSync(new URL(n, FIX)));
if (absent.length) {
  console.log(`SKIP: PDF extraction tests — missing fixtures: ${absent.join(", ")}`);
  console.log("      See groundwork/fixtures/pdf/README.md.");
  process.exit(0);
}

const script = readFileSync(HTML, "utf8").match(/<script>([\s\S]*)<\/script>/)[1];
const start = script.indexOf("function latin1(");
const end = script.indexOf("async function inflateBytes(");
const extractorSrc = script.slice(start, end);
const { extractPdfText, parseCMap } = new Function(extractorSrc + "; return { extractPdfText, parseCMap };")();

const inflate = async (b) => new Uint8Array(zlib.inflateSync(Buffer.from(b)));
const load = (n) => readFileSync(new URL(n, FIX));

let passed = 0;
function check(name, cond) {
  if (!cond) { console.error(`FAIL: ${name}`); process.exit(1); }
  console.log(`PASS: ${name}`); passed++;
}

// --- Centerville fillable form: subset fonts + per-fragment BT/ET blocks ---
{
  const t = await extractPdfText(load("centerville-fillable.pdf"), inflate);
  check("fillable form: title reads as whole words, not shattered per letter",
    t.includes("Grant Request Form") && t.includes("Centerville-Washington Foundation"));
  check("fillable form: labels survive intact",
    t.includes("Amount of Request") && t.includes("Name/Title of Project") && t.includes("Describe Project"));
  // This line uses a Type0 subset font reached through an INDIRECT /Font
   // reference. Before dictFor() resolved that, it came out as every
   // character shifted by 29 — readable gibberish that would have been fed
   // to the parser as if it were a real question.
  check("fillable form: subset-font question decoded via ToUnicode CMap",
    t.includes("How does this request support the Foundation") && t.includes("purpose?"));
  check("fillable form: curly punctuation from the CMap survives", t.includes("Foundation’s"));
  check("fillable form: no residual +29 shift artifacts", !/\bU H T X H V W\b|\bG R H V\b/.test(t));
  check("fillable form: all narrative questions present",
    t.includes("What other sources of funds") &&
    t.includes("previous projects funded by the Foundation") &&
    t.includes("What is the full budget for the project"));
  check("fillable form: no run-together words from a bad space heuristic",
    !/\bNam e\b|\bRequ est\b|\bAm ount\b/.test(t));
}

// --- Foundation For The Carolinas sample: long multi-page narrative ---
{
  const t = await extractPdfText(load("carolinas-sample.pdf"), inflate);
  check("multi-page sample: paragraphs reflow as sentences",
    t.includes("Foundation For The Carolinas administers 22 public grant programs"));
  check("multi-page sample: reaches content beyond the first page", t.length > 8000);
  check("multi-page sample: numbered question list survives", /\d+\.\s+\w/.test(t));
}

// --- Sussex online application: curly quotes, en-dashes, form labels ---
{
  const t = await extractPdfText(load("sussex-online.pdf"), inflate);
  check("online form: heading and required-field markers extract",
    t.includes("Online Grant Application") && t.includes("Organizational Name"));
  check("online form: non-ASCII punctuation decodes rather than dropping",
    /[–—‘’“”]/.test(t));
}

// --- Scanned form: must be reported, never returned as noise ---
{
  let msg = null;
  try { await extractPdfText(load("scanned-no-text-layer.pdf"), inflate); }
  catch (e) { msg = e.message; }
  check("scanned PDF is detected rather than returning garbage", msg !== null);
  check("scanned PDF error tells the person what to do instead",
    /no readable text layer/.test(msg) && /paste/.test(msg));
}

// --- Non-PDF input ---
{
  let msg = null;
  try { await extractPdfText(new TextEncoder().encode("just some text"), inflate); }
  catch (e) { msg = e.message; }
  check("a non-PDF is rejected with a clear message", /doesn't look like a PDF/.test(msg || ""));
}

// --- CMap parsing units ---
{
  const { map } = parseCMap(`
    beginbfchar
    <01> <0048>
    <02> <0065>
    endbfchar
    beginbfrange
    <10> <12> <0041>
    <20> <21> [<0058> <0059>]
    endbfrange`);
  check("CMap bfchar maps single codes", map.get(1) === "H" && map.get(2) === "e");
  check("CMap bfrange maps a run", map.get(0x10) === "A" && map.get(0x12) === "C");
  check("CMap bfrange maps an explicit array", map.get(0x20) === "X" && map.get(0x21) === "Y");
}

console.log(`\nAll ${passed} PDF extraction tests passed.`);
