import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
url=os.getenv('DEMO_URL','http://127.0.0.1:8000');checks=[]
OUT=Path(os.getenv('QA_OUTPUT_DIR',str(ROOT)));(OUT/'docs/images').mkdir(parents=True,exist_ok=True);(OUT/'artifacts').mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url,wait_until='networkidle');page.get_by_text('+6.7916',exact=False).wait_for()
 page.screenshot(path=str(OUT/'docs/images/desktop.png'),full_page=True)
 checks.append('desktop_initial_prepared')
 page.get_by_role('button',name='MCP 실행').click();page.get_by_text('실제 MCP 실행',exact=False).wait_for(timeout=35000)
 checks.append('actual_mcp_run')
 page.locator('[data-evidence]').first.click();page.locator('dialog[open]').wait_for();assert '79,098,731' in page.locator('#evidence-content').inner_text();assert '#page=34' in page.locator('#evidence-content a').get_attribute('href')
 page.get_by_role('button',name='닫기',exact=True).click();checks.append('source_dialog_and_pdf_page')
 ids=['ytd-trap','scope-trap','currency-trap','negative-base','no-evidence','qoq-profit','reconcile-revenue','qoq-revenue']
 for cid in ids:
  page.locator(f'[data-case="{cid}"]').click();page.locator('#loading').wait_for(state='hidden');assert page.locator('#result-area').inner_text().strip();checks.append('prepared_'+cid)
 page.locator('[data-case="reconcile-revenue"]').click();page.locator('#loading').wait_for(state='hidden');assert '79,098,731' in page.locator('.result-number').inner_text()
 page.get_by_role('button',name='MCP 실행').click();page.get_by_text('실제 MCP 실행',exact=False).wait_for(timeout=35000);checks.append('actual_reconcile')
 page.locator('[data-tab="search"]').click();page.locator('#search-form button').click();page.locator('.search-hit').first.wait_for();checks.append('search_evidence')
 page.locator('#query').fill('samsung 2025 Q3 CFS revenue quarter KRW');page.locator('#search-form button').click();page.get_by_text('검색 결과 없음',exact=False).wait_for();checks.append('search_empty')
 for query in ['samsung 2024 Q3 CFS revenue quarter CHF','SK hynix 2024 Q3 CFS revenue quarter KRW']:
  page.locator('#query').fill(query);page.locator('#search-form button').click();page.get_by_text('검색 결과 없음',exact=False).wait_for();checks.append('unsupported_'+query.split()[0])
 page.route('**/api/search?*',lambda route:route.abort());page.locator('#search-form button').click();page.locator('#search-results [role="alert"]').wait_for();checks.append('search_network_error');page.unroute('**/api/search?*')
 page.locator('[data-tab="eval"]').click();assert page.locator('#eval-content tbody tr').count()==6;page.screenshot(path=str(OUT/'docs/images/evaluation.png'),full_page=True);checks.append('evaluation_six_configurations')
 page.locator('[data-tab="work"]').click();page.route('**/api/run/*',lambda route:route.fulfill(status=503,body='{}'));page.get_by_role('button',name='MCP 실행').click();page.locator('#alert').wait_for(state='visible');assert '연결 오류' in page.locator('#alert').inner_text();checks.append('run_api_unavailable');page.unroute('**/api/run/*')
 page.get_by_role('button',name='준비 결과',exact=True).click();page.locator('#loading').wait_for(state='hidden');assert '79,098,731' in page.locator('#result-area').inner_text();checks.append('recovery_after_error')
 mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
 mobile.goto(url,wait_until='networkidle');mobile.get_by_text('+6.7916',exact=False).wait_for();assert mobile.evaluate('document.documentElement.scrollWidth<=window.innerWidth');mobile.screenshot(path=str(OUT/'docs/images/mobile.png'),full_page=True);checks.append('mobile_layout_no_overflow')
 mobile.locator('[data-case="ytd-trap"]').click();mobile.locator('#loading').wait_for(state='hidden');assert '확인 필요' in mobile.locator('#result-area').inner_text();mobile.locator('[data-evidence]').first.click();mobile.locator('dialog[open]').wait_for();checks.append('mobile_case_and_source')
 fail=browser.new_page();fail.route('**/api/cases',lambda r:r.abort());fail.goto(url);fail.get_by_text('서비스 연결 불가').wait_for();assert fail.locator('#run-btn').is_disabled();checks.append('boot_network_failure')
 browser.close()
result={'base_url':url,'checks':checks,'passed':len(checks),'page_errors':errors,'browser':'Chromium via Playwright','viewports':['1440x1100','390x844']}
(OUT/'artifacts/browser-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2));assert not errors
