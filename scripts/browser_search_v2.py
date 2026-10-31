"""Search panel contract checks. All API/provider traffic is intercepted locally.

Default mode also serves assets from local files through Playwright routing, so
no HTTP server is required. --live-assets reads assets from DEMO_URL (default
http://127.0.0.1:8007), while API responses remain mocked and paid POSTs blocked.
This is browser UI evidence, not a live-backend or paid-provider integration run.
"""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quarterguard.search import SearchIndex
from quarterguard.store import load_facts
from quarterguard.worksheet import WorksheetRequest, preview


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--live-assets', action='store_true')
    args = args.parse_args()
    url = os.environ.get('DEMO_URL', 'http://127.0.0.1:8007')
    output = Path(os.environ.get('SEARCH_QA_ARTIFACT', ROOT / 'artifacts/browser-search-v2.json'))
    checks, errors, posts, blocked_external = [], [], [], []
    index = SearchIndex(load_facts())
    facts = [f.public() for f in load_facts()]
    sources = json.loads((ROOT / 'data/sources.json').read_text())
    state = {'hold': False, 'held': [], 'fail': False, 'malformed': False}

    def route_request(route):
        request = route.request
        parsed = urlparse(request.url)
        path = parsed.path
        if parsed.netloc != urlparse(url).netloc:
            blocked_external.append(request.url)
            return route.abort()
        if request.method == 'POST':
            posts.append(path)
            if path == '/api/worksheet':
                return route.fulfill(json=preview(WorksheetRequest.model_validate_json(request.post_data)))
            return route.fulfill(status=403, json={'detail': 'BROWSER_TEST_BLOCKED_POST'})
        if path == '/api/search':
            if state['hold']:
                state['hold'] = False
                state['held'].append(route)
                return
            if state['fail']:
                return route.abort()
            if state['malformed']:
                return route.fulfill(json={'hits': [{'fact_ids': [facts[0]['id']]}]})
            query = parse_qs(parsed.query).get('q', [''])[0]
            return route.fulfill(json=index.search_with_diagnostics(query) | {'configuration': 'hybrid_meta'})
        if path == '/api/facts':
            return route.fulfill(json=facts)
        if path == '/api/sources':
            return route.fulfill(json=sources)
        if path == '/health':
            return route.fulfill(json={'status': 'ok', 'commit': 'browser-mock-contract'})
        if path == '/api/providers':
            return route.fulfill(json={p: {'enabled': False, 'blocked_reasons': ['OPERATOR_DISABLED']} for p in ['dart', 'openai']})
        if path == '/api/cases':
            return route.fulfill(json=json.loads((ROOT / 'data/cases.json').read_text()))
        if path in ['/api/evaluation', '/api/evaluation/heldout']:
            artifact = 'evaluation.json' if path == '/api/evaluation' else 'heldout-evaluation.json'
            return route.fulfill(json=json.loads((ROOT / 'artifacts' / artifact).read_text()))
        if path.startswith('/api/'):
            return route.fulfill(status=503, json={'detail': 'UNMOCKED_API'})
        if args.live_assets:
            return route.continue_()
        asset = ROOT / 'web' / ('index.html' if path == '/' else path.removeprefix('/assets/'))
        if asset.is_file() and asset.resolve().is_relative_to(ROOT / 'web'):
            return route.fulfill(body=asset.read_bytes(), content_type=mimetypes.guess_type(asset.name)[0] or 'text/javascript')
        return route.fulfill(status=404, body='Not found')

    report = {'transport': 'all APIs mocked; provider POSTs blocked',
              'assets': 'live HTTP assets' if args.live_assets else 'local files via browser routing',
              'base_url': url, 'checks': checks, 'page_errors': errors,
              'post_paths': posts, 'blocked_external_requests': blocked_external,
              'paid_provider_calls': 0, 'success': False,
              'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                                for p in ['web/app.js', 'web/index.html', 'quarterguard/query.py']}}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1440, 'height': 1000})
            context.route('**/*', route_request)
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(url, wait_until='networkidle')
            expect(page.locator('#worksheet-rows tr')).to_have_count(6)
            page.locator('[data-view="search"]').click()

            def submit(query):
                page.locator('#query').fill(query)
                page.locator('#search-form button').click()

            korean = '삼성전자의 2024년 3분기 연결 매출액을 3개월 기준 백만원 단위로 알려주세요.'
            english = 'Please show Samsung Electronics consolidated revenue for Q3 2024 for three months in millions of Korean won.'
            for query in [korean, english]:
                submit(query)
                expect(page.locator('[data-search-status]')).to_have_attribute('data-search-status', 'ready')
                expect(page.locator('[data-search-field]')).to_have_count(8)
                expect(page.locator('[data-use-fact]')).to_have_count(1)
                expect(page.locator('[data-use-fact]')).to_have_text('후보를 작업지에서 대조 ↗')
                expect(page.locator('#search-results')).to_contain_text('검색 후보 · 검증된 답변 아님')
            checks.append('korean_english_complete_conditions_candidates_not_answers')

            incomplete = 'What was Samsung consolidated revenue in the third quarter of 2024?'
            submit(incomplete)
            expect(page.locator('[data-search-status]')).to_have_attribute('data-search-status', 'needs_clarification')
            for field in ['kind', 'currency', 'scale']:
                expect(page.locator(f'[data-search-missing="{field}"]')).to_be_visible()
            expect(page.locator('[data-use-fact]').first).to_be_visible()
            checks.append('missing_kind_currency_unit_explained_candidates_retained')
            page.locator('[data-use-fact]').first.click()
            expect(page.locator('#work')).to_be_visible()
            expect(page.locator('#desk')).to_have_attribute('aria-busy', 'false')
            expect(page.locator('#execution-status')).to_contain_text('현재 MCP 호출 없음')
            checks.append('candidate_explicitly_selected_for_existing_worksheet_calculation')
            page.locator('[data-view="search"]').click()

            for query, label in [
                ('Samsung 2024 Q3 CFS OFS revenue quarter KRW million', '범위 조건이 서로 다릅니다'),
                ('Unknown Company 2024 Q3 CFS revenue quarter KRW million', '해석하지 못한 표현'),
                ('Samsung 2024 Q3 CFS revenue quarter EUR million', '해석하지 못한 표현'),
            ]:
                submit(query)
                expect(page.locator('[data-search-status]')).to_have_attribute('data-search-status', 'needs_clarification')
                expect(page.locator('#search-results')).to_contain_text(label)
                expect(page.locator('[data-use-fact]')).to_have_count(0)
            checks.append('conflicts_unknown_company_currency_clarify_without_hits')

            submit('Samsung 2025 Q3 CFS revenue quarter KRW million')
            expect(page.locator('[data-search-status]')).to_have_attribute('data-search-status', 'no_results')
            expect(page.locator('#search-results')).to_contain_text('검색 결과 없음')
            checks.append('complete_unavailable_context_has_no_results')

            submit(korean)
            expect(page.locator('[data-use-fact]')).to_have_count(1)
            state['hold'] = True
            submit(english)
            expect(page.locator('[data-use-fact]')).to_have_count(0)
            expect(page.locator('#search-results')).to_contain_text('근거 검색 중')
            submit('Samsung 2024 Q3 CFS OFS revenue quarter KRW million')
            expect(page.locator('[data-search-status]')).to_have_attribute('data-search-status', 'needs_clarification')
            state['held'].pop().fulfill(json=index.search_with_diagnostics(english))
            page.wait_for_timeout(100)
            expect(page.locator('[data-use-fact]')).to_have_count(0)
            expect(page.locator('#search-results')).to_contain_text('범위 조건이 서로 다릅니다')
            checks.append('new_query_clears_old_hits_and_stale_success_cannot_overwrite')

            submit(korean)
            expect(page.locator('[data-use-fact]')).to_have_count(1)
            state['fail'] = True
            submit(korean)
            expect(page.locator('#search-results [role="alert"]')).to_be_visible()
            expect(page.locator('[data-use-fact]')).to_have_count(0)
            expect(page.locator('[data-search-status]')).to_have_count(0)
            state['fail'] = False
            checks.append('network_failure_clears_stale_candidates_and_diagnostics')

            state['hold'] = True
            submit(korean)
            expect(page.locator('#search-results')).to_contain_text('근거 검색 중')
            submit(incomplete)
            expect(page.locator('[data-search-missing="currency"]')).to_be_visible()
            state['held'].pop().abort()
            page.wait_for_timeout(100)
            expect(page.locator('#search-results [role="alert"]')).to_have_count(0)
            expect(page.locator('[data-search-missing="currency"]')).to_be_visible()
            checks.append('stale_failure_cannot_clear_new_candidates')

            state['malformed'] = True
            submit(korean)
            expect(page.locator('#search-results [role="alert"]')).to_be_visible()
            expect(page.locator('[data-use-fact]')).to_have_count(0)
            state['malformed'] = False
            checks.append('missing_diagnostic_contract_fails_closed')

            page.set_viewport_size({'width': 390, 'height': 844})
            submit(incomplete)
            expect(page.locator('[data-search-missing="scale"]')).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            checks.append('mobile_diagnostic_panel_no_body_overflow')
            assert not errors, errors
            assert all(path == '/api/worksheet' for path in posts), posts
            report['success'] = True
            browser.close()
    except Exception as exc:
        report['failure'] = str(exc)
        raise
    finally:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'success': report['success'], 'checks': len(checks), 'artifact': str(output)}))


if __name__ == '__main__':
    main()
