# New-document evaluation: frozen first baseline

This evaluation adds **two official 2025 Samsung reports, 64 atomic numeric facts and 40 cases** beyond the existing two-report 2024 development corpus. It is **AI-authored and not human-reviewed**. These documents were newly withheld from the existing frozen pipeline; this is not an independently curated human holdout or evidence of cross-company generalization. The first-run baseline was completed before any production change. After disclosure, canonical source validation was repaired and re-evaluated as a separately labeled **post-disclosure regression**, not as unseen heldout performance. The parser, search and development data remain unchanged.

There is **no successful end-to-end raw-PDF evaluation**: the production parser rejects all four new statement pages, and the production source registry accepts none of the 64 new facts. Downstream results below use explicit fixtures and an isolated source-manifest adapter. They must not be presented as PDF-to-answer success.

| Stage | Cases | Passed | Failed | Meaning |
| --- | ---: | ---: | ---: | --- |
| Raw ingestion | 4 | 0 | 4 | Real unmodified parser on PDF-extracted statement pages |
| Fixture-assisted retrieval | 10 | 5 | 5 | 5/5 controlled queries; 0/5 natural questions |
| Fixture-assisted calculation | 8 | 8 | 0 | Five growth comparisons, two consistent reconciliations, one detected source conflict |
| Fixture-assisted context | 10 | 10 | 0 | Period, scope, unit, company, metric, currency, translation, zero/negative base; equivalent scale normalization |
| Fixture-assisted citation | 8 | 5 | 3 | Metadata checks reject page/hash/URL/row changes, but miss value/scale/company substitutions |

Do not combine these into a headline accuracy score: their assistance and success criteria differ. Controlled retrieval recall@1/recall@5/MRR@5 are all 1.0; natural-query values are all 0.0. Each denominator is only five. Positive numeric comparisons use KRW million amounts and exact four-decimal percentage expectations; unit conversion is tested separately. Evidence preservation checks confirm the returned objects equal the supplied inputs, which does not establish that a supplied number is true.

## Post-disclosure remediation (separate from the baseline)

The latest `artifacts/heldout-evaluation.json` and `data/heldout/post-fix.json` record the subsequent run; `data/heldout/first-run.json` is unchanged. This run deliberately allows only `core.py` to differ from the frozen production hashes and records current hashes. It injects **both** the source manifest and canonical fact dictionaries from the same frozen fixtures. The real revised validator compares facts to these canonical dictionaries. This is stronger fixture assistance, still not PDF ingestion success.

| Stage | First baseline passed/total | Post-disclosure passed/total |
| --- | ---: | ---: |
| Raw ingestion | 0/4 | 0/4 |
| Fixture retrieval | 5/10 | 5/10 |
| Fixture calculation | 8/8 | 8/8 |
| Fixture context | 10/10 | 10/10 |
| Fixture citation | 5/8 | 8/8 |

All three disclosed citation mutations are now rejected. The revised binding compares normalized amount (`value × scale`) and requires the other canonical fields to match. It therefore preserves `context-scale-equivalent`: `74,566,317,000 × 1,000` and `74,566,317 × 1,000,000` represent the same amount, while changing the scale alone is rejected. The frozen expected result remains unchanged. An intermediate exact-field implementation rejected that equivalent conversion; the final post-disclosure run corrects that regression. Four ingestion failures and all five natural-query failures persist, for **9 post-disclosure failures** versus 12 baseline failures. Do not use the improved citation score as fresh heldout evidence.

## Sources, gold and split

Development remains in `data/sources.json`, `data/facts.json` and the existing template cases. Evaluation inputs live exclusively in `data/heldout/`; they are never inserted into the application corpus or its allowlist.

| Document | Official PDF | Statement pages | SHA-256 |
| --- | --- | --- | --- |
| 2025 Half-year report | [Samsung official source](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_Half_Interim_Report.pdf) | CFS 44, OFS 96; 270 pages total | `fde04bf7ebcd4bced0bd5c52c4df5b020db882ed7b65388349583af8e257e218` |
| 2025 Q3 report | [Samsung official source](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_3Q_Interim_Report.pdf) | CFS 34, OFS 89; 193 pages total | `da4ffec442cae45ffbba478dbb05001f8dbce0c236a5618c308225548c32667a` |

Accessed 2026-10-29. Page numbers are one-based PDF pages and match printed page numbers here. Only atomic numeric cells and source locators are distributed; PDFs, extracted full text and the rasterized page remain in ignored `work/heldout-raw/`.

The agent transcribed revenue, gross profit, operating profit and profit for the period for both scopes, both current/prior years, and quarter/YTD columns: 4 metrics × 2 scopes × 2 reports × 4 KRW cells = 64 facts. Production ingestion did not create these facts. The independent harness reopens hash-checked PDFs and matches all 64 literal row cells with the selected KRW column ordinal; it also checks scope and unit headings. The H1 separate statement wraps some revenue digits across lines; the audit joins digit-only line breaks explicitly. These checks are AI/script checks, not human review.

Expected growth labels were calculated using rational `Fraction` arithmetic before evaluation, separate from production Decimal arithmetic. Source-literal facts, expected statuses/issues and queries were frozen before the first benchmark run. `freeze.json` contains their hashes and the hashes of production `core.py`, `ingest.py`, `search.py` and development source/fact files. Baseline-mode reruns refuse changed frozen inputs. Explicit `--post-fix` mode permits a changed `core.py` only; source, gold, parser, search and development-data hashes still must match. Gold authors knew the existing controlled vocabulary and parser restrictions, so query and mutation selection are not blind. Half the retrieval questions use controlled vocabulary; half are English or Korean natural questions with additional words and paraphrases. Mutations are declared synthetic challenge cases derived from the new source facts, not additional real-world observations.

`data/heldout/first-run.json` preserves the first full result. Reruns write `artifacts/heldout-evaluation.json` and reference the first-run SHA-256; they never overwrite the baseline. The complete rows include successful cases, every failure, expected/observed outputs, queries, retrieved IDs, source audit, numeric evidence and issues. The baseline evaluator changes only `source_manifest` temporarily for downstream tests and restores it afterward; the post-disclosure adapter also supplies `source_facts`, as stated above. **It does not replace `valid_source` or return unconditional validation success.**

## Every observed failure

- `ingest-s25q2-CFS`, `ingest-s25q2-OFS`, `ingest-s25q3-CFS`, `ingest-s25q3-OFS`: `UNSUPPORTED_LAYOUT: header`. The production parser requires the literal 2024/2023 year sequence. Unsupported input is safely rejected, but generalization to these reports fails.
- `retrieve-06`: “What was Samsung consolidated revenue in the third quarter of 2025?” — empty results.
- `retrieve-07`: “삼성전자 2025년 2분기 별도 영업이익은 얼마인가요?” — empty results.
- `retrieve-08`: “How much gross profit did Samsung report for Q2 2025 on a consolidated basis?” — empty results.
- `retrieve-09`: “Show Samsung separate net income for the first nine months of 2025 in won.” — empty results.
- `retrieve-10`: “2025년 3분기 삼성전자 연결 누적 매출을 알려줘” — empty results.
- `citation-value`: a fact changed to numeric value `1` passes `valid_source`; expected rejection.
- `citation-scale`: a million-KRW source fact relabeled with scale `1000` passes `valid_source`; expected rejection.
- `citation-company`: the cited fact relabeled as company `other` passes `valid_source`; expected rejection.

All five natural retrieval failures arise from the controlled-token query gate; synonym normalization does not accept these complete questions. The three citation failures show that URL/hash/page/row/column metadata agreement does not bind the supplied value, scale or company to the actual cell. The raw allowlist rejection (0/64 accepted) is separately reported and does not excuse these weaknesses in the fixture-assisted validator.

## Source disagreement retained in gold

The hash-pinned Q3 PDF, CFS page 34, prints profit for the period as **5,116,435 million KRW** for Q3 2025 and **13,339,313** YTD—the same numbers shown in the H1 report. Yet its Q3 profit before tax (13,545,563) minus tax (1,319,816) is 12,225,747, and its YTD corresponding calculation is 25,565,060. The attribution rows also disagree with the printed net-profit row. `pypdf`, a separate PyMuPDF extraction, and AI inspection of the rasterized PDF page agree on the printed row. No human has adjudicated the issuer data or identified a corrected report.

The gold preserves the printed values. `calc-08` subtracts the H1 YTD net profit from Q3 YTD, obtaining zero, and compares it with printed Q3 5,116,435. Production reconciliation correctly returns `NUMERIC_CONFLICT`, difference `-5116435`. This is a successful refusal test, **not a verified net-profit calculation**. The PDF inconsistency is not silently repaired or omitted.

## Reproduction

From the repository root with dependencies installed:

```bash
mkdir -p work/heldout-raw
curl --fail --location https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_Half_Interim_Report.pdf --output work/heldout-raw/2025_Half_Interim_Report.pdf
curl --fail --location https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_3Q_Interim_Report.pdf --output work/heldout-raw/2025_3Q_Interim_Report.pdf
.venv/bin/python -m quarterguard.heldout_evaluation --post-fix
.venv/bin/python -m unittest discover -s tests -p test_heldout.py -v
```

The commands above reproduce the current post-disclosure run. Baseline mode omits `--post-fix` and requires the original frozen core; its code is present in commit `14b2159cb22d350f30c2a259a2469cfe579058be`, with the exact hash recorded in `freeze.json`. Use an isolated checkout to restore that code, rather than replacing current production code. The first-run artifact remains the record of the original baseline.

The runner checks downloaded bytes against frozen hashes and fails rather than updating gold when an official PDF changes. It makes zero model calls, uses no API secrets and invokes no paid services. The recorded API cost is $0; CPU, storage and network are excluded. This small same-issuer, similar-layout baseline cannot establish broader multilingual, cross-company or unknown-layout reliability. Future improvements require a separately versioned experiment; preserve this first baseline and avoid treating these now-observed cases as unseen data.
