# 설명 표현 방어의 오프라인 검증

- `before-tests.txt`: 제품 수정 전 8테스트 실행, 실패8건(서브테스트 포함).
- `after-targeted-tests.txt`: 첫 구현 후 8테스트 통과. 이후 마침표 경계 사례를 추가했다.
- `percent-boundary-before.txt`: 추가 경계 사례 실패1건. 삭제하지 않는다.
- `python-tests.txt`: 경계 수정 후 전체213테스트 통과.
- `node-tests.txt`: 13테스트 통과.
- `browser.json`: 2화면 크기의16검사 통과. 로컬HTTP·원응답재생·제공자경로 가로채기, 실제 API0회.
- `replay.json`: 기존 v5원응답8개의 동일 입력 재생. 이전 구조검사8/8, 현재 구조+표현검사5/8통과·3/8보류. 새 모델 성능이나 사람 정확도 점수가 아니다.

이 실행은 AI 수행이며 사용자·b의 직접 실행으로 세지 않는다. [설명·한계·재현](../../docs/prose-guards-20261110.md).
