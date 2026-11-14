"""Actual download and File API reopen; synthetic error/race probes explicitly labeled."""
import argparse,json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright,expect

A7='2024년 중국권 매출 감소는 판매량 감소만으로 설명할 수 있나?'

def main():
 p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--transport',required=True,choices=['local_http','direct_https','tls_verified_relay']);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 report={'actor':'AI-operated Playwright','human_participation':False,'transport':a.transport,'url':a.url,'new_paid_calls':0,'started_at_kst':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'checks':[],'status':'running'}
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);report['browser_version']=browser.version
   for width,height in [(1365,900),(390,844)]:
    page=browser.new_page(viewport={'width':width,'height':height},accept_downloads=True)
    page.set_default_timeout(20000);errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append({'method':r.method,'url':r.url}))
    page.goto(a.url,timeout=60000);page.locator('[data-view="analysis"]').click();page.locator('#source-document').select_option('apple-2024-10k')
    q=page.locator('#source-evidence-query');q.fill(A7);page.locator('#apple-review-submit').click();expect(page.locator('#apple-review-export')).to_be_enabled()
    with page.expect_download() as pending:page.locator('#apple-review-export').click()
    saved=a.output/f'A7-{width}.json';pending.value.save_as(saved);original=json.loads(saved.read_text())
    page.locator('#saved-json-reader>summary').click();field=page.get_by_label('내려받은 JSON 파일 선택');status=page.locator('#saved-json-status');summary=page.locator('#saved-json-summary');content=page.locator('#saved-json-content');error=page.locator('#saved-json-error')
    def choose_file(value):
     with page.expect_file_chooser() as chooser:field.click()
     chooser.value.set_files(value)
    page.wait_for_load_state('networkidle');start=len(requests)
    choose_file(saved);expect(status).to_contain_text('일치합니다');expect(summary).to_contain_text(A7);expect(summary).to_contain_text('인쇄 22');expect(summary).to_contain_text('CAUSAL_DECOMPOSITION_REQUIRED');expect(summary).to_contain_text('USD')
    assert page.locator('#saved-json-raw').text_content()==saved.read_text()
    assert field.evaluate('(el)=>el.files[0]?.name')==saved.name, 'Selected file name must remain visible after reading'
    assert len(requests)==start,requests[start:]
    page.screenshot(path=str(a.output/f'A7-reopened-{width}.png'),full_page=True)
    # A modified file is a synthetic negative case, never a new original document.
    changed={**original,'query':'different question','messages':['<img src=x onerror="window.untrustedRan=1">']}
    start=len(requests);choose_file({'name':'changed.json','mimeType':'application/json','buffer':json.dumps(changed).encode()})
    expect(status).to_contain_text('내용이 다릅니다');expect(summary).to_contain_text('<img src=x');expect(summary.locator('img')).to_have_count(0);assert page.evaluate('window.untrustedRan') is None;assert len(requests)==start
    choose_file({'name':'broken.json','mimeType':'application/json','buffer':b'{bad'})
    expect(error).to_be_visible();expect(content).to_be_hidden();expect(status).not_to_contain_text('일치합니다')
    choose_file({'name':'big.json','mimeType':'application/json','buffer':b' '*(1048577)})
    expect(error).to_contain_text('1MB');expect(content).to_be_hidden()
    choose_file(saved);expect(status).to_contain_text('일치합니다')
    field.dispatch_event('cancel');expect(content).to_be_hidden();expect(status).not_to_contain_text('일치합니다')
    # Simulate an OS read error; test only, never an observed participant failure.
    page.evaluate("() => {window.originalFileText=File.prototype.text;File.prototype.text=function(){return Promise.reject(new Error('injected read failure'))}}")
    choose_file(saved);expect(error).to_contain_text('injected read failure');expect(content).to_be_hidden()
    page.evaluate('() => {File.prototype.text=window.originalFileText}')
    # Simulate an in-flight read completing after the query has changed.
    page.evaluate("() => {File.prototype.text=function(){const f=this;return new Promise(resolve=>{window.releaseFileRead=()=>window.originalFileText.call(f).then(resolve)})}}")
    choose_file(saved);expect(status).to_contain_text('읽는 중');q.fill('2024 제품 서비스 매출총이익률');page.evaluate('window.releaseFileRead()');page.evaluate('() => {File.prototype.text=window.originalFileText}')
    expect(content).to_be_hidden();expect(status).not_to_contain_text('일치합니다')
    choose_file(saved);expect(status).to_contain_text('현재 비교할 검토 결과가 없습니다')
    q.fill(A7);page.locator('#apple-review-submit').click();expect(page.locator('#apple-review-export')).to_be_enabled();choose_file(saved);expect(status).to_contain_text('일치합니다')
    page.locator('#source-document').select_option('skh2024annual-in-2025oc');expect(content).to_be_hidden();page.locator('#source-calculator summary').click();mode=page.locator('#source-calc-mode');expect(mode).to_be_enabled();mode.select_option('inventory_months');page.locator('#source-calc-submit').click();expect(page.locator('#source-calc-export')).to_be_enabled()
    with page.expect_download() as pending:page.locator('#source-calc-export').click()
    sk=a.output/f'S4-{width}.json';pending.value.save_as(sk);page.wait_for_load_state('networkidle');start=len(requests);choose_file(sk)
    expect(status).to_contain_text('일치합니다');expect(summary).to_contain_text('13313937');expect(summary).to_contain_text('32765719');expect(summary).to_contain_text('F-73');expect(summary).to_contain_text('F-75');expect(summary).to_contain_text('RATIO_DEFINITION_REQUIRED');expect(summary).to_contain_text('계산하지 않음');assert page.locator('#saved-json-raw').text_content()==sk.read_text();assert len(requests)==start
    page.screenshot(path=str(a.output/f'S4-reopened-{width}.png'),full_page=True)
    mode.select_option('balance_yoy');expect(content).to_be_hidden();expect(status).not_to_contain_text('일치합니다')
    assert not errors,errors
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    report['checks'].append({'viewport':[width,height],'actual_A7_file_reopened':True,'actual_S4_file_reopened':True,'parsed_match_current_result':True,'raw_matches_downloaded_bytes_as_text':True,'file_read_network_requests':0,'modified_file_mismatch':True,'HTML_not_executed':True,'invalid_and_large_file_clear_prior_success':True,'injected_read_error_clears_prior_success':True,'injected_delayed_read_after_edit_ignored':True,'no_current_result_not_claimed_match':True,'document_and_selection_change_clear_match':True,'page_errors':errors})
    page.close()
   browser.close()
  report['status']='passed'
 except Exception as e:
  report['status']='failed';report['error']=f'{type(e).__name__}: {e}';raise
 finally:
  report['finished_at_kst']=datetime.now(ZoneInfo('Asia/Seoul')).isoformat();(a.output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
