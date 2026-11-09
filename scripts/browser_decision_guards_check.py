"""Local browser replay: real archived prose plus mocked provider status/results."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from quarterguard.explanation_context import build_context
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.getenv('DECISION_GUARD_QA_DIR',str(ROOT/'work/decision-guards-browser')))
OUT.mkdir(parents=True,exist_ok=False)
rows={r['case_id']:r for r in json.loads((ROOT/'artifacts/llm-followup-20261110/report.json').read_text())['records']}
checks=[];errors=[];posts=[]
status={p:{'enabled':p=='openai','blocked_reasons':[],'usage':{},'limits':{}} for p in ['openai','dart']}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in [(390,844),(1440,1000)]:
  context=browser.new_context(viewport={'width':width,'height':height})
  mode={'value':'scope'}
  def route(route):
   if route.request.method=='GET':route.fulfill(json=status);return
   posts.append(route.request.url)
   if mode['value']=='failed':
    route.fulfill(json={'status':'failed','execution':'live_provider_request','external_calls_this_request':0,
      'reason':'EXPLANATION_VALIDATION_REJECTED','validation_checks':{'citations_exact':False}});return
   row=rows['scope-mismatch' if mode['value']=='scope' else 'normal-qoq']
   route.fulfill(json={'status':'succeeded','execution':'live_provider_request','external_calls_this_request':0,
    'generated':row['generated'],'explanation_context':build_context(row['tool_result']),
    'model':'archived-response-local-replay','prose_semantics_verified':False})
  context.route('**/api/providers**',route)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(os.getenv('DEMO_URL','http://127.0.0.1:8789'),wait_until='networkidle');page.locator('[data-view="review"]').click()
  button=page.locator('#openai-request');result=page.locator('#openai-result')
  expect(button).to_be_enabled();button.click();expect(button).to_be_enabled()
  expect(result.locator('.generated-explanation')).to_have_text(rows['scope-mismatch']['generated']['explanation_ko'])
  expect(result.locator('.decision-basis')).to_contain_text('연결·별도')
  expect(result.locator('.decision-basis')).to_contain_text('기간 불일치로 판정하지 않았습니다')
  checks.append(f'{width}:scope_prose_unchanged_separate_issue_basis')
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  result.scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'{width}-decision-context.png'),full_page=True)
  mode['value']='failed';button.click();expect(button).to_be_enabled()
  expect(result).to_contain_text('실패 · 검증 통과 아님')
  expect(result).to_contain_text('설명을 표시하지 않습니다')
  expect(result.locator('.generated-explanation')).to_have_count(0)
  expect(result.locator('.explanation-context')).to_have_count(0)
  checks.append(f'{width}:failed_validation_clears_old_prose_and_context')
  mode['value']='normal';button.click();expect(button).to_be_enabled()
  expect(result.locator('.generated-explanation')).to_have_text(rows['normal-qoq']['generated']['explanation_ko'])
  expect(result.locator('.decision-basis')).to_have_count(0)
  checks.append(f'{width}:normal_recovery_drops_scope_warning')
  page.locator('#openai-target').select_option('no-evidence')
  expect(result).to_have_text('대상 변경 · 아직 요청하지 않았습니다.')
  checks.append(f'{width}:target_change_clears_result')
  context.close()
 browser.close()
assert not errors,errors
report={'mode':'local_HTTP_intercepted_provider_responses','checks':checks,'checks_passed':len(checks),
'provider_posts_intercepted':len(posts),'actual_external_calls':0,'new_model_responses':0,'human_review':False,
'physical_mobile':False,'direct_public_HTTPS':False,'page_errors':errors}
(OUT/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
