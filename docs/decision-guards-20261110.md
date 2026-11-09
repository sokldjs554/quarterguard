# 설명의 보류 사유·근거 ID 방어 보완

[b의 새 응답 검수](validation-kit/session-b-llm-followup-20261110.md)에서 남은 `scope-mismatch`의 모호한 설명과 `normal-yoy` 근거 ID 오타를 대상으로 코드·표시·회귀를 보완했다. **추가 유료 호출0회, 새 모델 응답0개, 이번 변경 후 b 재검수 미수행**이다. 과거 참7·모호1 및 구조필드7/8 결과를 수정하지 않는다.

## 무엇이 바뀌었는가

- **보류 이유:** 설명 지침에 `issues`와 도구의 `decision_basis`에 있는 사유만 사용하도록 명시했다. `SCOPE_MISMATCH`만 있을 때는 연결·별도 차이만 설명하며, 인접한 두3개월 분기 자체를 보류 이유로 덧붙이지 않도록 안내한다. 기간·범위가 모두 문제이면 두 사유를 모두 유지하고, 모르는 코드는 확인 필요로 남긴다.
- **화면:** 모델의 원문을 수정하지 않고 별도 ‘도구가 판정한 보류 사유’를 표시한다. 범위만 문제일 때는 도구가 기간 불일치로 판정하지 않았다는 안내를 덧붙인다. 이것은 도구의 문제 목록 설명이며 자유문장 전체 의미 검증이 아니다.
- **인용 ID:** 요청별 JSON Schema에서 근거 ID를 해당 도구 결과의 ID 목록으로 제한하고 배열 길이도 고정했다. 스키마는 순서와 중복까지 보장하지 않으므로 기존 서버의 정확한 배열 대조를 유지한다. 빈 근거는 길이0이다. 정본과 다른 ID를 자동으로 고치거나 검증된 결과로 승격하지 않는다.
- **실패:** 기존에도 틀린 ID를 거부했으며 이번에는 안전한 검사 항목별 참/거짓과 명시적 오류 사유를 남긴다. 거부된 모델 문장·출처 안내는 반환하지 않는다. 프런트엔드도 성공 상태에서만 설명을 렌더링한다. 실패 요청은 시도 횟수에 포함되고 성공 캐시에 저장되지 않으며 자동 재시도하지 않는다.
- **캐시:** 기존 검증 버전 해시가 수정한 프롬프트·제공자 코드를 포함하므로 이전 성공 응답을 새 정책의 결과로 재사용하지 않는다.

코드: [설명 문맥·지침](../quarterguard/explanation_context.py), [요청 스키마·서버 거부](../quarterguard/public_providers.py), [별도 사유 표시](../web/explanation-context.js), [실패 시 표시 제한](../web/providers.js).

## 검증 결과와 구분

|대상|결과|실행 성격|
|---|---|---|
|새 방어 테스트|수정 전5개 실패 → 최종7개 통과|최종2개는 ID 순서·중복 및 역사 스냅샷 무결성 보강|
|전체 Python|191개 통과|AI 실행. 사용자의 직접 실행으로 기록하지 않음|
|Node|8개 통과|HTML 이스케이프·사유 표시 등|
|브라우저|390×844, 1440×1000에서8개 통과|로컬 HTTP, 응답을 가로챈 재생. 실제 휴대폰·공개 HTTPS·새 LLM 실호출 아님|
|MCP|8개 사례 모두 통과|실제 MCP 실행. 모델 호출0회. 원문 PDF 신규 파싱 평가 아님|
|이전 전후 평가 재계산|사례별 감사와 집계 동일|동결된 과거 정책 사용. 새 프롬프트 성능으로 해석하지 않음|

[수정 전 실패](../artifacts/decision-guards-20261110/tests-before.txt), [전체 테스트](../artifacts/decision-guards-20261110/python-tests.txt), [브라우저 결과](../artifacts/decision-guards-20261110/browser.json), [실제 MCP 결과](../artifacts/decision-guards-20261110/mcp-evaluation.json), [MCP trace](../artifacts/decision-guards-20261110/mcp-runs.json). MCP 보고서의 retrieval 필드는 기존 기록을 포함한 것이며 이번에 검색 성능을 새 측정한 것으로 사용하지 않는다.

[회귀 테스트](../tests/test_explanation_decision_guards.py)는 실제 실패 JSON을 모의 HTTP 응답으로 재생한다. 제공자 메타데이터와 고정 대상 연결은 테스트용 합성이다. 이를 GPT-4.1-mini 실호출이나 오류율 감소로 쓰지 않는다. 스키마 제한의 실제 제공자 수용과 새 자유문장의 효과는 아직 실호출로 검증하지 않았다. 공급자 오류 시 기존 실패 처리로 보류한다.

## 과거 평가 보존과 재현

과거 평가 하네스·freeze·응답·사람 기록을 덮어쓰지 않았다. 그 평가에 사용한 변경 전 `explanation_context.py`와 `public_providers.py`를 [스냅샷](../data/llm-followup-20261110/source-snapshot/)으로 보존했다. [오프라인 로더](../quarterguard/frozen_followup.py)는 기존 freeze의 SHA256과 스냅샷을 대조하며 나머지 소스는 원래 검사를 유지한다. 원래 유료 하네스는 현재 코드가 바뀌면 소스 불일치로 멈추므로 새 정책으로 과거 승인 배치를 다시 실행할 수 없다. 기존8회 승인은 이미 소진됐다.

```bash
python -m unittest discover -s tests -p test_explanation_decision_guards.py -v
node --test tests/*.mjs
python scripts/compare_explanation_followup.py \
  --followup artifacts/llm-followup-20261110/report.json \
  --output /tmp/quarterguard-historical-comparison-new.json
```

비교 출력 경로는 기존 파일이 없는 경로를 사용한다. 브라우저 재현은 별도 터미널에서 `python -m uvicorn quarterguard.api:app --host 127.0.0.1 --port 8789`를 실행하고 `PYTHONPATH=. python scripts/browser_decision_guards_check.py`를 실행한다. 결과는 새 `work/decision-guards-browser` 디렉터리에 저장되며 기존 디렉터리가 있으면 덮어쓰지 않는다. `DECISION_GUARD_QA_DIR`로 새 저장 위치를 지정할 수 있다. 외부 제공자 요청은 모두 가로챈다.

## 남은 단계

코드 보완과 오프라인 회귀는 완료했다. **새 생성에서 모호함·ID 오류가 실제로 줄었는지는 미확인**이다. 새 실호출은 별도 모델·호출 수·입출력 상한·비용 승인 후 수행해야 하며, 새 응답에 대한 b의 재확인도 별도로 받아야 한다. 공개 설명 제공자의 활성화·유료 승인·영속 원장 조건은 변경하지 않았다.

지원서에는 “사람 검수로 남은 범위 설명의 모호함과 인용 ID 오류를 확인하고, 도구 사유 안내·요청 스키마·정확 대조·실패 표시 회귀를 보강했다”까지 사용할 수 있다. “모델의 두 오류를 해결했다”거나 “정확도가 향상됐다”고 쓰지 않는다.
