# SK하이닉스 연간·잔액·제품 비중 계산 — 2단계

[1단계](skhynix-source-support-20261111.md)의 원문 18개 셀을 사용해 **직접 선택한 두 근거의 계산**을 추가했다. 기준 커밋은 `4d56d6104ed4c4154fa277a77a39ff63fc493f02`다. 기존 0/3 파싱 실패, 0/5 검색 실패, 수동 음수 기준값 테스트와 1단계 검색 결과를 수정하지 않았다.

## 지원 범위와 실제 결과

현재 등록된 SK하이닉스 2024·2023 연결·KRW 자료에서만 지원한다. 임의 PDF 업로드, 모든 기업·계정·회계연도에 대한 일반 지원이 아니다.

| 사용자 질문에 대응한 명시적 선택 | 실제 결과 | 판정 |
| --- | --- | --- |
| Q1 현금 2024말 / 2023말 | +3,617,788백만 원 · +47.6820% | 조건 일치 |
| Q2 연간 매출 2024 / 2023 | +33,427,241백만 원 · +102.0189% | 조건 일치 |
| Q2 재고 2024말 / 2023말 | −166,722백만 원 · −1.2367% | 조건 일치 |
| Q3 2024 DRAM / 같은 제품 표 합계 | 67.5777% | 조건 일치 |
| Q4 영업손익 2024 / 2023 | +31,197,632백만 원 · 적자에서 흑자로 전환 | 음수 기준값으로 증감률 보류 |
| Q5 2024말 재고 / 2023 매출, 개월분 | 계산 없음 | 분모·기간·기말/평균 재고 정의 확인 |

질문 5개에 대해 **6개 연산**을 평가했다. Q2는 매출 흐름과 재고 잔액을 각각 계산한다. Q1의 기준 연도2024는 사용자의 답안에서 평가자가 명시적으로 선택한 조건이다. 검색이 누락 조건을 자동 확정한 것이 아니다. 자연어 검색은 계속 `not_calculated`이며, 계산은 별도 모드·A/B 선택 후 실행한다.

[실제 실행 원본·MCP 입출력](../artifacts/skhynix-calculations-20261111/evaluation/report.json). 공식 PDF 파일을 pypdf로 다시 파싱한 18개 셀이 등록 셀 전체와 일치하는지 확인한 뒤 등록 ID로 실제 계산했다. 과거 응답 재생이나 수동 금액 입력을 PDF 처리로 세지 않았다. 실제 stdio MCP 검색5회·근거 조회13회·계산6회, **평가 배치 총24회**다. 호출 순서는 평가 코드가 정했으며 LLM 계획·자율 도구 선택은 없다.

사용자 원본 질문·답안은 본인 직접 작성·AI 미사용 확인을 보존했다. 이 질문들은 이미 수정에 사용한 개발 사례다. 이번 정확한 네 자리 백분율, 추가 경계 사례, 코드·테스트·평가 실행은 AI 작업이다. 새 문서/질의 holdout, b의 새 검수, 새 고객 사용을 수행했다고 기록하지 않는다.

## 계산과 보류 규칙

[코드](../quarterguard/source_calculations.py), [테스트](../tests/test_source_calculations.py).

- `calculate_source_pair()`는 등록된 ID만 받는다. API는 임의 금액·배율 같은 추가 필드를422로 거부한다. 원본 셀 파일의 해시가 다르면503으로 실패한다. 응답에는 두 정본 근거와 스냅샷 해시가 남는다.
- **연간 비교:** 매출·매출원가·영업손익의 같은 항목, 기업·연결·통화와 단위를 확인한다. 1월1일~12월31일의 전체 기간이며 정확히 전년 관계여야 한다. 반기·분기·역방향·동일 연도는 통과하지 않는다.
- **잔액 비교:** 현금·재고의 같은 항목과 연속된12월31일 기준일만 받는다. 잔액에 시작일·종료일·12개월 길이를 만들어 붙이지 않는다.
- **제품 비중:** DRAM/NAND/기타 제품과 같은 문서·표·기간·연도 열의 제품 합계만 사용한다. 값이 같더라도 손익계산서 매출을 제품 표 합계로 바꾸지 않는다. 음수 제품·0이하 합계·합계 초과 금액은 보류한다.
- 문맥이 다르면 **차이·증감률·비중 모두 계산하지 않는다**. 문맥은 맞고 분모가0/음수이면 차이 금액만 계산하고 증감률을 보류한다. 각각 `difference_status`와 `percentage_status`를 구분한다. 원래 분기 `compare()`의 보류 정책은 변경하지 않았다.
- 금액은 Decimal로 원 단위 환산 후 계산하고, 차이는 항상 **백만 원**으로 반환한다. 출력에 `currency=KRW, scale=1000000`을 명시한다. 퍼센트는 소수점 넷째 자리, 동률이면 짝수 반올림한다.
- 재고 개월분은 분모와 기간 및 기말/평균 재고 정의가 필요해 자동 계산을 계속 보류한다.

MCP 실행: `python -m quarterguard.source_mcp_server`. 새 `calculate_source_pair`가 기존 확장 서버에 추가됐다. 과거4도구 서버 `quarterguard.mcp_server`와 그 고정 평가 해시는 그대로다. 이 전용 실행 진입점을 사용하는 제약을 유지해 과거 기록을 보존한다.

## 제품에서 재현

[공개 데모](https://quarterguard.onrender.com/) → **근거 검색** → **SK하이닉스 · 선택 문서의 근거 찾기** → **선택 근거로 계산**을 펼친다.

1. `전년 말 잔액 증감`에서 A2024현금/B2023현금을 확인하고 계산한다. 금액 아래의 기준일·연결·단위·원문 행·열과 링크를 본다.
2. `연간 실적 전년 대비`에서 A/B영업손익을 선택한다. 차이 금액과 흑자 전환이 표시돼도 증감률은 `—`인지 확인한다.
3. `제품 매출 비중` 기본값의 DRAM/제품 합계를 계산한다. B를2023합계로 바꾸면 모든 계산이 보류되는지 확인한다.
4. `재고 개월분 · 정의 확인`에서 분모와 기간의 확인 안내를 본다.
5. `계산·근거 JSON 저장`으로 선택 ID, 원문 위치, 검사 결과, 공식, 정규화 금액을 함께 저장한다. 조건을 바꾸거나 오류가 나면 이전 결과와 저장 버튼이 무효화된다.

검색 후보 카드의 `계산 A에 선택` / `계산 B에 선택`으로 값을 옮길 수도 있다. 계산 방식은 사용자가 직접 정한다. 기본값은 예시이며 질문에서 자동으로 확정한 조건이 아니다. 금융 문서 작업지 흐름을 유지했고 채팅 UI로 바꾸지 않았다.

API:

```text
GET /api/source-calculations/options
POST /api/source-calculations
{"mode":"balance_yoy","current_id":"skh2024annual-in-2025oc:financial-position:cash:2024","base_id":"skh2024annual-in-2025oc:financial-position:cash:2023"}
```

원본 추출 manifest는 1단계 그대로 보존한다. 현재 `/api/source-documents`와 계산 options의 문서 설명은 해당 스냅샷 위에 현재 계산 모드를 추가해서 반환한다.

## 검증과 한계

- Python294개 실행 **OK, 1개 skip**. Node14개 통과. 기존 Starlette/Pydantic 경고는 로그에 남겼다.
- [현재 등록 셀18×18×4모드=1,296조합](../artifacts/skhynix-calculations-20261111/verification/registered-pair-matrix.json): 완전 계산10조합, 음수 기준값으로 차이만1조합, 나머지1,285조합은 계산 보류. AI가 작성한 현재 카탈로그의 조합 검사이며 새로운 사람 평가가 아니다.
- [PC1365×900·모바일390×844 브라우저](../artifacts/skhynix-calculations-20261111/browser/): 실제 로컬 서버로 정상 계산, 음수 기준, 연도 불일치, 정의 보류, JSON저장, 조건 변경 후 무효화, 503·전송 시간초과 주입, 실제 응답의 늦은 전달 차단, 복구와 기존 +6.7916% 분기 비교를 확인했다. 새 시간초과는 주입 테스트로, 실제60초 대기가 아니다.
- [1단계 검색 브라우저 회귀](../artifacts/skhynix-calculations-20261111/phase1-browser-regression/)와 과거 artifact 일치 검사를 통과했다. 입력 fixture를 바꾼 회사·연결·통화·배율·날짜·0/음수 테스트는 실제 PDF 재파싱 평가와 구분한다.
- AI의 별도 설계·코드 검토를 진행했다. 차이 금액의 백만 원 표시를 명시했고, 최종 코드 검토에서 중대한 추가 문제는 보고되지 않았다. 사람의 코드 검토로 기록하지 않는다.
- 새 유료 API호출0회, 새 LLM생성0회, 새 비용0. 과거 청구액은 이번에 조회하지 않았다. 신규 사람 검수/사용과 고객 환경 배포는0건이다.

```bash
python -m unittest tests.test_source_calculations tests.test_source_calculation_api tests.test_source_calculation_mcp -v
python scripts/evaluate_source_calculations.py --pdf /path/to/offering-circular.pdf --output work/new-calculation-run
python -m unittest discover -s tests
node --test tests/*.mjs
python scripts/evaluate_source_pair_matrix.py
python -m uvicorn quarterguard.api:app --port 8771
# 다른 터미널; Playwright/Chromium 필요
python scripts/browser_source_calculation_check.py --url http://127.0.0.1:8771 --output work/new-browser-run
```

평가 출력은 새 폴더에만 쓴다. 원본 질문/답안, 모든 과거실패·검수·평가 파일은 [보존 점검](../artifacts/skhynix-calculations-20261111/preservation.json)에서 확인할 수 있다.

지원서에는 “SK하이닉스 공개 원문에서 추출한 근거를 연결해 연간 실적·전년 말 잔액·제품 비중을 각각 검증하고 계산하는 기능을 추가했다. 음수 기저에서는 증감률을 보류하고 금액 차이를 별도로 제공했다”라고 범위를 명시할 수 있다. 사용자5질문 자동 정답률100%, 모든 연간 재무제표 지원, 신규 전문가 검수 완료, 실제 고객 환경 배포는 주장할 수 없다.

후속 사람이 확인할 업무는 [새 계산 흐름 직접 확인 양식](validation-kit/source-calculation-followup.md)에 준비했다. 현재는 빈 양식이며 참여 완료 기록이 아니다.
