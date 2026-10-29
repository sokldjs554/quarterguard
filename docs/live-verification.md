# 외부 API 실호출 검증

공개 데모의 규칙 기반 MCP 실행과 분리된 **수동 실행 검증**입니다. 기본 데모에 외부 API 키를 배포하지 않습니다. 실제 성공 여부는 Actions의 `live-provider-verification` JSON artifact로 판별합니다. 키 없음은 `blocked`, 호출/대조 실패는 `failed`이며 성공으로 계산하지 않습니다.

## GitHub에서 실행

1. 저장소 Settings → Secrets and variables → Actions → **Repository secrets**에 `OPENAI_API_KEY`, `DART_API_KEY`를 등록합니다. Environment secret은 현재 workflow에서 참조하지 않습니다.
2. Actions → **live provider verification** → Run workflow → `openai`, `dart`, `all` 중 선택합니다.
3. 실행 로그는 상태만 출력합니다. JSON artifact에는 공개 재무 근거, 응답, 검사 결과, 토큰 사용량, 소요 시간, 실행 commit이 들어갑니다. 키·HTTP 인증 헤더·전체 오류 응답은 저장하지 않습니다.

자동 push/PR 테스트에서 유료 API를 호출하지 않습니다. 수동 실행 한 번당 OpenAI 최대 4회(각 출력 최대 700 tokens), DART 최대 4회입니다. 실패 시 자동 재시도하지 않습니다. 토큰 사용량은 API 응답값이며 청구 비용은 조회하지 않아 `null`입니다.

## 생성형 LLM

OpenAI Responses API의 `gpt-4.1-mini-2025-04-14`를 호출합니다. 실제 MCP 세션으로 매출 QoQ, 누적/분기 혼동, 근거 없음, 누적 차감의 네 사례를 실행하고 기존 gold와 대조한 후 모델에 결과를 전달합니다. 모델은 한국어 설명과 구조화된 상태·값·원인·인용 ID를 생성합니다.

상태·값·원인·인용은 도구 결과와 정확하게 같아야 통과합니다. 이 검증은 **도구 결과에 근거한 설명 생성**이며, LLM이 검색/도구 사용을 계획하는 자율 에이전트가 아닙니다. 자유 문장 전체의 의미 정확성을 자동 보장하지 않으며 실제 문장도 별도 확인해야 합니다. 회귀 사례 네 개는 독립 보류 평가셋이 아닙니다.

공식 문서: [Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

## DART 발급과 검증

1. [공식 인증키 신청](https://opendart.fss.or.kr/uss/umt/EgovMberInsertView.do)에서 약관 동의, 개인 사용자 정보, 사용환경/용도를 입력합니다. 실제 용도 예: 개인 포트폴리오의 재무제표 비교·검증.
2. 안내 메일 절차를 마치고 로그인합니다. **인증키 신청/관리 → 오픈API 이용현황**에서 키를 확인합니다.
3. 저장소 Repository secret에 이름 `DART_API_KEY`로 등록합니다. 키 값을 이슈·README·채팅에 붙이지 않습니다.

키가 준비되면 기존 `quarterguard.dart.fetch`로 삼성전자(`00126380`) 2024년 3분기(`11014`), 반기(`11012`)의 연결(`CFS`)·별도(`OFS`)를 호출합니다. 공식 계정 ID가 명확한 매출(`ifrs-full_Revenue`)·영업이익(`dart_OperatingIncomeLoss`)만 대조합니다. 분기 `thstrm_amount`와 누적 `thstrm_add_amount`를 구분하고, DART 원 단위를 IR 백만 원 × 1,000,000과 Decimal로 비교합니다. 총 **16개 금액**이 대상입니다.

응답의 회사·연도·보고서 코드를 요청과 대조합니다. 연결/별도 `fs_div`는 응답에 되돌아오지 않아 요청 범위로 기록하고 해당 IR 금액과 교차 대조합니다. 누락/중복 계정, 기간·통화 불일치, 유효하지 않은 공시 링크, 금액 차이는 실패입니다. 추측으로 계정명을 매칭하거나 허용 오차를 늘리지 않습니다. 이 검증은 DART 데이터의 기본 IR 코퍼스 자동 편입을 의미하지 않습니다.

공식 문서: [단일회사 전체 재무제표](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020).

## 로컬 실행

환경에 키가 설정된 경우 `python -m quarterguard.live_verification --provider openai` 또는 `--provider dart`. 결과는 Git에서 제외된 `work/live-verification.json`에 저장합니다. 비밀값을 명령행 인자로 넘기지 않습니다.
