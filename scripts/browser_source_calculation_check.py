"""Real backend browser calculations; error/timeout/late delivery explicitly injected."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright,expect
from quarterguard.source_evidence import load_source

def main():
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8770');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--backend-label',default='actual local FastAPI');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    ids={(c['metric'],c['year']):c['id'] for c in load_source()[1]};checks=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width,height in [(1365,900),(390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height},accept_downloads=True)
            page.goto(a.url);page.locator('[data-view="search"]').click()
            expect(page.locator('#source-calculator summary')).to_be_visible(timeout=3000)
            page.locator('#source-calculator summary').click()
            mode=page.locator('#source-calc-mode');current=page.locator('#source-calc-current');base=page.locator('#source-calc-base')
            button=page.locator('#source-calc-submit');result=page.locator('#source-calc-result');export=page.locator('#source-calc-export')
            expect(button).to_be_enabled();button.click()
            expect(result).to_contain_text('47.6820%');expect(result).to_contain_text('3,617,788')
            expect(result).to_contain_text('2024-12-31');expect(result).to_contain_text('2023-12-31')
            with page.expect_download() as d:export.click()
            saved=a.output/f'result-{width}.json';d.value.save_as(saved)
            assert json.loads(saved.read_text())['growth_pct']=='47.6820'
            mode.select_option('annual_yoy');expect(export).to_be_disabled();expect(result).not_to_contain_text('47.6820%')
            current.select_option(ids['operating_profit',2024]);base.select_option(ids['operating_profit',2023]);button.click()
            expect(result).to_contain_text('31,197,632');expect(result).to_contain_text('증감률 보류');expect(result).to_contain_text('적자에서 흑자로 전환')
            mode.select_option('product_share');button.click();expect(result).to_contain_text('67.5777%')
            expect(result).to_contain_text('제품 매출 비중');expect(result).not_to_contain_text('증감률 67.5777')
            base.select_option(ids['product_total',2023]);button.click();expect(result).to_contain_text('계산 보류');expect(result).not_to_contain_text('67.5777%')
            mode.select_option('inventory_months');button.click();expect(result).to_contain_text('분모');expect(result).to_contain_text('자동 계산하지 않습니다')
            page.screenshot(path=str(a.output/f'clarification-{width}.png'),full_page=True)
            mode.select_option('balance_yoy');button.click();expect(result).to_contain_text('47.6820%')
            page.route('**/api/source-calculations',lambda route:route.fulfill(status=503,json={'detail':'SOURCE_EVIDENCE_UNAVAILABLE'}))
            button.click();expect(result.locator('[role="alert"]')).to_be_visible();expect(export).to_be_disabled();expect(result).not_to_contain_text('47.6820%')
            page.unroute('**/api/source-calculations');button.click();expect(result).to_contain_text('47.6820%')
            page.route('**/api/source-calculations',lambda route:route.abort('timedout'))
            button.click();expect(result.locator('[role="alert"]')).to_be_visible();expect(export).to_be_disabled()
            page.unroute('**/api/source-calculations')
            held=[]
            def hold(route):held.append((route,route.fetch()))
            page.route('**/api/source-calculations',hold);button.click();page.wait_for_function("document.querySelector('#source-calc-result').textContent.includes('확인 중')")
            # Force delivery after a user changes the selected cell.
            while not held:page.wait_for_timeout(20)
            current.select_option(ids['inventory',2024]);held[0][0].fulfill(response=held[0][1])
            expect(result).not_to_contain_text('47.6820%');expect(export).to_be_disabled()
            page.unroute('**/api/source-calculations')
            base.select_option(ids['inventory',2023]);button.click();expect(result).to_contain_text('-166,722')
            page.screenshot(path=str(a.output/f'balance-{width}.png'),full_page=True)
            # A source candidate can be selected into explicit A/B conditions.
            page.locator('#source-evidence-query').fill('2024년 DRAM 매출');page.locator('#source-evidence-form button').click()
            expect(page.locator('[data-calc-side="current"]')).to_have_count(1)
            page.locator('[data-calc-side="current"]').click();expect(current).to_have_value(ids['dram',2024]);expect(export).to_be_disabled()
            page.locator('[data-view="work"]').click();expect(page.locator('#worksheet-rows')).to_contain_text('6.7916')
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
            checks.append({'viewport':[width,height],'cash':True,'negative_base':True,'share':True,'wrong_period_blocked':True,
                'inventory_definition':True,'export':True,'edit_invalidates':True,'503_recovery':True,'injected_transport_timeout':True,
                'late_response_ignored':True,'source_candidate_selection':True,'legacy_quarter':True})
            page.close()
        browser.close()
    (a.output/'report.json').write_text(json.dumps({'backend':a.backend_label,'checks':checks,'injections':['503','transport timeout','delayed delivery of actual response'],'paid_calls':0},indent=2)+'\n')
    print(json.dumps(checks))
if __name__=='__main__':main()
