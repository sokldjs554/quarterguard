# Document Worksheet Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. User already authorized implementation of the researched direction; proceed inline.

**Goal:** Replace the fixed-case dashboard with an interactive financial comparison worksheet and adjacent source evidence.
**Architecture:** A typed worksheet request selects immutable canonical facts. Existing core guards compute preview rows; the live route uses actual MCP with the existing shared capacity lock. Plain JS renders the table and source inspector without financial arithmetic in the browser.
**Tech Stack:** FastAPI, Pydantic, Decimal, MCP SDK, vanilla HTML/CSS/JS, unittest, Playwright.
**Spec:** docs/superpowers/specs/2026-10-29-document-worksheet-design.md

## Global Constraints
- No invented multi-company support, external API usage, or original-document rendering claims.
- Source PDFs remain on publisher infrastructure; no new dependencies required.
- All supported periods/scopes/currencies retain core fail-closed validation.
- Existing case endpoints and evaluation evidence remain reproducible.

## Review Focus
- Mixed period/scope/currency choices must block every affected row (Task 1 tests).
- Rapid selection changes must not display stale successful results (Task 2/3 browser check).
- Live MCP errors/timeouts must not fall back to a success label (Task 1 tests).
- Source panel must follow the clicked value, including base document and USD note (Task 3).
- Mobile, keyboard and provider-PDF failure must retain usable evidence (Task 3).

## Task 1 — Worksheet service
Files: quarterguard/worksheet.py, quarterguard/api.py, tests/test_worksheet.py.
Interfaces: Selection and WorksheetRequest Pydantic models; preview(request) -> dict; run_worksheet(request) -> awaitable dict; POST /api/worksheet and /api/worksheet/run.
- [x] Write failing tests for default six rows and revenue 6.7916, mismatches, unsupported selectors, exact source evidence, live protocol, failed tool handling and shared capacity.
- [x] Run targeted tests to confirm failures, implement canonical selection + core comparisons + MCP session.
- [x] Run targeted tests and existing suite; commit service.

## Task 2 — Document-first UI
Files: web/index.html, web/style.css, web/app.js, web/evidence.js, web/review.js.
Interfaces: app owns request/selection/navigation, evidence renders canonical facts and source link, review renders evaluation and old-case execution.
- [x] Replace rail/cards/case gallery with horizontal toolbar, independent document selectors, dense comparison rows, adjacent source inspector and contextual findings.
- [x] Preserve controlled search, saved/actual regression cases, downloads, measured evaluation and truthful API status.
- [x] Inspect desktop/mobile screenshots and correct layout/interaction issues before integration.

## Task 3 — Verification and release
Files: scripts/browser_check.py, artifacts/browser-check.json, docs/images, README.md, docs/ui-research.md.
- [x] Exercise column changes, row/source selection, live MCP, validation blocks, saved regression replay, search, evaluation, error/retry, stale responses, keyboard and mobile flow.
- [x] Run full unittest and artifact consistency checks; get independent code review; fix verified issues.
- [ ] Update screenshots, README, data limitations and user workflow; create PR and merge after CI.
- [ ] Verify Render health and deployed version; rerun browser flows against deployed responses with existing TLS-validating relay if direct Chromium TLS remains blocked.
