# Apple SEC source support

User authorized steps 1–4: real SEC HTML extraction/search, Q1–Q5 calculations, evidence-based Q6/Q7 abstention and regression evaluation. Existing worksheet UI stays.

Use a bounded, hash-pinned HTML source adapter and canonical extracted cells plus narrative evidence. No numeric answer fixtures in production. Read actual year columns, statement sections, USD units, XBRL periods/dimensions and signed cash flows. Preserve printed page vs HTML locator. Reject duplicate/changed/unsupported structures.

Approaches considered: generic unbounded SEC/XBRL importer (too broad to validate here); hardcoded answers (does not satisfy source processing); selected source adapter (chosen implementation judgment within authorized scope). Supported document is Apple FY2024 10-K only; do not claim general SEC coverage.

Keep legacy Samsung/SK APIs intact. Add Apple to source catalog, dispatch source search/cell reads by document, and add explicit source-review API/MCP/UI action. Search returns candidates only. Review follows registered rule-based operations, Decimal calculations and evidence-linked limitations, never LLM planning. Unknown question conditions fail closed. No paid calls.

FY2024 and FY2023 are 52/53-week years, not fabricated calendar periods. Annual reported differences include a duration warning; cash payments preserve negative source signs and positive spending magnitude. Aggregate and causal questions return needs_review with evidence and required information. Results/export record source snapshot hash, formulas and execution steps.

Seven user-authored cases become development/regression cases after this change; original first 0/7 and all earlier evidence are immutable. New synthetic variations are labeled AI-authored, not human holdout. No b re-review claimed. Browser checks cover desktop/mobile, failure/recovery, source change and stale results.
