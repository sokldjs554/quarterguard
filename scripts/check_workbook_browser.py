"""Actual browser/API workflow checks; injected failures explicitly identified."""
import argparse,csv,json
from pathlib import Path
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright,expect
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8021');parser.add_argument('--out',default='/tmp/qg-workbook-browser');parser.add_argument('--commit',default='');parser.add_argument('--tls-relay',action='store_true');parser.add_argument('--no-failure-injection',action='store_true');args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
expect.set_options(timeout=60000);checks=[];errors=[];paid=[];mcp=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w,h in [(1440,1000),(390,844)]:
  page=browser.new_page(viewport={'width':w,'height':h},accept_downloads=True);page.set_default_timeout(60000)
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:paid.append(r.url) if r.method=='POST' and '/api/providers/' in r.url else None)
  def ready():
   expect(page.locator('#desk')).to_have_attribute('aria-busy','false');expect(page.locator('#worksheet-rows tr')).to_have_count(6);expect(page.locator('#export-btn')).to_be_enabled()
  def check(name,kind='actual API / automated browser'):
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow: {w} {name}'
   checks.append({'width':w,'name':name,'kind':kind})
  def quick(key,value):
   page.locator('#quick-'+key if w>700 else '[data-quick="'+key+'"]').select_option(value);ready()
  response=page.goto(args.url+'/#work',wait_until='networkidle',timeout=90000)
  if args.tls_relay:assert response.headers.get('x-qa-tls-verified')=='true'
  ready()
  if args.commit:expect(page.locator('#version')).to_contain_text(args.commit[:7])
  expect(page.locator('#comparison-chart')).to_contain_text('6.7916%');expect(page.locator('.finance-bars')).to_be_visible();check('normal six rows and chart')
  page.screenshot(path=str(out/f'work-{w}.png'),full_page=True)
  page.locator('.metric-name[data-metric="operating_profit"]').click();expect(page.locator('#comparison-chart')).to_contain_text('-12.0693%');expect(page.locator('.metric-name[data-metric="operating_profit"]')).to_have_attribute('aria-pressed','true');check('selected operating profit and signed growth')
  page.locator('#worksheet-rows [data-fact][data-side="base"]').first.click();expect(page.locator('#finance-source-content')).to_contain_text('48쪽');expect(page.locator('#finance-source-content')).to_contain_text('74,068,302');assert page.locator('#finance-source-content a').first.get_attribute('href').endswith('#page=48');check('B evidence exact value and page')
  page.locator('[data-inspect-side="base"]').click();expect(page.locator('#source-panel')).to_be_visible();expect(page.locator('#evidence-content')).to_contain_text('74,068,302');page.screenshot(path=str(out/f'evidence-{w}.png'),full_page=True);page.locator('[data-return-compare]').first.click();check('source table and return to comparison')
  quick('period','ytd');expect(page.locator('#worksheet-rows tr').first).to_contain_text('145,983,903');expect(page.locator('.finance-bars')).to_have_count(0);expect(page.locator('#worksheet-rows .growth')).to_have_text(['—']*6);expect(page.locator('#comparison-recovery')).to_be_visible();assert page.locator('#comparison-recovery').bounding_box()['y']<page.locator('#worksheet-rows').bounding_box()['y'];check('period hold and recovery action above table')
  page.screenshot(path=str(out/f'period-hold-{w}.png'),full_page=True)
  page.locator('#comparison-recovery [data-review-setting="base-period"]').click();expect(page.locator('#base-period')).to_be_focused();page.locator('#base-period').select_option('q');ready();page.locator('#settings-results').click();expect(page.locator('#comparison-settings')).not_to_be_visible();expect(page.locator('#comparison-chart')).to_contain_text('6.7916%');check('edit condition then close settings and return')
  quick('scope','OFS');expect(page.locator('#worksheet-rows tr').first).to_contain_text('53,734,118');expect(page.locator('.finance-bars')).to_have_count(0);page.locator('[data-finance-source="base"]').click();expect(page.locator('#finance-source-content')).to_contain_text('104쪽');page.keyboard.press('Escape');check('scope hold and separate statement page 104')
  quick('period','ytd');expect(page.locator('#finding')).to_contain_text('연결 범위 불일치');expect(page.locator('#finding')).to_contain_text('기간 불일치');check('combined mismatch')
  page.locator('#stage-notes').click();page.locator('#review-note').fill('자동 UI 회귀 확인 · 실제 참여 기록 아님');page.locator('#save-note').click();expect(page.locator('#note-status')).to_contain_text('저장됨');page.locator('#mark-reviewed').click();expect(page.locator('#mark-reviewed')).to_have_attribute('aria-pressed','true');page.locator('#stage-compare').click();expect(page.locator('#worksheet-rows .growth')).to_have_text(['—']*6);check('existing personal note and mark do not approve held comparison')
  page.locator('#stage-notes').click();page.locator('#review-note').fill('');page.locator('#save-note').click();page.locator('#mark-reviewed').click();page.locator('#stage-compare').click();quick('period','q');quick('scope','CFS');expect(page.locator('#comparison-chart')).to_contain_text('6.7916%');check('normal recovery')
  page.locator('#settings-btn').click();page.locator('#mode').select_option('yoy');ready();page.locator('#base-document').select_option('s24q3');ready();page.locator('#base-year').select_option('2023');ready();expect(page.locator('#comparison-chart')).to_contain_text('17.3491%');expect(page.locator('#base-heading-label')).to_contain_text('2023');expect(page.locator('#quick-document')).to_have_value('s24q3');check('full settings YoY and quick-header synchronization')
  page.locator('#current-currency').select_option('USD');ready();expect(page.locator('.finance-bars')).to_have_count(0);expect(page.locator('#worksheet-rows .growth')).to_have_text(['—']*6);check('currency mismatch never plotted as verified')
  page.locator('#reset-btn').click();ready();page.locator('#settings-results').click()
  with page.expect_download() as dl:page.locator('#export-btn').click()
  path=out/f'comparison-{w}.csv';dl.value.save_as(path);rows=list(csv.reader(path.open(encoding='utf-8-sig')));assert len(rows)==7 and len(rows[0])==25;assert '6.7916' in rows[1];check('original CSV export with 25 columns preserved')
  page.locator('[data-view="search"]').click();page.locator('#search-form button').click();expect(page.locator('[data-use-fact]').first).to_be_visible();page.screenshot(path=str(out/f'search-{w}.png'),full_page=True);page.locator('[data-use-fact]').first.click();ready();check('natural-language search candidate to comparison')
  page.locator('[data-view="analysis"]').click();page.locator('#source-document').select_option('apple-2024-10k');page.locator('#apple-review-submit').click();expect(page.locator('#apple-review-result')).to_contain_text('73.8804%');page.screenshot(path=str(out/f'apple-{w}.png'),full_page=True);check('Apple product and service margins')
  page.locator('#source-evidence-query').fill('2024년 중국권 매출 감소는 판매량 감소만으로 설명할 수 있나?');expect(page.locator('#apple-review-export')).to_be_disabled();page.locator('#apple-review-submit').click();expect(page.locator('#apple-review-result')).to_contain_text('판단 보류')
  with page.expect_download() as dl:page.locator('#apple-review-export').click()
  path=out/f'apple-held-{w}.json';dl.value.save_as(path);assert json.loads(path.read_text())['status']=='needs_review';page.locator('#saved-json-reader>summary').click();page.set_input_files('#saved-json-file',str(path));expect(page.locator('#saved-json-status')).to_contain_text('일치합니다');check('Apple held result download and in-app JSON comparison')
  page.locator('#source-evidence-query').fill('2024년 자사주 매입에 쓴 현금은 2023년보다 얼마나 늘었나?');expect(page.locator('#apple-review-export')).to_be_disabled();expect(page.locator('#apple-review-result')).not_to_contain_text('판단 보류');page.locator('#apple-review-submit').click();expect(page.locator('#apple-review-result')).to_contain_text('17,399');check('Apple question change invalidates previous result')
  page.locator('#source-document').select_option('skh2024annual-in-2025oc');page.locator('#source-calculator>summary').click();expect(page.locator('#source-calc-submit')).to_be_enabled();page.locator('#source-calc-submit').click();expect(page.locator('#source-calc-result')).to_contain_text('47.6820%');page.screenshot(path=str(out/f'sk-{w}.png'),full_page=True);check('SK actual balance change')
  page.locator('#source-calc-mode').select_option('product_share');page.locator('#source-calc-submit').click();expect(page.locator('#source-calc-result')).to_contain_text('67.5777%');check('SK product revenue share')
  page.locator('#source-calc-mode').select_option('inventory_months');page.locator('#source-calc-submit').click();expect(page.locator('#source-calc-result')).to_contain_text('계산 보류')
  with page.expect_download() as dl:page.locator('#source-calc-export').click()
  path=out/f'sk-held-{w}.json';dl.value.save_as(path);assert json.loads(path.read_text())['status']=='needs_review';page.set_input_files('#saved-json-file',str(path));expect(page.locator('#saved-json-status')).to_contain_text('일치합니다');check('SK inventory hold and JSON roundtrip')
  page.locator('[data-view="home"]').click();expect(page.locator('.finance-document-index>button')).to_have_count(3);page.screenshot(path=str(out/f'library-{w}.png'),full_page=True);page.locator('[data-start="apple"]').click();expect(page.locator('#source-document')).to_have_value('apple-2024-10k');check('document library opens real Apple workflow')
  page.locator('[data-view="review"]').click();expect(page.locator('#current-evaluation-content')).not_to_be_empty();page.screenshot(path=str(out/f'review-{w}.png'),full_page=True);check('preserved historical and current evidence records')
  page.locator('[data-view="work"]').click();ready()
  if w==1440:
   page.locator('#run-btn').click();expect(page.locator('#execution-status')).to_contain_text('실제 MCP 재검증 완료',timeout=90000);page.locator('#trace-btn').click();expect(page.locator('#trace-content')).to_contain_text('18회 도구 호출');(out/'actual-mcp.txt').write_text(page.locator('#trace-content').inner_text());mcp.append(18);page.locator('#close-trace').click();check('actual 18 MCP tools, not prepared replay')
   if not args.no_failure_injection:
    page.route('**/api/worksheet',lambda route:route.fulfill(status=503,content_type='application/json',body='{"detail":"injected unavailable"}'))
    page.locator('#quick-period').select_option('ytd');expect(page.locator('#work-alert')).to_be_visible();expect(page.locator('#export-btn')).to_be_disabled();expect(page.locator('.finance-bars')).to_have_count(0);expect(page.locator('#finance-source-btn')).to_be_disabled();expect(page.locator('#worksheet-rows')).not_to_contain_text('79,098,731');expect(page.locator('#finance-source-content')).to_be_empty();check('failed request clears chart, source and export','injected HTTP 503')
    page.screenshot(path=str(out/'injected-503.png'),full_page=True);page.unroute('**/api/worksheet');quick('period','q');check('recovery after injected error')
  page.close()
 browser.close()
assert not errors,errors
assert not paid,paid
report={'at':datetime.now(timezone.utc).isoformat(),'checks':checks,'passed':len(checks),'errors':errors,'paid_provider_calls':0,'actual_mcp_tools':mcp,'actor':'AI Playwright; not human validation','transport':'TLS-verified fixed-origin relay' if args.tls_relay else 'local HTTP','commit_expected':args.commit,'physical_device':False}
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'passed':len(checks),'actual_mcp_tools':mcp,'paid_calls':len(paid),'errors':errors}))
