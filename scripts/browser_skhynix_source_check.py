"""Local live-backend browser checks; only error injection is mocked. No paid calls."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

def main():
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8765');p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    checks=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width,height in [(1365,900),(390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height})
            page.goto(args.url);expect(page.locator('#table-summary')).not_to_have_text('준비 중',timeout=30000)
            page.locator('[data-view="search"]').click()
            expect(page.locator('#source-evidence-query')).to_be_visible(timeout=3000)
            q=page.locator('#source-evidence-query');button=page.locator('#source-evidence-form button')
            q.fill('2024년 DRAM 매출은 전체 매출의 몇 %인가?');button.click()
            box=page.locator('#source-evidence-results')
            expect(box.locator('[data-source-cell]')).to_have_count(2)
            expect(box).to_contain_text('44,731,664');expect(box).to_contain_text('66,192,960')
            expect(box).to_contain_text('계산하지 않았습니다');expect(box).to_contain_text('인쇄 F-146')
            expect(box.locator('a').first).to_have_attribute('href',__import__('re').compile(r'#page=264$'))
            q.fill('2024년 재고가 2023년 매출의 몇 개월분인지 공시표만으로 단정할 수 있나?');button.click()
            expect(box.locator('[data-source-cell]')).to_have_count(3)
            expect(box).to_contain_text('2024-12-31 기준 잔액');expect(box).to_contain_text('2023-01-01 — 2023-12-31')
            expect(box).to_contain_text('정의 확인용 관련 근거')
            page.screenshot(path=str(args.output/f'source-{width}.png'),full_page=True)
            q.fill('2025년 매출');button.click();expect(box).to_contain_text('지원 범위와 다릅니다')
            expect(box.locator('[data-source-cell]')).to_have_count(0)
            page.route('**/api/source-search?*',lambda route:route.fulfill(status=503,json={'detail':'SOURCE_EVIDENCE_UNAVAILABLE'}))
            q.fill('2024년 매출');button.click();expect(box.locator('[role="alert"]')).to_be_visible()
            expect(box.locator('[data-source-cell]')).to_have_count(0)
            page.unroute('**/api/source-search?*');button.click();expect(box.locator('[data-source-cell]')).to_have_count(1)
            page.locator('[data-view="work"]').click();expect(page.locator('#worksheet-rows')).to_contain_text('6.7916')
            overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
            assert not overflow
            checks.append({'viewport':[width,height],'source_search':True,'literal_page_links':True,
                'instant_duration_distinct':True,'unsupported_clears_hits':True,'503_clears_and_recovers':True,
                'legacy_qoq':True,'horizontal_overflow':overflow})
            page.close()
        browser.close()
    (args.output/'report.json').write_text(json.dumps({'checks':checks,'backend':'actual local FastAPI',
        'error_injection':'503 mocked; normal search and recovery use actual backend','paid_calls':0},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(checks))
if __name__=='__main__':main()
