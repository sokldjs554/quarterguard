"""Behavior checks for the document worksheet; no external API keys required."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
URL = os.getenv('DEMO_URL', 'http://127.0.0.1:8005')
OUT = Path(os.getenv('QA_OUTPUT_DIR', str(ROOT)))
(OUT / 'docs/images').mkdir(parents=True, exist_ok=True)
(OUT / 'artifacts').mkdir(parents=True, exist_ok=True)
checks, errors = [], []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    page.on('pageerror', lambda e: errors.append(str(e)))

    def ready(pg=page):
        expect(pg.locator('#desk')).to_have_attribute('aria-busy', 'false', timeout=65000)
        expect(pg.locator('#worksheet-rows tr')).to_have_count(6)

    def settings(pg=page):
        if pg.locator('#comparison-settings').is_hidden():
            pg.locator('#settings-btn').click()

    def reset(pg=page):
        settings(pg)
        pg.locator('#reset-btn').click()
        ready(pg)

    page.goto(URL, wait_until='networkidle')
    ready()
    expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
    expect(page.locator('#execution-status')).to_contain_text('현재 MCP 호출 없음')
    assert not page.locator('.rail, .case-list, .hero-result').count()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(OUT / 'docs/images/desktop.png'), full_page=True)
    checks.append('document_worksheet_six_rows_no_case_gallery')

    page.locator('[data-fact="s24q2-CFS-operating_profit-2024-q-KRW"]').click()
    expect(page.locator('#source-counter')).to_have_text('B 비교 · 영업이익')
    expect(page.locator('.selected-location')).to_contain_text('10,443,878')
    assert '#page=48' in page.locator('#publisher-link').get_attribute('href')
    expect(page.locator('.chosen-cell')).to_have_text('10,443,878')
    checks.append('clicked_number_tracks_document_row_column')

    page.locator('[data-source-index="0"]').click()
    expect(page.locator('#source-counter')).to_have_text('A 기준 · 영업이익')
    expect(page.locator('.number-button.active')).to_have_attribute('data-side', 'current')
    page.locator('[data-source-index="1"]').focus()
    page.keyboard.press('Enter')
    expect(page.locator('[data-source-index="1"]')).to_be_focused()
    expect(page.locator('.number-button.active')).to_have_attribute('data-side', 'base')
    checks.append('source_switch_sync_and_keyboard_focus')

    # Simulate an unavailable publisher PDF. The direct link and reconstructed
    # table remain available; this is not a claim of PDF rendering success.
    page.route('https://images.samsung.com/**', lambda r: r.abort())
    page.locator('[data-source-mode="pdf"]').focus()
    page.keyboard.press('Enter')
    expect(page.locator('[data-source-mode="pdf"]')).to_be_focused()
    expect(page.locator('.pdf-frame')).to_have_attribute('src', __import__('re').compile(r'#page=48$'))
    expect(page.locator('.pdf-notice')).to_contain_text('표시가 제한되면')
    page.locator('[data-source-mode="table"]').click()
    expect(page.locator('.paper-caption')).to_contain_text('원문 이미지 아님')
    page.unroute('https://images.samsung.com/**')
    checks.append('publisher_pdf_failure_has_link_and_table_fallback')

    expect(page.locator('#comparison-settings')).to_be_hidden()
    expect(page.locator('[data-document]')).to_have_count(2)
    page.locator('[data-document="s24q2"]').click()
    expect(page.locator('#source-counter')).to_contain_text('B 비교')
    checks.append('actual_documents_open_matching_source')
    reset()
    page.locator('#review-note').fill('확인, "원문"\n검토')
    page.locator('#save-note').click()
    page.locator('#mark-reviewed').click()
    expect(page.locator('#mark-reviewed')).to_have_attribute('aria-pressed','true')
    expect(page.locator('#note-status')).to_contain_text('저장됨')
    page.reload(wait_until='networkidle'); ready()
    expect(page.locator('#review-note')).to_have_value('확인, "원문"\n검토')
    expect(page.locator('#mark-reviewed')).to_have_attribute('aria-pressed','true')
    checks.append('review_notes_and_manual_mark_persist_after_reload')
    with page.expect_download() as export:
        page.locator('#export-btn').click()
    content=Path(export.value.path()).read_text(encoding='utf-8-sig')
    import csv, io
    records=list(csv.DictReader(io.StringIO(content)))
    assert len(records)==6 and records[0]['개인 확인']=='수동 확인'
    assert records[0]['자동 판정']=='verified' and records[0]['메모']=='확인, "원문"\n검토'
    assert records[0]['증감률(%)']=='6.7916' and records[0]['A 출처'].startswith('https://')
    checks.append('csv_contains_real_values_sources_status_and_notes')
    reset()
    page.locator('#base-period').select_option('ytd'); ready()
    expect(page.locator('#review-note')).to_have_value('')
    expect(page.locator('#mark-reviewed')).to_have_attribute('aria-pressed','false')
    page.locator('#mark-reviewed').click()
    expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')
    expect(page.locator('#finding')).to_contain_text('기간 불일치')
    reset()
    expect(page.locator('#review-note')).to_have_value('확인, "원문"\n검토')
    checks.append('notes_isolated_by_context_manual_mark_never_overrides_guard')
    page.locator('#review-note').fill(''); page.locator('#save-note').click()
    page.locator('#mark-reviewed').click()
    for key, value, reason in [('period', 'ytd', '기간 불일치'), ('scope', 'OFS', '연결 범위 불일치'), ('currency', 'USD', '통화 불일치')]:
        page.locator('#base-' + key).select_option(value)
        ready()
        expect(page.locator('#worksheet-rows .growth').first).to_have_text('—')
        expect(page.locator('#finding')).to_contain_text(reason)
        if key == 'period':
            page.screenshot(path=str(OUT / 'docs/images/context-conflict.png'), full_page=True)
        if key == 'currency':
            page.locator('[data-source-index="1"]').click()
            expect(page.locator('.source-warning')).to_contain_text('1349.5')
        checks.append('block_mismatched_' + key)
        reset()

    page.locator('#base-document').select_option('s24q3'); ready()
    page.locator('[data-source-index="1"]').click()
    expect(page.locator('#source-counter')).to_have_text('B 비교 · 매출액')
    expect(page.locator('.number-button.active')).to_have_attribute('data-side', 'base')
    expect(page.locator('.source-switcher [aria-pressed="true"]')).to_have_count(1)
    checks.append('identical_fact_ids_keep_distinct_sides')
    page.locator('#base-year').select_option('2023'); ready()
    page.locator('#mode').select_option('yoy'); ready()
    expect(page.locator('#finding')).to_contain_text('비교 조건 일치')
    checks.append('same_document_prior_year_yoy')
    reset()

    page.locator('#run-btn').click(); ready()
    expect(page.locator('#execution-status')).to_contain_text('실제 MCP 재검증 완료')
    page.locator('#trace-btn').click()
    expect(page.locator('#trace-dialog .trace-row')).to_have_count(18)
    expect(page.locator('.trace-summary')).to_contain_text('생성형 모델 0회')
    with page.expect_download() as download:
        page.locator('#download-btn').click()
    assert download.value.suggested_filename.startswith('quarterguard-worksheet-')
    page.keyboard.press('Escape')
    checks.append('actual_mcp_18_calls_trace_and_download')
    page.locator('#base-scope').select_option('OFS'); ready()
    page.locator('#trace-btn').click()
    expect(page.locator('.trace-summary')).to_contain_text('MCP 실행 아님')
    expect(page.locator('#trace-dialog .trace-row')).to_have_count(0)
    page.keyboard.press('Escape')
    checks.append('changed_selection_clears_live_trace')
    reset()

    page.route('**/api/worksheet/run', lambda r: r.fulfill(status=503, body='{}'))
    page.locator('#run-btn').click()
    expect(page.locator('#work-alert')).to_contain_text('연결 오류', timeout=65000)
    expect(page.locator('#worksheet-rows')).to_contain_text('결과 없음')
    expect(page.locator('#export-btn')).to_be_disabled()
    expect(page.locator('#review-note')).to_be_disabled()
    page.unroute('**/api/worksheet/run')
    reset()
    checks.append('run_failure_clears_old_result_and_recovers')

    # Let an older preview finish after a newer one; only newer data may render.
    held = []
    def delayed(route):
        if not held:
            held.append(route)
        else:
            route.continue_()
    page.route('**/api/worksheet', delayed)
    page.locator('#current-scope').select_option('OFS')
    page.wait_for_timeout(100)
    expect(page.locator('#export-btn')).to_be_disabled()
    page.evaluate("document.querySelector('#current-scope').value='CFS';document.querySelector('#current-scope').dispatchEvent(new Event('change'))")
    ready()
    old = page.request.post(URL + '/api/worksheet', data=json.loads(held[0].request.post_data)).json()
    held[0].fulfill(json=old)
    page.wait_for_timeout(150)
    expect(page.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
    expect(page.locator('#source-counter')).to_have_text('A 기준 · 매출액')
    page.unroute('**/api/worksheet')
    checks.append('stale_preview_cannot_overwrite_new_selection')

    page.locator('[data-view="search"]').click()
    page.locator('#search-form button').click()
    expect(page.locator('[data-use-fact]').first).to_be_visible()
    page.locator('[data-use-fact]').first.click(); ready()
    expect(page.locator('#work')).to_be_visible()
    checks.append('search_fact_opens_matching_worksheet_selection')
    page.locator('[data-view="search"]').click()
    for query in ['samsung 2025 Q3 CFS revenue quarter KRW', 'samsung 2024 Q3 CFS revenue quarter CHF', 'SK hynix 2024 Q3 CFS revenue quarter KRW']:
        page.locator('#query').fill(query); page.locator('#search-form button').click()
        expect(page.locator('#search-results')).to_contain_text('검색 결과 없음')
    checks.append('unsupported_searches_have_no_fabricated_evidence')
    page.route('**/api/search?*', lambda r: r.abort())
    page.locator('#search-form button').click()
    expect(page.locator('#search-results [role="alert"]')).to_be_visible()
    page.unroute('**/api/search?*')
    checks.append('search_network_failure')

    page.locator('[data-view="review"]').click()
    expect(page.locator('#retrieval-table tbody tr')).to_have_count(6)
    expect(page.locator('#case-check-table tbody tr')).to_have_count(8)
    expect(page.locator('#case-check-table thead')).to_contain_text('거부 사유')
    page.screenshot(path=str(OUT / 'docs/images/evaluation.png'), full_page=True)
    checks.append('evaluation_configuration_and_case_level_checks')
    for case in ['qoq-revenue', 'ytd-trap', 'scope-trap', 'currency-trap', 'reconcile-revenue', 'qoq-profit', 'negative-base', 'no-evidence']:
        page.locator('#case-select').select_option(case)
        page.locator('#prepared-btn').click()
        expect(page.locator('.case-result-head')).to_contain_text('저장된 MCP 기록 재생')
        checks.append('saved_regression_' + case)
    page.locator('#case-select').select_option('reconcile-revenue')
    page.locator('#case-run-btn').click()
    expect(page.locator('.case-result-head')).to_contain_text('현재 MCP 실제 실행', timeout=65000)
    expect(page.locator('.case-result-head')).to_contain_text('79,098,731')
    checks.append('actual_mcp_reconciliation')

    # A wrong rejection reason must not appear as an entirely successful row.
    bad_eval = page.request.get(URL + '/api/evaluation').json()
    bad_eval['workflow']['checks'][1]['issue_correct'] = False
    bad_eval['workflow']['checks'][1]['case_correct'] = False
    regression = browser.new_page()
    regression.route('**/api/evaluation', lambda r: r.fulfill(json=bad_eval))
    regression.goto(URL, wait_until='networkidle')
    regression.locator('[data-view="review"]').click()
    expect(regression.locator('#case-check-table tbody tr').nth(1).locator('.warn')).to_have_count(2)
    checks.append('incorrect_rejection_reason_marks_overall_failure')
    regression.close()

    mobile = browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    mobile.on('pageerror', lambda e: errors.append(str(e)))
    mobile.goto(URL, wait_until='networkidle'); ready(mobile)
    assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
    # Both comparison values fit in the same mobile row, without horizontal scrolling.
    row = mobile.locator('#worksheet-rows tr').first
    for button in row.locator('.number-button').all():
        box = button.bounding_box(); assert box['x'] >= 0 and box['x'] + box['width'] <= 390
    mobile.screenshot(path=str(OUT / 'docs/images/mobile.png'), full_page=True)
    checks.append('mobile_both_values_visible_no_body_overflow')
    mobile.locator('[data-fact="s24q2-CFS-revenue-2024-q-KRW"]').click()
    expect(mobile.locator('#source-counter')).to_have_text('B 비교 · 매출액')
    assert mobile.locator('#source-panel').bounding_box()['y'] < 120
    settings(mobile)
    mobile.locator('#base-period').select_option('ytd'); ready(mobile)
    expect(mobile.locator('#finding')).to_contain_text('기간 불일치')
    checks.append('mobile_source_navigation_and_context_guard')

    fail = browser.new_page()
    fail.route('**/api/facts', lambda r: r.abort())
    fail.goto(URL)
    expect(fail.locator('#boot-error')).to_be_visible()
    expect(fail.locator('#run-btn')).to_be_disabled()
    fail.unroute('**/api/facts')
    fail.locator('#boot-retry').click(); ready(fail)
    checks.append('boot_failure_retry')

    ancillary = browser.new_page()
    ancillary.route('**/api/evaluation', lambda r: r.fulfill(status=503,body='{}'))
    ancillary.goto(URL,wait_until='networkidle'); ready(ancillary)
    ancillary.locator('[data-view="review"]').click()
    expect(ancillary.locator('#review-retry')).to_be_visible()
    ancillary.unroute('**/api/evaluation')
    ancillary.locator('#review-retry').click()
    expect(ancillary.locator('#case-check-table tbody tr')).to_have_count(8)
    expect(ancillary.locator('#prepared-btn')).to_be_enabled()
    checks.append('evaluation_failure_does_not_block_work_and_can_retry')
    storage = browser.new_page()
    storage.add_init_script("Storage.prototype.setItem=function(){throw new Error('quota')}")
    storage.goto(URL,wait_until='networkidle'); ready(storage)
    storage.locator('#review-note').fill('저장 실패 메모')
    storage.locator('#save-note').click()
    expect(storage.locator('#note-status')).to_contain_text('저장 실패')
    storage.locator('[data-metric="operating_profit"]').first.click()
    expect(storage.locator('#review-note')).to_have_value('')
    storage.locator('[data-metric="revenue"]').first.click()
    expect(storage.locator('#review-note')).to_have_value('저장 실패 메모')
    expect(storage.locator('#note-status')).to_contain_text('저장 실패')
    expect(storage.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
    with storage.expect_download() as recovered:
        storage.locator('#export-btn').click()
    assert '저장 실패 메모' in Path(recovered.value.path()).read_text(encoding='utf-8-sig')
    checks.append('storage_failure_visible_draft_retained_and_exportable')
    unreadable=browser.new_page()
    unreadable.goto(URL,wait_until='networkidle');ready(unreadable)
    unreadable.locator('#review-note').fill('읽기 복구 후 보존할 기존 기록')
    unreadable.locator('#save-note').click()
    unreadable.locator('#mark-reviewed').click()
    unreadable.add_init_script("window.originalGetItem=Storage.prototype.getItem;Storage.prototype.getItem=function(){throw new DOMException('denied','SecurityError')}")
    unreadable.reload(wait_until='networkidle');ready(unreadable)
    expect(unreadable.locator('#note-status')).to_contain_text('메모 읽기 실패')
    for selector in ['#review-note','#save-note','#mark-reviewed','#export-btn']:
        expect(unreadable.locator(selector)).to_be_disabled()
    expect(unreadable.locator('#worksheet-rows .growth').first).to_have_text('+6.7916%')
    unreadable.evaluate("() => {Storage.prototype.getItem=window.originalGetItem;}")
    unreadable.locator('#retry-note').click()
    expect(unreadable.locator('#review-note')).to_have_value('읽기 복구 후 보존할 기존 기록')
    expect(unreadable.locator('#mark-reviewed')).to_have_attribute('aria-pressed','true')
    expect(unreadable.locator('#export-btn')).to_be_enabled()
    expect(unreadable.locator('#retry-note')).to_be_hidden()
    checks.append('storage_read_failure_blocks_overwrite_and_export_until_retry')
    browser.close()

result={'base_url':URL,'checks':checks,'passed':len(checks),'page_errors':errors,
        'browser':'Chromium via Playwright','viewports':['1440x1000','390x844'],
        'publisher_pdf_rendering':'External failure simulated; direct URL/page and table fallback checked. Actual PDF rendering not asserted.'}
(OUT/'artifacts/browser-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
assert not errors
