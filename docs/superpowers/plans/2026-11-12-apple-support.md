# Apple support Implementation Plan

> Execute inline using executing-plans; one fresh whole-branch review at the end.

**Goal:** Connect the official Apple HTML through evidence and guarded calculations in the existing product.
**Architecture:** Isolated Apple extractor and review module; source registry dispatch and explicit review UI. Existing comparison core unchanged.
**Tech Stack:** Python/FastAPI, lxml, Decimal, JS, unittest/Playwright.
**Spec:** docs/superpowers/specs/2026-11-12-apple-support-design.md

## Constraints
Preserve all prior artifacts. No paid calls. Explicitly bounded source. Missing context rejects. Separate human authorship and AI evaluation.

## Review focus
Duplicate cells/headers; signed outflows; wrong-year/unknown query qualifiers; unsupported generalization/causality; stale asynchronous UI success.

## Tasks
- [x] 1. tests/test_apple_source.py: failing catalog/extraction assertions; quarterguard/apple_source.py parses raw HTML to immutable cells/narratives; data/apple-source stores hash-checked snapshot. Reject hash/duplicate/context/dimension/unit mismatch. Reproduce raw HTML output.
- [x] 2. tests/test_apple_review.py: seven human inputs plus synthetic adversarial variations; quarterguard/apple_review.py selects bounded intents and calculates with canonical cells, records checks/steps, returns explicit limitations. Search stays not_calculated.
- [x] 3. API source catalog/search/cells + /api/source-review; MCP review_source_document. Existing SK tests remain. Web document selector and explicit review/output/export, fail/recovery clearing. Browser desktop/mobile.
- [x] 4. Full Python/Node tests, original hash preservation, after-results separate from 0/7, docs/README, fresh AI code review, CI/publish/deploy verification.
