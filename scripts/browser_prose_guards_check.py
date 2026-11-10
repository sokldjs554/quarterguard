"""Local browser replay of current guards; no provider calls or new human review."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from quarterguard.explanation_context import build_context
from quarterguard.explanation_guards import check_prose
from quarterguard.live_verification import check_explanation

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('PROSE_GUARD_QA_DIR', ROOT/'work/prose-guards-browser'))
OUT.mkdir(parents=True, exist_ok=False)
rows = {r['case_id']: r for r in json.loads(
    (ROOT/'artifacts/llm-guards-v5-20261110/report.json').read_text())['records']}
checks, errors, posts = [], [], []
status = {p: {'enabled': p == 'openai', 'blocked_reasons': [], 'usage': {}, 'limits': {}}
          for p in ['openai', 'dart']}

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width, height in [(390, 844), (1440, 1000)]:
        context = browser.new_context(viewport={'width': width, 'height': height})
        mode = {'case': 'normal-qoq'}
        def route(request):
            if request.request.method == 'GET':
                request.fulfill(json=status)
                return
            posts.append(request.request.url)
            row = rows[mode['case']]
            flags = check_explanation(row['generated'], row['tool_result']) | check_prose(row['generated'], row['tool_result'])
            result = {'status': 'failed', 'execution': 'local_archived_replay',
                      'external_calls_this_request': 0}
            if all(flags.values()):
                result.update(status='succeeded', generated=row['generated'],
                              explanation_context=build_context(row['tool_result']),
                              prose_semantics_verified=False)
            else:
                result.update(reason='EXPLANATION_VALIDATION_REJECTED', validation_checks=flags)
            request.fulfill(json=result)
        context.route('**/api/providers**', route)
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(os.environ.get('DEMO_URL', 'http://127.0.0.1:8798'), wait_until='networkidle')
        page.locator('[data-view="review"]').click()
        button, result = page.locator('#openai-request'), page.locator('#openai-result')
        button.click()
        expect(button).to_be_enabled()
        expect(result.locator('.generated-explanation')).to_have_text(rows['normal-qoq']['generated']['explanation_ko'])
        checks.append(f'{width}:accepted_archived_text_unchanged')
        for case in ['period-mismatch', 'citation-draft', 'no-evidence']:
            mode['case'] = case
            button.click()
            expect(button).to_be_enabled()
            expect(result).to_contain_text('실패 · 검증 통과 아님')
            expect(result).to_contain_text('설명 표현 검사 불일치')
            expect(result.locator('.generated-explanation')).to_have_count(0)
            expect(result.locator('.explanation-context')).to_have_count(0)
            assert rows[case]['generated']['explanation_ko'] not in result.inner_text()
            checks.append(f'{width}:{case}_rejected_without_old_or_new_prose')
            if case == 'citation-draft':
                result.scroll_into_view_if_needed()
                page.screenshot(path=str(OUT/f'{width}-withheld.png'), full_page=True)
            mode['case'] = 'normal-qoq'
            button.click()
            expect(button).to_be_enabled()
            expect(result.locator('.generated-explanation')).to_have_text(rows['normal-qoq']['generated']['explanation_ko'])
            expect(result).not_to_contain_text('실패 · 검증 통과 아님')
            checks.append(f'{width}:recovery_after_{case}')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#openai-target').select_option('no-evidence')
        expect(result).to_have_text('대상 변경 · 아직 요청하지 않았습니다.')
        checks.append(f'{width}:target_change_clears_result')
        context.close()
    browser.close()
assert not errors, errors
report = {'mode': 'local_HTTP_archived_outputs_current_guards_intercepted_provider_routes',
          'checks': checks, 'checks_passed': len(checks), 'page_errors': errors,
          'intercepted_posts': len(posts), 'actual_external_calls': 0, 'new_model_responses': 0,
          'new_human_reviews': 0, 'physical_mobile': False, 'direct_public_HTTPS': False}
(OUT/'browser.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False))
