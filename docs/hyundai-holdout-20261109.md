# Hyundai 2024 Q3 frozen document evaluation

This is an **AI-authored, AI-inspected, small new-document evaluation, not human-reviewed or expert gold**. The evaluator acquired and visually inspected the official Hyundai 2024 Q3 consolidated statement, then froze 16 literal KRW-million cells, eight English/Korean query contracts and two exact year-over-year calculations before reading or running the new Hyundai parser. Only the baseline parser interface at `0b1613c` was inspected. The old failed Hyundai 2023 Q3 source remains disclosed development evidence; none of its artifacts was replaced.

The 2024 report is a newly withheld document, but its comparative 2023 amounts can overlap disclosed data. This is one statement from one issuer, not evidence of broad layout coverage or independent expert accuracy. The queries are authored by the same-task AI evaluator with knowledge of the existing system contract. Query baseline failures are disclosed separately and must not be described as untouched query generalization after remediation.

## Frozen source and cells

- [Official PDF](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2024/2024-q3-consolidated-audit-report-en.pdf), accessed 2026-11-09; 73 PDF pages.
- SHA-256: `3894d0c7948e337a1f32f1be3186159b8d4bbcdea27b7cf4eb8bf61fa74e125a`.
- Consolidated statement of income: **PDF page 8, printed page 3**.
- Literal unit: **In millions of Korean Won, except per share amounts**. Selected rows are monetary statement totals, not per-share amounts.
- Column order: **2024 three months, 2024 nine months, 2023 three months, 2023 nine months**, all ending September 30.
- AI inspection used both a rasterized page and `pypdf` text. No human or expert independently verified this gold.

| Literal source row | 2024 Q3 | 2024 YTD | 2023 Q3 | 2023 YTD |
| --- | ---: | ---: | ---: | ---: |
| Sales | 42,928,332 | 128,607,452 | 40,991,126 | 120,994,346 |
| Gross profit | 8,497,928 | 26,662,951 | 8,463,307 | 25,132,602 |
| Operating profit | 3,580,900 | 11,417,398 | 3,828,468 | 11,719,109 |
| Profit for the period | 3,205,850 | 10,755,751 | 3,303,451 | 10,069,667 |

`Sales` maps explicitly to the existing canonical metric/row `revenue` / `Revenue`. Literal source rows, cell strings and one-based column positions are preserved in `data/hyundai-holdout-20261109/source_cells.json`; canonical facts, complete source metadata, bilingual query expectations and rational-arithmetic calculation expectations are frozen separately alongside `freeze.json`. PDFs, extracted text and page renderings remain in ignored `work/hyundai-holdout-20261109/`.

The independent audit verifies PDF bytes, page count, issuer, consolidated statement title, ordered period/year header, unit, four literal amount cells, selected column, exact value, dates and scale before invoking the production parser. It does not use the production ingestion function to create or validate gold. Expected Q3 growth is **4.7259% revenue** and **−6.4665% operating profit**, calculated with rational arithmetic and four-decimal half-even rounding before evaluation.

## Preserved baseline

`artifacts/hyundai-holdout-20261109/baseline-first.json` runs the actual code from isolated baseline revision `0b1613c`; `baseline-first-failures.json` separately preserves failure details and the baseline artifact hash. Both are exclusively created and cannot be overwritten by the runner.

| Stage | Passed / total |
| --- | ---: |
| Independent source-cell audit | 16 / 16 |
| Raw statement ingestion | 0 / 1 |
| Raw exact cells | 0 / 16 |
| Raw query contracts | 0 / 8 |
| Fixture-assisted query contracts | 7 / 8 |
| Fixture-assisted citations | 16 / 16 |
| Fixture-assisted calculations | 2 / 2 |

The old parser rejects this statement with `UNSUPPORTED_LAYOUT: ordered header, units or periods`. The English natural positive query `What was Hyundai Motor consolidated revenue for the third quarter of 2024 in KRW million?` retrieves the correct top candidate but fails the answerability contract with `MISSING_KIND` (quarter versus YTD is unresolved); its original query and expectation are retained. All four intentionally ambiguous English/Korean queries must request clarification; candidate retrieval alone does not count as a verified answer.

## First revised-parser observation: retained failure

`artifacts/hyundai-holdout-20261109/current-first.json` and `current-first-failures.json` preserve the first run of the new Hyundai adapter. **It failed: 0/1 raw statements and 0/16 exact cells.** The source audit still passes all 16 frozen cells. The error is `UNSUPPORTED_LAYOUT: Hyundai net_profit preceding row cells or notes`.

The 2024 source has a `Loss from discontinued operations` row immediately before `Profit for the period`. Its four cells are `-`, `(319,110)`, `(38,297)`, `(262,372)`; the first parser did not accept that preceding-row shape. The parser returned no partial result, so raw query, citation and calculation chains are blocked. Fixture-assisted results remain 7/8 query contracts, 16/16 citations and 2/2 calculations. Those fixture passes do not imply PDF ingestion success.

The complete implementation module hashes are recorded, including the separate `hyundai_ingest.py` adapter, as well as the frozen-input and evaluator hashes. This failure was disclosed after preserving the first observation. Any subsequent fix or rerun of this document is **post-disclosure regression**, not unseen holdout success. The frozen queries and numeric gold are unchanged.

## Post-disclosure regression and a second final document

The bounded preceding-row dash repair passes the original 2024 source on replay: **1/1 statement, 16/16 exact cells, 7/8 raw query contracts, 16/16 raw citations, 2/2 raw calculations**. `artifacts/hyundai-holdout-20261109/post-disclosure-regression.json` is explicitly remediation evidence. The original English `MISSING_KIND` query still fails; its text and expectation were not changed. All baseline and first-failure artifacts remain unchanged.

After this disclosure, the evaluator froze a second official document while the parser worker repaired the disclosed case. A guessed 2022 Q3 PDF URL returned HTTP 404, so the available 2025 Q3 report was selected. The parser worker did not inspect the final document or gold before declaring the repair ready. The evaluator did not read the changed parser implementation.

- [Official Hyundai 2025 Q3 PDF](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2025/2025-q3-consolidated-audit-report-en.pdf), accessed 2026-11-09; 72 PDF pages, statement **PDF page 8 / printed page 3**, CFS.
- PDF SHA-256: `d2ad517018d5498f834a45bd3f976549b6c1be8a5b1d29930d8b149f542d1219`.
- Separate freeze: `data/hyundai-final-20261109/freeze.json`; same four metrics, 16 exact cells, four positive and four ambiguous bilingual query contracts, two year-over-year calculations.
- The eight comparative 2024 cells exactly overlap the now-disclosed 2024 source. **Eight current-year 2025 cells are new.** This is newly withheld source-document evidence, not wholly unseen numeric data.
- Positive final queries explicitly specify quarter/YTD, scope and currency. The first English query was authored after the earlier `MISSING_KIND` observation, as requested. These are frozen explicit query contracts informed by disclosed limitations, **not blind natural-language generalization**.

| Literal source row | 2025 Q3 | 2025 YTD | 2024 Q3 | 2024 YTD |
| --- | ---: | ---: | ---: | ---: |
| Sales | 46,721,448 | 139,415,886 | 42,928,332 | 128,607,452 |
| Gross profit | 8,284,059 | 26,373,397 | 8,497,928 | 26,662,951 |
| Operating profit | 2,537,266 | 9,772,472 | 3,580,900 | 11,417,398 |
| Profit for the period | 2,548,183 | 9,180,747 | 3,205,850 | 10,755,751 |

`artifacts/hyundai-final-20261109/current-first.json` preserves the **first** final-document observation. Its results are:

| Stage | Raw parsed corpus | Fixture-assisted corpus |
| --- | ---: | ---: |
| Statement / exact cells | 1/1 statement; 16/16 cells | Not ingestion evidence |
| Query contracts | 8/8 | 8/8 |
| Canonical citations | 16/16 | 16/16 |
| Exact calculations | 2/2 | 2/2 |

All 16 independent source audits pass. The four positive queries rank the expected fact first and meet the ready contract; the four ambiguous queries request clarification. Revenue Q3 growth is **8.8359%**, operating-profit Q3 growth **−29.1445%**. These results establish a narrow actual-PDF-to-parsed-facts-to-query/citation/calculation chain **inside the explicit evaluation adapter**. The unchanged production registry accepts **0/16** parsed facts; this evaluation does not make Hyundai available in the production corpus. Fixture results are reported separately even though their counts match.

`current-first-failures.json` records the empty final failure lists and first-result hash. `artifacts/hyundai-final-20261109/summary.json` pins both freezes and every baseline, failure, remediation and final result by SHA-256. No original result is overwritten, and none is relabeled as expert-reviewed gold.

To replay the final document after downloading its PDF as `work/hyundai-final-20261109/h25q3.pdf`:

```bash
python scripts/evaluate_hyundai_holdout.py --data data/hyundai-final-20261109 --cache work/hyundai-final-20261109 --label 'Final document replay; not fresh holdout' --output artifacts/hyundai-final-20261109/replay.json
```

## Evaluation boundary and reproduction

`scripts/evaluate_hyundai_holdout.py` reuses the existing `quarterguard/evaluation_v2.py` isolated adapter while supplying an independent audit for the newly frozen source. Each revision runs in a new Python process. Raw downstream evaluation may register only independently audited exact parser outputs inside temporary `source_manifest` and `source_facts` patches. Fixture-assisted downstream checks instead supply the gold directly. Actual `valid_source`, query, search and calculation functions remain in use. Neither stage changes the production source registry or corpus; successful isolated raw parsing does not establish production end-to-end availability.

```bash
mkdir -p work/hyundai-holdout-20261109
curl --fail --location 'https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2024/2024-q3-consolidated-audit-report-en.pdf' --output work/hyundai-holdout-20261109/h24q3.pdf
python scripts/evaluate_hyundai_holdout.py --label 'Explicit replay; not a fresh holdout' --output artifacts/hyundai-holdout-20261109/replay.json
```

Use a fresh output path for every run. Frozen-input or PDF-hash changes fail closed instead of updating gold. Baseline reproduction additionally requires `--code-root` pointing to an isolated checkout of `0b1613c`. The harness records implementation hashes, its own hash, the reused adapter hash and the freeze hash. No model API is called: provider API cost is **$0**, excluding local CPU, storage and network.
