"""Check A7/S4 downloads against real HTTP responses; no fixture replay or LLM calls."""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import expect, sync_playwright

A7 = '2024년 중국권 매출 감소는 판매량 감소만으로 설명할 수 있나?'
A1 = '2024회계연도에 제품과 서비스 중 어느 쪽의 매출총이익률이 더 높았나?'


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def export_result(page, button, path, expected):
    with page.expect_download() as pending:
        button.click()
    download = pending.value
    assert download.failure() is None
    download.save_as(path)
    # Reopen the actual downloaded bytes, not a separately generated fixture.
    actual = json.loads(path.read_text())
    assert actual == expected, 'Downloaded JSON differs from actual server response'
    return actual, {'filename': download.suggested_filename,
                    'artifact': path.name, 'bytes': path.stat().st_size,
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'reopened_equals_http_response': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--transport', choices=['direct_https', 'tls_verified_relay'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'started_at_kst': datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),
              'actor': 'AI-operated automated Playwright', 'human_participation': False,
              'browser_url': args.url, 'transport': args.transport,
              'ignore_https_errors': False, 'new_paid_calls': 0,
              'mocked_responses': False, 'checks': [], 'status': 'running'}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                         args=['--no-sandbox'])
            report['browser_version'] = browser.version
            for width, height in [(1365, 900), (390, 844)]:
                page = browser.new_page(viewport={'width': width, 'height': height}, accept_downloads=True)
                page.set_default_timeout(20000)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(args.url, timeout=60000)
                page.locator('[data-view="search"]').click()
                picker = page.locator('#source-document')
                picker.select_option('apple-2024-10k')
                query = page.locator('#source-evidence-query')
                button = page.locator('#apple-review-submit')
                result = page.locator('#apple-review-result')
                export = page.locator('#apple-review-export')
                query.fill(A7)
                with page.expect_response(lambda r: r.url.endswith('/api/source-review') and r.request.method == 'POST') as response:
                    button.click()
                assert response.value.status == 200
                a7_response = response.value.json()
                expect(export).to_be_enabled()
                expect(result).to_contain_text('판단 보류')
                a7, a7_file = export_result(page, export, args.output / f'A7-{width}.json', a7_response)
                assert a7['query'] == A7 and a7['document_id'] == 'apple-2024-10k'
                assert a7['status'] == 'needs_review' and a7['issues'] == ['CAUSAL_DECOMPOSITION_REQUIRED']
                assert a7['currency'] == 'USD' and a7['scale'] == 1000000
                assert a7['values'] == {} and a7['required_information']
                assert all(c['printed_page'] == 22 and c['row'] == 'Greater China' for c in a7['evidence'])
                assert any(n['key'] == 'china_drivers' and n['printed_page'] == 22 for n in a7['narratives'])
                assert a7['messages'][0] in result.inner_text()
                page.screenshot(path=str(args.output / f'A7-{width}.png'), full_page=True)
                query.fill(A1)
                expect(export).to_be_disabled()
                expect(result).to_contain_text('이전 결과는 표시하지 않습니다')
                expect(result).not_to_contain_text(a7['messages'][0])
                page.screenshot(path=str(args.output / f'A7-edited-{width}.png'), full_page=True)
                with page.expect_response(lambda r: r.url.endswith('/api/source-review') and r.request.method == 'POST') as response:
                    button.click()
                assert response.value.status == 200
                expect(export).to_be_enabled()
                expect(result).to_contain_text('73.8804%')
                a1, a1_file = export_result(page, export, args.output / f'A1-after-edit-{width}.json', response.value.json())
                assert a1['query'] == A1 and a1['status'] == 'verified'
                assert a1['operation'] == 'gross_margin' and a1['query'] != a7['query']
                picker.select_option('skh2024annual-in-2025oc')
                page.locator('#source-calculator summary').click()
                mode = page.locator('#source-calc-mode')
                expect(mode).to_be_enabled()
                mode.select_option('inventory_months')
                request_ids = [page.locator('#source-calc-current').input_value(), page.locator('#source-calc-base').input_value()]
                with page.expect_response(lambda r: r.url.endswith('/api/source-calculations') and r.request.method == 'POST') as response:
                    page.locator('#source-calc-submit').click()
                assert response.value.status == 200
                sk_box = page.locator('#source-calc-result')
                sk_export = page.locator('#source-calc-export')
                expect(sk_export).to_be_enabled()
                expect(sk_box).to_contain_text('자동 계산하지 않습니다')
                sk, sk_file = export_result(page, sk_export, args.output / f'S4-{width}.json', response.value.json())
                assert sk['mode'] == 'inventory_months' and sk['status'] == 'needs_review'
                assert sk['issues'] == ['RATIO_DEFINITION_REQUIRED']
                assert sk['growth_pct'] is None and sk['share_pct'] is None and sk['difference'] is None
                assert sk['formula'] is None
                assert [c['id'] for c in sk['evidence']] == request_ids
                assert [(c['metric'], c['year'], c['page'], c['printed_page']) for c in sk['evidence']] == [('inventory', 2024, 191, 'F-73'), ('revenue', 2023, 193, 'F-75')]
                assert all(c['currency'] == 'KRW' and c['scale'] == 1000000 and c['source_url'].startswith('https://links.sgx.com/') for c in sk['evidence'])
                assert sk['messages'][0] in sk_box.inner_text()
                page.screenshot(path=str(args.output / f'S4-{width}.png'), full_page=True)
                assert not errors, errors
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                report['checks'].append({'viewport': [width, height], 'A7_download': a7_file,
                    'A7_edit_clears_result_and_disables_export': True, 'new_question_new_result': a1_file,
                    'S4_download': sk_file, 'S4_selection_matches_export': True,
                    'S4_source_and_withholding_preserved': True, 'page_errors': errors})
                save_json(args.output / 'report.json', report)
                page.close()
            browser.close()
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        report['finished_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
        save_json(args.output / 'report.json', report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
