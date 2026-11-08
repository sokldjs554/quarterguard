"""Check each mobile amount retains its own period/scope/unit as inputs change.

Use the real backend. Only the explicit failure case intercepts a response.
No provider calls; a fresh output directory preserves prior test evidence.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

URL = os.getenv('DEMO_URL', 'http://127.0.0.1:8005')
OUT = Path(os.getenv('MOBILE_CONTEXT_QA_DIR', 'work/mobile-context-qa'))
OUT.mkdir(parents=True, exist_ok=False)
checks, errors = [], []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in [320, 390]:
        page = browser.new_page(viewport={'width': width, 'height': 844})
        page.on('pageerror', lambda e: errors.append(str(e)))

        def ready():
            expect(page.locator('#desk')).to_have_attribute('aria-busy', 'false', timeout=65000)
            expect(page.locator('#worksheet-rows tr')).to_have_count(6)

        def context(side, metric='revenue'):
            return page.locator(f'#context-{side}-{metric}')

        def no_overflow():
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            for cell in page.locator('#worksheet-rows .value-cell').all():
                assert cell.evaluate('(el) => el.scrollWidth <= el.clientWidth + 1')

        def reset():
            if page.locator('#comparison-settings').is_hidden():
                page.locator('#settings-btn').click()
            page.locator('#reset-btn').click()
            ready()

        page.goto(URL, wait_until='networkidle')
        ready()
        expect(page.locator('.value-context')).to_have_count(12)
        for row in page.locator('#worksheet-rows tr').all():
            for side, period in [('current', '2024.07–09'), ('base', '2024.04–06')]:
                info = row.locator(f'.value-context[data-context-side="{side}"]')
                expect(info).to_be_visible()
                expect(info).to_contain_text(period)
                expect(info).to_contain_text('3개월 · 연결')
                expect(info).to_contain_text('백만 원')
                button = row.locator(f'.number-button[data-side="{side}"]')
                expect(button).to_have_attribute('aria-describedby', info.get_attribute('id'))
                assert info.bounding_box()['y'] >= button.bounding_box()['y'] + button.bounding_box()['height'] - 1
        no_overflow()
        page.screenshot(path=str(OUT / f'mobile-{width}-normal.png'), full_page=True)
        checks.append(f'{width}:all_amounts_show_own_period_scope_unit_below_number')

        context('base').click()
        expect(page.locator('#source-counter')).to_contain_text('B 비교')
        checks.append(f'{width}:base_context_click_keeps_base_source_selected')
        reset()
        page.locator('#base-period').select_option('ytd')
        ready()
        expect(context('base')).to_contain_text('2024.01–06')
        expect(context('base')).to_contain_text('6개월 · 연결')
        expect(context('current')).to_contain_text('2024.07–09')
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')
        no_overflow()
        page.locator('#settings-close').click()
        page.screenshot(path=str(OUT / f'mobile-{width}-period-hold.png'), full_page=True)
        checks.append(f'{width}:ytd_updates_base_context_and_preserves_period_hold')

        reset()
        page.locator('#base-scope').select_option('OFS')
        ready()
        expect(context('base')).to_contain_text('3개월 · 별도')
        expect(context('current')).to_contain_text('3개월 · 연결')
        expect(page.locator('[data-row="revenue"] .number-button[data-side="base"]')).to_have_text('53,734,118')
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')
        checks.append(f'{width}:scope_change_labels_each_side_and_preserves_hold')

        reset()
        page.locator('#base-document').select_option('s24q3')
        ready()
        page.locator('#base-year').select_option('2023')
        ready()
        page.locator('#mode').select_option('yoy')
        ready()
        expect(context('base')).to_contain_text('2023.07–09')
        expect(context('current')).to_contain_text('2024.07–09')
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('+17.3491%')
        checks.append(f'{width}:context_uses_fact_year_not_report_title_year')

        reset()
        page.locator('#base-currency').select_option('USD')
        ready()
        expect(context('base')).to_contain_text('천 USD · 참고')
        expect(context('current')).to_contain_text('백만 원')
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')
        no_overflow()
        checks.append(f'{width}:usd_reference_unit_stays_distinct_and_blocked')

        page.route('**/api/worksheet', lambda r: r.fulfill(status=503, body='{}'))
        page.locator('#base-currency').select_option('KRW')
        expect(page.locator('#work-alert')).to_be_visible()
        expect(page.locator('.value-context')).to_have_count(0)
        page.unroute('**/api/worksheet')
        reset()
        expect(context('base')).to_contain_text('2024.04–06')
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
        checks.append(f'{width}:failure_clears_stale_context_and_retry_recovers')
        page.close()

    desktop = browser.new_page(viewport={'width': 1440, 'height': 1000})
    desktop.goto(URL, wait_until='networkidle')
    expect(desktop.locator('#desk')).to_have_attribute('aria-busy', 'false')
    expect(desktop.locator('.value-context')).to_have_count(12)
    for info in desktop.locator('.value-context').all():
        expect(info).to_be_hidden()
    expect(desktop.locator('#base-heading')).to_contain_text('2024-04–2024-06')
    checks.append('desktop:existing_column_context_preserved_without_duplicate_lines')
    browser.close()

assert not errors, errors
result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'url': URL,
          'passed': len(checks), 'checks': checks, 'page_errors': errors,
          'external_provider_calls': 0, 'physical_device': False,
          'method': 'Real backend; explicit 503 injected only for stale-context/recovery case'}
(OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
