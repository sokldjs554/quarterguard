# Finance Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Apply the user-approved interactive financial workspace to the real product.
**Architecture:** Keep app.js financial state and existing API owners. Pure chart geometry in finance-chart.mjs; rendering/drawer in finance-view.js; finance.css supplies the new shell and responsive styles.
**Tech Stack:** Vanilla JS/CSS, FastAPI, Node test runner, Playwright Chromium.
**Spec:** docs/superpowers/specs/2026-11-14-finance-workspace-design.md

## Global Constraints
- No prototype snapshots in production; no new paid calls.
- Preserve existing APIs, errors, records and all product views.
- New default route is work; old #home remains a compact document index.
- Chart and drawer must clear on pending/error.

## Review Focus
- Negative and zero chart values have a truthful baseline and finite geometry.
- Unsupported USD/mixed scopes/periods cannot display a misleading comparison chart.
- Advanced YoY/year/document changes synchronize quick controls and labels.
- API failure after success cannot leave a stale chart, drawer, export or source.
- 320px navigation, dialogs and downloads remain usable.

### Task 1: Financial presentation and live wiring
Files: web/finance-chart.mjs, web/finance-view.js, web/app.js, tests/test_finance_chart.mjs.
Interface: chartModel(row) returns null for non-comparable data, else chronological bars with fact references and a zero-inclusive axis. renderFinance(row, mode), clearFinance(), openFinanceSources(side), mountFinanceSources(onInspect) own presentation only.
- [ ] Test chart values, ordering, negatives, zero, hold/status/currency/scale/invalid guards; run RED then implement and run GREEN.
- [ ] Connect render/clear/source navigation to existing successful/pending/failure lifecycle. Add synced quick inputs; preserve advanced selectors.

### Task 2: Approved layout and all views
Files: web/index.html, web/finance.css, web/navigation.js.
- [ ] Replace editorial shell with light rail and compact company view. Default work, retain document index and all analysis/search/review controls.
- [ ] Style chart/table/drawer and other views; desktop/mobile screenshots against approved preview.
- [ ] Browser real-backend tests: normal, period/scope/USD hold, YoY, recovery, sources, notes/CSV, search, Apple/SK, synthetic pending/503 clearing. No provider calls.

### Task 3: Review, publication and evidence
Files: scripts/browser_finance_workspace.py, docs/finance-workspace-20261114.md.
- [ ] Run complete Python and Node suites, selected existing browser regression flows; preserve output.
- [ ] Fresh whole-branch review; fix material findings with regression coverage.
- [ ] Publish PR/merge, verify Render live revision/assets and public flow; document source of every check and API usage.
