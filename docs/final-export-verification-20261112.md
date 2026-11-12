# A7·S4 저장·질문 변경 후 상태 점검

수행자: AI가 실행한 Playwright/Chromium 자동 검사. 실제 사람 또는 b의 재확인 기록이 아니다. 날짜는 2026-11-12 KST이며 정확한 시작·종료 시각은 각 report.json에 있다. 새 유료 LLM 호출 0회, 새 생성 0건이다.

## 확인 결과

|대상|실제 확인|결과|
|---|---|---|
|A7 저장|공개 서버에서 질문 실행 → 브라우저 다운로드 → 파일 다시 읽기 → 실제 HTTP 응답과 전체 JSON 대조|PC·모바일 크기 모두 일치|
|A7 내용|질문, Apple 문서, USD·백만 달러, 인쇄 22쪽 Greater China 행, 원인 설명 문단, `CAUSAL_DECOMPOSITION_REQUIRED`|판단 보류와 필요한 추가 정보 보존|
|A7 질문 변경|질문을 A1로 편집하고 실행 전 결과·저장 버튼 확인|이전 결과 제거, 저장 비활성화|
|A7 이후 재실행|A1 실행 후 새 파일 다운로드|새 질문·gross_margin·verified에 해당하는 결과만 저장|
|S4 저장|재고2024/매출2023 선택 → 정의 확인 → 다운로드 → 파일 재열기|선택한 두 ID와 HTTP 응답 전체가 파일과 일치|
|S4 내용|KRW·백만 원, PDF191/F-73 재고·PDF193/F-75 매출, 원문 URL, `RATIO_DEFINITION_REQUIRED`|입력·출처·보류 이유 보존, 계산값·공식 null|

화면 크기는 1365×900 및 390×844이다. 모바일 크기의 데스크톱 Chromium 검사이며 실제 안드로이드/모바일 Chrome 사용을 뜻하지 않는다. 실제 공개 서버의 규칙 기반 API를 호출했으며 준비된 결과 재생·응답 모킹·LLM 호출은 하지 않았다. API가 사용하는 등록된 원문 추출 스냅샷을 확인한 것이며 이번에 PDF/SEC 원문을 새로 파싱한 평가는 아니다.

## 발견한 화면 문구 오류와 수정

초기 공개 서버 `4989b288adf884005dc1a650c1c4b2b144a57d37`에서 저장 자체는 정상이다. 다만 S4 보류 결과에 `2023년 대비 2024년 연간 실적`, `증감률 —`가 표시됐다. 입력은 2024년 말 재고 잔액과 2023년 연간 매출이므로, 연간 실적 증감률을 비교한 것으로 오해할 수 있다.

원인은 [source-calculator.js](../web/source-calculator.js)의 `renderResult()`가 제품 비중·잔액 비교를 제외한 모든 모드에 연간 비교 제목을 사용한 것이다. `inventory_months`를 별도로 표시해 다음으로 수정했다.

- `재고 개월분 · 선택한 A/B 자료의 정의 확인`
- `재고 개월분 —`

백엔드 판정·금액·원문·JSON 형식은 바꾸지 않았다. 수정 전 실패를 실제 로컬 브라우저에서 재현했고, 수정 후 같은 검사를 두 화면 크기에서 통과했다. 이 오류는 AI 점검 중 발견한 것으로 b가 발견하거나 수정한 경험으로 기록하지 않는다.

## 근거와 재현

- [최초 공개 서버 검사](../artifacts/final-export-check-20261112/browser/report.json): 다운로드·상태 검사는 통과, 캡처에는 수정 전 문구가 남아 있음.
- [문구 회귀 검사 RED](../artifacts/final-export-check-20261112/label-red.log): 기존 연간 실적·증감률 표시로 실패. 이전 실패 보존.
- [수정 후 로컬 검사](../artifacts/final-export-check-20261112/local-fixed/report.json): 두 화면 크기 통과.
- [기존 계산·복구 브라우저 회귀](../artifacts/final-export-check-20261112/calculation-regression/report.json): 현금, 음수 기준값, 비중, 잘못된 기간, 오류·복구와 기존 삼성 작업지 확인. 503·시간초과·늦은 응답은 명시적 주입이며 실제 장애 건수로 세지 않음.
- [검사 스크립트](../scripts/browser_final_export_check.py), [초기 검사 스크립트 스냅샷](../artifacts/final-export-check-20261112/initial-browser-check.py).
- [다운로드 Apple JSON](../artifacts/final-export-check-20261112/browser/A7-390.json), [다운로드 SK JSON](../artifacts/final-export-check-20261112/browser/S4-390.json).

로컬 서버 실행 후 다음 명령으로 재현한다. 출력 폴더는 존재하지 않는 새 경로를 지정한다.

```bash
python scripts/browser_final_export_check.py --url http://127.0.0.1:8000 --transport local_http --output work/new-export-check
```

공개 사이트 직접 HTTPS를 사용할 수 있는 환경에서는 URL을 `https://quarterguard.onrender.com`으로, transport를 `direct_https`로 바꾼다. 이번 환경의 직접 Chromium 접속은 `ERR_CERT_AUTHORITY_INVALID`로 실패했으며 우회 옵션을 켜지 않았다. 공개 서버 브라우저 검사는 기존 [고정 원본 중계](../scripts/https_qa_relay.py)의 TLS 검증 HTTP 클라이언트를 사용했다. 직접 HTTPS 브라우저 검사 성공으로 표현하지 않는다.

첫 health 조회는 25초 시간초과, 재조회는 200/약0.8초였다. [최초 실패](../artifacts/final-export-check-20261112/health-before.json), [재조회](../artifacts/final-export-check-20261112/health-retry.json), [직접 HTTPS 실패](../artifacts/final-export-check-20261112/direct-https.json)를 보존한다. 이 소수 표본으로 가용성을 보장하지 않는다.

## 회귀 검사

Python339개 실행·실패0·1skip, Node18개 통과. [Python 로그](../artifacts/final-export-check-20261112/python-tests.log)에는 기존 의존성 경고·테스트 로그도 그대로 남겼다. [Node 로그](../artifacts/final-export-check-20261112/node-tests.log), [보존·다운로드 동일성 확인](../artifacts/final-export-check-20261112/verification.json).

## 공개 배포 후 확인

수정 PR [#67](https://github.com/sokldjs554/quarterguard/pull/67)의 병합 커밋 `161ae0bb528b4e43498697f6862e659035b2dd6f`가 GitHub main·Render live 배포·공개 health에 일치했다. Render 배포 ID는 `dep-dbqguujrjlhs73fsei5g`다.

- [배포 후 공개 브라우저 검사](../artifacts/final-export-check-20261112/public-fixed/browser/report.json): PC·모바일 크기 A7/S4 저장, 편집 후 이전 결과 제거, 새 결과 저장, 수정된 S4 문구 모두 통과. TLS 검증 중계 경로이다.
- [Render 배포](../artifacts/final-export-check-20261112/public-fixed/render-deploy.json), [공개 코드·health 대조](../artifacts/final-export-check-20261112/public-fixed/assets-health.json): 배포된 JavaScript 두 파일이 검토한 로컬 파일과 바이트 단위로 같음.
- [최종 A7 JSON](../artifacts/final-export-check-20261112/public-fixed/browser/A7-390.json), [최종 S4 JSON](../artifacts/final-export-check-20261112/public-fixed/browser/S4-390.json), [최종 S4 모바일 크기 화면](../artifacts/final-export-check-20261112/public-fixed/browser/S4-390.png).

수정 전·로컬 수정 후·배포 후의 다운로드 내용도 일치했다. 배포 대기 중 이전 커밋을 응답한 기록은 [health 폴링](../artifacts/final-export-check-20261112/public-fixed/health-polls.json)에 남겼다. 이후 이 결과를 게시하는 문서·캡처 커밋은 제품 코드 변경이 아니며, 위 브라우저 캡처의 기준 커밋을 새 커밋으로 바꾸어 적지 않는다.

## 사람이 남길 부분

기술적인 다운로드·내용·상태 검사는 위와 같이 수행했다. b의 A7·S4 직접 기기 확인은 여전히 미확인이다. [두 과제 기록 양식](validation-kit/final-followup-20261112/remaining-checks.md)에 실제 결과만 추가하면 된다. 자동 검사 결과를 b의 수행 결과로 옮기지 않는다.

b에게 전달할 짧은 안내:

> 남은 것은 두 가지만 부탁해. A7 결과를 JSON으로 저장해 파일을 열고 질문·출처·보류 이유가 맞는지 봐 줘. 질문만 바꿨을 때 이전 결과가 없어지고 저장이 막히는지도 확인해 줘. S4도 JSON 다운로드를 마친 뒤 선택한 재고/매출과 원문 위치·보류 이유를 파일에서 읽어 줘. 읽은 내용과 막힌 부분만 적으면 되고, 다른 과제와 LLM20건은 다시 할 필요 없어.

이 안내를 AI가 b에게 직접 전송하지 않았다. 기존 직접 검수20건의 참/거짓/모호 판정과 고유 참여자 수는 유지한다.
