# v6 준비 기록 — 실제 모델 호출0회

- `before-tests.txt`: 신규 하네스 도입 전8실패.
- `registry-months-before.txt`: 격리 정본의 months 누락8오류. 이후 Fact.public()로 날짜 기반 개월 수를 포함해 수정.
- `targeted-tests.txt`: 계약8테스트 통과, HTTP는 합성 fixture.
- `python-tests.txt`: 전체221테스트 통과. 실제 로컬 MCP 회귀와 합성 제공자 테스트를 포함하며 새 LLM 호출은 없음.
- `initial-freeze-before-workflow-pin.json`: setup-python 일괄 치환을 발견하기 전 동결본. 승인·실행 대상이 아님. 기존v5 action pin 복구 후 아래 최종 동결본을 생성했다.

실행 대상은 [최종 freeze](../../data/llm-prose-v6-20261110/freeze.json), 원문 재파싱·새 과제는 [new-inputs](../../data/llm-prose-v6-20261110/new-inputs.json)이다. [설계·예산·재현·한계](../../docs/llm-prose-v6-20261110.md).
