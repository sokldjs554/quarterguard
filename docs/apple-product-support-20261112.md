# Apple 원문·계산·판단 보류 지원

Apple FY2024 Form 10-K의 **공식 SEC HTML → 원문 수치/설명 추출 → 선택 문서 검색 → 조건 검증 → 계산 또는 보류 → 실행 기록·JSON 저장**을 제품에 연결했다. 기존 삼성 분기 작업지와 SK하이닉스 계산은 유지했다. 이 기능은 규칙 기반이며 LLM 생성·자율 계획 기능이 아니다.

## 이번 범위와 결과

|항목|상태|검증 범위|
|---|---|---|
|1. SEC HTML 원문 수집·검색|완료|공식 URL 새 HTTPS GET200, 등록 SHA 일치. 제품 추출기로 25셀·2문단 재현. 사용자 지정 19개 수치·행·연도·쪽·단위 일치|
|2. Q1~Q5 계산과 출처|완료|매출총이익률·지역 매출 변화·영업현금흐름 차감·자사주 지출·세금 대조. 원문/계산식·기간·통화·단위 함께 표시|
|3. Q6~Q7 근거 있는 보류|완료|집계→개별 일반화, 판매량 단독 원인 판단을 보류하고 관련 표/문단과 필요한 자료 표시|
|4. 수정 후 평가·회귀|완료|동일 7문항 7/7, AI 합성 변형 19/19. Python339개 실행·실패0·1skip, Node18개 통과. PC/모바일 정상·보류·저장·오류·복구 및 기존 기능 회귀|

[최초 0/7 기록](apple-first-evaluation-20261112.md)은 그대로 보존했다. 본인이 AI 없이 작성했다고 확인한 원래 7문항을 **이번 구현에 사용했으므로 수정 후 결과는 개발·회귀 평가**다. 새 독립 holdout이나 일반 금융 질문 정확도100%로 표현하지 않는다.

## 실제 처리와 근거

- [원문](https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm)은 HTML이다. **PDF 파싱 0건**. 22·29·33·34·40은 인쇄 쪽수이며 HTML XPath, 실제 행·연도 열, XBRL fact/context도 저장한다.
- [제품 추출기](../quarterguard/apple_source.py)는 실제 표에서 숫자를 읽는다. 질문 정답 파일의 금액을 주입하지 않는다. 매출/원가 구역을 구분해 반복되는 Products/Services를 처리하고, XBRL 기업·기간·USD·scale·제품 차원을 대조한다. 지역별 표시 표는 colspan과 연도 열을 사용한다.
- [공식 원문 압축 보관본](../data/apple-source/source.html.gz)은 원문과 동일한 바이트로 복원된다. [새 수집·파싱 기록](../artifacts/apple-support-20261112/fresh-fetch.json), [등록 추출 결과](../data/apple-source/evidence.json). 실행 시에는 해시 확인한 추출 스냅샷을 읽으며 매 요청마다 SEC에 접속하지 않는다.
- 금액은 **백만 미국 달러**. FY2024 `2023-10-01~2024-09-28`은52주, FY2023 `2022-09-25~2023-09-30`은53주다. 단순 보고금액 변화이며 같은 주수로 조정한 수치가 아니다.
- 19개 제출 수치 이외의 6개 추가 셀도 원문에서 추출했지만, 이 6개를 작성자나 b가 추가 검수했다고 기록하지 않는다.
- 제품은 이 해시의 Apple FY2024 문서와 선택 표만 지원한다. 다른 SEC 공시, 정정 문서, 모든 표·계정·질의를 처리하는 범용 파서가 아니다. 변경된 원문은 재검증·등록 전까지 거부한다.

|질문|수정 후 결과|표현 한계|
|---|---|---|
|Q1|제품37.1806%, 서비스73.8804%|집계 매출총이익률, 개별/순수익성 아님|
|Q2|중국권−5,607, 전체+7,750백만 달러|연도 생략은 선택 문서의2023→2024열이라고 표시,52/53주 경고|
|Q3|118,254 + (−9,447) =108,807백만 달러|현금 유출의 부호 유지. 회사 정의 특정 지표라고 단정하지 않음|
|Q4|지출액 증가17,399, 부호 유지 변화−17,399백만 달러|매입 주식 수 추론 안 함|
|Q5|영업이익+8,915·법인세비용+13,008·순이익−3,259, 세액조정 영향10,246|세금은 일부 설명 요인, 유일 원인/현금 납부액 아님|
|Q6|관련 매출·원가와 집계 비율 제시 후 판단 보류|개별 원가와 공통비 배분 필요|
|Q7|중국권 두 연도 금액·원문 설명을 제시 후 판단 보류|판매량·가격·구성·환율별 기여도 필요|

[검색·판정 코드](../quarterguard/apple_review.py)는 제한된 한국어·영어 문법으로 작업을 해석한다. 지원하지 않는 조건이나 여러 연산, 비교 방향·차감 순서가 불분명한 질문은 보류한다. 모든 자연어 표현을 이해하지 않으며, 질문을 간단히 다시 써야 하는 경우가 남는다.

## 실패·평가 기록

- [최종 평가](../artifacts/apple-support-20261112/evaluation-reviewed/results.json): 7개 원문 질문, 실제 로컬 FastAPI 검색/검토/근거조회, 반환값과 계산·출처 대조. 정답은 실행 후 채점에만 사용한다. 정성 설명은 규칙/AI 검토 기준이며 새 사람 판정이 아니다.
- [별도 AI 코드 검토](../artifacts/apple-support-20261112/code-review.json)는 연도 역방향·차감 역순·추가 조건 누락3개를 발견했다. [실패 재현](../artifacts/apple-support-20261112/review-findings-red.txt) 후 수정했다.
- 강화한 문법이 정상 영어2개도 막은 [17/19 중간 결과](../artifacts/apple-support-20261112/evaluation-final/results.json)를 보존했다. 연산별 허용 문법을 수정한 뒤19/19. 합성 변형은 AI 작성이며 새로운 사람 사례로 세지 않는다.
- [전체 Python](../artifacts/apple-support-20261112/python-tests-reviewed.txt), [Node](../artifacts/apple-support-20261112/node-tests.txt). Starlette/httpx와 Pydantic 등의 기존 환경 경고는 로그에 남아 있다.
- [원기록 보존](../artifacts/apple-support-20261112/preservation.json): 기존694개 artifact/data/사람 기록 파일의 해시 일치.

## 실제 실행과 화면

[실제 MCP stdio 기록](../artifacts/apple-support-20261112/evaluation-reviewed/mcp.json)은 검색→2셀 조회→정상 검토→판단 보류→잘못된ID 오류→정상 복구의7회 호출이다. 실행 순서는 Python 스크립트가 정했으며 LLM 도구 계획이 아니다. 검토 응답의 `steps`는 내부 규칙 단계이고, 개별 단계가 MCP 통신이라는 뜻은 아니다.

[PC1365×900·모바일390×844 로컬 브라우저 기록](../artifacts/apple-support-20261112/browser-final/report.json). 실제 FastAPI를 사용했고503·전송 시간 초과·늦은 응답은 의도적으로 주입했다. 문서/질문 변경이나 실패 후 이전 성공과 저장 버튼을 무효화한다. [기존 SK 계산 회귀](../artifacts/apple-support-20261112/browser-sk-regression/report.json)도 같은 두 화면에서 수행했다. 로컬 HTTP 브라우저와 공개 서버 직접HTTPS·TLS검증 중계 검사는 서로 구분한다.

이번 새 LLM 생성·유료 API 호출은 **0회**, 새 비용0달러, 청구액 미조회. 작성자/b의 새 사용·재검수, 금융기관 고객 환경 배포를 수행했다고 기록하지 않는다.

## 재현·직접 확인

[데모](https://quarterguard.onrender.com/) → **근거 검색 → 검토 문서에서 Apple 선택 → 질문 입력 → 원문 근거 검색 → 질문의 근거·계산 검증**. 원문 표·행·열·실제 날짜와 단위를 확인하고 JSON을 저장할 수 있다. Q6/Q7은 판단 보류가 정상이다. 삼성 분기 작업지·SK 계산과 분리된 선택 문서 흐름이다.

```bash
python -m unittest tests.test_apple_source tests.test_apple_review -v
python scripts/evaluations/evaluate_apple_support.py --output work/apple-support-reproduction-new
python -m unittest discover -s tests
node --test tests/*.mjs
python -m uvicorn quarterguard.api:app --port 8781
# 다른 터미널
python scripts/browser_apple_support.py --url http://127.0.0.1:8781 --output work/apple-browser-new
```

출력 경로는 새 경로여야 한다. 공개 배포는 [서버 health](https://quarterguard.onrender.com/health)의 `commit`, GitHub main과 Render 배포 commit으로 대조한다. CI·배포 확인은 PR과 실제 서버 응답을 기준으로 한다.

## 지원서에 쓸 수 있는 범위

> 직접 작성한 Apple 공시 질문7개에서 제품의 문서 미지원 실패0/7을 먼저 보존한 뒤, SEC HTML의 표·연도열·XBRL 문맥을 연결하는 제한형 추출과 계산·판단 보류를 추가했습니다. 같은 개발 사례7개와 합성 변형19개를 회귀 평가하고, 비교 방향·차감 순서·추가 조건 누락 오류를 수정했습니다. 기존 금융 문서 검토 UI와 실제 MCP 실행을 검증했습니다.

구현과 자동 검증에는 AI의 도움을 사용했다. 직접 작성한 것은 질문·답안이며, 이번 구현 전체를 본인 독립 작성이나 사람 검수 완료로 바꾸어 표현하지 않는다.

## 공개 배포 후 확인

[배포 기록](../artifacts/apple-deployment-20261112/publication.json). 제품 커밋 `91135119539387e023f0e08c4232ed38ab6f5caa`에서 GitHub main·Render live·공개 health가 일치했다. GitHub CI2건 통과, Render 배포 `dep-dbqaj7navr4c739s78p0` live를 확인했다.

[공개 HTTPS API7/7](../artifacts/apple-deployment-20261112/public-api.json)은 로컬 정본 응답과 전체 일치했다. TLS인증서 검증을 유지했다. 배포 전환 중 첫 health 요청은20초 ReadTimeout이었고, 이후 live 상태의 health는200·약0.523초였다. 첫 실패는 보존했으며 가용성 보장이나 장기 성능 통계로 확대하지 않는다.

[공개 서버 중계 브라우저](../artifacts/apple-deployment-20261112/browser-relay.json)는 PC1365×900·모바일390×844에서7문항·원문 표시·JSON 저장·문서/질문 변경·503/전송시간초과/지연응답 주입·복구·기존SK/삼성 회귀를 통과했다. HTTPS상류의 인증서를 검증하는 고정 대상 중계를 사용했다. 직접 Chromium HTTPS는 이 환경에서 ERR_CERT_AUTHORITY_INVALID였으며, 검증을 끄고 성공으로 처리하지 않았다. 사용자의 실제 기기 확인이나 b 재검수로 세지 않는다.

[PC 캡처](../artifacts/apple-deployment-20261112/Q1-1365.png) · [모바일 캡처](../artifacts/apple-deployment-20261112/Q1-390.png) · [판단 보류](../artifacts/apple-deployment-20261112/Q6-390.png). 캡처와 공개 응답의 제품 커밋은9113511이다. 이 배포 기록을 추가하는 후속 커밋은 문서·검증 자료만 바꾸며 제품 코드는 동일하다. 최초0/7 재현은 당시 기준 커밋60af1fd에서, 수정 후 재현은 위 새 평가 스크립트로 실행한다.
