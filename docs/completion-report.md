# v1.3.1 보완·검증 보고

최초 작성: 2026-10-29, DART 후속 검증 갱신: 2026-10-30 (한국 시간). 기능 배포와 공개 서버 검증을 구분해 기록한다. 과거 API 검증을 이번 호출로 합산하지 않는다.

## 지원 프로젝트로서의 판단

[현재 채용 공고](https://treasurer.recruit.roundhr.com/c/nLeVw9amBH)를 다시 읽고 [직무 대조표](job-fit-audit.md)를 작성했다. 금융 문서 파싱·청킹, 임베딩 비교, Python API, MCP 도구, 평가·실패 추적의 증거는 지원에 활용할 수 있다. 실제 고객 운영·자율 에이전트·범용 금융 RAG·사람 팀 협업을 완성했다는 근거는 아니다. 지원자가 AI 작성 코드를 이해하고 실패 원인을 설명하는 능력은 별도로 필요하다.

## 완료한 구현

- 기존 규칙 기반 MCP와 준비된 결과를 유지했다. 공개 DART는 4개 고정 조회만 제공하며 실제 요청/과거 응답 캐시/실패/차단을 구분한다.
- LLM 설명 생성 경로와 구조 검증을 구현했다. 비용 승인·서버 키·지속 사용량 기록이 모두 있어야 호출한다. 무료 서버에서는 지속 기록 조건이 충족되지 않아 차단한다.
- [호출·비용 통제](public-providers.md): 요청 전 원자적 시도 예약, 실패도 차감, 자동 재시도 없음, 60초 간격, 24시간 성공 캐시, 고정 모델/입력/출력 제한, 키/공급자 오류 본문 비노출. 새 유료 인프라를 만들지 않았다.
- 정본 수치와 기업·문맥을 대조해 출처 메타데이터만 맞춘 위조 입력을 거부한다. 동등한 단위 환산은 유지한다.

## 평가와 실패

[평가 설계·출처·정답 방법](heldout-evaluation.md), [전체 결과](../artifacts/heldout-evaluation.json), [수정 전 첫 결과](../data/heldout/first-run.json).

같은 기업의 2025 반기/3분기 공식 자료 2건, 64수치, 40사례를 추가했다. 기존 2024 개발 코퍼스와 분리하고 첫 실행 전에 해시를 고정했다. AI가 정답을 작성했으며 사람/전문가 검수는 없다. 다른 기업은 추가하지 않았다.

|단계|수정 전|수정 후|해석|
|---|---:|---:|---|
|원문 파싱|0/4|0/4|새 연도 헤더를 거부; 미해결|
|검색|5/10|5/10|제어 질의 5/5, 자연어 0/5; 미해결|
|계산·불일치 탐지|8/8|8/8|수동 작성 수치 fixture 기반|
|기간·범위·단위 등 문맥|10/10|10/10|동등한 단위 환산 포함, fixture 기반|
|출처 검증|5/8|8/8|금액·배율·기업 위조 3건 수정, fixture 기반|

후속 단계에는 명시적인 fixture/manifest 주입이 있으므로 PDF부터 답변까지의 성공률이 아니다. 수정 후는 이미 공개한 사례의 회귀 결과이지 새 보류셋 성능이 아니다. Q3 원문 순이익 행의 내부 불일치는 원문 그대로 보존하고 `NUMERIC_CONFLICT`로 기록했다. 전문가의 정정 여부 판단은 없다.

## 테스트와 호출 비용

배포 전 Python 75개·Node 5개 통과, 기존 artifact 정합성 검사 통과. 공급자 테스트는 mock HTTP를 사용하며 실제 API 성공 증거와 구분한다. 로컬 PC·모바일 기존 흐름 37개와 공급자 화면 mock 검사 7개도 통과했다. [mock 결과](../artifacts/provider-browser-check.json)는 모든 공급자 요청을 가로챈 UI 검사이며 실제 API 호출이 아니다. [main CI](https://github.com/sokldjs554/quarterguard/actions/runs/40893175143)도 통과했다. 공개 브라우저 검증과 배포 확인은 아래 기록을 따른다.

|실행 범위|OpenAI|DART|비용|
|---|---:|---:|---|
|과거 수동 Actions|4회|4회 / 16금액 일치|OpenAI 입력 2,576·출력 438 tokens; 현재 공개 단가로 약 $0.0017312, 실제 청구액 미조회|
|공개 데모 후속 실호출|0회|4회 / 16금액 일치|DART 무료 API, 새 유료 API $0, 유료 서비스 전환 없음|

과거 [OpenAI 기록](../artifacts/live-openai.json)·[DART 기록](../artifacts/live-dart.json)은 별도 실행이다. 이후 사용자가 Render 환경 변수를 저장·재배포한 뒤 공개 서버의 DART 활성화를 확인했다. 삼성전자 2024 반기·3분기 × 연결·별도 4개 고정 조회를 실제 실행했고 매출·영업이익의 분기·누적 16개 금액이 모두 일치했다. [공개 DART 요청·응답 원본](../artifacts/public-dart.json). 각 조회를 한 번 더 요청한 4개 응답은 모두 캐시 재사용으로 추가 외부 호출 0회였다. 과거 Actions DART 4회와 이번 공개 DART 4회는 별도이며, 확인한 두 기록의 합계는 8회다. API 비용은 CPU·네트워크·저장 비용 전체를 의미하지 않는다.

## 미완료·제한

공개 LLM 실호출은 승인·지속 기록·서버 키가 충족되지 않아 실행하지 않았다. 고정 모델 총 20회/$0.20의 보수적 예상 예산안은 준비했으나 사용 승인을 받았다고 간주하지 않는다. 저장 서비스 비용은 이 금액에 포함되지 않는다.

다중 기업, 새 문서 자동 파싱, 자유 자연어 질의, 전문가 gold, 자유 문장 의미 검증, 신경망 재랭커, 고객 트래픽에서의 비용·지연 평가, 다중 사용자 인증/개인별 할당량은 미완료다. DART의 무료 인스턴스 기록은 재시작 시 초기화될 수 있다.

## 공개 서버와 HTTPS 검증

기능 커밋 [`79fc4e2af479c94ec6d1c4df2970936a8ab0d923`](https://github.com/sokldjs554/quarterguard/commit/79fc4e2af479c94ec6d1c4df2970936a8ab0d923), [PR #9](https://github.com/sokldjs554/quarterguard/pull/9), Render live 배포 `dep-dbhljr0473hc73covhhg`, 공개 `/health.commit`이 일치했다. API/UI 버전은 **1.3.0**이다. 이 보고 파일을 추가하는 문서 커밋은 후속 배포이므로 DART 검증 반영 후 최종 SHA와 배포 확인은 [v1.3.1 릴리스](https://github.com/sokldjs554/quarterguard/releases/tag/v1.3.1)에 남긴다. 이전 v1.3.0 검증 커밋과 현재 배포를 혼동하지 않도록 분리한다.

[최초 공개 서버 대조 원본](../artifacts/public-deployment-check.json) (키 설정 전 기록): 기본 TLS 검증을 켠 HTTPS로 HTML·app.js·providers.js·heldout.js·CSS의 SHA-256이 저장소와 같음을 확인했다. 개발 평가와 추가 문서 평가 API JSON도 저장소 artifact와 정확히 일치한다. 이 조회 자체는 외부 공급자 호출을 하지 않았다.

최초 `/api/providers` 조회에서는 DART `KEY_NOT_CONFIGURED`로 차단됐으나 후속 재배포 `dep-dbhlsqhsrm7s7386at8g`에서 해결됐다. 실제 호출 기록의 애플리케이션 커밋은 `c89af39f169d114d8e95a3a2e59f791ee30b8d9f`(v1.3.0)이다. 서버 키 값은 읽거나 노출하지 않았고 공개 API로 실제 응답만 검증했다. OpenAI는 계속 `KEY_NOT_CONFIGURED`, `PAID_APPROVAL_REQUIRED`, `DURABLE_LEDGER_REQUIRED`로 차단된다. DART 사용량 4회, OpenAI 사용량 0회도 조회 전후 기록에 남겼다.

직접 Chromium HTTPS는 **PC 1440×1000와 모바일 크기 390×844 모두 `ERR_CERT_AUTHORITY_INVALID`**로 막혔다. 새 v1.3 배포 이후에도 재시도했고 결과를 [원본](../artifacts/https-browser-limitations.json)에 저장했다. 정당한 환경 CA를 격리 프로필에 설치한 Firefox 시도도 브라우저 시작 오류로 페이지 탐색 전 실패했다. 인증서 무시 옵션이나 유료 TinyFish는 사용하지 않았다. HTTPS HTTP 요청 성공은 직접 브라우저 성공을 대신하지 않는다.

공개 서버를 대상으로 [고정 목적지 중계기](../scripts/https_qa_relay.py)를 사용한 Chromium PC·모바일 크기 검사는 **37/37 통과, 페이지 오류 0건**이었다. [공개 브라우저 결과](../artifacts/public-browser-check.json). 이 경로는 `브라우저 → 로컬 HTTP → 인증서 검증 HTTPS → Render`이며, 직접 HTTPS 브라우저 검증과 물리 휴대폰 검증이 아니다. 출처 이동·기간/범위/통화 차단·실제 MCP·메모/CSV·저장 결과·실패 복구를 확인했다. 외부 발행사 PDF 렌더링 성공은 주장하지 않는다.

재현: `python -m uvicorn scripts.https_qa_relay:app --host 127.0.0.1 --port 8006` 후 `DEMO_URL=http://127.0.0.1:8006 QA_OUTPUT_DIR=work/public-check python scripts/browser_check.py`. 실제 공급자 요청은 이 브라우저 회귀 스크립트에 포함되지 않는다. [키 설정 전 공개 공급자 화면](../artifacts/public-provider-browser-check.json)도 PC·모바일에서 차단 이유·9개 평가 실패 노출·가로 넘침 없음·외부 POST 0회를 별도로 확인했다.


## DART 활성화 후 실제 공개 화면 확인

[후속 브라우저 기록](../artifacts/public-dart-browser.json): PC 1440×1000과 모바일 크기 390×844에서 DART 요청 버튼이 활성화되고, 실제 공급자에서 받아 저장한 응답의 금액 4개·캐시 재사용·이번 외부 호출 0회가 표시되는 것을 확인했다. 두 브라우저 요청은 모두 캐시를 사용했으며 OpenAI 버튼은 비활성 상태를 유지했다. 페이지 오류와 가로 넘침은 없었다. [화면 캡처](images/public-providers.png).

외부 DART 실제 요청은 HTTPS API 검사 4회뿐이다. HTTP 반복 확인 4회와 브라우저 확인 2회는 모두 캐시 응답이므로 추가 외부 요청이 아니다. 직접 HTTPS 브라우저의 인증서 제한은 해결된 것으로 표현하지 않으며, 후속 화면 검사도 TLS 검증 중계 경로를 사용했다. 이 후속 검증은 v1.3.0 기능 코드에서 수행했고, v1.3.1은 API/UI 버전 표시와 문서·검증 증거를 갱신한다. 공급자 실행·검증 코드는 동일하다.

후속 문서 배포로 무료 인스턴스 사용량/캐시가 초기화될 수 있으므로 현재 화면의 누적 값이 과거 실제 검증 4회를 영구 누적한 값은 아니다. 과거 실행 시각·사용량·응답은 위 원본에 보존한다.
