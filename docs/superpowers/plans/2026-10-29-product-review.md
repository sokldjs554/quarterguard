# Product Review Workspace Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline. The user explicitly requested research and rebuilding; continue through the authorized deployment.

**Goal:** Turn the demo into a usable financial document review workspace.
**Architecture:** Retain the canonical FastAPI/MCP calculation path. Replace presentation with a compact document workspace. A separate browser module owns context-bound review notes and CSV export.
**Tech Stack:** Existing FastAPI, vanilla JS/CSS, Playwright, unittest; no new runtime dependency.
**Spec:** docs/superpowers/specs/2026-10-29-product-review-design.md

## Global Constraints
- Only the two actually collected reports; no fake uploads, accounts or server persistence.
- Manual review labels do not override automated calculation guards.
- Background change alone is explicitly rejected by the user.

## Review Focus
- Notes must not leak across fact pairs or different comparison modes.
- Storage failures must be visible and cannot prevent core review.
- Export must be unavailable during loading or after failed runs.
- CSV strings must not become spreadsheet formulas.
- Hidden settings, mobile layout and source switching must remain keyboard accessible.

## Task 1: Workspace presentation
- [x] Replace web/index.html and web/style.css with compact header, actual document rail, source/worksheet panes and collapsible condition settings.
- [x] Update web/app.js and web/evidence.js to synchronize source files, settings summary and clear error states; remove pseudo-PDF decoration.
- [x] Inspect desktop/mobile plus search/review/error states. Preserve existing canonical guards and real MCP path.

## Task 2: Complete a review
- [x] Add browser checks for context-specific notes, refresh persistence, review marking, storage failure and CSV escaping.
- [x] Implement web/review-notes.mjs with reviewKey(row, mode), read/write review state and CSV export helpers. Wire rendered row selection and execution resets in app.js.
- [x] Run local browser/unit/artifact checks and obtain independent review. Fixed unreadable stored reviews; 37 browser flows pass. Required CI is part of publishing below.

## Task 3: Publish evidence
- [x] Document attempted vs observed live demos and concrete adoption/rejection decisions in docs/live-demo-research.md.
- [x] Update README/screenshots/version.
- [ ] Commit and open PR; merge after CI.
- [ ] Confirm Render commit and public asset hashes; verify the deployed workflow and record results in release notes.

Publishing completion and public verification are recorded in the v1.2.0 GitHub release after deployment, rather than asserted ahead of deployment in this commit.
