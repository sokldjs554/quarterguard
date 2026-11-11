"""Local HTTP UI: archived responses and explicitly synthetic Korean examples.

Provider routes are intercepted; no real LLM requests or human sessions.
"""
import copy
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from quarterguard.store import ROOT
from quarterguard.explanation_context import build_context
from quarterguard.explanation_guards import check_prose
from quarterguard.live_verification import check_explanation
from quarterguard.evaluate_live_explanations_v8 import registry

out=Path(os.environ['PLAIN_QA_DIR']);out.mkdir(parents=True,exist_ok=False)
rows={r['case_id']:r for r in json.loads((ROOT/'artifacts/llm-prose-v7-20261110/report.json').read_text())['records']}
synthetic={
    'no-evidence':'현재 검색 조건으로 확인할 수 있는 근거를 찾지 못했습니다. 기업의 실적 자체가 없다는 뜻은 아닙니다.',
    's22-op-qoq':'두 기간은 모두 3개월이지만 바로 이어지는 분기가 아니므로 전분기 대비 증감률 계산을 보류합니다.',
}
checks=[];errors=[];posts=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(390,844),(1440,1000)]:
        context=browser.new_context(viewport={'width':width,'height':height})
        state={'case':'normal-qoq','synthetic':False}
        def route(request):
            if request.request.method=='GET':
                request.fulfill(json={p:{'enabled':p=='openai','blocked_reasons':[],'usage':{},'limits':{}} for p in ['openai','dart']});return
            posts.append(request.request.url)
            row=rows[state['case']];answer=copy.deepcopy(row['generated'])
            if state['synthetic']:answer['explanation_ko']=synthetic[state['case']]
            flags=check_explanation(answer,row['tool_result'])|check_prose(answer,row['tool_result'])
            response={'status':'failed','execution':'local_synthetic_or_archived_replay','external_calls_this_request':0}
            if all(flags.values()):
                with registry(row):ctx=build_context(row['tool_result'])
                response.update(status='succeeded',generated=answer,explanation_context=ctx,prose_semantics_verified=False)
            else:response.update(reason='EXPLANATION_VALIDATION_REJECTED',validation_checks=flags)
            request.fulfill(json=response)
        context.route('**/api/providers**',route)
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(os.environ['DEMO_URL'],wait_until='networkidle')
        page.locator('[data-view="review"]').click()
        button=page.locator('#openai-request');result=page.locator('#openai-result')
        button.click();expect(button).to_be_enabled()
        expect(result.locator('.generated-explanation')).to_have_text(rows['normal-qoq']['generated']['explanation_ko'])
        checks.append(f'{width}:archived_valid_response_displayed_unchanged')
        for case in ('no-evidence','s22-op-qoq'):
            state.update(case=case,synthetic=False)
            button.click();expect(button).to_be_enabled()
            expect(result).to_contain_text('실패 · 검증 통과 아님')
            expect(result.locator('.generated-explanation')).to_have_count(0)
            expect(result.locator('.explanation-context')).to_have_count(0)
            checks.append(f'{width}:{case}:internal_code_rejection_clears_previous_success')
            state['synthetic']=True
            button.click();expect(button).to_be_enabled()
            expect(result.locator('.generated-explanation')).to_have_text(synthetic[case])
            expected='현재 검색 조건으로 확인할 수 있는 근거를 찾지 못했습니다' if case=='no-evidence' else '바로 이어지는 분기(인접 분기)가 아닙니다'
            expect(result.locator('.explanation-context')).to_contain_text(expected)
            expect(result.locator('.generated-explanation')).not_to_contain_text('SEARCH_EMPTY')
            expect(result.locator('.generated-explanation')).not_to_contain_text('qoq_adjacent')
            checks.append(f'{width}:{case}:synthetic_Korean_and_deterministic_context_displayed')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        checks.append(f'{width}:viewport_fits')
        result.scroll_into_view_if_needed();page.screenshot(path=str(out/f'{width}-context.png'),full_page=True)
        context.close()
    browser.close()
assert not errors,errors
report={'mode':'local_HTTP_archived_v7_and_synthetic_Korean_with_intercepted_provider_routes',
        'checks':checks,'checks_passed':len(checks),'page_errors':errors,'intercepted_posts':len(posts),
        'actual_external_calls':0,'new_model_responses':0,'new_human_reviews':0,
        'physical_mobile':False,'direct_public_HTTPS':False}
(out/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
