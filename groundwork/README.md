# Groundwork

**An interview-first grant narrative tool for nonprofit leaders.** It asks
questions, records only what the leader actually said, flags what doesn't hold
up, and assembles a draft from approved facts — never from invention.

A small nonprofit's executive director usually knows their community, their
participants and their program design better than any reviewer will. What they
often lack is the specialized convention of grant writing: naming a baseline,
attaching a number to a track record, connecting an activity to the outcome it
produces. Groundwork scaffolds that translation. It does not write on the
leader's behalf.

---

## What it does

1. **Reads the funder's own application.** Paste it or upload the PDF. The
   funder's sections, wording, order and word limits become the interview.
2. **Interviews one question at a time.** Every answer is judged against a
   rigor bar. A miss returns a coaching question, not a rewrite.
3. **Routes everything uncertain back to the leader.** Gaps and contradictions
   wait for a single Resolve pass at the end — never interrupting mid-thought.
   Four choices: correct, explain, accept, override.
4. **Assembles a draft, then verifies it.** Every number in the drafted prose
   must trace to something the leader said, or that section falls back to their
   own plain wording.
5. **Exports the narrative plus an evidence table** showing what is sourced,
   what is the leader's own words, and what is still a gap.

## What it will not do

- No invented statistics, beneficiaries or outcomes.
- No confidence scores. Uncertain material goes to the leader instead of being
  scored and shaded.
- No submitting on anyone's behalf. Export is the last step and it is manual.

---

## Two design decisions worth the detail

### The funder decides structure; the criteria library decides rigor

Mirroring a funder's questions alone loses the push for specifics that is the
whole point — funders frequently ask vague questions. Imposing a fixed set of
sections misses what a given funder actually requires. So the application
supplies the container and `CRITERIA` supplies the standard:

```
Funder's question  ->  "How will you know it worked?"      (their words, their order)
Our bar underneath ->  a named indicator, a baseline,
                       a target with a date, a data source  (what the answer must clear)
```

Everything downstream — consistency checks, grounding validation, the Resolve
pass, the evidence table — is section-agnostic, so an unfamiliar funder form
changes the questions without weakening the standard.

### Fact generation and language generation are separated

The model may transform approved facts into prose. It may not introduce facts.
That boundary is enforced in code, not by prompt discipline: `assembleSection()`
builds the set of numbers the section's facts license, and rejects drafted prose
containing any number outside it, falling back to the leader's own sentences.

The same rule governs the reflection summary and the coaching affirmation. Both
are grounded or absent — the affirmation returns `null` rather than manufacture
generic praise.

---

## Running it

The web app is a single self-contained HTML file with no build step and no
dependencies. Published as a Claude Artifact, it reaches Claude through the
viewer's own account, so a nonprofit leader needs no API key and no setup.

```bash
npm test              # logic, PDF extraction, welcome-screen suites
npm run test:logic    # 83 pure-logic tests, no network
npm run test:e2e      # live end-to-end; costs real tokens, needs ANTHROPIC_API_KEY
```

`test:pdf` and `test:welcome` need real funder forms that are not
redistributed here — they skip with instructions. See
[`fixtures/pdf/README.md`](./fixtures/pdf/README.md).

---

## Layout

```
web/
  groundwork.html     The whole application: markup, styles, logic, PDF extractor.
  pdftext.js          Standalone source of the extractor, inlined into the above.
  test_port.mjs       Pure logic. Loads the app's <script> into a sandbox.
  test_pdftext.mjs    Extraction, against the copy that actually ships.
  test_welcome.mjs    Fires the real upload handler with a real PDF.
  test_e2e.mjs        Live: real PDF -> parse -> interview -> resolve -> draft.
cli/                  Earlier Python prototype of the same interview engine.
docs/
  DESIGN.md           The design rationale this was built from.
  PROJECT_LOG.md      Defect ledger: what broke, and what the fix was.
fixtures/pdf/         Test forms (not vendored — see its README).
```

### On the PDF extractor

`pdftext.js` is written rather than pulled from a CDN for one reason: it can be
tested against real funder forms in Node before shipping, whereas a library
loaded inside the artifact sandbox cannot be verified until it is live. It
handles what funder forms actually use — FlateDecode streams, `/ToUnicode`
CMaps for subset-embedded fonts, and font dictionaries reached either inline or
by indirect reference. Scanned forms have no text layer at all; those are
detected and reported rather than returned as noise.

---

## Testing approach

Unit tests alone were repeatedly insufficient on this project. Every class of
defect worth fixing surfaced from running the real thing against real inputs:

- A false-positive contradiction flag surfaced only from a full live run
  against a funder form the fixes had never been tested on.
- A "PDF upload didn't work" report turned out to be a misleading UI, not a
  broken extractor — found by driving the actual file-input handler.
- The single worst piece of interview friction (a rejected answer wiping the
  leader's typed text) never appeared in any unit test. It took a scripted
  walkthrough with realistic answers to see it.

So the suite is layered deliberately: fast logic tests for the rules, extraction
tests against the shipped copy, a DOM-level test for the upload path, and a live
end-to-end run for anything the others structurally cannot catch.

---

## Status and limits

A working prototype, tested against four real funder forms and live end-to-end
runs. Known limits, stated plainly:

- **Consistency checking is internal.** It compares the leader's answers against
  each other. It does not verify claims against external records such as IRS
  filings.
- **It cannot tell whether a claim is true.** It checks that a draft is
  grounded in what the leader said, which is a different thing.
- **No memory across sessions.** Each interview starts fresh; the reflection
  summary covers one sitting, not a leader's patterns over time.
- **Judgment varies.** The classifier occasionally rejects a reasonable answer.
  The interface handles this (text is preserved, attempts are visible, context
  carries to Resolve) but the underlying variance is real.

## License

MIT — see [LICENSE](./LICENSE).
