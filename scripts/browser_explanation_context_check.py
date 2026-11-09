"""Local UI replay of historical responses; all provider endpoints intercepted."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
URL = os.getenv('DEMO_URL', 'http://127.0.0.1:8005')
OUT = Path(os.getenv('EXPLANATION_QA_DIR', 'work/explanation-context-browser'))
OUT.mkdir(parents=True, exist_ok=False)
source = json.loads((ROOT/'artifacts/llm-live-20261109/report.json').read_text())
replay = json.loads((ROOT/'artifacts/explanation-context-20261110/replay.json').read_text())
contexts = {r['case_id']:r['deterministic_context'] for r in replay['records']}
rows = {r['case_id']:r for r in source['records']}
status = {p:{'enabled':p=='openai','blocked_reasons':[],'usage':{},'limits':{},
             'ledger_scope':'instance_ephemeral_resets_on_restart'} for p in ('openai','dart')}
checks, errors, intercepted = [], [], []

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(320,568),(390,844),(1440,1000)]:
        context=browser.new_context(viewport={'width':width,'height':height})
        state={'case':'normal-qoq','mode':'replay'}

        def route_provider(route):
            if route.request.method=='GET':
                route.fulfill(json=status)
                return
            intercepted.append(route.request.url)
            if state['mode']=='failure':
                route.fulfill(status=503,json={'detail':'offline injected error'})
                return
            row=rows[state['case']]
            result={'status':'succeeded','provider':'openai','target':'qoq-revenue',
                'execution':'cached_provider_response' if state['mode']=='cached' else 'live_provider_request',
                'external_calls_this_request':0,'created_at':source['created_at'],'served_at':source['created_at'],
                'generated':row['generated'],'explanation_context':contexts[state['case']],
                'model':'historical-response-browser-replay','input_tokens':0,'output_tokens':0,
                'estimated_cost_usd':'0','billed_cost_usd':None}
            if state['mode']=='legacy':result.pop('explanation_context')
            route.fulfill(json=result)

        context.route('**/api/providers**',route_provider)
        page=context.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL,wait_until='networkidle')
        page.locator('[data-view="review"]').click()
        button=page.locator('#openai-request')
        result=page.locator('#openai-result')
        expect(button).to_be_enabled()
        for case in rows:
            state.update(case=case,mode='replay')
            button.click()
            expect(button).to_be_enabled()
            expect(result.locator('.generated-explanation')).to_have_text(rows[case]['generated']['explanation_ko'])
            expect(result).to_contain_text('도구 결과의 단위·출처')
            if case=='no-evidence':
                expect(result).to_contain_text('해당 검색 범위')
                expect(result.locator('.explanation-context a')).to_have_count(0)
            else:
                expect(result.locator('.explanation-context')).to_contain_text('백만 원')
                expect(result.locator('.explanation-context a')).to_have_count(len(rows[case]['tool_result']['evidence']))
                for i,fact in enumerate(rows[case]['tool_result']['evidence']):
                    expect(result.locator('.explanation-context a').nth(i)).to_have_attribute('href',fact['source_url']+'#page='+str(fact['page']))
                if case in ('period-mismatch','scope-mismatch'):
                    expect(result.locator('.explanation-context')).to_contain_text('계산 보류')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            checks.append(f'{width}:{case}:raw_prose_preserved_context_and_locators')
        result.scroll_into_view_if_needed()
        page.screenshot(path=str(OUT/f'{width}-context-replay.png'),full_page=True)
        state.update(mode='failure')
        button.click()
        expect(button).to_be_enabled()
        expect(result).to_contain_text('확인 불가')
        expect(result.locator('.explanation-context')).to_have_count(0)
        expect(result.locator('.generated-explanation')).to_have_count(0)
        checks.append(f'{width}:failure_clears_previous_prose_and_context')
        state.update(mode='cached')
        button.click()
        expect(button).to_be_enabled()
        expect(result).to_contain_text('캐시 응답 재사용')
        expect(result.locator('.explanation-context a')).to_have_count(2)
        checks.append(f'{width}:cached_context_is_labeled')
        state.update(mode='legacy')
        button.click()
        expect(button).to_be_enabled()
        expect(result).to_contain_text('근거 안내 없음')
        expect(result.locator('.explanation-context a')).to_have_count(0)
        checks.append(f'{width}:legacy_response_does_not_reuse_context')
        page.locator('#openai-target').select_option('no-evidence')
        expect(result).to_have_text('대상 변경 · 아직 요청하지 않았습니다.')
        checks.append(f'{width}:target_change_clears_result')
        context.close()
    browser.close()
assert not errors,errors
report={'mode':'local_HTTP_browser_with_intercepted_historical_provider_responses',
    'physical_mobile':False,'direct_public_HTTPS':False,'new_provider_calls':0,
    'intercepted_post_count':len(intercepted),'checks_passed':len(checks),'checks':checks,'page_errors':errors,
    'new_human_review':False,'limitations':['Browser replay, not fresh LLM output or live provider execution.',
    'Viewport simulation, not physical phone or participant testing.']}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
