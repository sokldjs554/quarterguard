# Search query diagnostics v2

The bounded Korean/English parser retains explicit company, metric, year, end quarter, direct-quarter/YTD kind, statement scope, currency, and scale. It does not infer omitted fields from the corpus. Recognized phrases are consumed longest-first; residual words, numbers, currency symbols, and operators must be recognized grammatical tokens or retrieval is blocked. Negation and conflicting conditions require clarification. This is a finite vocabulary, not general language understanding.

`SearchIndex(facts, config='hybrid_meta', company_aliases=None)` derives eligible company identifiers from the supplied facts. Samsung and Hyundai Motor aliases are enabled only when their corresponding canonical issuers (`samsung`, `hyundai`) are registered. Bare `현대` is not treated as Hyundai Motor. Other canonical names work directly; optional aliases use `{canonical_company: [alias, ...]}`. Shared aliases produce a company conflict. Configuration cannot register facts or authorize a source.

`search_with_diagnostics(query, k=5)` returns:

- `hits`: ranked candidate chunks, never verified financial answers.
- `status`: `ready` for a complete query with available unambiguous candidates; `needs_clarification` for missing, conflicting, unsupported, or ambiguous conditions; `no_results` for a complete query with no retrieved candidate.
- `filters`, `missing_fields`, `issues`, `unknown_terms`, and `blocked`: the explicit interpretation and reasons it cannot proceed.
- `trusted_query`: all eight required conditions are explicit and no parsing/source-selection ambiguity was detected. This does **not** attest source validity or authorize a comparison.
- `candidate_fact_count`: compatible facts before ranking/top-k, or zero for blocked requests. Multiple complete-context matches produce `AMBIGUOUS_FACT`, including when `k=1`.
- `answer_status`: always `not_verified`. Existing canonical-source, period, scope, currency, convenience-translation, denominator, and arithmetic guards remain in the verification workflow.

Missing fields permit candidates matching the supplied filters, with `needs_clarification`. Unsupported/contradictory terms return no candidates. `Q3`, `3분기`, and `third quarter` specify the end quarter without assuming direct-quarter versus YTD. `3개월`/`three months` specify direct-quarter; `first nine months` specifies YTD ending Q3. `won`/`원화` identify currency, not reporting scale. `millions`, `백만원`, and `백만 원` identify scale; the Korean denomination also identifies KRW. Explicit units filter stored representation exactly, without conversion. A complete USD query can be retrieved, but convenience translation remains blocked by the unchanged comparison guard.

Examples:

```text
Please show Samsung Electronics consolidated revenue for Q3 2024 for three months in millions of Korean won.
삼성전자의 2024년 3분기 연결 매출액을 3개월 기준 백만원 단위로 알려주세요.
```

Both select the same fully specified candidate. `What was Samsung consolidated revenue in the third quarter of 2024?` instead requests clarification for kind, currency, and scale, even when the target appears among its candidates.

For compatibility, `search(query, k)` still returns a list. In `hybrid_meta` it returns the diagnostic candidate list, including safe but incomplete queries. The non-hybrid list API preserves unfiltered lexical benchmark behavior; product/API callers must use `search_with_diagnostics`, which applies constraints for **every** ranking configuration. `constraints(query, companies=None, company_aliases=None)` remains a filters-or-None compatibility helper; pass registered companies explicitly for new issuers. New ranking code can use `parse_query(query, companies, company_aliases=None)` to distinguish blocked requests from incomplete queries.

## Benchmark interpretation

The old `data/heldout` natural queries were disclosed before these changes and are development regressions. They are not a fresh blind evaluation. `artifacts/search-development-v2.json` preserves baseline/current results separately, with input/source hashes and the historical failure artifact hash. Missing conditions are reported explicitly; candidate recall is not answer accuracy. No new blind gold was accessed during parser development. No paid API was used and no human review is claimed.

Fixed-width chunks previously inserted `samsung ... 2024 2023 KRW USD quarter ytd` into every document. Their header now derives company, years, currencies, and period kinds from each document/scope group. The 180-character splitting policy remains unchanged, but corrected header length changes chunk boundaries and hence baseline performance. Re-run all configurations over the same corrected serialization for a fair new comparison; historical fixed-chunk scores remain historical and should not be attributed solely to parser or ranking improvements.

## Post-disclosure vocabulary correction

The separate first v2 evaluation reported misses on `상반기` and Hyundai Motor names. After disclosure, two new regression tests demonstrated the missing behavior using synthetic facts based on existing development data. `상반기` now means YTD ending Q2; `Hyundai Motor`, `Hyundai Motor Company`, and `현대자동차` resolve to registered `hyundai`. This is a post-disclosure correction, not evidence of success on untouched questions. The initial development artifact and the separate first evaluation remain unchanged; `artifacts/search-development-v2-followup.json` records the follow-up and its provenance. No new final-evaluation gold was accessed for these changes.

Verification: `PYTHONPATH=tests .venv/bin/python -m unittest test_pipeline test_review_regressions test_query_v2` passed 25 tests after the follow-up (23 at the initial snapshot). Root integration owns the full suite and the historical heldout assertion update. The original full-suite attempt was interrupted at root's request; it is not reported as a pass.
