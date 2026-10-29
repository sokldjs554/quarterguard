# UI 조사와 반영 · v1.1 (2026-10-29)

이 문서는 이전 작업지의 조사 기록입니다. 현재 v1.2의 실제 데모 조사·화면·검증은 [후속 기록](live-demo-research.md)을 참조하세요.

## 문제와 기준

기존 화면은 8개 테스트 사례와 큰 결과 카드를 전면에 두어 실제 문서 검토보다 데모 목록에 가까웠다. 채용 공고의 금융 문서 파싱·검색·수치/문맥 검사·MCP 실행 기록을 사용자가 직접 확인하는 작업 흐름으로 바꾼다.

[채용 공고](https://treasurer.recruit.roundhr.com/c/nLeVw9amBH) 원문을 다시 읽어 직무 범위를 확인했다. 공개 제품·도움말 15개와 검색 색인만 확인 가능한 Duco 1개를 조사했다. DataSnipper, BamSEC, AlphaSense Grid, ARIA, Langfuse의 공식 화면 자료도 살펴봤다. 유료 계정이나 로그인한 제품 기능은 시험하지 않았으며, 홍보 이미지를 실운영 성능의 근거로 보지 않는다.

## 참고 제품

|제품·출처|관찰|반영 판단|
|---|---|---|
|[AlphaLenz](https://alpha-lenz.com/en/agents/check_claim)|공개 주장·실적·위험 검토 기능이 이미 있어, 일반적인 금융 검증 챗봇을 차별점으로 삼지 않음|기존 기능과 범위 비교|
|[ARIA](https://insightre.ai/)|문서 분류·파싱·매칭·미해결 항목 흐름|문제 항목에서 근거를 확인하는 순서|
|[Findle](https://findle.io/)|교육·퀴즈 중심|업무 화면 참고에서는 제외|
|[Hebbia Matrix](https://www.hebbia.com/product)|문서 집합에 질문 열을 적용하는 비교 구조|항목별 비교 행|
|[AlphaSense Generative Grid](https://help.alpha-sense.com/hc/en-us/articles/41680141048979-Leveraging-Generative-Grid)|여러 문서를 열과 행으로 정리하는 근거 기반 검토|비교표와 출처 연결|
|[BamSEC](https://bamsec.readme.io/docs/compare-filings)|공시 변경 부분을 나란히 확인|차이를 발생 지점에서 확인|
|[DataSnipper](https://www.datasnipper.com/resources/meet-datasnipper-excel-online-extract-cross-reference-and-validate-data-via-your-browser)|Excel 수치와 문서 뷰어를 나란히 연결|숫자 클릭 → 해당 근거 셀|
|[Daloopa](https://daloopa.com/benefits/financial-data-in-spreadsheets)|재무 스프레드시트의 수치와 출처 연결|셀 단위 근거 위치|
|[Workiva](https://support.workiva.com/hc/en-us/articles/32709250416276-Should-I-use-links-or-connections)|셀 링크와 데이터 연결의 구분|수치 출처의 명시|
|[Numeric](https://www.numeric.io/product/variance-analysis)|차이 분석에서 세부 거래로 이동|증감률과 검토 사유 연결|
|[BlackLine](https://www.blackline.com/products/financial-close/transaction-matching/)|매칭 및 예외 처리|불일치가 있는 항목을 구별|
|[MindBridge](https://support.mindbridge.ai/hc/en-us/articles/360058192493-Data-table-dashboard-Overview-for-GL-MAC-v-2)|위험 행·필터·세부 조사|표 안에서 상태를 표시|
|[Rogo](https://rogo.com/)|금융 업무 결과물 중심 소개|챗봇 대신 대조 작업 결과물|
|[Langfuse](https://langfuse.com/docs/observability/overview)|도구 실행과 세부 trace 탐색|실행 기록은 별도 상세|
|[LangSmith](https://www.langchain.com/langsmith/evaluation)|개별 사례와 평가 구성 비교|전체 통과뿐 아니라 원인·수치·인용 확인|
|[Duco](https://support.du.co/hc/en-us/articles/360033635794-Configuring-exceptions-workflow)|검색 색인의 예외 처리 설명만 확인; 본문 로그인 제한|검증된 UI 근거로 사용하지 않음|

## 반영한 화면

첫 화면을 **공시 대조 작업지**로 바꿨다. 왼쪽에는 독립적으로 조건을 선택하는 A/B 열과 손익 6개 항목, 오른쪽에는 선택한 숫자의 문서 근거를 둔다. DataSnipper의 수치·문서 연결, BamSEC의 차이 확인, Matrix의 비교 구조를 참고하되 제품 화면이나 이미지를 복제하지 않았다.

- 보고서·연도·연결/별도·단독 분기/누적·통화를 각각 선택한다.
- 숫자를 누르면 해당 문서·행·열이 강조된다. 비교 자료 B를 눌렀을 때 원문 페이지도 B를 따른다.
- 조건이 다르면 증감률을 비우고 해당 항목의 불일치 이유를 보여준다.
- 기본 표 계산과 실제 MCP 근거 재검증을 구분한다. 재검증은 6행 × 근거 2회/검증 1회 = 18회 도구 호출이며, 실패하면 이전 결과를 지운다.
- 평가·저장 사례·도구 기록은 별도 탭과 상세에 둔다. 테스트 사례를 메인 작업으로 오인하지 않게 한다.
- 모바일은 각 항목의 A/B 수치가 함께 보이도록 재배치한다. 근거 표는 표 영역에서 가로로 스크롤할 수 있다.

## 삼성전자와 원문 표시

삼성전자는 최초 구현에서 선택한 **단일 기업 회귀 검증용 예시 데이터**다. 사용자가 정한 제품 주제나 트레져러와의 거래 관계를 의미하지 않는다. 회사 이름을 제품 정체성으로 쓰지 않고, 화면 상단에 “예시 데이터 · 삼성전자 · 보고서 2건”으로 범위를 표시한다. 실제 수집·평가하지 않은 다른 기업 선택지는 만들지 않았다.

근거표는 수집한 수치로 재구성한 표이며 원문 이미지가 아님을 화면에 표시한다. “원문 PDF”는 발행사 주소를 직접 여는 iframe과 새 탭 링크다. PDF 원본을 저장소에 배포하거나 서버에서 재호스팅하지 않는다. 외부 PDF 차단 시 링크·재구성 표를 사용할 수 있으며, 실제 브라우저 PDF 렌더링까지 검증했다고 주장하지 않는다.

## 검증

로컬 단위·통합 테스트 54개, Playwright PC/모바일 흐름 31개를 통과했다. 실제 MCP 18회 호출, 조건 불일치, 오래된 응답 차단, 네트워크 실패·재시도, 키보드 포커스, A/B 출처 전환, 평가의 잘못된 거절 사유 표시를 포함한다. 독립 AI 코드 리뷰에서 발견한 출처 선택 상태·평가 표시·포커스 문제를 수정했다. [브라우저 결과](../artifacts/browser-check.json), [구현 설계](superpowers/specs/2026-10-29-document-worksheet-design.md).
