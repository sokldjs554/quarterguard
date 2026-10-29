"""Build transparent template-derived regression queries, not a human-reviewed benchmark."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
metrics={'revenue':'매출액','cost_of_sales':'매출원가','gross_profit':'매출총이익','operating_expenses':'판매관리비','operating_profit':'영업이익','net_profit':'당기순이익'}
rows=[]
# Fixed grid is defined independently of retrieved documents/results.
for metric,label in metrics.items():
 for q,year,scope,kind,curr in [(3,2024,'CFS','q','KRW'),(2,2024,'CFS','ytd','KRW'),(3,2023,'OFS','q','KRW'),(2,2023,'OFS','ytd','USD'),(3,2024,'OFS','ytd','KRW'),(2,2024,'CFS','q','USD')]:
  rows.append({'id':f'q{len(rows)+1:02}','query':f'삼성전자 {year} {q}분기 {"연결" if scope=="CFS" else "별도"} {label} {"3개월" if kind=="q" else "누적"} {curr}',
   'gold_fact_id':f's24q{q}-{scope}-{metric}-{year}-{kind}-{curr}','origin':'fixed_template','human_reviewed':False})
(root/'data/retrieval_gold.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
