# QuarterGuard: 3분 검토와 실행 근거

공시의 숫자를 분석표로 옮길 때, 숫자가 맞아도 기간·연결 범위·통화가 다르면 잘못된 비교가 됩니다. QuarterGuard는 원문 위치와 비교 조건을 함께 보여 주고, 조건이 맞을 때만 계산합니다. 지원 파서와 등록 자료의 범위 안에서 동작하는 개인 프로젝트입니다.

## 화면에서 확인하는 순서

1. [재무 비교](https://quarterguard.onrender.com/#work)를 열어 삼성전자 연결 매출 A **79,098,731**, B **74,068,302**, 증가율 **6.7916%**를 확인합니다. 단위는 백만 원입니다.
2. B 금액을 눌러 문서·쪽수·기간·행·열과 발행사 PDF 링크를 확인합니다. 출처 정보 창은 PDF 원문 이미지가 아닙니다.
3. 비교 설정에서 B를 상반기 누적으로 바꿉니다. 3개월과 6개월이 달라 **계산 보류**가 되고 증가율이 비워집니다. B를 분기로 복구하면 원래 결과가 돌아옵니다.
4. **비교 검증 → 실행 상세**를 열어 실제 MCP 호출을 확인합니다. 일반 표 계산과 별도 실행입니다. LLM이 선택한 실행 순서로 설명하지 않습니다.

공개 서버가 응답하지 않으면 아래 로컬 실행과 [기존 화면 캡처](../artifacts/readme-current-20261115/)를 사용할 수 있습니다. 캡처는 2026-11-15 기록이며 현재 가용성 증거가 아닙니다.

## LLM은 어디에서 사용하는가

| 경로 | 코드와 실제 역할 | 확인 근거·한계 |
|---|---|---|
| 공개 작업지 | [worksheet.py](../quarterguard/worksheet.py), [orchestrator.py](../quarterguard/orchestrator.py), [mcp_server.py](../quarterguard/mcp_server.py): 코드가 검색·조회·비교 순서를 실행 | 표 계산과 명시적 MCP 재검증. 기본 경로의 모델 호출은 0회 |
| 설명 생성 | [public_providers.py](../quarterguard/public_providers.py), [live_verification.py](../quarterguard/live_verification.py): OpenAI에 도구 결과를 전달하고 구조·출처·문장을 검사 | [실제 20건 생성 기록](model-completion-live-results-20261112.md). 생성 완료·구조 일치를 설명의 의미 정확도로 해석하지 않음 |
| 제한형 도구 선택 | [bounded_planner.py](../quarterguard/bounded_planner.py): 모델이 허용된 검색·조회·비교 도구를 선택 | 같은 기록의 개발 4과제 4/4. 사용자 지정 검색 조건 두 개에 한정. 공개 작업지의 자율 계획 기능 아님 |
| 설명 검증 보완 | [explanation_guards.py](../quarterguard/explanation_guards.py), [prose_bindings.py](../quarterguard/prose_bindings.py) | [동일 N01–N20 응답 재검사](prose-binding-followup-20261113.md): 참으로 기록된 17건 통과, 모호 3건 보류. 새 생성·독립 평가 아님 |

모델은 금액을 자유롭게 계산하는 주체가 아닙니다. [core.py](../quarterguard/core.py)의 문맥 검사와 Decimal 계산이 수치 결과를 결정합니다. 설명에서 값·근거 ID가 맞아도 기간이나 비교 의미가 틀릴 수 있어 문장 검사를 별도로 둡니다.

## 데이터 처리 근거

- [ingest.py](../quarterguard/ingest.py): 지원 PDF의 연도·분기/누적·통화·단위·수치·출처 추출. 임의 PDF 전체를 지원하지 않습니다.
- [search.py](../quarterguard/search.py): 문맥 필터와 검색 후보. 검색 결과를 검증된 답으로 간주하지 않습니다.
- [원문/fixture·최초 실패/수정 후 결과](evaluation-v2.md): 2025년 4개 표 추출과 192개 전체 독립 정답 검수를 구분합니다.
- [검색 비교](ranking-v2.md): 실제 cross encoder가 지연을 늘리면서 별도 집합 R@1을 개선하지 못해 기본 검색에 채택하지 않았습니다.

## 재현 명령

Python 3.12와 Node를 준비합니다. 아래 명령은 저장소 루트에서 실행합니다.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn quarterguard.api:app --host 127.0.0.1 --port 8000
```

별도 터미널에서 같은 가상환경을 활성화한 뒤 검사합니다.

```bash
python -m unittest discover -s tests -v
node --test tests/*.mjs
python scripts/check_artifacts.py
python -m quarterguard.final_evaluation --dry-run --output work/it-ai-review-new
```

마지막 명령은 실제 stdio MCP를 호출하지만 **도구 선택은 준비된 테스트 정책**이고 유료 LLM 호출은 0회입니다. 출력 폴더는 아직 없는 경로를 사용합니다. PDF 캐시가 없는 검사는 건너뛸 수 있습니다. [이번 재검증 결과와 실행 로그](verification/deloitte-20261117/README.md)를 함께 확인합니다.

실제 유료 생성은 위 재현 명령에 포함되지 않습니다. 공개 제공자 경로는 API 설정·승인·지속 장부·호출 한도를 검사하며, 이 문서를 따른다는 이유로 과거 승인이나 한도가 갱신되지 않습니다.

## 본인 기여를 설명할 때

[기간 진단 코드 제출 기록](code-review-kit/04-period-diagnostic-author-20261110.md), [기간·DART 테스트 기록](code-review-kit/README.md)을 먼저 제시합니다. 저장소에는 본인의 코드 제출·테스트 실행과 AI의 통합·별도 검증을 구분한 기록이 있습니다. 해당 코드 작성 당시 도움 범위는 기록되지 않아 독립 구현 여부는 추가 확인이 필요합니다. 전체 제품 구현·배포를 본인 단독 수행으로 확대하지 않습니다.

Render 배포 경험은 AWS·GCP·Azure 운영 경험과 별도로 소개합니다. 이번 변경은 설명과 근거 연결을 보완한 것이며 제품 기능·정본·평가 수치를 바꾸지 않았습니다.
