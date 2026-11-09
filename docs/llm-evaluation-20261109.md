# Bounded live explanation evaluation — 2026-11-09

This harness samples **eight new provider-generated Korean explanations**, with copied structured result fields and freely generated prose. It changes no product behavior. The historical four GPT-4.1-mini outputs in `artifacts/live-openai.json` remain untouched. Preparation and tests made zero paid calls. The approved live run has now completed; its results are recorded below separately from the offline fixtures.

The user approved this exact run on 2026-11-09: `gpt-5.4-mini-2026-03-17`, reasoning `none`, at most eight attempts, at most 700 output tokens per request, 6000 input-token admission limit, no retries, estimated maximum **$0.0612**, budget **$0.07 before tax**. The existing GitHub Actions `OPENAI_API_KEY` secret is used; no new key is created. The root agent is the sole dispatcher. This approval does not authorize another dispatch, a retry, an alternate model, or a larger run.

| Dimension | Authoritative input | Additional challenge |
|---|---|---|
| Normal QoQ | Actual MCP comparison, 6.7916% | None |
| Normal YoY | Actual MCP comparison, 17.3491% | None |
| Period | Actual MCP rejection of 9-month versus 3-month comparison | None |
| Scope | Actual MCP rejection of consolidated versus separate comparison | None |
| Unit | Actual MCP QoQ result | Explicitly synthetic draft incorrectly says thousand KRW |
| No evidence | Actual MCP search-empty rejection | None |
| Conflicting number | Actual MCP QoQ result | Explicitly synthetic draft claims 9.9999% |
| Citation | Actual MCP QoQ result | Explicitly synthetic draft supplies an invented URL |

All authoritative inputs are real MCP responses validated against canonical source evidence, expected status, value and issues before freezing. The eight prompts include deliberately authored development challenges; they are not held-out, representative, or randomly sampled. The three misleading drafts are clearly marked untrusted synthetic data. They are not fabricated financial evidence, model outputs, or human review labels. Six separate authored validator fixtures live in `synthetic-validator-checks.json`; their results must never be mixed into the real-output denominator.

`data/llm-eval-20261109/freeze.json` records case order, exact prompts by hash, the model contract, live MCP traces, source/code hashes, and the freeze timestamp. Generation refuses changed prompts, code, source facts or contract. It also refuses an output directory containing any prior attempt journal. Each network attempt is recorded and fsynced before HTTP. HTTP failures, timeouts, incomplete output, malformed response, wrong model or excessive measured usage stop the run immediately. There are no SDK retries or automatic resumptions. GitHub reruns (`GITHUB_RUN_ATTEMPT != 1`) are blocked; operators must not dispatch a second run under this approval.

Input admission counts the UTF-8 bytes of the **entire request JSON, including instructions and output schema, plus a 1024-token framing reserve**. Byte-level tokenization uses no more tokens than the source bytes. The frozen maximum admission value is 4023, well below 6000. This is a conservative local admission bound, not an API-enforced input-token cap: undocumented provider framing cannot be guaranteed by a client. Actual input/output usage is checked after every response, and any overage stops remaining requests. No tokenizer dependency is added.

The official model page lists $0.75 per million input tokens and $4.50 per million output tokens, checked 2026-11-09: <https://developers.openai.com/api/docs/models/gpt-5.4-mini>. Conservative maximum: `(8 × 6000 × $0.75 + 8 × 700 × $4.50) / 1,000,000 = $0.0612`. Reports retain measured tokens and list-price cost estimates. **Actual billed cost remains unknown**; failed attempts without usage, taxes, hosting and local compute are excluded from measured estimates.

The evaluator checks exact structured status/value/issues/evidence IDs and existing conservative prose rules for numbers, period, scope, units, rejection language and inline/canonical citations. Every result retains `semantic_certified: false`, `human_review_required: true`, and `semantic_accuracy: null`. A clean automatic result means only that no covered rule violation was detected. Attribution, negation, omitted qualifications, compound Korean quantities and citation relevance still require human judgment. Do not adapt rules or prompts after seeing these responses and then present the same run as untouched evaluation.

The output directory contains `attempts.jsonl`, one sanitized raw response per received response, `report.json`, and `human-review.json`. Response artifacts allowlist provider IDs/model/status/output text and token usage; HTTP requests, headers, keys, arbitrary provider metadata and error bodies are never serialized. Literal secret echoes are redacted. Human review tasks copy only actual successfully generated responses and their source results. Reviewer, timestamp, verdict, detailed checks and notes start blank; no synthetic human judgment is supplied.

Preparation already completed without paid calls:

```bash
python -m quarterguard.evaluate_live_explanations_v3 --prepare
python -m unittest discover -s tests -p test_live_explanations_v3.py -v
```

Do not run `--prepare` again against the existing freeze. The manual workflow `.github/workflows/live-explanations-v3.yml` checks out its exact event SHA, requires `approved_contract: true` and the exact approved `content_sha256`, validates the freeze before exposing the existing secret, and runs:

```bash
python -m quarterguard.evaluate_live_explanations_v3 --execute-approved \
  --output work/live-explanations-20261109
```

Download only artifact `live-explanations-v3-<run_id>` from that one run. Preserve failed-attempt evidence too. Successful generation is not a passing accuracy result: report the eight real-response audit outcomes separately from synthetic fixture detection and leave semantic accuracy unknown until the blank human tasks are completed by a real reviewer.

## Actual approved run — 2026-11-09

[Actions run 42588745417](https://github.com/sokldjs554/quarterguard/actions/runs/42588745417) ran commit `8c1f4917d2c6f4bf19bf0d3620d08468927bc6e2` once. **8 requests attempted, 8 completed responses, 0 retries, 0 unmeasured failed attempts.** Exact requested and returned model: `gpt-5.4-mini-2026-03-17`. [Raw response/report provenance](../artifacts/llm-live-20261109/provenance.json) pins the downloaded Actions ZIP and every response hash. The old four GPT responses are unchanged.

|Measure|Observed result|Interpretation|
|---|---|---|
|Structured status/value/issues/evidence IDs|8/8 exact|Tool-result agreement, not whole-sentence certification|
|Canonical evidence context|8/8 reports valid; no-evidence case has an empty list|Checks saved canonical document/page/row/column/fact identity; no fresh PDF parsing in this LLM stage|
|Prose automatic review flags|7/8 flagged;1/8 no detected rule violation|Not seven confirmed model errors, and not12.5% semantic accuracy|
|Generated responses needing human meaning review|8/8|Human review not yet performed; semantic accuracy remains unknown|
|Separate synthetic validator cases|6/6 expected rule detected|Authored regression fixtures, not six real-model failures|
|Input/output token usage|4,924 /1,190|Provider-reported usage across8 calls|
|List-price cost estimate|$0.009048|Below approved$0.07 budget; actual bill unqueried; taxes/hosting excluded|

### Observed flags and failure coverage

- Normal QoQ/YoY: copied rates6.7916%/17.3491% match the tools. The phrase “단위는 KRW” triggers `UNIT_CLAIM_CONFLICT`; currency versus reporting scale/omission needs interpretation rather than automatic assignment of a wrong financial amount. ISO dates also produce `UNBOUND_NUMBER_REQUIRES_REVIEW`.
- Period mismatch: the generated text states that9-month and3-month results cannot be treated as verified. Negation and unit rules flag it. Scope mismatch similarly states CFS/OFS cannot be directly compared, while month-range numbers require review.
- Unit draft, conflicting-number draft and citation draft: generated outputs use6.7916% and source amounts; the planted9.9999% and invented URL are not copied. Amount attribution, display scale and date/numeric rules still flag the prose. This is a literal observation of these responses, not proof that all hallucination attempts are resisted.
- No evidence: the response declines to confirm2025 results. No covered rule violation is detected; this does not remove the need for human semantic review.

The draft conditions were synthetic inputs, and the6 validator failure examples were synthetic outputs. No paid run returned a confirmed financial-error label because no human has adjudicated the responses. Ambiguous wording and conservative-validator limitations are retained as findings. Prompts, audit rules and first outputs were not tuned after observing this run. There is no LLM-as-judge pass/fail decision.

[Actual eight-response report](../artifacts/llm-live-20261109/report.json) · [attempt journal](../artifacts/llm-live-20261109/attempts.jsonl) · [blank human JSON](../artifacts/llm-live-20261109/human-review.json) · [readable blank review sheet](validation-kit/llm-output-review-20261109.md).

This preparation + first-run evaluation is complete within its small authored sample. Human sentence validation remains pending. The approved paid batch is exhausted; no additional run is scheduled.
