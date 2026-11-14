# Teal Review Workspace Implementation Plan

**Goal:** 선택된 C안을 기존 비교/근거 검토 UI에 적용한다.
**Architecture:** CSS 중심 변경. HTML 구조와 JavaScript/API 계약을 보존한다.
**Tech Stack:** 기존 HTML/CSS/JavaScript, FastAPI, Chromium/Playwright.
**Spec:** ../specs/2026-11-14-teal-workspace-design.md

## Global Constraints
유료 호출 0회. 과거 캡처/결과 보존. 사용자 검수를 새로 수행한 것으로 기록하지 않는다.

## Review Focus
좁은 화면 가로 넘침, 설정 복구 버튼 접근, 보류 강조, 밝고 어두운 영역의
텍스트 대비, 입력 변경/오류 후 이전 결과 및 저장 버튼 상태.

## Task 1: Theme and layout
- [x] 최신 main 및 clean baseline 확인, 기존 Node 30개 테스트 통과.
- [x] 변경 전 PC/모바일 캡처 준비.
- [x] web/style.css의 색상·표·패널·반응형 규칙 변경.
- [x] 실제 브라우저에서 정상/보류/근거/모바일 화면 검토.

## Task 2: Regression and delivery
- [x] 기존 browser_check, browser_settings_return_check, browser_apple_support 실행.
- [x] Node 테스트 및 git diff --check 실행.
- [x] 독립 코드 검토 및 필요한 수정 검증.
- [ ] 새 결과 요약 작성, 커밋/PR/배포와 공개 버전 확인.

CSS 시각 변경이므로 구현을 그대로 반복하는 새 단위 테스트는 추가하지 않는다.
이미 승인된 C안 선택과 기존 GitHub/Render 공개 승인의 범위로 진행한다.
