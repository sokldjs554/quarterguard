"""Local HTTP browser checks for dated evidence presentation, no provider POSTs."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.getenv('LATEST_PROGRESS_QA_DIR',str(ROOT/'work/latest-progress-browser')))
OUT.mkdir(parents=True,exist_ok=False)
checks=[];errors=[];posts=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in [(390,844),(1440,1000)]:
  context=browser.new_context(viewport={'width':width,'height':height})
  state={'fail_latest':False,'fail_history':False}
  def route(route):
   if route.request.method=='POST' and '/api/providers/' in route.request.url:
    posts.append(route.request.url);route.abort();return
   if state['fail_latest'] and route.request.url.endswith('/api/evaluation/latest'):
    route.fulfill(status=503,json={'detail':'injected summary error'});return
   if state['fail_history'] and route.request.url.endswith('/api/evaluation/current/progress'):
    route.fulfill(status=503,json={'detail':'injected archive error'});return
   route.continue_()
  context.route('**/api/**',route)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(os.getenv('DEMO_URL','http://127.0.0.1:8791'),wait_until='networkidle')
  page.locator('[data-view="review"]').click()
  current=page.locator('#latest-evidence-summary');past=page.locator('#historical-evaluation')
  expect(current).to_contain_text('참 5·모호 3 → 참 7·모호 1')
  expect(current).to_contain_text('현대차는 공개 작업지에 미등록')
  expect(current).to_contain_text('v5 새 8회')
  expect(current).to_contain_text('7/8 → 8/8')
  expect(current).to_contain_text('참 6·모호 1·거짓 1')
  expect(current).to_contain_text('전체 설명의 개선으로 해석하지 않습니다')
  expect(current).to_contain_text('v6 검수 후 코드 보완')
  expect(current).to_contain_text('새 모델 호출 0회·새 사람 검수 0건')
  expect(current).to_contain_text('v6 새 16회')
  expect(current).to_contain_text('8/8 → 3/8')
  expect(current).to_contain_text('새 과제: 구조 5/8, 제품 검사 4/8')
  expect(current).to_contain_text('기존 8건 참 8·모호 0, 새 8건 참 7·모호 1')
  expect(current).to_contain_text('구조 실패와 자동 제품 판정은 그대로 유지')
  expect(current).not_to_contain_text('변경 후 새 실호출·b 재검수는 아직 없습니다')
  expect(current).to_contain_text('합계 5개')
  expect(current).to_contain_text('직전 기능 변경(f5377ad)')
  expect(past).not_to_have_attribute('open','')
  checks.append(f'{width}:current_evidence_and_limits_separate_from_closed_history')
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  for cell in current.locator('tbody td:nth-child(3)').all():
   box=cell.bounding_box()
   assert box and box['x'] >= 0 and box['x']+box['width'] <= width,box
  expect(page.locator('#heldout-content')).to_contain_text('2026-10-29 과거 기록')
  expect(page.locator('#heldout-content')).not_to_contain_text('현재 실패')
  expect(page.locator('#review > .scope-notice')).not_to_contain_text('사람 검수는 없습니다')
  current.scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'{width}-latest.png'),full_page=True)
  past.locator(':scope > summary').click()
  expect(past).to_contain_text('2026-10-31 당시 평가')
  expect(past).to_contain_text('현재 상태가 아닙니다')
  expect(past.locator('#v2-document-table tbody tr')).to_have_count(3)
  checks.append(f'{width}:original_history_and_failures_still_available')
  state['fail_latest']=True;page.reload(wait_until='networkidle');page.locator('[data-view="review"]').click()
  expect(page.locator('#latest-evidence-error')).to_contain_text('최신 자료를 불러오지 못했습니다')
  expect(page.locator('#latest-evidence-summary')).to_have_count(0)
  expect(page.locator('#historical-evaluation')).to_contain_text('2026-10-31')
  checks.append(f'{width}:latest_failure_never_falls_back_to_old_summary')
  state['fail_latest']=False
  page.get_by_role('button',name='평가 자료 다시 불러오기',exact=True).click()
  expect(page.locator('#latest-evidence-summary')).to_contain_text('최신 근거 요약')
  expect(page.locator('#latest-evidence-error')).to_have_count(0)
  checks.append(f'{width}:latest_retry_recovers_without_stale_error')
  state['fail_history']=True;page.reload(wait_until='networkidle');page.locator('[data-view="review"]').click()
  expect(page.locator('#latest-evidence-summary')).to_be_visible()
  expect(page.locator('#historical-evaluation')).to_contain_text('과거 평가 기록을 불러오지 못했습니다')
  checks.append(f'{width}:historical_failure_does_not_hide_current_evidence')
  context.close()
 browser.close()
assert not errors,errors
assert not posts,posts
report={'mode':'local_HTTP_real_summary_API_with_injected_read_failures','checks_passed':len(checks),'checks':checks,
'page_errors':errors,'provider_calls':0,'new_human_review':False,'physical_mobile':False,'direct_public_HTTPS':False}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
