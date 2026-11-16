# 2026-11-17 지원 근거 재검증

실행 주체: Codex. Linux·Python 3.12.14, 저장소별 가상환경을 사용했다. 기본 런타임 패키지를 공유하는 가상환경이므로 완전히 빈 환경의 의존성 재현으로 주장하지 않는다. [조사 SHA](revisions.json) · [조회한 GitHub 실행 상태](github-runs.json) · [파일 해시](sha256.json).

## QuarterGuard: 이번 실행

기준 `635a0cba04b22634ed8dc9d923d228d8541ec5bc`. `requirements.txt`를 설치한 환경에서 다음을 실행했다.

| 명령·검사 | 결과 | 로그 |
|---|---|---|
| `python -m unittest discover -s tests -v` | 406개 실행, 405개 통과·1개 건너뜀, 실패/오류 0; 55.028초 | [전체 로그](quarterguard-unittest.log) |
| `node --test tests/*.mjs` | 39개 통과, 실패 0 | [Node](quarterguard-node.log) |
| `python scripts/check_artifacts.py` | corpus/gold 해시, 8사례, 정본 인용 일관성 통과 | [산출물 검사](quarterguard-artifacts.log) |
| `python -m quarterguard.final_evaluation --dry-run --output <새 폴더>` | 4과제 모두 기준 결과와 일치; 준비된 선택 정책의 실제 MCP 16호출; 새 유료 모델 0호출 | [전체 결과](quarterguard-mcp-dry-run.json) |
| FastAPI TestClient로 정상·기간·범위 비교 및 `/api/worksheet/run` 호출 | 정상 6.7916%, 불일치 계산 보류, 실제 stdio MCP 18호출·모델 0호출 | [API 검사](quarterguard-api-checks.json) |
| `scripts/browser_finance_workspace.py` | Chromium 실행 단계에서 환경의 `socket() ... Operation not permitted`로 중단 | [브라우저 실패 원본](quarterguard-browser.log) |

건너뛴 항목은 공식 PDF 캐시가 필요한 현대차 파서 검사다. 브라우저 조작의 새 성공이나 실제 사용자 검수를 주장하지 않는다. API 검사는 프로세스 내부 TestClient와 실제 MCP 자식 프로세스이고 공개 서버 접속 검사가 아니다. 이번 문서 변경은 제품 코드와 데이터를 바꾸지 않아 위 검사 이후 전체 회귀를 반복하지 않았다.

## 다른 프로젝트의 이번 부분 검사

| 프로젝트 | 범위 | 결과 |
|---|---|---|
| Harbinger | `tests/test_aws_deploy.py`, `pytest -o addopts='' -q` | [34개 통과](harbinger-aws-tests-explicit.log). 모의 AWS 경계 검사이며 실제 새 배포 아님 |
| TableTrace | `test_numbers_calculator.py`, `test_program_verifier.py`, `test_verifier_repair_option.py` | [72개 통과](tabletrace-focused-tests.log). CPU 계산·검증 검사, GPU 학습/추론 재실행 아님 |
| ko-search-clinic main | gate·loop·rag·REST·MCP 5개 모듈 | 처음 기본 환경의 MCP 1.29.0에서 [77통과·3실패](clinic-focused-tests.log). 선언된 `mcp>=2.0`에 맞춰 2.3.0을 설치한 뒤 [80개 통과](clinic-focused-tests-declared-mcp.log). 제품 코드 수정 없음 |
| llm-data-analyst-agent | `PYTHONPATH=src python -m pytest -q` | [38개 검사 통과, 종료 코드 0](analyst-tests.log). 실제 Claude 호출은 재실행하지 않음 |
| aiops-sentinel | `tests/test_detector.py` | [4개 통과](aiops-tests.log). LLM/API 검사는 아님. 최초에 존재하지 않는 API 검사 경로를 지정한 실행은 수집되지 않아 결과에 포함하지 않음 |
| Preflight | 전체·핵심 부분 검사 | [Preflight 자체 재검증 문서](https://github.com/sokldjs554/toss-ads-ai-project/blob/docs/deloitte-it-ai-evidence-20261117/docs/verification/deloitte-20261117/README.md)에 실패·건너뜀 포함 기록 |

ko-search-clinic의 초기 실패는 MCP 생성자 `on_list_tools` 인자 차이였으며, 선언된 선택 의존성을 설치한 뒤 같은 80검사로 확인했다. main 결과를 미병합 서비스·연구 브랜치의 전체 검증으로 확대하지 않는다.

## 공개 주소와 배포 상태

[HTTP 기록](public-http.json)은 TLS 검증을 유지한 curl 조회다. 조회 시각은 각 기록의 UTC이며 한국시간 확인일은 2026-11-17이다.

- QuarterGuard `/health`, `/`: 각각 25초 내 응답 없음. 현재 서버 커밋·제공자 활성 상태 미확인.
- Preflight 무료 Pages: HTTP 200. Render `/_stcore/health`: 25초 내 응답 없음. LIVE 로그인·새 호출은 확인하지 않음.
- Harbinger Pages 진입: HTTP 200, AWS IP로 이동하는 안내. AWS `/health`: TLS 이름 검증 실패. 서버 중지/인증서 만료 여부는 단정하지 않음.
- TableTrace Pages: HTTP 200. 저장된 결과 모드이며 공개 모델 추론 서버 확인을 뜻하지 않음.

Render 관리 연결에는 선택된 workspace가 없어 서비스 상태 조회를 완료하지 못했다. 사용자의 workspace를 임의로 고르거나 서비스 설정을 변경하지 않았다. 웹 조회 경로에서도 두 Render 서비스를 확인하지 못했다. 과거 배포 원결과와 현재 GitHub CI 성공만으로 지금 정상 운영이라고 쓰지 않는다.

QG 현재 조사 SHA의 [CI](https://github.com/sokldjs554/quarterguard/actions/runs/43620347903), Preflight [CI](https://github.com/sokldjs554/toss-ads-ai-project/actions/runs/40076009819)·[Pages](https://github.com/sokldjs554/toss-ads-ai-project/actions/runs/40076009803), Harbinger [CI](https://github.com/sokldjs554/harbinger/actions/runs/40435358083), TableTrace [CI](https://github.com/sokldjs554/tabletrace/actions/runs/43904238719)·[Pages](https://github.com/sokldjs554/tabletrace/actions/runs/43904238732)는 조회 시 성공 상태였다. 이는 이번 문서 변경 전의 기준 SHA 기록이다.

## 변경 범위

README에서 3분 검토 안내·공고 대조표로 바로 이동하도록 연결했다. 새 문서에는 실제 LLM 경로, 규칙 경로, 데이터 준비/검색/계산, 실행 방법, 직접 기여의 근거와 한계를 정리했다. 기존 실행 수치·정본·모델 응답·사람 판정은 수정하지 않았다. 새 유료 API 호출·운영 DB 접근·인프라 변경은 없다.
