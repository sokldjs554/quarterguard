# v6 결과 게시 검증 — 새 모델 호출 없음

- `before-python.txt`, `before-node.txt`: v6 요약 반영 전 실패를 보존.
- `python-tests.txt`: 전체222개 통과.
- `node-tests.txt`: 14개 통과.
- `browser.json`: 로컬HTTP·390/1440화면 크기10검사 통과. 실제 최신 요약 API와 주입한 읽기 실패/복구 검사이며 제공자 호출0회, 물리 모바일·직접 공개HTTPS·새 사람 검수 아님.

실제 유료16회 기록은 별도 `artifacts/llm-prose-v6-20261110/`에 있으며 이 게시 검사를 새 모델 평가로 더하지 않는다. 기존247개 데이터/평가 파일과 실제 실행 원본20파일의 바이트 일치를 확인했다. GitHub CI·Render·공개 커밋 대조는 게시 PR에 기록한다.
