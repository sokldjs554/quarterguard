"""UI regression with intercepted providers only. Never calls an external API."""
import copy
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
URL = os.getenv('DEMO_URL', 'http://127.0.0.1:8005')
checks = []
status = {
    p: {'enabled': p == 'dart',
        'blocked_reasons': [] if p == 'dart' else ['PAID_APPROVAL_REQUIRED', 'DURABLE_LEDGER_REQUIRED'],
        'usage': {'attempts_total': 2, 'attempts_today_utc': 1},
        'limits': {'attempts_total': 200 if p == 'dart' else 20, 'attempts_per_day': 8 if p == 'dart' else 5,
                   'global_cooldown_seconds': 60, 'cache_seconds': 86400},
        'ledger_scope': 'instance_ephemeral_resets_on_restart', 'estimated_cost_ceiling_usd': '0.20'}
    for p in ['dart', 'openai']
}
sample = {
    'provider': 'dart', 'target': 's24q3-CFS', 'status': 'succeeded',
    'execution': 'live_provider_request', 'external_calls_this_request': 1,
    'created_at': '2026-10-29T10:00:00Z', 'served_at': '2026-10-29T11:00:00Z',
    'estimated_cost_usd': '0', 'billed_cost_usd': None,
    'checks': [{'fact_id': 's24q3-CFS-revenue-2024-q-KRW', 'source_field': 'thstrm_amount',
                'expected_krw': '79098731000000', 'dart_krw': '79098731000000', 'passed': True,
                'dart_source': 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20241114000001'}],
}
heldout = json.loads((ROOT / 'artifacts/heldout-evaluation.json').read_text())
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    posts = []
    outcome = {'kind': 'live'}

    def intercept(route):
        req = route.request
        if req.method == 'GET':
            route.fulfill(json=status)
            return
        posts.append(req.url)
        if outcome['kind'] == 'transport':
            route.abort()
        elif outcome['kind'] == 'quota':
            route.fulfill(status=429, json={'detail': 'QUOTA_EXHAUSTED'})
        else:
            result = copy.deepcopy(sample)
            if outcome['kind'] == 'cached':
                result.update(execution='cached_provider_response', external_calls_this_request=0)
            elif outcome['kind'] == 'failed':
                result.update(status='failed', reason='PROVIDER_REQUEST_FAILED_OR_VALIDATION_REJECTED')
                result['checks'][0]['passed'] = False
            elif outcome['kind'] == 'openai':
                result.update(provider='openai', target='qoq-revenue', checks={'value_exact': True},
                              generated={'status': 'verified', 'value': '6.7916', 'issues': [],
                                         'evidence_ids': ['source-a'], 'explanation_ko': '<img src=x onerror=alert(1)>설명'},
                              model='gpt-4.1-mini-2025-04-14', input_tokens=100, output_tokens=50,
                              estimated_cost_usd='0.00012')
            route.fulfill(json=result)

    # Intercept every provider route for all pages, including any future POST path.
    context.route('**/api/providers**', intercept)
    context.route('**/api/evaluation/heldout', lambda r: r.fulfill(json=heldout))
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL, wait_until='networkidle')
    page.locator('[data-view="review"]').click()
    expect(page.locator('#dart-request')).to_be_enabled()
    expect(page.locator('#openai-request')).to_be_disabled()
    expect(page.locator('#openai-availability')).to_contain_text('유료 호출 승인 미설정')
    expect(page.locator('#openai-availability')).to_contain_text('재시작 후에도 유지')
    assert page.locator('#dart-target option').count() == 4
    assert page.locator('#openai-target option').count() == 4
    assert not posts
    checks.append('get_only_boot_fixed_targets_and_explicit_blocked_llm')

    expect(page.locator('#heldout-content')).to_contain_text('정답은 AI가 작성')
    expect(page.locator('#heldout-content')).to_contain_text('현재 결과를 미공개 보류셋 성능으로 볼 수 없습니다')
    expect(page.locator('#heldout-content')).to_contain_text('자연어 질의 Recall@1 0.0%')
    expect(page.locator('#heldout-content')).to_contain_text('UNSUPPORTED_LAYOUT: header')
    expect(page.locator('#heldout-stage-table tbody tr')).to_have_count(5)
    checks.append('heldout_raw_parser_natural_query_failures_and_fixture_limits_visible')

    def request(kind):
        outcome['kind'] = kind
        page.locator('#dart-request').click()
        expect(page.locator('#dart-request')).to_be_enabled()

    request('live')
    expect(page.locator('#dart-result')).to_contain_text('현재 외부 API 요청')
    expect(page.locator('#dart-result')).to_contain_text('이번 외부 호출 1회')
    expect(page.locator('#dart-result')).to_contain_text('원 응답 생성:')
    expect(page.locator('#dart-result')).to_contain_text('이번 응답 제공:')
    expect(page.locator('#dart-result')).to_contain_text('실제 청구액: 미조회')
    checks.append('live_dart_exact_amounts_timestamps_and_unknown_bill')
    request('cached')
    expect(page.locator('#dart-result')).to_contain_text('캐시 응답 재사용')
    expect(page.locator('#dart-result')).to_contain_text('이번 외부 호출 0회')
    expect(page.locator('#provider-session')).to_contain_text('외부 호출 1회 · 캐시 응답 1회')
    checks.append('cache_does_not_increment_external_calls')
    request('failed')
    expect(page.locator('#dart-result')).to_contain_text('실패 · 검증 통과 아님')
    expect(page.locator('#provider-session')).to_contain_text('실패 1건')
    request('quota')
    expect(page.locator('#dart-result')).to_contain_text('공유 호출 한도 소진')
    expect(page.locator('#provider-session')).to_contain_text('차단 1건')
    request('transport')
    expect(page.locator('#dart-result')).to_contain_text('외부 호출·과금 발생 여부는 확인 불가')
    expect(page.locator('#provider-session')).to_contain_text('호출 여부 미확인 1건')
    assert len(posts) == 5
    checks.append('failed_blocked_and_unknown_outcomes_no_automatic_post_retry')

    status['openai'].update(enabled=True, blocked_reasons=[], ledger_scope='durable_volume')
    page.locator('#provider-refresh').click()
    expect(page.locator('#openai-request')).to_be_enabled()
    outcome['kind'] = 'openai'
    page.locator('#openai-request').click()
    expect(page.locator('#openai-result')).to_contain_text('<img src=x onerror=alert(1)>설명')
    expect(page.locator('#openai-result img')).to_have_count(0)
    expect(page.locator('#openai-result')).to_contain_text('사람이 검수하지 않았습니다')
    expect(page.locator('#openai-result')).to_contain_text('$0.00012')
    expect(page.locator('#openai-request')).to_be_enabled()
    page.locator('#openai-target').select_option('no-evidence')
    expect(page.locator('#openai-result')).to_have_text('대상 변경 · 아직 요청하지 않았습니다.')
    checks.append('mock_llm_output_escaped_prose_limits_and_target_reset')

    mobile = context.new_page()
    mobile.set_viewport_size({'width': 390, 'height': 844})
    mobile.goto(URL, wait_until='networkidle')
    mobile.locator('[data-view="review"]').click()
    expect(mobile.locator('#provider-refresh')).to_be_visible()
    assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
    checks.append('mobile_provider_and_heldout_no_page_overflow')
    assert len(posts) == 6
    assert not errors, errors
    browser.close()
print(json.dumps({'passed': len(checks), 'checks': checks, 'external_provider_calls': 0,
                  'provider_requests': 'all intercepted in browser', 'page_errors': errors}, ensure_ascii=False, indent=2))
