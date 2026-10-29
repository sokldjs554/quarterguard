# 조사 기록 · 2026-10-29

## 공고 직접 확인

[트레져러 채용 원문](https://treasurer.recruit.roundhr.com/c/nLeVw9amBH)을 일반 웹 도구로 열 때 실패했고, JavaScript 페이지를 읽는 TinyFish로 동일 URL의 본문을 직접 확인했다. 제공된 소개·4개 문제·4개 업무·5개 자격·4개 우대사항은 의미상 일치했다. 원문에는 기술 스택을 중요하게 보지 않는 설명, 간식·식대·영어 이름·자율 연차 관련 복지가 추가되어 있었다. 추출한 채용 절차는 최종 합격만 표시해 사용자가 제공한 중간 면접 단계는 확인하지 못했다. 단계가 없다는 뜻은 아니다. 현재 채용 조건은 원문 재확인이 필요하다.

## 회사 사실과 적용 해석

- **직접 확인한 회사 설명:** [공식 홈페이지](https://www.treasurer.co.kr/)는 금융 데이터 수집·정제·추론 및 금융·보험·미디어 등의 업무 적용을 소개한다. [금융 AX 페이지](https://www.treasurer.co.kr/story/finance)는 금융 리서치·트레이딩·백오피스 및 한국·아시아 데이터 기반 도구를 설명한다.
- **프로젝트의 해석:** 답변 생성보다 잘못된 근거 조합을 막고 수치 검증을 재현하는 좁은 업무가 직무 적합성을 보여줄 수 있다고 판단했다. 회사 내부 구현·고객 트래픽·실제 성능은 확인하지 않았고 본 프로젝트와 제휴 관계가 없다.

## 후보 비교

|후보|사용자 문제|차별점과 기존 범위|직무 연결|데이터·평가 가능성|데모 적합성|
|---|---|---|---|---|---|
|분기 실적 비교 검증|같은 표의 3개월·누적, 연결·별도, 원화·달러 혼동|범용 QA 대신 잘못된 비교 차단과 누적 차감 교차검증|파서·청킹·검색·MCP·수치 평가|실제 반기·분기 PDF; 날짜/통화 검증과 Decimal 정답|숫자 두 개와 출처, 차단 이유로 이해 가능|
|사업부 매출 합계 검증|내부거래 제거를 빼고 매출 합산|제거 항목을 명시한 조정표|표 해석·계산 도구|실제 주석으로 가능; 사업부별 구조 변화 대응 필요|명확하나 이번 분기 검증과 함께 하면 범위 과대|
|정정공시 영향 추적|새 공시가 예전 분석 수치를 오염|버전·시점 조건이 핵심|수집·버전 검색·추적|정정 전후 원문과 정답 사례 확보 난도 높음|가치 크지만 첫 데모에서 설명 부담|

선정은 구현 난도만이 아니라 명시적인 검증 정답, 잘못된 비교의 가시성, 원문 접근성을 함께 고려했다.

## 유사 제품·공개 프로젝트

|자료|직접 확인한 공개 흐름|이번 프로젝트에 반영한 점·차이|
|---|---|---|
|[FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)|금융 리서치·밸류에이션, 결정론 계산, 출처 및 에이전트 검증을 README에 설명|계산/출처 추적 자체는 차별점 아님. 한국 분기 공시의 문맥 호환성 오류를 재현하는 데 집중|
|[FinanceBench](https://github.com/patronus-ai/financebench)|질문·답·evidence·문서 위치 구조, 공개 150개 표본 설명|정답 근거 ID와 개별 실패 결과를 공개. 해당 데이터셋/성능 수치를 본 프로젝트 평가로 사용하지 않음|
|[Docling](https://github.com/docling-project/docling)|문서 변환, 표 구조 인식, 시작 예제와 지원 형식|파싱 책임과 출력 스키마를 분리. 범용 PDF 파서를 구현했다고 주장하지 않음|
|[AlphaSense 도움말](https://help.alpha-sense.com/hc/en-us/articles/42591266633875-Quick-Start-Guide-to-Generative-Search)|답변 인용에서 원문/발췌 확인, 질문 후속 검증 흐름|결과에서 근거 상세로 연결. 유료 제품에 로그인하거나 성능을 비교한 것은 아님|
|[AlphaSense 금융 데이터 통합](https://help.alpha-sense.com/hc/en-us/articles/48564174120595-Financial-Data-Integration-into-Generative-Search)|구조화 금융 데이터와 인용 연결|단순 인용 버튼을 독창성으로 주장하지 않음|
|[FinBalance reconciliation benchmark](https://github.com/mohamedAtoui/finance-accounting-agent-benchmark/tree/finbalance-reconciliation-benchmark)|합성 회계 대사 업무와 프로그램 검증을 공개 문서에서 설명|결정론 검증의 선행 사례. 실제 공개 분기 공시의 문맥 혼동이라는 다른 업무 범위|

조사 범위 안에서 초점의 차이를 설명할 뿐, 최초·유일·시장 전체 희소성을 주장하지 않는다. 공개 문서 검토이며 경쟁 제품에 대한 실사용 벤치마크가 아니다.

## SK Family와 README·데모 참고

사용자가 URL을 제공하기 전에는 이전 저장소를 특정하지 않았다. 이후 다음 README를 GitHub API로 직접 읽었다.

- [SKN27-FINAL-1Team · 밥벌이](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN27-FINAL-1Team): 서비스 링크와 소개를 앞에 놓고 광고·시연·MCP 영상을 분리한다. 기능/아키텍처/기술 상세를 연결한다. 이번에는 첫 화면에 문제, 데모 링크, 실제 화면을 배치하고 MCP 기록은 별도 근거로 연결한다.
- [SKN27-FINAL-3Team · 차분해](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN27-FINAL-3Team): 주요 기능 → 서비스 흐름 → 에이전트 → 설치·데이터 파이프라인 → API·테스트·배포·유의사항 흐름. 이번에는 실제 흐름과 재현 명령을 짧게 제공하고 미실행 항목을 별도로 둔다.
- [SKN32-FINAL-6TEAM · 구구루트](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN32-FINAL-6TEAM): 프로젝트 범위·고객 흐름·계층 책임·데이터/외부 소스·운영 불변식 구분. 시연용 mock과 실제 기능을 구분하는 설명을 참고해 준비 재생과 실제 MCP 실행을 UI에 분리한다.
- 외부 README는 FinRobot의 사용 경로 구분, Docling의 빠른 실행, FinanceBench의 근거 스키마 설명을 참고했다. 화면이나 문구를 복제하지 않았다. 링크된 영상을 직접 시청하거나 모든 공개 데모의 운영 상태를 검증했다고 주장하지 않는다.

## 데이터 접근·사용 조건

[DART 이용약관](https://opendart.fss.or.kr/intro/terms.do)은 인증키 기반 접근, 저작권 및 공공데이터 관련 법령 적용을 설명한다. 공개 공시라는 이유만으로 모든 PDF에 자유 재배포 라이선스가 있다고 가정하지 않는다. [DART 전체 재무제표 API 문서](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020)는 분·반기 손익계산서의 thstrm_amount가 3개월, thstrm_add_amount가 누적이라는 차이를 명시한다.

삼성전자 IR PDF는 로그인 없이 직접 다운로드에 성공했다. 해당 보고서에 대한 명시적 오픈 재배포 라이선스는 확인하지 못했다. 삼성 관련 공개 법적 고지에서도 저작권 유보를 확인했으나 다른 지역/서비스 약관을 IR에 그대로 적용한 법률 판단은 하지 않았다. 따라서 **PDF와 전체 추출 텍스트·원문 스크린샷은 저장소와 배포본에서 제외**한다. 수치 사실 192개와 원문 URL·페이지·행·열·해시, 직접 작성한 설명만 제공한다. 사용자 환경에서 재수집하는 명령을 제공하며 재사용자는 원문 이용 조건을 확인해야 한다. 코드 MIT 라이선스는 원문 PDF나 모델 가중치에 적용되지 않는다.
