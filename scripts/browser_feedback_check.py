"""Real worksheet UI checks for session-a feedback; no provider/model API calls.

Catch stale enlarged source details, report/selected-period confusion, and
shortcuts that silently change comparison conditions or focus the wrong field.
Outputs use an exclusive, new directory so earlier runs cannot be overwritten.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

URL = os.getenv('DEMO_URL', 'http://127.0.0.1:8005')
OUT = Path(os.getenv('FEEDBACK_QA_DIR', 'work/feedback-qa'))
OUT.mkdir(parents=True, exist_ok=False)
checks, errors = [], []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for label, size in [('desktop', {'width': 1440, 'height': 1000}),
                        ('mobile-size', {'width': 390, 'height': 844})]:
        page = browser.new_page(viewport=size)
        page.on('pageerror', lambda e: errors.append(str(e)))

        def ready():
            expect(page.locator('#desk')).to_have_attribute('aria-busy', 'false', timeout=65000)
            expect(page.locator('#worksheet-rows tr')).to_have_count(6)

        def no_growth():
            expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')

        page.goto(URL, wait_until='networkidle')
        ready()
        page.locator('[data-source-index="1"]').click()
        expect(page.locator('.source-header')).to_contain_text('반기')
        expect(page.locator('.source-period')).to_contain_text('2024-04-01')
        expect(page.locator('.source-period')).to_contain_text('2024-06-30')
        expect(page.locator('.source-period')).to_contain_text('3개월')
        checks.append(f'{label}:half_year_document_contains_second_quarter')

        page.locator('#enlarge-source').focus()
        page.keyboard.press('Enter')
        dialog = page.locator('#source-detail-dialog')
        expect(dialog).to_be_visible()
        expect(dialog).to_contain_text('74,068,302')
        expect(dialog).to_contain_text('Revenue')
        expect(dialog).to_contain_text('원문 이미지 아님')
        assert dialog.locator('a').get_attribute('href').endswith('#page=48')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT / f'{label}-source-detail.png'), full_page=True)
        page.keyboard.press('Escape')
        expect(dialog).not_to_be_visible()
        expect(page.locator('#enlarge-source')).to_be_focused()
        checks.append(f'{label}:enlarged_evidence_matches_selected_fact_and_returns_focus')

        page.locator('[data-source-index="0"]').click()
        page.locator('#enlarge-source').click()
        expect(dialog).to_contain_text('79,098,731')
        expect(dialog).not_to_contain_text('74,068,302')
        assert dialog.locator('a').get_attribute('href').endswith('#page=34')
        dialog.get_by_role('button', name='확대 근거 닫기').click()
        checks.append(f'{label}:source_change_does_not_reuse_previous_amount')

        page.locator('#settings-btn').click()
        page.locator('#base-period').select_option('ytd')
        ready()
        page.locator('#settings-close').click()
        no_growth()
        page.locator('[data-review-setting="base-period"]').click()
        expect(page.locator('#comparison-settings')).to_be_visible()
        expect(page.locator('#base-period')).to_be_focused()
        expect(page.locator('#base-period')).to_have_value('ytd')
        no_growth()
        checks.append(f'{label}:period_shortcut_focuses_without_changing_conditions')

        page.locator('#base-period').select_option('q')
        ready()
        page.locator('#base-scope').select_option('OFS')
        ready()
        page.locator('#settings-close').click()
        page.locator('[data-review-setting="base-scope"]').click()
        expect(page.locator('#base-scope')).to_be_focused()
        expect(page.locator('#base-scope')).to_have_value('OFS')
        no_growth()
        page.locator('#base-scope').select_option('CFS')
        ready()
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
        checks.append(f'{label}:scope_shortcut_preserves_guard_until_user_corrects_scope')
        page.locator('#settings-close').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT / f'{label}-worksheet.png'), full_page=True)
        checks.append(f'{label}:worksheet_has_no_horizontal_page_overflow')
        page.close()
    browser.close()

report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'url': URL,
          'checks': checks, 'page_errors': errors, 'provider_calls': 0,
          'method': 'Playwright Chromium desktop/mobile viewport; not a physical phone or human usability study'}
(OUT / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
assert not errors, errors
print(f'{len(checks)} feedback UI checks passed; {OUT}')
