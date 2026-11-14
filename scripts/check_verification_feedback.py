"""Observe pending UI with held browser routes; distinguish replay/fault injection from live MCP."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8021');p.add_argument('--out',default='/tmp/verification-feedback');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
checks=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (1440,390,320):
  page=browser.new_page(viewport={'width':width,'height':1000 if width==1440 else 844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(a.url+'/#work');expect(page.locator('#export-btn')).to_be_enabled()
  # Capture the real preview response, replay only to exercise the pending UI deterministically.
  request={'mode':'qoq','current':{'document':'s24q3','year':2024,'scope':'CFS','period':'q','currency':'KRW'},'base':{'document':'s24q2','year':2024,'scope':'CFS','period':'q','currency':'KRW'}}
  payload=page.request.post(a.url+'/api/worksheet',data=request).json()
  expect(page.locator('.sheet-legend')).to_contain_text('항목명')
  page.locator('.metric-name[data-metric="operating_profit"]').click();expect(page.locator('#comparison-chart')).to_contain_text('-12.0693%')
  cells=page.locator('#worksheet-rows [data-fact]').all_text_contents();held=[]
  page.route('**/api/worksheet/run',lambda route:held.append(route));page.locator('#run-btn').click()
  expect(page.locator('#verification-progress')).to_contain_text('이전 결과 · 재검증 중');expect(page.locator('#worksheet-rows tr')).to_have_count(6)
  assert page.locator('#worksheet-rows [data-fact]').all_text_contents()==cells
  assert all(t=='재검증 중' for t in page.locator('#worksheet-rows .status-cell').all_text_contents())
  expect(page.locator('#export-btn')).to_be_disabled();expect(page.locator('#finance-source-btn')).to_be_disabled();expect(page.locator('.metric-name').first).to_be_disabled()
  assert page.locator('#comparison-chart').evaluate('(e)=>e.inert')
  expect(page.locator('#verification-progress [aria-current="step"]')).to_contain_text('응답 대기')
  page.screenshot(path=str(out/f'pending-{width}.png'),full_page=True)
  held.pop().fulfill(json=payload);expect(page.locator('#export-btn')).to_be_enabled();expect(page.locator('#verification-progress')).to_have_attribute('data-state','done')
  expect(page.locator('#comparison-chart')).to_contain_text('-12.0693%')
  checks.append({'width':width,'check':'same selection retains values; pending labels, locked export/source; replay restores selected metric','method':'real preview response replay, not a live MCP run'})
  for fault in ('http503','tool_timeout','abort','empty_success'):
   page.locator('#run-btn').click();expect(page.locator('#desk')).to_have_attribute('aria-busy','true');expect(page.locator('#verification-progress')).to_contain_text('재검증 중')
   route=held.pop()
   if fault=='http503':route.fulfill(status=503,body='injected unavailable')
   elif fault=='tool_timeout':route.fulfill(json={**payload,'workflow_success':False,'rows':[],'issues':['TOOL_TIMEOUT']})
   elif fault=='abort':route.abort('timedout')
   else:route.fulfill(json={**payload,'rows':[]})
   expect(page.locator('#verification-progress')).to_have_attribute('data-state','failed');expect(page.locator('#worksheet-rows [data-fact]')).to_have_count(0);expect(page.locator('#comparison-chart')).to_be_hidden();expect(page.locator('#export-btn')).to_be_disabled();expect(page.locator('#finance-source-btn')).to_be_disabled()
   checks.append({'width':width,'check':fault+' clears retained values, chart and export','method':'injected browser fault'})
   page.locator('#run-btn').click();expect(page.locator('#desk')).to_have_attribute('aria-busy','true');held.pop().fulfill(json=payload);expect(page.locator('#export-btn')).to_be_enabled()
  page.unroute('**/api/worksheet/run')
  # A condition change must clear the old table immediately, not reuse it.
  changed=[];page.route('**/api/worksheet',lambda route:changed.append(route))
  page.locator('#quick-period' if width>700 else '[data-quick="period"]').select_option('ytd');expect(page.locator('#worksheet-rows [data-fact]')).to_have_count(0);expect(page.locator('#export-btn')).to_be_disabled();expect(page.locator('#verification-progress')).to_be_hidden()
  changed.pop().fulfill(json={**payload,'workflow_success':False,'rows':[],'issues':['TOOL_ERROR']});expect(page.locator('#desk')).to_have_attribute('aria-busy','false')
  checks.append({'width':width,'check':'changed condition removes old result immediately','method':'held request / injected failure'})
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');assert not errors,errors;page.close()
 browser.close()
(out/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print(f'{len(checks)} checks passed; held/replayed/injected responses explicitly separated from live execution')
