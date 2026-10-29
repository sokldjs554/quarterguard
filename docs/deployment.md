# 공개 데모 배포

- URL: https://quarterguard.onrender.com
- GitHub: https://github.com/sokldjs554/quarterguard
- Render: 사용자 지정 `my2 workspace`, Singapore, free compute plan, 단일 Python 웹 서비스.
- build: `pip install -r requirements.txt`
- start: `python -m uvicorn quarterguard.api:app --host 0.0.0.0 --port $PORT`
- Python: `.python-version`의 3.12.8. 환경 비밀키 불필요.
- 배포 branch: main. commit 기반 자동 배포. `/health`의 `commit`이 실제 Render source SHA다.
- 현재 생성 도구의 기본 TCP health check를 사용한다. `/health`는 외부 확인용으로 별도 검증한다.
- 원문 PDF, 모델 가중치, 키, 개인 정보는 배포하지 않는다. 읽기 전용 기본 코퍼스와 준비 결과를 포함한다.
- 동시 실시간 실행은 1개로 제한하고 초과 요청은 HTTP 429를 반환한다. 첫 공개 측정에서 약 14.5초가 걸려 기존 사례의 25초 실행 제한과 무료 CPU 한도를 고려했다. v1.1 작업지 재검증은 18회 도구 호출에 45초 제한을 적용하며 같은 동시 실행 제한을 공유한다.
- 최초 PR: https://github.com/sokldjs554/quarterguard/pull/1

## 공개 버전 대조

```bash
git rev-parse origin/main
curl -fsS https://quarterguard.onrender.com/health
curl -fsS -X POST https://quarterguard.onrender.com/api/run/qoq-revenue
```

`/health.commit`과 Git SHA, `/api/evaluation.corpus_sha256`과 저장소 facts 파일 해시를 비교한다. 실행 결과의 `execution_mode`는 `live_mcp`여야 하며 `protocol`과 tool trace를 확인한다. 준비 재생의 결과를 실시간 실행으로 오인하지 않는다.

무료 서비스는 유휴 15분 후 절전되고 재기동이 느릴 수 있다. 무료 compute여도 워크스페이스의 빌드/네트워크 사용량 한도는 별도다. 총 운영비를 0으로 보장하지 않는다. 본 데모는 운영 금융 시스템이나 고객용 SLA가 없다.
