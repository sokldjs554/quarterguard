# Task Review UI Implementation Plan

Goal: replace the previous single workbench with a clear task entry, separate analysis views, and broad comparison/evidence stages.
Architecture: keep existing financial modules and DOM IDs, add a small navigation module, relocate existing DOM sections, and replace shell/layout styling with a dedicated stylesheet.
Tech stack: HTML, CSS, ES modules, FastAPI, Playwright.
Spec: docs/superpowers/specs/2026-11-14-task-review-ui-design.md

Constraints: no financial calculation changes; no synthetic usage stats; preserve historical results; no paid calls; support 320/390/1440px and keyboard navigation.
Review focus: stale figures after failures, switching documents with existing exports, notes across tabs, hash/back and initial deep links, mobile source overflow/focus.

- [x] Add browser coverage proving home task routing, separate evidence/notes, return navigation and direct links (baseline fails on absent home).
- [x] Rebuild index.html shell/home; split search and source analysis without replacing existing controls. Add navigation.js with route allowlist, history and stage controls.
- [x] Integrate selected metric summary and pending/error clearing with app.js; create workspace.css for full layout/typography, cards, responsive behavior.
- [x] Run real-backend browser checks: normal/period/scope/recovery, source/notes, SK calculation, Apple hold/export invalidation and injected failures. Run Python/Node suites.
- [x] Inspect desktop/mobile screenshots; fresh code review; document results and preserved limits. Local evidence ready; publication and deployed-commit check follow this implementation commit.

## Execution ledger

- Initial home test failed on the prior UI (preserved). New workflow passed 66 checks, then 72 after navigation fixes.
- Ruling: reuse existing task modules and DOM IDs; move SK/Apple into analysis, preserving financial behavior.
- Navigation regression reproduced: returning from notes via work menu/candidate kept notes visible. Fixed by entering comparison on work navigation. Skip link now focuses main without changing the route.
- Fresh reviewer independently reproduced and verified both fixes; no outstanding important findings.
- Python 406 (1 skipped), Node 30; settings return 21; Apple/SK/JSON PC+mobile suites passed. Real MCP run18 tools, model0.
