"""AI-authored exhaustive combinations of the current catalog; not a holdout."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quarterguard.source_evidence import load_source
from quarterguard.source_calculations import calculate_source_pair,MODES

def main():
 cells=load_source()[1];counts={'verified':0,'difference_only':0,'blocked':0}
 for a in cells:
  for b in cells:
   for mode in MODES:
    r=calculate_source_pair(a['id'],b['id'],mode)
    compare=(mode=='annual_yoy' and a['metric']==b['metric'] and a['metric'] in {'revenue','cost_of_sales','operating_profit'} and a['year']==2024 and b['year']==2023) or (mode=='balance_yoy' and a['metric']==b['metric'] and a['metric'] in {'cash','inventory'} and a['year']==2024 and b['year']==2023)
    share=mode=='product_share' and a['metric'] in {'dram','nand','other_products'} and b['metric']=='product_total' and a['year']==b['year']
    if compare:
     assert r['difference'] is not None
     if a['metric']=='operating_profit':assert r['growth_pct'] is None and r['issues']==['NEGATIVE_BASE']
     else:assert r['status']=='verified' and r['growth_pct'] is not None
    elif share:assert r['status']=='verified' and r['share_pct'] is not None
    else:assert all(r[k] is None for k in ['difference','growth_pct','share_pct']) and r['status']=='needs_review'
    counts['verified' if r['status']=='verified' else 'difference_only' if r['difference'] else 'blocked']+=1
 print(json.dumps({'origin':'AI-authored exhaustive combinations over current registered18cells, not new documents or human queries','combinations':len(cells)**2*len(MODES),'counts':counts,'all_expected':True,'paid_calls':0},indent=2))
if __name__=='__main__':main()
