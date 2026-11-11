"""Local v8 archived-response replay with intercepted providers; no paid calls."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from quarterguard.store import ROOT
from quarterguard.explanation_context import build_context
from quarterguard.explanation_guards import check_prose
from quarterguard.live_verification import check_explanation
from quarterguard.evaluate_live_explanations_v8 import registry

out=Path(os.environ['V8_FIX_QA_DIR']);out.mkdir(parents=True,exist_ok=False)
rows={r['case_id']:r for r in json.loads((ROOT/'artifacts/llm-prose-v8-20261111/report.json').read_text())['records']}
checks=[];errors=[];posts=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(390,844),(1440,1000)]:
        context=browser.new_context(viewport={'width':width,'height':height})
        state={'case':'normal-qoq'}
        def route(request):
            if request.request.method=='GET':
                request.fulfill(json={p:{'enabled':p=='openai','blocked_reasons':[],'usage':{},'limits':{}} for p in ['openai','dart']});return
            posts.append(request.request.url)
            row=rows[state['case']]
            flags=check_explanation(row['generated'],row['tool_result'])|check_prose(row['generated'],row['tool_result'])
            response={'status':'failed','execution':'local_archived_v8_replay','external_calls_this_request':0}
            if all(flags.values()):
                with registry(row):ctx=build_context(row['tool_result'])
                response.update(status='succeeded',generated=row['generated'],explanation_context=ctx,prose_semantics_verified=False)
            else:response.update(reason='EXPLANATION_VALIDATION_REJECTED',validation_checks=flags)
            request.fulfill(json=response)
        context.route('**/api/providers**',route)
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(os.environ['DEMO_URL'],wait_until='networkidle')
        page.locator('[data-view="review"]').click()
        button=page.locator('#openai-request');result=page.locator('#openai-result')
        for case,accepted in [('normal-qoq',True),('h25-net-yoy',False),('s22-net-period',True),
                              ('cross-company-period',False),('no-evidence',False)]:
            state['case']=case;button.click();expect(button).to_be_enabled()
            if accepted:
                expect(result.locator('.generated-explanation')).to_have_text(rows[case]['generated']['explanation_ko'])
                checks.append(f'{width}:{case}:original_prose_unchanged')
            else:
                expect(result).to_contain_text('실패 · 검증 통과 아님')
                expect(result.locator('.generated-explanation')).to_have_count(0)
                expect(result.locator('.explanation-context')).to_have_count(0)
                checks.append(f'{width}:{case}:rejected_and_prior_success_cleared')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        checks.append(f'{width}:viewport_fits')
        result.scroll_into_view_if_needed();page.screenshot(path=str(out/f'{width}-result.png'),full_page=True)
        context.close()
    browser.close()
assert not errors,errors
report={'mode':'local_HTTP_v8_archived_responses_intercepted_provider_routes','checks':checks,
        'checks_passed':len(checks),'page_errors':errors,'intercepted_posts':len(posts),'actual_external_calls':0,
        'new_model_responses':0,'new_human_reviews':0,'physical_mobile':False,'direct_public_HTTPS':False}
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
