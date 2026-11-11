"""Real local or public backend; failures/timeouts/delayed delivery are explicit injections."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8781');p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
cases=json.loads(Path('data/apple-submitted-20261112/submission.json').read_text())['cases'];checks=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(1365,900),(390,844)]:
  page=browser.new_page(viewport={'width':width,'height':height},accept_downloads=True)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(a.url);page.locator('[data-view="search"]').click();picker=page.locator('#source-document');picker.select_option('apple-2024-10k')
  q=page.locator('#source-evidence-query');button=page.locator('#apple-review-submit');box=page.locator('#apple-review-result');export=page.locator('#apple-review-export')
  page.locator('#source-evidence-form button').click();expect(page.locator('#source-evidence-results .source-cell-card')).to_have_count(4)
  for i,c in enumerate(cases):
   q.fill(c['question']);expect(export).to_be_disabled();button.click();expect(export).to_be_enabled()
   expect(box).to_contain_text('계산 완료' if i<5 else '판단 보류')
   if i==0:expect(box).to_contain_text('73.8804%');expect(box).to_contain_text('37.1806%')
   if i==2:expect(box).to_contain_text('108,807')
   if i==3:expect(box).to_contain_text('17,399')
   page.screenshot(path=str(a.output/f'{c["id"]}-{width}.png'),full_page=True)
  with page.expect_download() as d:export.click()
  d.value.save_as(a.output/f'export-{width}.json');assert json.loads((a.output/f'export-{width}.json').read_text())['status']=='needs_review'
  q.fill(cases[0]['question']);button.click();expect(box).to_contain_text('73.8804%')
  page.route('**/api/source-review',lambda r:r.fulfill(status=503,json={'detail':'injected failure'}));button.click();expect(box.locator('[role="alert"]')).to_be_visible();expect(box).not_to_contain_text('73.8804%');expect(export).to_be_disabled();page.unroute('**/api/source-review')
  button.click();expect(box).to_contain_text('73.8804%')
  page.route('**/api/source-review',lambda r:r.abort('timedout'));button.click();expect(box.locator('[role="alert"]')).to_be_visible();expect(export).to_be_disabled();page.unroute('**/api/source-review')
  held=[]
  page.route('**/api/source-review',lambda r:held.append((r,r.fetch())))
  button.click()
  while not held:page.wait_for_timeout(20)
  q.fill('2025 제품 서비스 매출총이익률');held[0][0].fulfill(response=held[0][1]);expect(export).to_be_disabled();expect(box).not_to_contain_text('73.8804%');page.unroute('**/api/source-review')
  button.click();expect(box).to_contain_text('확인 필요');expect(box).not_to_contain_text('73.8804%')
  picker.select_option('skh2024annual-in-2025oc');expect(box).not_to_contain_text('73.8804%');expect(export).to_be_disabled()
  page.locator('#source-calculator summary').click();expect(page.locator('#source-calc-submit')).to_be_enabled();page.locator('#source-calc-submit').click();expect(page.locator('#source-calc-result')).to_contain_text('47.6820%')
  page.locator('[data-view="work"]').click();expect(page.locator('#worksheet-rows')).to_contain_text('6.7916')
  assert not errors,errors
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  checks.append({'viewport':[width,height],'human_development_cases':7,'real_backend':a.url,'exports':True,'injected_503_recovery':True,'injected_transport_timeout':True,'late_delivery_after_edit_ignored':True,'document_switch':True,'sk_balance':True,'samsung_quarter':True,'page_errors':errors})
  page.close()
 browser.close()
(a.output/'report.json').write_text(json.dumps({'checks':checks,'tls_note':'Local HTTP unless URL explicitly HTTPS; browser never ignores HTTPS certificate errors.','new_paid_calls':0},indent=2))
print(json.dumps(checks))
