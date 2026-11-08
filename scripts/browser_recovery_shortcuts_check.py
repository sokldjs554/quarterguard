"""Check comparison recovery before six financial rows, using the real backend.

Only the explicit pending/failure case intercepts a worksheet response.
No external provider/model calls. Keep every run in a new output directory.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

URL = os.getenv('DEMO_URL', 'http://127.0.0.1:8005')
OUT = Path(os.getenv('RECOVERY_QA_DIR', 'work/recovery-shortcuts-qa'))
OUT.mkdir(parents=True, exist_ok=False)
checks, errors = [], []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in [320, 390, 1440]:
        page = browser.new_page(viewport={'width': width, 'height': 900 if width == 1440 else 844})
        page.on('pageerror', lambda e: errors.append(str(e)))
        quick = page.locator('#comparison-recovery')

        def ready():
            expect(page.locator('#desk')).to_have_attribute('aria-busy', 'false', timeout=65000)
            expect(page.locator('#worksheet-rows tr')).to_have_count(6)

        def no_growth():
            expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')

        def no_overflow():
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert quick.evaluate('(el) => el.scrollWidth <= el.clientWidth + 1')

        page.goto(URL, wait_until='networkidle')
        ready()
        expect(quick).to_be_hidden()
        checks.append(f'{width}:normal_has_no_recovery_prompt')
        page.locator('#settings-btn').click()
        page.locator('#base-period').select_option('ytd')
        ready()
        page.locator('#settings-close').click()
        page.locator('#sheet-title').scroll_into_view_if_needed()
        page.screenshot(path=str(OUT / f'{width}-period-before-check.png'))
        expect(quick).to_be_visible()
        expect(quick).to_contain_text('기간 불일치')
        period = quick.get_by_role('button', name='B 기간 설정 확인', exact=False)
        expect(period).to_have_count(1)
        assert quick.bounding_box()['y'] + quick.bounding_box()['height'] <= page.locator('#worksheet-rows tr').first.bounding_box()['y']
        no_overflow()
        no_growth()
        checks.append(f'{width}:period_action_before_first_row_not_after_six_rows')

        period.focus()
        page.keyboard.press('Enter')
        expect(page.locator('#base-period')).to_be_focused()
        expect(page.locator('#base-period')).to_have_value('ytd')
        no_growth()
        checks.append(f'{width}:keyboard_shortcut_focuses_without_changing_period')
        page.locator('#base-scope').select_option('OFS')
        ready()
        expect(quick.locator('button')).to_have_count(2)
        expect(quick).to_contain_text('연결 범위 불일치')
        page.locator('#settings-close').click()
        quick.get_by_role('button', name='B 범위 설정 확인', exact=False).click()
        expect(page.locator('#base-scope')).to_be_focused()
        expect(page.locator('#base-scope')).to_have_value('OFS')
        no_growth()
        no_overflow()
        checks.append(f'{width}:two_issues_deduplicated_and_scope_action_focuses')

        page.locator('#base-period').select_option('q')
        ready()
        expect(quick.locator('button')).to_have_count(1)
        expect(quick).not_to_contain_text('기간 불일치')
        expect(quick).to_contain_text('연결 범위 불일치')
        page.locator('#base-scope').select_option('CFS')
        ready()
        expect(quick).to_be_hidden()
        expect(quick.locator('button')).to_have_count(0)
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
        checks.append(f'{width}:partial_and_full_correction_clear_obsolete_actions')

        page.locator('#base-currency').select_option('USD')
        ready()
        expect(quick).to_be_hidden()
        no_growth()
        expect(page.locator('#finding')).to_contain_text('계산 보류')
        checks.append(f'{width}:currency_hold_does_not_offer_unrelated_period_scope_fix')
        page.locator('#base-currency').select_option('KRW')
        ready()
        page.locator('#base-period').select_option('ytd')
        ready()
        held = []
        page.route('**/api/worksheet', lambda route: held.append(route))
        page.locator('#base-period').select_option('q')
        expect(page.locator('#desk')).to_have_attribute('aria-busy', 'true')
        expect(quick).to_be_hidden()
        expect(quick.locator('button')).to_have_count(0)
        page.wait_for_function('document.querySelector("#worksheet-rows").textContent.includes("대조 중")')
        assert held, 'worksheet request was not intercepted'
        held.pop().fulfill(status=503, body='{}')
        expect(page.locator('#work-alert')).to_be_visible()
        expect(quick).to_be_hidden()
        expect(page.locator('#worksheet-rows')).to_contain_text('결과 없음')
        page.unroute('**/api/worksheet')
        page.locator('#reset-btn').click()
        ready()
        expect(quick).to_be_hidden()
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
        checks.append(f'{width}:pending_and_failure_remove_stale_actions_then_recover')
        page.locator('#base-period').select_option('ytd')
        ready()
        page.locator('#settings-close').click()
        quick.scroll_into_view_if_needed()
        page.screenshot(path=str(OUT / f'{width}-period-recovery.png'))
        page.close()
    browser.close()

assert not errors, errors
result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'url': URL,
          'passed': len(checks), 'checks': checks, 'page_errors': errors,
          'physical_device': False, 'external_provider_calls': 0,
          'method': 'Real backend; pending/503 worksheet response explicitly injected only for stale-state case'}
(OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
