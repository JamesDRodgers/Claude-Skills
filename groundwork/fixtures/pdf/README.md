# Test fixtures

The PDF extraction tests run against **real funder application forms**. Those
are third-party documents, so they are not redistributed in this repository
(`fixtures/pdf/*.pdf` is gitignored). Tests that need them skip with a message
rather than failing.

To run the full suite, drop four files here:

| Filename | What it exercises |
|---|---|
| `centerville-fillable.pdf` | A fillable form with subset-embedded fonts reached through an **indirect** `/Font` reference, and every text fragment wrapped in its own `BT…ET` block. This is the hard case: without `/ToUnicode` CMap handling it extracts as gibberish shifted by a constant. |
| `carolinas-sample.pdf` | A long multi-page narrative application (17 sections). Exercises multi-page walking and the compact-parse path that keeps a long section list from overrunning the reply budget. |
| `sussex-online.pdf` | An online application export with curly quotes, en-dashes and required-field markers. Exercises non-ASCII decoding. |
| `scanned-no-text-layer.pdf` | A scanned form with **no text layer at all**. The negative case: extraction must detect this and say so, never return noise. |

Any comparable forms will do if you adjust the assertions in
`web/test_pdftext.mjs`, which check for specific phrases in each document.
Most foundations publish their application forms publicly.

## Why they aren't vendored

Two reasons. They are documents this project does not own, and they are the
kind of file a repository accumulates and never prunes (~1.5 MB for four).
Keeping them out also makes the dependency explicit: the extractor's
correctness claims rest on real forms, not on synthetic PDFs generated to
match the parser's own assumptions.
