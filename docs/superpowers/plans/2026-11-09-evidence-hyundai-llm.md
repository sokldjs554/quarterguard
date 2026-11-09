# Evidence, Hyundai and LLM follow-up implementation plan

> For agentic workers: execute independent parser, frozen holdout and LLM preparation tasks in parallel, then review and integrate.

Goal: consolidate application evidence, prepare genuine human gold review, support verified Hyundai source tables, and evaluate new LLM outputs within explicitly approved bounds.
Architecture: retain strict existing parser and add issuer-specific parsing; keep frozen holdout and historical failure artifacts separate. Run offline checks before any paid request; new generated samples never replace old GPT 4 records.
Tech stack: existing Python/pypdf/MCP/httpx/unittest/GitHub Actions.
Spec: user's 2026-11-09 instruction and original nine-part requirements. Demo access is assigned to the user. GitHub publication/Render deployment already authorized; no paid plan changes.

## Tasks
- [x] Inspect current source, historical evaluations and completed personal/human records.
- [x] Consolidate current status with links, preserve all historical reports, prepare blank human cell/query audit.
- [x] Reproduce Hyundai2023 failure; implement strictly mapped four-column table parser and regression tests.
- [x] Freeze separate Hyundai2024 official PDF gold before parser inspection; run raw-PDF and fixture evaluations separately and preserve first results.
- [ ] Freeze 8 new LLM cases, implement bounded runner and deterministic checks, obtain exact model/cost/key approval, execute once and save failures/usage.
- [ ] Review changes, run regression/artifact integrity checks, publish and check deployment metadata without claiming a user browser test.

## Review focus
- Incorrect year/period or swapped column accepted: malformed header rejection tests.
- Duplicate/shifted rows or currency/unit ambiguity: fail-closed parser tests.
- Evaluation gold reused for development: freeze and first-run artifacts with declared provenance.
- Untrusted draft number or invented citation copied into prose: generated challenge cases plus deterministic audit and human review flag.
- Failed paid request retried or secret exposed: attempt limit/no retry/exclusive output/sanitized errors.
