import test from 'node:test';
import assert from 'node:assert/strict';

test('source context escapes text and only links HTTPS publisher PDFs at the supplied page', async () => {
  const module = await import('../web/explanation-context.js').catch(() => null);
  assert.ok(module, 'source-context renderer is missing');
  const base = {status:'available', notice:'도구 결과', evidence:[{
    document_title:'Report <img src=x>', page:34, statement:'79,098,731 백만 원',
    source_href:'https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2024_3Q_Interim_Report.pdf#page=34'
  }]};
  let html = module.renderExplanationContext(base);
  assert.match(html, /백만 원/);
  assert.match(html, /p\.34/);
  assert.match(html, /&lt;img/);
  assert.doesNotMatch(html, /<img/);
  assert.match(html, /href="https:\/\/images.samsung.com/);
  for (const url of ['javascript:alert(1)', 'https://evil.invalid/a.pdf#page=34',
    'https://images.samsung.com/a.pdf#page=99', 'https://user@images.samsung.com/a.pdf#page=34']) {
    html = module.renderExplanationContext({...base,evidence:[{...base.evidence[0],source_href:url}]});
    assert.doesNotMatch(html, /href=/);
  }
});

test('empty, missing and unresolved context never show old source links', async () => {
  const module = await import('../web/explanation-context.js').catch(() => null);
  assert.ok(module, 'source-context renderer is missing');
  for (const context of [null,{status:'needs_review',notice:'확인 필요',evidence:[]},
    {status:'no_evidence',notice:'해당 검색 범위에서 확인할 수 없습니다.',evidence:[]}]) {
    const html = module.renderExplanationContext(context);
    assert.doesNotMatch(html,/href=/);
    assert.match(html,/안내|확인/);
  }
});
