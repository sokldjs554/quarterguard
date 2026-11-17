# 딜로이트 안진 IT AI 엔지니어: 기존 프로젝트 대조

확인일: 2026-11-17 KST. [공고 원문](https://join.deloitte.co.kr/WiseRecruit2/User/RecruitView.aspx?ridx=5231)의 경영지원부문 IT AI 엔지니어 채용을 기준으로 한다. 저장소 코드·실행 산출물·GitHub Actions·공개 HTTP 확인을 구분했다. 이번 조사·문서 수정·재검사는 Codex가 수행했다.

## 후속 확인: 병합·공개 화면·본인 역할

2026-11-17 후속 확인에서 QuarterGuard #90, Preflight #7, Harbinger #23을 main에 병합했다. 아래 최초 조사 당시의 로컬 실패·접속 제한 기록은 당시 상태를 보존한 것이다. 현재 확인 결과는 이 절과 문서 끝의 최종 링크를 우선한다.

- QuarterGuard 배포 화면에서 `7d37947` 빌드를 확인했다. 정상 비교 6.7916%, 비교 검증의 실제 MCP 18회 실행 완료, B를 6개월 누적으로 변경했을 때 기간 불일치·계산 보류를 확인했다. 이 공개 경로는 LLM을 호출하지 않는다.
- Preflight 배포 화면에서 `634fb6e` 빌드를 확인했다. 무료 예시 3건은 통과 2·보류 1, 모델 대역 9회, 실제 LLM 0회·비용 0으로 완료됐다. 이번에 새 유료 LIVE 요청이나 로그인 검증을 수행한 것은 아니다.
- Harbinger 저장 예제는 응답했다. AWS 직접 주소는 브라우저에서도 인증서 이름 불일치가 나타났으며 우회하지 않았다. 기존 EC2 재배포·인증서 수정은 수행하지 않았다.
- Preflight 전체 CI는 4,505개 통과를 확인했다. QuarterGuard는 Python 405통과·1건너뜀, Node 39통과. Harbinger의 PR 검사는 일반·브라우저·운영·Docker·TensorFlow가 성공했고, 병합 후 재검사는 일반·TensorFlow 성공을 확인했으며 Docker 작업은 이 기록 시점에 진행 중이다.
- [추가 기여 기록](code-review-kit/05-period-diagnostic-test-20261111.md)을 확인해 QuarterGuard의 개인 제출 테스트를 기간 2 + DART 3 + 진단 1 = 총 6개로 정리했다. 진단 테스트 내부의 2개 subTest는 별도 테스트 2개로 세지 않는다.
- [Harbinger 역할 기록](https://github.com/sokldjs554/harbinger/blob/main/docs/submission-evidence-20261026.md)에는 본인의 GitHub Secret·네이버 SMTP 설정과 실제 메일 수신 확인이 명시되어 있다. 전체 AWS 배포 명령을 직접 수행했다는 뜻으로 확대하지 않는다.
- 이번 후속 병합·공개 화면 검사·지원 문서 작성은 Codex가 수행했다. 본인의 새 개발·운영 실적으로 표현하지 않는다.

## 추천 결론

**새 프로젝트나 새 데모를 만들 필요는 없다. QuarterGuard를 대표로, Preflight의 LLM 운영 구조와 Harbinger의 AWS 운영 근거를 조합한다.** TableTrace는 오픈소스 LLM 활용 질문에 대비한 추가 사례로 둔다. 프로젝트 수를 늘리기보다 실제 수행 범위와 본인 역할을 명확히 하는 것이 우선이다.

| 순위 | 프로젝트 | 추천 이유 | 핵심 한계 |
|---|---|---|---|
| 1 | [QuarterGuard](https://github.com/sokldjs554/quarterguard) | 공시 데이터 추출·검색·문맥 비교·계산·LLM 설명 검증을 업무 흐름으로 제시 가능. 직접 제출 코드·회귀 실행 기록 존재 | 등록 문서/지원 파서 범위. 공개 작업지는 규칙 기반. Render 배포를 3대 클라우드 경험으로 쓰지 않음 |
| 2 | [Preflight](https://github.com/sokldjs554/toss-ads-ai-project) | 실제 RAG·function calling·비용 예약·계정별 저장·실패 처리와 본인 LIVE 사용 기록 | 광고 도메인·합성 데이터·단기 1인 파일럿. 무료 화면은 모델 대역 |
| 3 | [Harbinger](https://github.com/sokldjs554/harbinger) | AWS EC2에서 ML API 배포·복구·인증서 갱신 시험·장애/복구 알림 근거. 클라우드 요건을 직접 보완 | 생성형 AI 프로젝트 아님. 합성 데이터. 이번 환경에서 현재 AWS TLS 접속 검증 실패 |
| 4 | [TableTrace](https://github.com/sokldjs554/tabletrace) | 오픈소스 LLM이 표의 연산·근거를 제안하고 계산·검증기로 연결. 학습과 평가 원결과 존재 | 연구 범위가 넓음. Pages는 저장 결과. Kaggle/Colab 학습을 GCP AI 서비스 운영으로 쓰지 않음 |
| 5 | [ko-search-clinic](https://github.com/sokldjs554/ko-search-clinic) | 검색 진단·RAG·LLM 수정안·회귀 게이트·실패 분석 | 서비스 PR #2와 연구 PR #3 미병합. main에 모든 기능이 있는 것처럼 설명하면 안 됨 |

추가 후보도 코드까지 확인했다. [llm-data-analyst-agent](https://github.com/sokldjs554/llm-data-analyst-agent)는 Claude의 도구 호출로 Titanic 분석·ML 예측을 연결해 업무 문구와 잘 맞지만, 배포·운영·평가 근거의 폭은 대표 후보보다 작다. [aiops-sentinel](https://github.com/sokldjs554/aiops-sentinel)는 합성 로그 분석과 선택적 LLM 요약 경로가 있으나 API 키 부재/실패 시 규칙 응답을 쓰므로 챗봇 실행만으로 실제 LLM 사용을 입증할 수 없다. 전체 GitHub 저장소에 대한 전수 코드 감사는 아니다.

## 공고 원문 요약

공고상 정규직, 서울 여의도, IT 부서, 학사 이상, 신입 또는 경력 7년 이하이다. 마감 표시값은 **2026-11-19 16:00**이며 조기 마감 가능 문구가 있다. 원문은 시간대를 별도 표기하지 않는다.

| 구분 | 공고 내용의 요지 |
|---|---|
| 담당 업무 1 | 상용·오픈소스 LLM을 활용한 데이터 분석·처리 프로그램 개발 |
| 담당 업무 2 | AI 로직 설계와 시스템 구축 |
| 담당 업무 3 | 테스트·배포·운영을 포함하는 애플리케이션 수명주기 관리 |
| 담당 업무 4 | AI 인프라와 개발 환경 구성 지원 |
| 응시자격 | 생성형 AI 시스템 개발, AWS/GCP/Azure 환경의 AI 서비스 운영, 문제 해결·협업 소통, 해외여행 결격 사유 없음, Deloitte Global Talent Standards 부합 |
| 우대사항 | AI·데이터·클라우드 관련 자격증, Secure Coding 경험 |

OpenAI·Gemini는 공고의 예시다. 확인되지 않은 Gemini 사용 경험을 추가할 필요는 없다. 학력·경력·여행 가능 여부·자격증은 저장소로 확인할 수 없고 별도 증빙이 필요하다. Global Talent Standards에 부합한다고 기술 스택만으로 판정하지 않는다.

## 공고 항목별 코드·결과 대조

| 공고 항목 | 연결 프로젝트·코드 | 실제 확인한 결과 | 지원서에서의 범위 |
|---|---|---|---|
| 생성형 AI 시스템 개발 | QuarterGuard [bounded_planner.py](../quarterguard/bounded_planner.py), [public_providers.py](../quarterguard/public_providers.py); Preflight [live_pilot.py](https://github.com/sokldjs554/toss-ads-ai-project/blob/b5793cc83dfbb5272bd3245a6058b8985dc49865/agents/live_pilot.py) | QG의 실제 모델 도구 선택 개발 4과제 4/4, 실제 설명 생성·구조 검사 기록. Preflight 본인 6요청·10 모델 호출 기록 | 도구 실행·검증·실패 보류까지 설명. 기능 존재와 본인 독립 구현은 별도 |
| LLM 데이터 분석·처리 | QG [ingest.py](../quarterguard/ingest.py), [search.py](../quarterguard/search.py), [core.py](../quarterguard/core.py), [explanation_guards.py](../quarterguard/explanation_guards.py) | 삼성 2024년 정본 192개, 2025년 4표 추출과 선언된 KRW 64셀 검증. 비교 조건 부적합 시 계산 보류 | PDF 추출·조건 처리·Decimal 계산은 코드, LLM은 제한형 도구 선택과 설명. 전부 LLM이 처리한다고 쓰지 않음 |
| 오픈소스 LLM 활용 | TableTrace [모델 코드](https://github.com/sokldjs554/tabletrace/tree/437362e4dd360c042c7e808f7f51a34fa2f9d4fb/src/tabletrace/model), [검증기](https://github.com/sokldjs554/tabletrace/blob/437362e4dd360c042c7e808f7f51a34fa2f9d4fb/src/tabletrace/verify/verifier.py), [학습 루프](https://github.com/sokldjs554/tabletrace/blob/437362e4dd360c042c7e808f7f51a34fa2f9d4fb/src/tabletrace/training/lm_loop.py) | 저장된 EXAONE 평가 699문항 verified EM 0.8426. 근거 셀·계산·보류를 별도 평가 | 이번에 GPU 학습/추론을 재실행하지 않았음. 지표는 특정 저장 실험 조건의 값 |
| 로직 설계·시스템 구축 | QG의 [MCP 서버](../quarterguard/mcp_server.py)·[실행기](../quarterguard/orchestrator.py); Preflight [gateway](https://github.com/sokldjs554/toss-ads-ai-project/blob/b5793cc83dfbb5272bd3245a6058b8985dc49865/llm/live_pilot_gateway.py)·[store](https://github.com/sokldjs554/toss-ads-ai-project/blob/b5793cc83dfbb5272bd3245a6058b8985dc49865/ops/live_pilot_store.py) | 규칙·모델·데이터·저장 경계와 실제 호출 기록이 코드로 분리됨 | 모델 호출을 연결한 뒤 오류·비용·권한을 제어한 설계 사례 |
| 테스트·배포·운영 | QG [test.yml](../.github/workflows/test.yml); Preflight [CI](https://github.com/sokldjs554/toss-ads-ai-project/blob/b5793cc83dfbb5272bd3245a6058b8985dc49865/.github/workflows/ci.yml) | 현재 조사 SHA의 CI 성공 확인. 이번 실행 결과는 아래 별도 로그. 과거 사용자 재접속·저장 보존 기록 | CI 성공, 과거 배포 성공, 지금 접속 가능은 서로 다른 사실 |
| AWS AI 서비스 운영 | Harbinger [EC2 배포 코드](https://github.com/sokldjs554/harbinger/blob/7daa95603d7dc7235135933b8ff18113c8133128/deploy/aws/ec2/deploy.py), [배포 원결과](https://github.com/sokldjs554/harbinger/blob/7daa95603d7dc7235135933b8ff18113c8133128/docs/verification/closeout-20261027/release/aws/deployment-result.json) | ap-southeast-2 단일 EC2, 재부팅 복구·갱신 시험·모델 버전 확인·임시 SSH 종료 기록 | 개인 ML 서비스 AWS 운영 근거. 생성형 AI의 AWS 운영이나 상용 고객 SLA로 확대하지 않음 |
| 인프라·개발 환경 | Harbinger Docker/Nginx/EC2 배포, Preflight 격리 PostgreSQL·Chromium CI, QG Python/MCP 개발 환경 | 설정뿐 아니라 CI와 일부 실제 배포 결과가 있음 | GCP 설정 파일만으로 GCP 운영을 주장하지 않음. Azure 근거 미확인 |
| Secure Coding | Preflight 토큰 해시·계정별 쿼리·매개변수 SQL·비용 예약; QG 입력 모델·도구 허용 목록·출력 검증; Harbinger SSH 신원·소유 태그·IMDSv2 | 관련 코드와 회귀 검사가 존재 | 보안 요구를 고려한 구현 사례. 외부 보안 심사·인증·침투시험 완료를 뜻하지 않음 |
| 문제 해결·협업 소통 | QG 진단 설명 오류의 코드 제출과 실행 기록, Preflight 사용 판단 저장·피드백, Harbinger 운영자 알림 확인 | 무엇이 문제이고 어떤 증거로 판단했는지 남아 있음 | 사람 사용·피드백은 협업 정황. 동료와 공동 개발한 업무 경험으로 확대하지 않음 |
| 자격증·개인 조건 | 코드로 확인 불가 | AI/데이터/클라우드 자격증 증빙 이번 조사에서 미확인 | 보유 여부·정확한 자격명·학력·경력을 지원 전 확인 |

## 수치와 실제 실행을 읽는 법

QuarterGuard의 [2026-11-12 모델 실행](model-completion-live-results-20261112.md)은 GPT-4.1 mini **36호출 = 설명 20 + 도구 선택 16**이다. 도구 선택은 4과제를 완료했지만 회복 경로가 실제로 발동한 사례는 없었다. 구조·근거 ID 20/20 일치는 문장 전체 정확도 100%가 아니다. 이후 [N 배치 20건의 검사 보완](prose-binding-followup-20261113.md)은 같은 응답을 재검사한 결과이며 새로운 모델 생성 성능으로 해석하지 않는다.

Preflight의 [현재 범위 문서](https://github.com/sokldjs554/toss-ads-ai-project/blob/b5793cc83dfbb5272bd3245a6058b8985dc49865/docs/CURRENT_STATUS.md)는 본인 1명·LIVE 요청 6건·실제 API 10회·판단 6건 저장을 구분한다. 무료 데모·과거 재생·새 실제 호출도 별개다. RAG와 도구 호출은 한 서비스의 두 활용 방식이다.

TableTrace의 [원결과](https://github.com/sokldjs554/tabletrace/blob/437362e4dd360c042c7e808f7f51a34fa2f9d4fb/experiments/eval/exaone_full_vllm_ko_test/metrics.json)는 verified EM 0.8426, 699문항, 근거 셀 정확 일치 0.8552를 기록한다. [현재 README](https://github.com/sokldjs554/tabletrace/blob/437362e4dd360c042c7e808f7f51a34fa2f9d4fb/README.md)는 반복 학습 수치·개선되지 않은 결과·소유자 루프 실행을 구분한다. 이번에는 계산·검증기 CPU 검사만 수행했다.

ko-search-clinic의 [PR #2](https://github.com/sokldjs554/ko-search-clinic/pull/2)는 Draft·미병합이고 `493935f`의 서비스 코드와 실제 24응답 기록을 확인했다. [PR #3](https://github.com/sokldjs554/ko-search-clinic/pull/3) 역시 미병합이다. `a7df146`의 [개발 비교](https://github.com/sokldjs554/ko-search-clinic/blob/a7df146d04948a00743f6374e4702379122a9d78/docs/research/v5/GENERATED_COMPARISON_RESULT_20261102.md)는 GPT/Pair 0.611720, RulesPlus 0.859490으로 우위를 입증하지 못했다. 암호화된 상세 원응답은 이번에 복호화하지 않았으며 공개 집계의 완전한 재현으로 주장하지 않는다.

## 직접 기여와 도구 역할

아래는 **저장소에 기록된 역할**이며 커밋 작성자만으로 저자를 추론하지 않았다. 파일 제출 사실만으로 AI 도움 없는 독립 작성을 입증할 수 없다.

| 프로젝트 | 본인 수행으로 기록된 범위 | Codex·도구 역할/추가 확인 |
|---|---|---|
| QuarterGuard | 기간 진단 설명 코드 수정·제출, 기간·DART·진단 테스트 보강, macOS 전체 회귀 실행 보고, 사용·검수 피드백 | [코드 제출 기록](code-review-kit/04-period-diagnostic-author-20261110.md)에 AI의 통합·별도 재검사 명시. 제출 당시 환경·날짜·도움 범위 일부 누락. 전체 제품 독립 구현으로 확대 금지 |
| Preflight | 범위·우선순위 결정, 결과 검수, 선호 응답 수집, LIVE 입력·판단 저장·재접속, 경쟁 서비스 사용 | AI 개발 도구가 코드·테스트·배포·분석·문서 지원. 본인이 직접 작성한 개별 제품 코드의 추가 증빙 필요 |
| Harbinger | 제품·기술 범위 결정, 피드백·결과 확인, 장애/복구 메일 수신 확인 | Codex의 구현·실험 세부 기준·코드·검증·문서 지원 기록. Secret·SMTP 직접 설정 기록은 확인. EC2 배포/복구 명령의 직접 수행 범위는 확인 필요 |
| TableTrace | 저장소에는 소유자 제출 모듈·평가 문항·Kaggle/Colab 실행이 기록됨 | AI 지원 범위와 코드별 작성 과정을 별도 확인해야 함. 이번 조사만으로 README의 모든 저자 표기를 독립 인증하지 않음 |
| 이번 보완 | 사용자가 목표·우선 프로젝트·사실성 기준을 지정 | 조사·선정 판단·문서 작성·테스트 실행·PR 준비는 Codex가 수행. 사용자 본인의 새 개발 실적으로 쓰지 않음 |

## 지원서·면접용 핵심 설명

다음 문장은 확인된 프로젝트 흐름과 기록된 역할 범위에 맞춘 예시다. 실제 본인 역할을 묻는 질문에는 아래의 구체 사례와 도움 범위를 함께 말한다.

**대표 프로젝트 설명:** “QuarterGuard는 기업 공시의 수치와 출처를 연결하고 기간·연결 범위·통화가 맞을 때만 비교하는 도구입니다. 계산은 검증 코드가 수행하고 LLM의 설명은 구조·근거·문장 문맥으로 나누어 검사했습니다. 공개 작업지는 규칙 기반이며, 모델이 도구를 선택하는 기능은 별도의 제한된 4과제로 평가했습니다.”

**직접 기여 설명:** “저는 기간 비교에서 실제로 실행된 조건과 별도 재계산 진단을 혼동하지 않도록 설명 코드를 수정·제출하고, 기간과 DART 관련 테스트를 보강하고 회귀 검사를 실행했습니다. 제품 전체 구현·통합·배포와 자동 검증에는 AI 개발 도구를 활용했습니다.” 작성 당시 도움의 구체 범위는 본인이 추가 확인해야 한다.

**운영 설명:** “Preflight에서는 실제 모델을 이용해 광고를 검토하고 판단과 사유를 저장한 뒤 재접속을 확인했습니다. 코드에는 호출 전 비용 예약과 계정별 기록 분리가 있습니다. AWS 경험은 Harbinger의 EC2 모델 API·복구·알림 기록으로 별도 설명하겠습니다.” 직접 수행한 인프라 작업은 기록된 범위만 덧붙인다.

| 면접 질문 | 답변에서 제시할 내용 |
|---|---|
| 왜 LLM이 계산하지 않는가? | 금융 조건과 Decimal 계산은 결정적인 코드로 검증하고, LLM은 도구 선택·설명에 제한적으로 활용 |
| 구조가 맞으면 정확한 응답인가? | 아니다. 같은 금액·근거 ID라도 기간·범위·진단 설명이 틀릴 수 있어 별도 문장 검사가 필요 |
| 더 복잡한 검색 모델을 왜 적용하지 않았는가? | 동일 후보 top 20의 실제 리랭커 비교에서 별도 집합 R@1 개선 없이 지연 증가. 기본 검색에 미채택 |
| AWS에서 무엇을 운영했는가? | Harbinger의 ML 모델 API와 단일 EC2·Nginx·Docker 구성, 배포/복구/알림 근거. 생성형 AI AWS 운영과 구분 |
| 직접 한 일은 무엇인가? | 파일 제출·테스트·사용 기록 단위로 답하고 Codex의 구현·배포 역할을 분리 |

## 남은 보완 우선순위

1. **현재 공개 접속 확인:** 후속 검사에서 두 Render 서비스의 화면 동작과 배포 빌드를 확인했다. Harbinger AWS 인증서 이름 오류는 남아 있으며 저장 예제를 제공한다.
2. **AWS 직접 수행 범위:** 서비스가 AWS에서 실행됐다는 증거는 있지만 본인이 설정·배포·복구를 직접 수행한 작업은 별도로 정리해야 한다. 본인의 GitHub Secret·SMTP 설정과 수신 확인은 추가로 확인했다. EC2 배포 명령·복구 명령의 직접 수행 여부는 별도다.
3. **기업 운영 경험의 차이:** 실제 고객 데이터, 조직 IAM/SSO, 장기 SLA, 장애 대응 당직, 감사·보안 인증 근거는 부족하다. 관련 코드의 존재로 대체하지 않는다.
4. **자격증·협업:** 관련 자격증 증빙과 실제 사람과의 개발 협업 역할·방법·결과를 확인한다. 사용자 피드백이나 AI 협업을 사람 팀 공동 개발로 바꾸지 않는다.
5. **클라우드 구분:** Render는 별도, AWS는 Harbinger, GCP는 설정 또는 학습 환경 수준, Azure는 미확인으로 유지한다.
6. **Preflight 테스트 재현성:** 이번 전체 검사에서 4,425개는 통과했지만 68개 건너뜀·2개 실패·10개 오류가 남았다. 브라우저/격리 DB 환경 준비와 Streamlit 긴 입력 안내의 테스트 기대를 구분해 정리했다. 이전 성공 CI 환경을 근거로 Ubuntu 24.04·Streamlit 1.66.1을 고정한 후 핵심·대화 UI 187개가 통과했다. 전체 CI 결과는 별도 실행 링크에서 확인하며 부분 검사를 전체 통과로 표현하지 않는다.

## 이번 수정·검증과 최종 링크

QuarterGuard의 처음 보는 사람용 3분 안내·LLM/규칙 경로·재현 명령과 이 공고 대조표를 추가했다. Preflight에는 같은 목적의 안내와 개발 의존성·격리 DB·Chromium 테스트 절차를 보완했다. Harbinger에는 AWS 실제 실행과 GCP 설정 파일, 현재 접속 상태를 구분하는 안내를 추가했다. 새 PR CI에서 Preflight·Harbinger의 Playwright가 Ubuntu 26.04를 지원하지 않아 브라우저 테스트 작업을 Ubuntu 24.04로 고정했고, Preflight는 이전 성공 버전 Streamlit 1.66.1로 고정했다. 제품 코드·정본·정책·모델·기존 평가 수치는 변경하지 않았다.

[이번 검사 명령·수치·원본 로그·배포 상태](verification/deloitte-20261117/README.md)에 전체 결과를 정리했다. 과거 CI와 이번 로컬 검사를 합산하지 않는다. 새 유료 LLM·DART 호출, GPU 학습, EC2 재배포는 수행하지 않았다.

| 결과물 | 링크 | 이번 확인의 범위 |
|---|---|---|
| QuarterGuard | [데모](https://quarterguard.onrender.com/#work) · [저장소](https://github.com/sokldjs554/quarterguard) | 후속 공개 화면 7d37947 확인. 실제 MCP 18회 실행, 정상 계산·기간 불일치 보류 동작 확인 |
| Preflight | [무료 데모](https://sokldjs554.github.io/toss-ads-ai-project/app/) · [LIVE](https://preflight-toss-ads.onrender.com/?view=LIVE%20검토) · [저장소](https://github.com/sokldjs554/toss-ads-ai-project) | 무료 페이지·LIVE health 응답. Render 634fb6e 무료 예시 실행 확인. 로그인·새 모델 호출은 이번에 미실행 |
| Harbinger | [AWS 진입](https://sokldjs554.github.io/harbinger/live.html) · [저장 예제](https://sokldjs554.github.io/harbinger/) · [저장소](https://github.com/sokldjs554/harbinger) | 진입 페이지 HTTP 200, 연결되는 AWS IP의 TLS 검증 실패. 과거 AWS 배포 성공 기록 확인 |
| TableTrace | [저장 결과 데모](https://sokldjs554.github.io/tabletrace/) · [저장소](https://github.com/sokldjs554/tabletrace) | HTTP 200·현재 SHA Pages/CI 성공. 공개 백엔드 추론 아님 |
| ko-search-clinic | [main](https://github.com/sokldjs554/ko-search-clinic) · [RAG PR #2](https://github.com/sokldjs554/ko-search-clinic/pull/2) · [연구 PR #3](https://github.com/sokldjs554/ko-search-clinic/pull/3) | 서비스/연구 브랜치 미병합. 공개 운영 데모는 이번 조사에서 확인하지 못함 |

변경은 PR [QuarterGuard #90](https://github.com/sokldjs554/quarterguard/pull/90), [Preflight #7](https://github.com/sokldjs554/toss-ads-ai-project/pull/7), [Harbinger #23](https://github.com/sokldjs554/harbinger/pull/23)으로 main에 병합했다. QuarterGuard·Preflight의 자동 배포와 실제 공개 화면을 확인했다. Harbinger AWS 재배포는 수행하지 않았다. 최초 실패와 후속 수정 검사는 각 PR의 검증 문서에서 함께 확인할 수 있다.
