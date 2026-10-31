# Document, Search and Evidence Implementation Plan

> **For agentic workers:** Use systematic debugging and test-driven implementation for each assigned independent domain; root integrates and reviews.

**Goal:** Fix known parser/search failures, expand honest raw-document evaluation, compare real reranking, and prepare applicant/user evidence.

**Architecture:** Retain deterministic MCP, canonical facts and bounded providers. Version all new evaluation records and distinguish raw PDF ingestion, fixture-assisted diagnostics, disclosed regression and separately frozen evaluation.

**Tech Stack:** Python/FastAPI/MCP, pypdf, scikit-learn, optional local CPU ONNX reranker, existing HTML/JS/Playwright.

**Spec:** docs/superpowers/specs/2026-10-31-document-search-evidence-design.md

## Global constraints

Preserve existing artifacts/data hashes. No paid calls/services. No invented participants or completed personal review. Maintain current financial review UI. Never bypass TLS checks. No model weights/PDF full text committed.

## Review focus

- A flexible year parser must still reject contradictory date/scope/header/column alignment.
- Korean synonyms must not swallow scope/period negation, unsupported currencies, or unit constraints.
- A reranker must not recover forbidden candidates or relabel the context filter as reranking.
- Prose checks may detect explicit numeric/context errors but cannot certify all meaning.
- Timeouts/provider failures must clear stale UI state and preserve trace provenance.

## Tasks

- [x] Baseline: GitHub/Render/public version + fresh job + existing tests; hash-preserve all prior artifacts/data.
- [x] Parser: quarter/year/header reconstruction, source provenance; failing tests before changes; 2024/2025 before/after new artifact.
- [x] Search: structured bilingual query diagnostics and candidate constraints; old failures vs new frozen questions separately.
- [x] Independent evaluation: freeze new official-period/company facts/questions before executing changed pipeline; raw PDF and fixture stages separate; retain first post-fix failures.
- [x] Ranking: real local reranking plus sparse/dense baselines, same questions/gold, timing and dataset/model fingerprints.
- [x] Explanation: offline original GPT replay + explicit synthetic failures; conservative numeric/context/citation checks and remaining human task.
- [x] MCP: real ordered calls and failure injection; timeouts/errors; immutable new traces; UI stale-result safeguards.
- [x] Participation/code review kits: blank user/customer consent/tasks/results + three requested code walkthroughs and questions.
- [x] Integrate diagnostic UI without chat redesign; preserve legacy artifacts; version API references for current results.
- [ ] Full tests and independent review; PC/mobile browser, CI, deploy version/asset consistency; actual free DART request only if needed and counted.
- [ ] Nine-part truthful completion report, supported application statements, outstanding user participation, API counts/costs.
