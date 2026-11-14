# Approved Workbook Implementation Plan
> Execution: superpowers:executing-plans, inline; final fresh branch review.
**Goal:** 승인된 표 중심 검토본을 전체 제품의 실제 기능에 연결.
**Architecture:** 기존 API와 상태 소유 모듈을 유지. index.html DOM/새 workbook.css, finance-view.js 시각화 갱신, app.js 조건 컨트롤 동기화.
**Tech Stack:** Python/FastAPI, vanilla JS/CSS, Playwright, Node test.
**Spec:** docs/superpowers/specs/2026-11-15-approved-workbook-design.md

## Global Constraints
- 과거 검증 기록 보존. 새 디자인을 사람 검수 결과로 표현하지 않음.
- 표의 실제 금액/기간/범위/통화/단위와 출처 연결 유지.
- 저장 응답을 실시간 결과로 사용하는 코드 없음. 유료 모델 호출 없음.

## Review Focus
- 전체 조건에서 USD/연도 변경 시 빠른 조건과 열 제목이 뒤처지지 않을 것.
- 요청 실패 시 차트/모달/내보내기에 이전 성공 결과가 남지 않을 것.
- 음수/0은 실제 0 기준의 시각화; 미검증 입력은 차트 보류.
- 모바일 보류 후 설정 수정과 결과 복귀가 가까이 있을 것.
- 메모 키/기존 저장 기록과 Apple/SK JSON 읽기 동작 보존.

### Task 1: 제품 화면 배치
Files: web/index.html, web/workbook.css, web/app.js, web/navigation.js
- [x] 기존 앱에서 첫 행 y<300 / 마지막 행 하단<650 및 모바일 양쪽 수치 표시 검사 실패 확인.
- [x] 상단 탐색·회사 헤더, 표 열 속 조건, 표 아래 검토 영역 구현.
- [x] 나머지 네 화면 공용 디자인과 실제 탐색 연결. 전체 조건/MCP/메모 기능 유지.

### Task 2: 근거·계산 표시와 회귀
Files: web/finance-view.js, scripts/check_workbook_browser.py
- [x] 숫자/방향/단위는 서버 결과 사용. 음수 포함 공통 0축, 보류는 차트 없음.
- [x] 실제 API로 정상·기간/범위/동시 불일치·복구·YoY·USD·검색·Apple/SK·JSON·CSV·메모·MCP 점검.
- [x] 1440/390/320px 및 오류 주입 확인. 기존 Python/Node suite 실행.

### Task 3: 비교·검토·배포
Files: docs/workbook-release-20261115.md, README.md
- [ ] 승인 시안/직전 화면/제품을 같은 viewport로 비교. 전체 요구 대조 기록.
- [ ] 전체 diff fresh review. 필요한 수정과 회귀 확인 후 PR/CI 확인.
- [ ] 승인 범위 내 merge/deploy, 공개 버전 일치·브라우저 검증. 직접 HTTPS와 TLS relay 구분.
