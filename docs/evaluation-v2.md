# Frozen official-document evaluation v2

The final, separately frozen Samsung 2022 Q3 sample passed the isolated raw-PDF pipeline: 16/16 exact cells, 8/8 query contracts and 2/2 calculations. It does not establish production support because the new documents remain outside the application's canonical registry. The earlier first post-fix run failed all five 2023 statements; those failures remain unchanged and are reported first below.

| Measure | Baseline `39b59bd` | First post-fix |
|---|---:|---:|
| Independently audited source cells | 80/80 | 80/80 |
| Raw statements with every gold cell exact | 0/5 | 0/5 |
| Raw parsed cells matching all fact/provenance fields | 0/80 | 0/80 |
| Raw query contract passes | 0/24 | 0/24 |
| Raw citation checks | 0/80 | 0/80 |
| Raw calculations | 0/6 | 0/6 |
| Fixture query contract passes | 1/24 | 20/24 |
| Fixture positive retrieval R@1 / R@5 / MRR@5 | 0 / 0 / 0 | 0.7143 / 0.7143 / 0.7143 |
| Fixture citation checks with isolated registration | 80/80 | 80/80 |
| Fixture calculations with isolated registration | 6/6 | 6/6 |

The positive retrieval denominator is 14. The other ten cases request clarification for missing/conflicting/unsupported context or require no result for an unsupported source unit. A query contract pass requires the expected clarification/no-result response, or a rank-one positive hit plus complete parsed constraints. It is not a final financial-answer certification: the search API itself reports `answer_status=not_verified`. The baseline has no diagnostic API and thus cannot pass the nine required-clarification cases merely by returning no candidates. Its low query contract score must not be described as an unsafe-answer rate.

## Documents and freeze

Official PDFs were fetched with ordinary TLS verification on 2026-10-31. Only atomic numeric cells, URLs, page/row/column locators and short header metadata are committed. Full PDFs and extracted text remain under ignored `work/v2-blind-raw/`.

| Official document | PDF pages | Statement PDF pages | Evaluation facts |
|---|---:|---|---:|
| [Samsung Electronics 2023 H1](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2023_Half_Interim_Report.pdf) | 303 | CFS 47; OFS 103 | 32 |
| [Samsung Electronics 2023 Q3](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2023_3Q_Interim_Report.pdf) | 205 | CFS 38; OFS 93 | 32 |
| [Hyundai Motor 2023 Q3](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2023/2023-q3-consolidated-audit-report-en.pdf) | 68 | CFS 8 (printed page 3) | 16 |

The Hyundai PDF was discovered through its official IR quarterly-earnings page and its `financial-statements.enPastReport.do` response for 2023. Each source's exact PDF SHA-256, report-end date, issuer, page count and statement pages are in `data/v2-blind/sources.json`. Facts contain current 2023 and comparative 2022 columns, direct quarter and cumulative periods, KRW million units, CFS/OFS context and exact values. Literal source rows and one-based data-column positions are separately preserved in `source_cells.json`; canonical `Sales -> Revenue` and `Operating profit (loss) -> Operating profit` mappings are explicit.

The 80 facts, 24 Korean/English questions and six calculation expectations were frozen at **2026-10-31T12:23:14.398410+00:00**, before either evaluation run. `freeze.json` SHA-256 is `0c34675a0a408ee92f4e4bccc8d2552eb929f145c0aab0b432bdfc2c8b18dfec`. The author was a separate AI worker in the same task. The worker inspected only baseline code at `39b59bd` for interfaces before freezing, not the changed parser/search or their outcomes. There was **no human review, independent expert curation, or participant evaluation**.

These are new source documents and reporting-period tests, with a new Hyundai issuer. Samsung's 2023 values also appear as comparative figures in the existing 2024 documents, so the dataset is **not wholly unseen financial data**. Existing 2025 cases remain disclosed remediation regression, not part of this new freeze. No old evaluation/data records were changed.

## What actually ran

`quarterguard/evaluation_v2.py` verifies the frozen input hashes, PDF hashes and page counts, then independently audits the literal gold cells and table headers using pypdf. This audit never invokes production ingestion. It runs each revision's actual `parse_statement` on actual PDF-extracted statement pages. Every gold cell requires exact company, metric, value, period, currency, scale, source URL, page, row, column, document ID and PDF hash; successful count alone is insufficient.

The baseline is a `git archive 39b59bd` snapshot imported in a fresh process. Current and baseline use the identical frozen facts, queries and calculation expectations. The first observed results are exclusive-created artifacts that the CLI refuses to overwrite:

- `artifacts/evaluation-v2-baseline.json`
- `artifacts/evaluation-v2-first-post-fix.json`
- `artifacts/evaluation-v2-summary.json` links their hashes and records module fingerprints.

The raw stage constructs its search corpus only from actual parser output. Missing parsed facts block citation/calculation evaluation; negative queries receive no credit when ingestion produced no corpus. An isolated evaluation adapter patches the manifest and canonical fact registry, accepting only parser outputs that match independently frozen gold. This adapter is disclosed and does not install the documents in the application's production registry. The separate fixture stage supplies gold directly to SearchIndex/core and uses an isolated registry, measuring only downstream behavior. Production canonical registration remains unchanged.

All five parser calls failed in both revisions, so there were no actual parsed downstream facts and no successful raw end-to-end chain. The fixture calculations cover four Samsung YTD-minus-H1 reconciliations and two current/prior-year revenue comparisons, including Hyundai. Fixture citation results demonstrate canonical registration checks against supplied fixtures; they do not prove a general Hyundai row parser exists.

## First observed failures, retained

The first post-fix parser required the unit phrase `Korean won and in thousands`. All four 2023 Samsung statement headers use `Korean won, in thousands`, so they rejected with `UNSUPPORTED_LAYOUT: ordered header, units or periods`. Hyundai has `STATEMENTS OF INCOME`, four KRW columns grouped by year, and a different header layout; it also rejected. These are retained failures. After disclosure, the comma-header behavior and missing query aliases were explicitly fixed; the follow-up is regression evidence, described below.

Four positive fixture questions failed in that first run: Korean `상반기` was not normalized to the Q2 cumulative endpoint; two Korean Hyundai issuer queries lacked a recognized issuer alias; and `Hyundai Motor` left `Motor` unsupported. The shorter English `Hyundai` query succeeded against the fixture. No gold questions were edited. `first_observed_failures` in the artifacts preserves exact case IDs and observed issues, even after the disclosed alias changes.

The ranking worker separately used the same frozen facts/questions; its first run is `artifacts/ranking-v2-blind-first.json`. Those candidate-ranking results do not change the raw-ingestion failures here.

## Reproduction and integrity checks

Download the three source URLs into ignored cache files `s23q2.pdf`, `s23q3.pdf`, `h23q3.pdf`, then:

```sh
mkdir -p work/v2-blind-raw/baseline
git archive 39b59bd | tar -x -C work/v2-blind-raw/baseline
.venv/bin/python quarterguard/evaluation_v2.py --code-root work/v2-blind-raw/baseline --label baseline-replay --output artifacts/evaluation-v2-baseline-replay.json
.venv/bin/python quarterguard/evaluation_v2.py --label current-replay --output artifacts/evaluation-v2-current-replay.json
.venv/bin/python -m unittest tests.test_evaluation_v2 -v
```

New output filenames are required; the first-observation artifacts are immutable. Six integrity tests cover freeze tampering, complete provenance matching, missing raw inputs, no credit for failed-ingestion negative queries, and candidate retrieval versus trusted complete query handling. No paid model/provider call occurred. Reported provider API cost is $0; local CPU/storage/network costs are outside that figure.

## Disclosed follow-up and final frozen round

After the first 2023 failures were disclosed, root authorized accepting the comma unit separator and adding `상반기`/registered Hyundai aliases. `artifacts/evaluation-v2-post-disclosure-regression.json` records the same frozen 2023 gold after these changes: raw statements **4/5**, exact cells **64/80**, raw query contracts **20/24**, raw calculations **5/6**, fixture query contracts **24/24**. Hyundai's raw layout remains unsupported. This is explicitly post-disclosure regression; it cannot replace the original holdout outcome.

A new final-round source was then independently collected: [Samsung 2022 Q3 Interim Report](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2022_3Q_Interim_Report_vF.pdf), 198 PDF pages, consolidated statement on PDF page37. Its PDF hash is `0a00681375790f92a4660c65983473b70a8bac17f163c84cadc062493b4851fd`. The narrow sample is four metrics × direct/cumulative × current/comparative years: 16 KRW cells, eight new questions and two YoY calculations. It does not include the separate statement or establish coverage of the entire report.

`data/v2-final/freeze.json` was created at **2026-10-31T12:29:25.431926+00:00**, SHA-256 `90f47e7bf0a58c6afbe22614f0b0796db42dd2c5efe1210d9f386e4fa516055f`, before any final-source pipeline run. The earlier fixes already existed, and the evaluation author knew their disclosed purpose; final gold was not shared with fix workers. The 2022 values overlap the first-round 2023 comparative column; the 2021 values are new to both earlier datasets. Four of the six positive final questions target 2021. This is a small same-task AI freeze after disclosed development, not independent human curation or proof of broad generalization.

| Final-round measure | Baseline `39b59bd` | First current run |
|---|---:|---:|
| Source audit | 16/16 | 16/16 |
| Raw statement / exact KRW cells | 0/1; 0/16 | 1/1; 16/16 |
| Raw query contract passes | 0/8 | 8/8 |
| Raw exact citation checks | 0/16 | 16/16 |
| Raw YoY calculation checks | 0/2 | 2/2 |
| Raw positive retrieval R@1 | 0/6 | 6/6 |
| Fixture query contract passes | 0/8 | 8/8 |
| Fixture citation / calculation checks | 16/16; 2/2 | 16/16; 2/2 |

The actual parser produced 32 cells, including 16 USD convenience-translation cells outside this gold sample. The raw downstream corpus uses those actual outputs; only the 16 exact, independently audited KRW cells are registered in the isolated evaluation adapter. The production registry accepted **0/32**, so this evidence is **raw PDF → exact parsed facts → isolated registered search/citations/calculations**, not deployed end-to-end product support.

The immutable final artifacts are `artifacts/evaluation-v2-final-first.json` and `artifacts/evaluation-v2-final-baseline.json`; `artifacts/evaluation-v2-final-summary.json` links their hashes and the preserved earlier observations. Reproduce with the downloaded official PDF named `2022_3Q_Interim_Report_vF.pdf` in the same ignored cache, adding `--data data/v2-final` and a new output path to the CLI commands above. The harness's independent source audit was generalized from fixed 2023 header years to the frozen manifest's report year; no production parser/search changes were made by this evaluation worker.

## Replay after independent row-label review

Independent code review found that an unrelated prefixed row such as `Adjusted Gross profit` could be mistaken for the canonical metric. The parser worker reproduced and fixed this with synthetic adversarial cases, without changing frozen gold. `artifacts/evaluation-v2-final-reviewed.json` repeats the final source after that guard: **1/1 statement, 16/16 exact cells, 8/8 raw query contracts, 16/16 raw citations and 2/2 raw calculations**, unchanged from the first final observation. `artifacts/evaluation-v2-regression-reviewed.json` likewise retains the disclosed 2023 results: **4/5 statements, 64/80 cells, 20/24 raw query contracts and 5/6 raw calculations**; Hyundai's raw layout still fails. Both are explicitly replays rather than new holdout results. The five observations linked by `evaluation-v2-final-summary.json` were hash-checked unchanged before this replay; the original final-first artifact remains preserved.
