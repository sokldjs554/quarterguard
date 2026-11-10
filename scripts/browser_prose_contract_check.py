"""Local v6 replay in the browser; intercepted provider routes, no paid calls."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from quarterguard.store import ROOT
from quarterguard.explanation_context import build_context
from quarterguard.explanation_guards import check_prose
from quarterguard.live_verification import check_explanation
from quarterguard.evaluate_live_explanations_v6 import registry

out=Path(os.environ['CONTRACT_QA_DIR']);out.mkdir(parents=True,exist_ok=False)
rows={r['case_id']:r for r in json.loads((ROOT/'artifacts/llm-prose-v6-20261110/report.json').read_text())['records']}
checks=[];errors=[];posts=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(390,844),(1440,1000)]:
        context=browser.new_context(viewport={'width':width,'height':height})
        state={'case':'s22-net-period'}
        def route(request):
            if request.request.method=='GET':
                request.fulfill(json={p:{'enabled':p=='openai','blocked_reasons':[],'usage':{},'limits':{}} for p in ['openai','dart']});return
            posts.append(request.request.url)
            row=rows[state['case']]
            flags=check_explanation(row['generated'],row['tool_result'])|check_prose(row['generated'],row['tool_result'])
            response={'status':'failed','execution':'local_archived_replay','external_calls_this_request':0}
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
        button.click();expect(button).to_be_enabled()
        expect(result.locator('.generated-explanation')).to_have_text(rows[state['case']]['generated']['explanation_ko'])
        checks.append(f'{width}:negation_passes_original_text_unchanged')
        state['case']='normal-qoq';button.click();expect(button).to_be_enabled()
        expect(result).to_contain_text('실패 · 검증 통과 아님')
        expect(result.locator('.generated-explanation')).to_have_count(0)
        expect(result.locator('.explanation-context')).to_have_count(0)
        checks.append(f'{width}:percent_value_rejection_clears_previous_text_and_context')
        state['case']='s22-op-qoq';button.click();expect(button).to_be_enabled()
        expect(result.locator('.generated-explanation')).to_have_text(rows[state['case']]['generated']['explanation_ko'])
        expect(result.locator('.explanation-context')).to_contain_text('인접한 분기 관계가 아닙니다')
        expect(result.locator('.explanation-context')).not_to_contain_text('기간 길이 또는')
        checks.append(f'{width}:specific_context_with_unchanged_ambiguous_model_text')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        result.scroll_into_view_if_needed();page.screenshot(path=str(out/f'{width}-context.png'),full_page=True)
        checks.append(f'{width}:viewport_fits')
        page.locator('#openai-target').select_option('no-evidence')
        expect(result).to_have_text('대상 변경 · 아직 요청하지 않았습니다.')
        checks.append(f'{width}:target_change_clears_result')
        context.close()
    browser.close()
assert not errors,errors
report={'mode':'local_HTTP_archived_v6_with_intercepted_provider_routes','checks':checks,'checks_passed':len(checks),'page_errors':errors,
        'intercepted_posts':len(posts),'actual_external_calls':0,'new_model_responses':0,'new_human_reviews':0,'physical_mobile':False,'direct_public_HTTPS':False}
(out/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
