"""Real backend search/progress smoke checks; never invokes external providers."""
import json, os
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
URL=os.getenv('DEMO_URL','http://127.0.0.1:8009')
OUT=Path(os.getenv('PRODUCT_QA_ARTIFACT','work/product-v2.json'))
checks=[]; errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(1440,1000),(390,844)]:
        page=browser.new_page(viewport={'width':width,'height':height})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL,wait_until='networkidle')
        page.locator('[data-view="review"]').click()
        progress=page.locator('#current-evaluation-content')
        expect(progress).to_contain_text('실제 MCP 흐름 8/8 통과')
        expect(progress).to_contain_text('합성 반례 21/21')
        expect(page.locator('#v2-document-table tbody tr')).to_have_count(3)
        assert 'undefined' not in progress.inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        checks.append(f'{width}:current_report_counts_and_no_overflow')
        page.locator('[data-view="search"]').click()
        for query,status in [('삼성전자 2024년 3분기 연결 매출액 3개월 백만원','ready'),('What was Samsung consolidated revenue for Q3 2024 quarter in million KRW?','ready'),('삼성전자 2024 3분기 연결 매출액','needs_clarification'),('Apple 2024 Q3 consolidated revenue quarter million KRW','needs_clarification')]:
            page.locator('#query').fill(query)
            with page.expect_response(lambda r:'/api/search?' in r.url) as resp:
                page.locator('#search-form button').click()
            data=resp.value.json()
            assert data['status']==status,(query,data)
            if status=='ready':
                assert data['hits'][0]['fact_ids']==['s24q3-CFS-revenue-2024-q-KRW']
            if query.startswith('Apple'):assert not data['hits']
            expect(page.locator('#search-results')).not_to_contain_text('검색 중')
            checks.append(f'{width}:search:{query}')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.close()
    browser.close()
assert not errors,errors
report={'created_at':datetime.now(timezone.utc).isoformat(),'base_url':URL,'passed':len(checks),'checks':checks,'page_errors':errors,'external_provider_calls':0,'backend':'real, not intercepted','physical_mobile_device':False}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
