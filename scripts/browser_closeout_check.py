"""Local HTTP PC/mobile summary regression. No provider requests or TLS claims."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

OUT=Path(os.getenv('CLOSEOUT_BROWSER_OUTPUT','artifacts/final-closeout-20261112/browser'))
OUT.mkdir(exist_ok=False)
checks=[];errors=[];paid_requests=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in ((390,844),(1440,1000)):
        context=browser.new_context(viewport={'width':width,'height':height})
        state={'fail':False}
        def route(request):
            if request.request.method=='POST' and '/api/providers/' in request.request.url:
                paid_requests.append(request.request.url);request.abort();return
            if state['fail'] and request.request.url.endswith('/api/evaluation/latest'):
                request.fulfill(status=503,json={'detail':'INJECTED_SUMMARY_FAILURE'});return
            request.continue_()
        context.route('**/api/**',route)
        page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8795',wait_until='networkidle')
        page.locator('[data-view="review"]').click()
        section=page.locator('#latest-evidence-summary')
        for text in ('SK 5개 + Apple 7개','참 11·거짓 4·모호 5','JSON 다운로드·내용 대조 완료',
                     '10건 통과','사람 참 차단 1건','테스트 6개','새 유료 호출 0회'):
            expect(section).to_contain_text(text)
        expect(section).not_to_contain_text('아직 미수신')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        section.scroll_into_view_if_needed()
        page.screenshot(path=str(OUT/f'{width}-summary.png'),full_page=True)
        checks.append(f'{width}:completed_work_and_replay_scope_visible')
        state['fail']=True
        page.reload(wait_until='networkidle');page.locator('[data-view="review"]').click()
        expect(page.locator('#latest-evidence-summary')).to_have_count(0)
        expect(page.locator('#latest-evidence-error')).to_contain_text('최신 자료를 불러오지 못했습니다')
        checks.append(f'{width}:failure_does_not_display_stale_summary')
        state['fail']=False
        page.get_by_role('button',name='평가 자료 다시 불러오기',exact=True).click()
        expect(page.locator('#latest-evidence-summary')).to_contain_text('10건 통과')
        checks.append(f'{width}:retry_restores_current_summary')
        context.close()
    browser.close()
report={'mode':'local_http_chromium_automated','checks':checks,'page_errors':errors,
        'provider_posts':paid_requests,'new_human_review':False,'direct_https_browser':False}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert not errors and not paid_requests,report
print(json.dumps(report,ensure_ascii=False))
