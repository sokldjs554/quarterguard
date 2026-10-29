# Provider controls and evaluation completion

User specification: current request's four sections. Paid API calls or paid infrastructure require separate user approval; all implementation and free checks are authorized.

Architecture: Keep canonical calculator and real MCP paths. Add an opt-in provider service accepting only allowlisted case/report IDs, never arbitrary prompts or URLs. Separate provider request provenance from historical replay. An atomic SQLite ledger reserves attempts before network access. Paid calls fail closed without explicit approval configuration and durable storage; Render free ephemeral storage is not a durable paid budget.

- [x] Implement provider status, bounded requests, cache/provenance, approval/durable-ledger gate, safe errors, cost estimates, tests. Public LLM default off; no paid requests in this work before approval.
- [x] Independently collect other-period official sources and freeze AI-authored evaluation cases before evaluating unchanged pipeline. Separate raw pipeline failures from adapter-assisted checks; preserve failures.
- [x] Add UI actions/status with explicit actual/cached/blocked distinctions; keep deterministic MCP and prepared replay.
- [x] Audit job fit and direct HTTPS browser trust without bypass; reconcile README/evidence/counts.
- [x] Run full tests, browser flows, independent review; publish after CI and match GitHub/Render/public assets/version. Ask for paid approval only once the executable, tested scope and budget are reviewable.

Review focus: retries and concurrency spend before success; resets on ephemeral storage; cached responses not mislabeled live; tampered IDs/SSRF/key leakage; evaluation leakage and fixture-assisted results overclaim.

Outcome: implementation/CI/public version validation completed; public DART blocked by runtime KEY_NOT_CONFIGURED despite reported setup; paid LLM deliberately remains blocked. Direct HTTPS browser trust failed without bypass. Detailed evidence and final deployment follow docs/completion-report.md and release.
