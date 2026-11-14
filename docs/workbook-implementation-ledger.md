# SDD ledger — plan: docs/superpowers/plans/2026-11-15-approved-workbook.md
기준 commit: d1039922f7d64b27be4ef4d8a81eb2a0492417d2
기존 linked worktree 재사용, feat/approved-workbook 브랜치.
Pre-flight: app.js는 기존 DOM ID로 상태를 관리한다. index 배치 변경 시 ID를 유지하고 열 제목 갱신을 별도 span에 한정해 quick selectors를 지우지 않는다.
Ruling: 승인 시안의 제한된 입력 재생을 제품에 복사하지 않는다. 기존 API와 전체 조건·MCP·메모 모듈을 유지한다 — 시안만 덮어쓸 경우 기능이 유실되기 때문.

Task 1: complete — 승인 시안 구조 실제 DOM 연결, 1440/390/320px 배치 확인. 처음 y=308.391로 미달 → 298.391 수정.
Task 2: complete — actual browser 47 passed, Python406/1skip, Node37. 기존 API/메모 키 유지.
Final review: fresh reviewer found P2 hidden mobile quick selectors tabbable; CSS hide duplicate controls. Added tab-order test failed before fix and passed afterward. No financial/integration blockers found.
Task 3: code/doc ready; pending CI/deployment and public verification.
