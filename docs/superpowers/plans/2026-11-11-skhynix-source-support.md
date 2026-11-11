# SK hynix source evidence support — phase 1

User correction: fix the documented 0/3 PDF pages and 0/5 evidence retrieval first. The Samsung/Hyundai quarter-catalog proposal was not applied.

## Contract

- Parse the pinned official Offering Circular's F-73/PDF191, F-75/PDF193 and F-146/PDF264. Keep instant dates distinct from annual durations; preserve original row labels, year columns, KRW/million scale, consolidation, document hash and physical PDF page.
- A bounded adapter supports selected rows of these three tables, not arbitrary annual statements. Fail closed on changed structure, ambiguous rows, missing headers, extra columns or unsupported source identity. Do not manufacture values.
- Register an independent source-evidence corpus. Existing quarter facts, comparisons, providers, historical reports and user submissions remain intact.
- Document-scoped retrieval returns source candidates and explicit context/clarifications for the user's five original questions. No calculated answer, annual comparison, inventory ratio, product-share calculator or new paid LLM call in phase 1.
- UI: keep financial document review flow; show dated evidence, literal rows, table/year columns, original PDF links, and calculation limitations. Do not offer unsupported source cells as quarter worksheet facts.
- User's original questions are human-authored, now development examples. AI-added boundary tests are labelled separately. Do not claim an independent held-out benchmark or new human review.

## Implementation / verification

1. Tests first: three raw extraction texts and source metadata; parser rejection mutations; source-cell schema. Run red, implement, run green. Then run actual PDF (not fixture) through adapter; store new artifacts without overwriting baseline.
2. Tests first: five questions, context conflicts, unsupported currencies/scopes/periods, per-metric year bindings, missing-definition requests, source integrity. Implement deterministic retrieval and API/MCP read tools; no financial answer generation.
3. Connect document-scoped search in existing evidence-search view. Desktop/mobile browser checks: results and original links, limitations, failures clear prior results, recovery; legacy quarter workflow unchanged.
4. Evaluate actual PDF parsing and retrieved row/column/value identities separately from text-fixture tests. Preserve all tracked baseline data/artifact hashes. Full Python/Node suites, whole-branch code review; fix material findings, publish/deploy under prior authorization.

## Decisions

Use a separate source-cell type and endpoints so year-end stocks cannot silently become twelve-month flows. Supported source is the exact public PDF hash; generalized annual-table parsing is deferred. Annual/instant/share calculations are the next stage after this evidence foundation.

## Execution ledger

- Tasks 1–3 implemented and verified: raw PDF3/3 selected tables,18 cells; user5 required evidence sets; 14 targeted test methods; actual MCP18 tool calls; desktop/mobile live local backend.
- Ruling: preserve the original MCP module byte-for-byte and add `source_mcp_server` — original LLM freezes pin that module hash; changing historical freeze records would violate preservation. Cost: callers must choose the extended server entry point for new evidence tools.
- Whole-branch AI reviewer found explicit date loss, shared/postpositive year misbinding, and global product/revenue suppression. All reproduced RED and fixed GREEN. Unknown explicit dates reject; ambiguous trailing-year grammar asks rather than asserts a binding.
- Ruling: treat acceptance of an extra year header as material to the fail-closed parser contract although exact PDF hashing limits production exposure; added a failing header mutation test and anchored the header. Cost: more conservative rejection of unsupported layouts.
- Final verification: Python279, one skip; Node14; historical artifact consistency; all existing data/artifacts/validation-kit files unchanged. Initial failed run preserved. No new paid generation, human review or customer deployment claim.
