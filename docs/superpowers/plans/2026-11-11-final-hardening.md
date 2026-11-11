# Final evidence hardening implementation plan

Goal: close the six job-fit gaps within authorized scope, preserving every historical failure and human record.
Architecture: keep the deployed GPT-4.1-mini-2025-04-14 payload builder and financial tools. Add an opt-in evaluation runner and bounded experimental planner, not a public paid endpoint. Never substitute fixtures for live generation or human review.
Tech: Python, MCP stdio, Responses HTTP API, existing unittest and browser checks.
Authorization: user requested all six audit items; earlier publication/deployment authorization persists. Paid requests need a separate concrete contract approval. No new approval inferred from silence.

## Design decisions
- Use the existing production model/prompt/schema for parity; do not switch public runtime to an unevaluated model.
- Explanation evaluation runs real MCP first; generated-response checks are exactly production checks. Historical v9 remains a different-model replay batch.
- Planner only sees a query and allowlisted schemas; it may search, read retrieved facts, then compare read IDs. No arbitrary execution, network tool, write tool, or raw supplied amounts. 6 decisions, 6 tools, deadline, no retries. Final numeric answer only from validated tool output.
- Human-authored holdout intake is empty until supplied by a human. Freeze before execution, record exact bytes/code version/first run, never regenerate a first score. Existing five SK questions are development data.
- Human follow-up combines v9 semantics, new SK tasks and fresh actual responses when generated. No fabricated participation.
- Public probes are small laboratory samples, not load/SLA/customer traffic. First observed request is not proven cold.

## Review focus
Unretrieved IDs and fabricated tool outputs; deadline/loop/provider failures after success; budget/attempt restart bypass; holdout mutation and nonhuman authorship; production/evaluation policy drift.

## Tasks
- [ ] 1. Add production-parity evaluator, immutable first-run output, capped paid client and one-shot workflow. Tests: wrong model, input budget, repeated output path, tool failure prevents generation. Run real MCP dry evaluation.
- [ ] 2. Add human-case freeze/score CLI and strict provenance checks. Tests: missing provenance, changed data, same output overwrite, unknown operation. Empty author template only.
- [ ] 3. Add bounded planner with tests for normal search/read/compare and blocked bypass, unsupported mode, duplicate loop, invalid arguments, timeout/error. Run scripted policy tests separately from actual LLM selection.
- [ ] 4. Run low-volume HTTPS endpoint timing and local workflow benchmark; record p50/p95/errors/sample sizes and limits. Preserve raw probes.
- [ ] 5. Prepare consolidated human packet and rewrite current README/job-fit/demo/status documentation. Archive current README. Keep dated records unchanged.
- [ ] 6. Whole suite, browser regression, independent code review, preserved-file hashes, CI/PR/deploy and commit equality. Paid batch only after concrete approval; humans pending until responses.

## Ledger
Baseline: 1bb6a8229d0d512c7bd362d8f318cf5d4fb5ded2.
Ruling: implementation and isolated worktree proceed under explicit six-item authorization; no repeated design approval. All external human/paid steps remain separately gated.

Design review rulings: canonical comparison equality, terminal success, comparison-only planner, exact production validator reuse, fixed-contract reservation, gold isolated from runtime. Implemented.
Tasks1–3: implementation and20new tests passed. Paid/human execution still gated. Task4 measured first timeout and probe-parameter error; both retained. Task5 current README consolidated; historical docs preserved.

Final independent review: 3 findings fixed with red-to-green tests (production case-gold preflight; real transport restricted to single guarded workflow; runtime errors never score as successful hold). Targeted23 passed. No remaining blocking findings.

Final suite317 tests OK(skip1), Node14, local/public-relay browser pass. Direct Chromium HTTPS cert error preserved. Historical570 files unchanged. Paid approval and human submissions are pending; never mark these completed by AI.
