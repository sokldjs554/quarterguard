"""Actual PDF parsing and MCP retrieval, separate from text-fixture tests. No LLM."""
import argparse,asyncio,hashlib,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from quarterguard.source_evidence import parse_pdf,load_source,DOCUMENT_ID,PDF_SHA
from quarterguard.store import ROOT

EXPECTED=[{('cash',2024),('cash',2023)},
 {('inventory',2024),('inventory',2023),('revenue',2024),('revenue',2023)},
 {('dram',2024),('product_total',2024)},
 {('operating_profit',2024),('operating_profit',2023)},
 {('inventory',2024),('revenue',2023),('cost_of_sales',2023)}]

def unpack(r):
    if r.isError:raise ValueError('MCP_TOOL_ERROR')
    return r.structuredContent or json.loads(next(c.text for c in r.content if c.type=='text'))

async def run(pdf,output):
    output.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();cells=parse_pdf(pdf);parse_ms=(time.perf_counter()-start)*1000
    manifest,stored=load_source()
    assert cells==stored,'REGISTERED_CELLS_DIFFER_FROM_RAW_PDF'
    gold=json.loads((ROOT/'artifacts/skhynix-human-20261111/source-review-ai.json').read_text())
    checks=[]
    for g in gold['selected_submitted_cells']:
        row=g['literal_row_or_section']
        table=None
        if row.startswith('24(2) '):
            table='note-24-2';row='DRAM' if row.endswith('DRAM') else ''
        found=[c for c in cells if c['page']==g['pdf_page'] and c['row']==row and c['column']==g['year_column'] and (not table or c['table_id']==table)]
        assert len(found)==1
        c=found[0]
        period=c['as_of'] if c['period_kind']=='instant' else c['start']+'/'+c['end']
        passed=(c['value']==g['value_million_krw'] and c['printed_page']==g['printed_page'] and
                c['period_kind']==g['period_type'] and period==g['period'] and
                all(c[k]==g[k] for k in ('scope','currency','scale')) and
                c['amount_column']==(1 if c['year']==2024 else 2))
        checks.append({'cell_id':c['id'],'passed':passed,'gold':g})
        assert passed
    cases=json.loads((ROOT/'data/skhynix-human-20261111/cases.json').read_text())
    traces=[];searches=[]
    async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','quarterguard.source_mcp_server'],cwd=str(ROOT))) as (r,w):
        async with ClientSession(r,w) as session:
            init=await session.initialize()
            for case,want in zip(cases,EXPECTED):
                args={'document_id':DOCUMENT_ID,'query':case['question']}
                start=time.perf_counter();result=unpack(await session.call_tool('search_source_evidence',args));elapsed=(time.perf_counter()-start)*1000
                traces.append({'order':len(traces)+1,'tool':'search_source_evidence','input':args,'output':result})
                actual={(h['cell']['metric'],h['cell']['year']) for h in result['hits']}
                assert actual==want
                for hit in result['hits']:
                    cell=unpack(await session.call_tool('get_source_cell',{'cell_id':hit['cell']['id']}))
                    assert cell==hit['cell'] and cell in cells
                    traces.append({'order':len(traces)+1,'tool':'get_source_cell','input':{'cell_id':cell['id']},'output':cell})
                searches.append({'id':case['id'],'question':case['question'],'exact_required_cell_set':True,
                    'result':result,'elapsed_ms':elapsed,'human_authored_question':True,
                    'required_cell_mapping':'AI-authored from user evidence locations; development, not fresh holdout'})
    report={'at_utc':datetime.now(timezone.utc).isoformat(),'scope':'phase 1 source evidence; no calculated answers',
        'raw_pdf':{'sha256':PDF_SHA,'pages_attempted':3,'pages_parsed':3,'cells':18,'parse_elapsed_ms':parse_ms,
            'pdf_to_registered_cells_exact':True,'source_discovery':'Three user-identified pages; selected rows, not entire report'},
        'preexisting_selected_cell_annotations':{'origin':'User submitted values, AI source-reviewed before adapter development; not new human review','checks':checks,'passed':len(checks)},
        'queries':searches,'exact_evidence_sets_passed':len(searches),
        'mcp':{'execution':'actual stdio tools; deterministic caller sequence, no LLM planning','protocol':init.protocolVersion,'calls':len(traces),'trace':traces},
        'baseline':'artifacts/skhynix-human-20261111/first-baseline/report.json',
        'after_development_not_holdout':True,'new_human_review':False,'paid_api_calls':0,'new_model_generations':0,
        'answers_calculated':0,'limitations':['18 selected source cells; no general annual statement parser.',
            'Document-scoped conditions from explicitly selected source; conservative rule vocabulary.',
            'Original five questions used in development. No claim of general accuracy or five correct calculated answers.',
            'Annual/instant/share calculation and inventory-ratio definition remain unsupported.',
            'Latency is one local run, not production load or comparative performance evidence.'],
        'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['quarterguard/source_evidence.py','quarterguard/source_mcp_server.py','data/source-evidence/cells.json','data/source-evidence/manifest.json','scripts/evaluate_skhynix_source_support.py']}}
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'raw_pdf_pages':'3/3','cells':18,'selected_gold_cells':len(checks),'queries':'5/5 evidence sets, 0 calculated answers','actual_mcp_calls':len(traces),'paid_calls':0},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pdf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();asyncio.run(run(a.pdf,a.output))
