# SK hynix Calculations Implementation Plan

> **For agentic workers:** Use executing-plans; native implementation with final whole-branch review.

**Goal:** Compute bounded annual, year-end balance and product-share results from registered source cells.
**Architecture:** Separate Decimal calculation module; strict API and MCP entry point; explicit form in the source-evidence view. Historical corpus stays immutable.
**Tech Stack:** Python/FastAPI/MCP, vanilla JS, existing dependencies only.
**Spec:** ../specs/2026-11-11-skhynix-calculations-design.md

## Global constraints

No paid calls, no LLM-generated explanation, no mutation of original data/artifacts/human records; stock/duration distinct; no automatic answer claim for human questions; preserve quarter UI. ROUND_HALF_EVEN four decimals. Same calendar-year or consecutive Dec31 as specified, no general fiscal-calendar claim.

## Review focus

- Reverse/same-year comparison, leap year and wrong type must not create numbers.
- Part/total relation must use source table identity, not just equal money.
- Zero/negative base must distinguish difference from withheld percentage.
- Client cannot override source amounts; snapshot failures cannot produce old success.
- In-flight response after input/mode changes must not revive result/export.

## Tasks

1. Tests first in tests/test_source_calculations.py: canonical cash3617788/47.6820; annual operating loss-to-profit difference31197632 with null percent; DRAM67.5777; inventory decrease166722; contexts/modes/zero/unit fixtures and unknown IDs. Implement source_calculations.calculate_source_pair(current_id,base_id,mode), internal typed guard arithmetic, and options(). RED then GREEN.
2. Tests first in tests/test_source_calculation_api.py and MCP: options GET and strict POST fields/IDs, errors, no client values; actual source MCP search/read/calculate sequence and legacy4 tools. Add routes to api.py and tool to source_mcp_server.py. Runtime catalog overlay; original manifest unchanged.
3. Browser test RED: explicit mode/A/B form, default cash/annual/share, evidence links, negative-base difference plus held percentage, input change invalidation, stale requests, injected failure/recovery, export. Implement web/source-calculator.js and index/CSS with candidate selection wiring. No chat UI.
4. Actual-PDF evaluation of six explicitly selected operations linked to user5 questions; output fresh immutable report with source hashes and complete MCP traces. Preserve all prior data/artifact/validation records. Full suites, code review and any fixes, docs/README, publish/CI/deploy verification.

## Execution ledger

- Tasks1–4 complete locally: unit/API/MCP RED→GREEN; Python294 with one skip, Node14; rawPDF18 cells equality and24 actual MCP evaluation calls for6 explicit operations; desktop/mobile calculator and phase1 browser regression passed.
- Builder check clarified output denomination: difference is always million KRW, including equivalent unit representations; returned currency/scale and test make this explicit. This is an implementer decision, not a user-authored code change.
- Runtime document capabilities are an overlay. The original phase1 extraction manifest and all545 existing data/artifact/validation-kit files remain byte-for-byte unchanged.
- Independent AI code review reported no material findings. The reviewer also exercised all1,296 registered pair/mode combinations; the reproducible matrix script confirms10 full results,1 difference-only result and1,285 blocked results. No general accuracy or human-review claim.
- New paid calls0, new LLM generations0, new human reviews0. Human followup is an unfilled kit.
