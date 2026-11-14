"""Real-backend checks for the nearby return-to-results action.

Only pending/503 and initial-load failure cases inject responses.
Each output directory is new.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

URL = os.getenv('DEMO_URL', 'http://127.0.0.1:8005')
OUT = Path(os.getenv('SETTINGS_RETURN_QA_DIR', 'work/settings-return-qa'))
OUT.mkdir(parents=True, exist_ok=False)
checks, errors = [], []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width, height in [(320, 568), (390, 844), (1440, 900)]:
        page = browser.new_page(viewport={'width': width, 'height': height})
        page.on('pageerror', lambda e: errors.append(str(e)))
        back = page.get_by_role('button', name='설정 닫고 결과 보기', exact=True)

        def ready():
            expect(page.locator('#desk')).to_have_attribute('aria-busy', 'false', timeout=65000)
            expect(page.locator('#worksheet-rows tr')).to_have_count(6)

        def in_view(locator):
            expect(locator).to_be_in_viewport(ratio=1)
            box = locator.bounding_box()
            assert box and box['y'] >= 0 and box['y'] + box['height'] <= height, box

        page.goto(URL+'#work', wait_until='networkidle')
        ready()
        page.locator('#settings-btn').click()
        page.locator('#base-period').select_option('ytd')
        ready()
        page.locator('#settings-close').click()
        page.locator('#comparison-recovery [data-review-setting="base-period"]').click()
        expect(page.locator('#base-period')).to_be_focused()
        page.screenshot(path=str(OUT / f'{width}-before-return-check.png'))
        expect(back).to_be_visible()
        in_view(back)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        checks.append(f'{width}:return_action_in_view_near_focused_base_period')

        back.focus()
        page.keyboard.press('Enter')
        expect(page.locator('#comparison-settings')).to_be_hidden()
        expect(page.locator('#settings-btn')).to_have_attribute('aria-expanded', 'false')
        expect(page.locator('#sheet-title')).to_be_focused()
        in_view(page.locator('#worksheet-rows tr').first)
        expect(page.locator('#base-period')).to_have_value('ytd')
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')
        checks.append(f'{width}:keyboard_return_keeps_period_hold_and_shows_first_row')

        page.locator('#comparison-recovery [data-review-setting="base-period"]').click()
        page.locator('#base-period').select_option('q')
        ready()
        expect(page.locator('#comparison-settings')).to_be_visible()
        in_view(back)
        back.click()
        expect(page.locator('#sheet-title')).to_be_focused()
        expect(page.locator('#comparison-recovery')).to_be_hidden()
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
        in_view(page.locator('#worksheet-rows tr').first)
        page.screenshot(path=str(OUT / f'{width}-normal-return.png'))
        checks.append(f'{width}:explicit_return_after_correction_shows_current_normal_result')

        page.locator('#settings-btn').click()
        page.locator('#base-scope').select_option('OFS')
        ready()
        back.click()
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')
        expect(page.locator('#comparison-recovery')).to_contain_text('연결 범위 불일치')
        expect(page.locator('#sheet-title')).to_be_focused()
        page.locator('#comparison-recovery [data-review-setting="base-scope"]').click()
        page.locator('#base-scope').select_option('CFS')
        ready()
        checks.append(f'{width}:scope_return_does_not_override_guard')

        held = []
        page.route('**/api/worksheet', lambda route: held.append(route))
        page.locator('#base-period').select_option('ytd')
        expect(page.locator('#desk')).to_have_attribute('aria-busy', 'true')
        back.click()
        expect(page.locator('#comparison-settings')).to_be_hidden()
        expect(page.locator('#worksheet-rows')).to_contain_text('대조 중')
        expect(page.locator('#sheet-title')).to_be_focused()
        assert held, 'pending request was not intercepted'
        held.pop().fulfill(status=503, body='{}')
        expect(page.locator('#work-alert')).to_be_visible()
        expect(page.locator('#worksheet-rows')).to_contain_text('결과 없음')
        checks.append(f'{width}:return_while_pending_never_reuses_previous_success')

        page.locator('#settings-btn').click()
        back.click()
        expect(page.locator('#work-alert')).to_be_focused()
        in_view(page.locator('#work-alert'))
        expect(page.locator('#comparison-settings')).to_be_hidden()
        page.unroute('**/api/worksheet')
        page.locator('#settings-btn').click()
        page.locator('#reset-btn').click()
        ready()
        back.click()
        expect(page.locator('#sheet-title')).to_be_focused()
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
        checks.append(f'{width}:failure_return_focuses_error_then_retry_returns_to_results')
        page.route('**/api/facts', lambda route: route.fulfill(status=503, body='{}'))
        page.reload(wait_until='networkidle')
        expect(page.locator('#boot-error')).to_be_visible()
        page.locator('#settings-btn').click()
        back.click()
        expect(page.locator('#boot-error')).to_be_focused()
        # Native scrolling can round the outer border by a fraction of a pixel.
        # Verify the content users must read and activate is fully in view.
        in_view(page.locator('#boot-error h2'))
        in_view(page.locator('#boot-error p'))
        in_view(page.locator('#boot-retry'))
        expect(page.locator('#comparison-settings')).to_be_hidden()
        checks.append(f'{width}:initial_load_failure_return_focuses_connection_error')
        page.close()
    browser.close()

assert not errors, errors
result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'url': URL,
          'passed': len(checks), 'checks': checks, 'page_errors': errors,
          'physical_device': False, 'external_provider_calls': 0,
          'method': 'Real backend; explicit pending/503 worksheet and initial facts-load failure injections'}
(OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
