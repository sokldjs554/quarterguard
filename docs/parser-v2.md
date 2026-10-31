# Bounded parser v2

`parse_statement(text, doc, page, metrics=None)` still returns the existing `Fact` objects. The adapter now accepts a reporting year from the verified eight-column year header, checks it against an explicit `report_end` when present, and never derives dates or companies from a document ID. Existing Samsung manifests retain the historical `company='samsung'` default; an explicit `company` is carried into every fact. New companies must supply that field. This adapter does not identify arbitrary issuers from prose.

The accepted layout remains narrow: Q2 or Q3 interim consolidated/separate profit-or-loss statements, current/prior adjacent years, direct-quarter columns before YTD, and KRW millions/USD thousands. All eight year and currency columns, both period labels, units, one scope header, optional manifest scope, and known statement-page locator must agree. Duplicate/missing metric rows, conflicting dates, malformed numbers, extra or missing cells, and unsupported layouts raise `UNSUPPORTED_LAYOUT`.

Whitespace may wrap labels and headers. `_normalize_statement` repairs a comma-group number broken by a physical newline only when the two incomplete pieces uniquely complete a three-digit group. It does not concatenate complete numbers or numbers separated by ordinary spaces. `_row_cells` validates eight complete amounts plus an optional leading Notes cell containing one to three short references, optionally parenthesized or comma separated. An unannotated short first amount is ambiguous with a note plus a missing cell, so that layout is rejected. `_statement_context` performs the header/date/scope/column checks. The adapter does not infer missing monetary cells, recalculate source values, or invent translation rates.

## Recorded raw-PDF development results

[`artifacts/parser-development-v2.json`](../artifacts/parser-development-v2.json) records before/after page counts, every remaining parsing failure, source PDF hashes, parser hashes, and source/fact file preservation hashes. Baseline data and prior evaluation artifacts were not overwritten.

| Dataset | Before | After | Numeric/context comparison |
| --- | --- | --- | --- |
| Existing 2024 regression | 4/4 pages, 192 facts | 4/4 pages, 192 facts | Exact equality of all 192 public records |
| Disclosed 2025 development | 0/4 pages, 0 facts | 4/4 pages, 192 facts | All declared fields match 64/64 reference facts; 128 additional extracted facts |

The 2025 results come from `pypdf` extraction of the four actual official PDF pages, including the wrapped numbers in Q2 OFS. Frozen facts are used only for comparison and never substituted as parser output. This is disclosed development evidence, not a fresh blind result. The independently collected evaluation is reported elsewhere. No new facts were registered into the production canonical corpus by this work.

The known 2025 Q3 CFS net-profit row repeats Q2 values in the source. Extraction preserves those printed values; passing the extraction comparison does not resolve the financial arithmetic conflict. USD facts remain convenience translations, with unknown translation metadata left unknown. Human review has not been performed.

## Local replay

Run `python -m unittest tests.test_parser_v2 tests.test_core tests.test_review_regressions` for the small, synthetic positive and rejection cases. The initial v2 positive cases failed on the old hardcoded header; the trailing malformed-amount test also failed before its boundary check was added.

With the ignored PDFs already in `work/raw` and `work/heldout-raw`, the following read-only command repeats the full raw extraction comparison without calling `collect()` or changing any source/fact files:

```bash
python - <<'PY'
import json
from pathlib import Path
from pypdf import PdfReader
from quarterguard.ingest import parse_statement

for directory, cache in [('data', 'work/raw'), ('data/heldout', 'work/heldout-raw')]:
    gold = {f['id']: f for f in json.loads(Path(directory, 'facts.json').read_text())}
    actual = {}
    for doc in json.loads(Path(directory, 'sources.json').read_text()):
        reader = PdfReader(Path(cache, doc.get('cache_filename', doc['id'] + '.pdf')))
        for scope, page in doc['statement_pages'].items():
            facts = parse_statement(reader.pages[page - 1].extract_text(), doc, page)
            actual.update({f.id: f.public() for f in facts})
            print(doc['id'], scope, page, len(facts))
    failures = [key for key, expected in gold.items()
                if any(actual.get(key, {}).get(field) != value
                       for field, value in expected.items())]
    if directory == 'data':
        assert actual == gold
    assert not failures, failures
    print(directory, 'actual', len(actual), 'matched gold', len(gold))
PY
```

Full PDF files and page text remain ignored. Future issuers, Q1/year-end statements, transposed currency/year headers, OCR, and genuinely ambiguous note/cell geometry require another adapter or explicit rejection; no claim of general financial-PDF support is made.

## Post-disclosure punctuation correction

The first independent-worker evaluation was preserved with 0/5 raw pages accepted. It disclosed that a 2023 Samsung statement writes the units as “In millions of Korean won, in thousands of US dollars”; the initial parser required “and”. After that disclosure, a synthetic regression was observed failing and the unit separator was expanded to accept this comma form. The currency, scale, column count/order, dates, scope and numeric-cell checks remain in force. Hyundai's four-column layout remains unsupported.

This correction is **post-disclosure development**, not a successful first blind evaluation. The original `parser-development-v2.json` and independent first-run records remain unchanged; [`parser-development-v2-followup.json`](../artifacts/parser-development-v2-followup.json) records the new parser hash, failed-then-passing regression, and repeated 2024/2025 development checks. The parser author did not inspect the newly frozen 2022 follow-up documents; their evaluation is recorded separately.
