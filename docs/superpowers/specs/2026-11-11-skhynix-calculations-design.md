# SK hynix source calculations, phase 2

The user authorized the next stage after PDF source support: annual comparisons, year-end balance changes and product revenue shares. Existing human-authored questions and answers are development cases, not a new holdout. Implementer choices below are not attributed to the user.

## Approach

Extend the separate typed source-cell workflow with deterministic Decimal calculations and explicit A/B selection. Reusing quarter Fact would incorrectly turn balances into durations; adding an LLM planner would introduce cost and ambiguity without helping these calculations. No paid API calls or generated prose are needed. Keep the financial-review UI and legacy quarter workflow.

## Contracts

- Public calculation accepts mode plus two registered cell IDs, never client-supplied values. Load the hash-checked snapshot and retain evidence and exact calculation direction.
- `annual_yoy`: same entity/account/scope/currency, valid unit scales, full calendar-year durations, current year exactly one after base. Display amount difference and (current/base-1)*100 rounded to four decimal places using ROUND_HALF_EVEN.
- `balance_yoy`: cash or inventory, same account/entity/scope/currency, consecutive December31 instants, no fabricated start/end or months. Display year-end balance difference and change percent; do not label it annual cash flow.
- `product_share`: DRAM/NAND/other product numerator and same-document/table/period/column product_total denominator, same entity/scope/currency, full-year duration, nonnegative numerator, positive total, numerator<=total. Percentage numerator/total*100; no growth-rate label.
- Context mismatch means no difference or percentage. A zero/negative comparison base blocks percentage but, if context matches, still permits separately marked arithmetic difference. Negative operating-profit base -> positive current can display 'loss to profit', not an ordinary growth percentage.
- `inventory_months`: explicit unsupported-definition response, no ratio. Need denominator metric/period and ending/average inventory definition.
- Every response includes executed checks, canonical evidence, normalized KRW inputs, formulas, blocked/calculated status per output, and a deterministic execution label. Rule-based MCP, no autonomous LLM planning.
- UI: source search remains candidate-only. An explicit calculation form offers modes and A/B selectors, shows dates/units/source links, and computes only on submit. Input changes invalidate old result/download immediately; stale responses cannot restore it. Errors and timeout clear prior result. JSON export is current result only.
- No rewrite of original PDF cells/manifest, source failures, old evaluation outputs or human records. Runtime catalog adds current calculation capabilities to the preserved extraction manifest.

## Acceptance

Original five questions map to six explicit pair operations: cash change3617788 and47.6820%; revenue increase33427241 and inventory decrease166722 (stock/flow distinguished); DRAM share67.5777%; operating-profit difference31197632 and no negative-base percentage; inventory-months clarification. These operations are explicitly selected by the evaluator/UI, not automatic understanding of all five natural-language questions.

Actual official PDF -> parser -> equality to registered18cells -> real MCP search/read/calculate traces. Separate AI-authored mutation/unit tests for invalid contexts. Local/public desktop-mobile checks, existing Python/Node suites, preservation audit, CI/deploy under prior authorization. New b/user review is pending and must not be invented.
