# Approved finance workspace design

User approved the interactive Fiscal.ai/Numeric-style Samsung preview on 2026-11-14 and requested applying it. The preview and its screenshot are the visual acceptance reference. Earlier alternatives (dark card dashboard, editorial paper layout, Rogo chat workspace) were rejected. Rogo contributes compact navigation only.

Use a narrow light navigation rail, company header, compact comparison tabs/controls, prominent selected financial values, zero-baseline two-value chart, nearby source links and a full-width financial table. Default entry opens Samsung comparison; the document list remains accessible. Source details open in a right drawer with a route to the full existing original/evidence inspector. Other product views adopt the same typography, spacing and neutral surfaces.

Use existing vanilla JS/FastAPI APIs and keep every currently supported condition, actual MCP verification, provenance, notes/CSV, Apple/SK calculations/JSON, search and evaluation/provider records. The prototype's stored responses must not enter production. No paid provider calls in verification. Existing failed evaluations and records are preserved. Do not describe chart rendering as financial verification.

Charts must clear immediately on pending/error and be suppressed for held comparisons, including mismatched period/scope/currency and reference USD. Reflect both directions and years from actual facts, support negative values without inventing history. New quick controls synchronize with advanced controls. Preserve 320/390px access, keyboard focus, and error recovery.

Implementation decisions: retain existing owning modules; add a small presentation module and pure chart geometry helper. Replace editorial stylesheet inclusion with a finance stylesheet; preserve historical assets in git. Release via reviewed branch/PR and existing Render service under previously authorized GitHub/Render publishing. Verify deployed health commit and assets; report direct browser HTTPS vs verified relay separately.
