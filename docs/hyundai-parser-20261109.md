# Hyundai income-statement adapter — 2026-11-09

The parser now accepts the verified Hyundai Motor Company consolidated interim income-statement layout through `quarterguard.ingest.parse_statement`. The existing production document/fact registry is unchanged. This is parser support and isolated evaluation evidence, not a claim that Hyundai is available in the deployed application.

## Official source and literal table

Development used the already disclosed [official 2023 Q3 consolidated report](https://www.hyundai.com/content/dam/hyundai/ww/en/images/company/investor-relations/financial-Information/report-en/2023/2023-q3-consolidated-audit-report-en.pdf), PDF page **8**, printed page 3. The existing local PDF cache was reused, not freshly downloaded. Its 68-page count and SHA-256 `5ac749a9810e566bc92e23234137c9bc7ab60c734f7ead2badc6b73f9ef38121` match the frozen source manifest. Full PDF/text remains in the ignored local cache.

The source heading says **INTERIM CONSOLIDATED STATEMENTS OF INCOME** and **In millions of Korean Won, except per share amounts**. Physical columns are ordered by year: 2023 Q3, 2023 nine months, 2022 Q3, 2022 nine months.

| Literal source row | 2023 Q3 | 2023 nine months | 2022 Q3 | 2022 nine months |
| --- | ---: | ---: | ---: | ---: |
| Sales | 41,002,663 | 121,031,051 | 37,705,442 | 104,003,906 |
| Gross profit | 8,461,358 | 25,076,757 | 7,357,191 | 20,530,701 |
| Operating profit | 3,821,799 | 11,652,429 | 1,551,819 | 6,460,543 |
| Profit for the period | 3,303,451 | 10,069,667 | 1,411,490 | 6,273,692 |

[`hyundai-2023-extracted.json`](../artifacts/hyundai-parser-20261109/hyundai-2023-extracted.json) contains all **24 actual parser outputs** for six existing metrics, their complete source context, and physical column/literal-row locators. Sixteen cells match the pre-existing frozen gold in every field. Eight extra cost-of-sales/operating-expense outputs are not counted as independently validated gold.

## Mapping and rejection rules

[`hyundai_ingest.py`](../quarterguard/hyundai_ingest.py) is selected only by explicit manifest `company='hyundai'`. It verifies the issuer heading, consolidated income-statement title, report period, matching adjacent current/prior year headings, Notes header, all four ordered period labels, KRW-million units, and any manifest date/scope/page constraint. The canonical `Fact.row` vocabulary is preserved: literal **Sales → Revenue**; the other five source row names map directly. Literal labels and physical column numbers are separately retained in the extraction artifact.

Q2/six-month and Q3/nine-month versions of this exact header are accepted; the Q2 form has synthetic coverage. Dates are derived from the verified header, never the document ID. Columns 1–2 belong to the current year, columns 3–4 to the prior year; odd physical columns are direct quarters and even columns are YTD. Facts retain issuer, metric, scope, currency, scale, period, source URL, PDF hash, page and canonical row/column. No USD conversion or inferred value is produced.

Unknown layouts, separate statements, Q1/year-end formats, conflicting headers, missing/duplicate/qualified metric rows, ambiguous note/amount sequences, malformed amounts and missing/extra cells raise `UNSUPPORTED_LAYOUT`. Parentheses denote negative numbers. Whitespace may wrap labels and headers. Four currency signs or no currency signs are allowed per monetary row; mixed/partial currency-sign rows are rejected. OCR and arbitrary number-fragment repairs are unsupported.

The independent 2024 first run disclosed a dash in a preceding discontinued-operations row. The first failure is retained by the holdout worker. A new failing test reproduced that rejection; the correction permits a standalone dash **only for structural validation of an unrelated preceding row**. A requested metric with a dash is still rejected rather than converted to zero. [`disclosed-dash-before.txt`](../artifacts/hyundai-parser-20261109/disclosed-dash-before.txt) and [`disclosed-dash-after.txt`](../artifacts/hyundai-parser-20261109/disclosed-dash-after.txt) preserve this development step. Subsequent 2024 success must be described as post-disclosure remediation, not a first-pass holdout success.

## Preserved development results

| Check | Before Hyundai adapter | After initial adapter |
| --- | ---: | ---: |
| Existing frozen 2023 raw statements | 4/5 | 5/5 |
| Existing frozen 2023 exact gold cells | 64/80 | 80/80 |
| Existing frozen 2023 raw query contracts | 20/24 | 24/24 |
| Existing frozen 2023 raw citations | 64/80 | 80/80 |
| Existing frozen 2023 raw calculations | 5/6 | 6/6 |

These are **known-case remediation results** from the actual PDF extraction pipeline. The old 2023 first observations remain unchanged. The new [`known-2023-before.json`](../artifacts/hyundai-parser-20261109/known-2023-before.json) and [`known-2023-after.json`](../artifacts/hyundai-parser-20261109/known-2023-after.json) do not overwrite earlier evaluations. The evaluation's raw corpus uses actual parser output, and its isolated canonical registration admits only exact frozen-gold matches. The separately labeled fixture stage supplies gold directly and does not prove ingestion.

[`samsung-regression-after.json`](../artifacts/hyundai-parser-20261109/samsung-regression-after.json) records actual official PDF regression: **2024: 4/4 statements, 192/192 complete public records identical**; **2025: 4/4 statements, 192 extracted facts, 64/64 sampled gold facts identical**. The remaining 128 extracted 2025 facts are not independently checked gold. Known 2025 source arithmetic conflicts are not resolved by successful extraction.

The original 12 new Hyundai tests first failed on unsupported headers (three assertion failures and three rejection errors), then passed. After the disclosed dash case, **13/13 Hyundai tests pass**, including the real 2023 PDF comparison. The initial full-suite snapshot ran 166 tests with seven failures in the concurrently unfinished `test_live_explanations_v3` harness; its log is retained rather than relabeled as green. The completed final suite passes **167/167 tests** in [`tests-suite-final.txt`](../artifacts/hyundai-parser-20261109/tests-suite-final.txt).

The final code was also rerun against the known 2023 PDFs and Samsung regressions after the dash correction: [`known-2023-final-regression.json`](../artifacts/hyundai-parser-20261109/known-2023-final-regression.json) retains 5/5 statements, 80/80 exact cells, 24/24 query contracts, 80/80 citations and 6/6 calculations; [`samsung-regression-final.json`](../artifacts/hyundai-parser-20261109/samsung-regression-final.json) retains the 2024/2025 counts above. Separate first-run and post-disclosure holdout outcomes are documented by the independent worker in [`hyundai-holdout-20261109.md`](hyundai-holdout-20261109.md).

[`historical-preservation.json`](../artifacts/hyundai-parser-20261109/historical-preservation.json) verifies all **109 tracked historical data/artifact files** are byte-identical to the branch baseline. No paid model/provider calls occurred in this parser work; paid provider API cost is $0, excluding CPU, storage and network. Evaluation and fixtures are same-task AI-authored, with no human/expert review.

## Product boundary and minimal route

The current production registry accepts **0/24 Hyundai facts**. The 2023 mixed-issuer evaluation similarly reports **0/144 parsed facts registered**. `collect()` still targets the existing two-statement Samsung corpus; it has not been extended into a Hyundai importer. Parser support therefore does not silently change API/search/UI availability.

The smallest product integration is a separately reviewed, explicit registration of one verified Hyundai document and its parsed facts, keeping literal source-cell mappings alongside the canonical fact records. Then exercise the normal application search, citation validator, compare/reconcile and source-link UI against that registered corpus. Do not bypass `valid_source`, present the evaluation's temporary registry as deployment, or automatically register unchecked additional rows. Broader issuer/period support requires more source layouts and tests.

## Replay

With the existing ignored official PDF cache present:

```bash
python -m unittest tests.test_hyundai_parser tests.test_parser_v2 -v
python quarterguard/evaluation_v2.py --label hyundai-known-2023-replay --output artifacts/hyundai-known-2023-replay.json
```

Use a new output filename for every evaluation. The harness refuses to overwrite its output. Hash both `quarterguard/ingest.py` and `quarterguard/hyundai_ingest.py`: the older generic harness fingerprints `ingest.py` but does not yet include the separate Hyundai module automatically.
