"""Browser regression for the approved design's readable comparison layout."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8021');p.add_argument('--out',default='/tmp/workbook-layout');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);results=[]
 for w,h in [(1440,1000),(390,844),(320,568)]:
  page=b.new_page(viewport={'width':w,'height':h});page.goto(a.url+'/#work');expect(page.locator('#export-btn')).to_be_enabled();page.evaluate('window.scrollTo(0,0)');first=page.locator('#worksheet-rows tr').first;last=page.locator('#worksheet-rows tr').last
  fb=first.bounding_box();lb=last.bounding_box();page.screenshot(path=str(out/f'work-{w}.png'),full_page=True)
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),f'{w}: page overflows'
  if w==1440:
   assert fb['y']<300,f'First comparison row is below the approved working area: {fb["y"]}'
   assert lb['y']+lb['height']<650,f'Sixth row below 650: {lb}'
  else:
   for locator in [first.locator('[data-fact]').nth(0),first.locator('[data-fact]').nth(1),first.locator('.growth'),first.locator('.status-cell')]:
    box=locator.bounding_box();assert box['x']>=0 and box['x']+box['width']<=w,f'{w}: both amounts and verdict must fit'
   page.locator('[data-quick="scope"]').focus();page.keyboard.press('Tab');page.keyboard.press('Tab')
   assert not page.evaluate('document.activeElement.id.startsWith("quick-")'),'Mobile keyboard focus must not enter clipped duplicate desktop controls'
  results.append({'width':w,'first_row':fb,'last_row':lb});page.close()
 b.close();(out/'layout.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
