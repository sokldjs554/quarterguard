# 구현 계획

1. 조사/설계 및 격리 저장소: 공식 자료와 후보 비교, 데이터 사용 범위 고정.
2. 테스트 → 문서 파서/정규화: 실제 PDF 2개, 4개 손익 표, 6개 지표; 본문/표 분리, 8개 열의 문맥 보존, 재현 manifest.
3. 테스트 → Decimal 검증과 검색: fixed-window vs context-cell, 단어/문자 TF-IDF, 선택적 ONNX dense, metadata rerank. 고정 gold 질의는 검색 결과와 독립 작성.
4. 테스트 → 실제 MCP 도구와 오케스트레이터/API: 근거 조회, 비교, 누적 차감; 명시적 실패 분류; prepared/live 구분.
5. 평가·실패 보고: raw cases, 결과 JSON, 환경과 latency, 비용 측정 범위. baseline과 개선 구성 동일 질의 비교.
6. 제품 UI: 실적 검증/근거/실행 기록/평가 화면, 반응형, 오류/없음/로딩. 브라우저 desktop/mobile 반복 검증.
7. 전체 검증과 독립 코드 리뷰, GitHub PR, Render 무료 배포, 최종 SHA 일치 확인 및 보고.

## 인터페이스
data/facts.json → Fact → SearchIndex/Verifier → MCP → orchestrator.run_case → API/UI. artifacts/evaluation.json은 README와 UI가 같은 파일을 사용한다. 공개 raw PDF 금지. 테스트는 unittest 사용.

## Review focus
분기 기간 간 호환성과 누적 기간 동일 시작점, 다른 통화의 무단 변환, 출처 없는 사실, 의도치 않은 최신/임의 사실 선택, API 오류가 성공으로 표시되는 UI.
