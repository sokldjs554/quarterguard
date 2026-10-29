"""Fail-closed financial context checks; no LLM judgement or float arithmetic."""
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import calendar

@dataclass(frozen=True)
class Fact:
    id: str
    company: str
    metric: str
    scope: str
    currency: str
    scale: int
    start: str
    end: str
    value: str
    source_url: str
    page: int
    row: str
    column: str
    document_id: str
    document_sha256: str

    def __post_init__(self):
        try:
            if not Decimal(self.value).is_finite(): raise ValueError('NONFINITE_VALUE')
            if date.fromisoformat(self.start)>date.fromisoformat(self.end): raise ValueError('INVALID_PERIOD')
        except InvalidOperation as e: raise ValueError('INVALID_VALUE') from e

    @property
    def amount(self): return Decimal(self.value)*self.scale
    @property
    def months(self):
        s,e=date.fromisoformat(self.start),date.fromisoformat(self.end)
        if s.day!=1 or e.day!=calendar.monthrange(e.year,e.month)[1]: return None
        return (e.year-s.year)*12+e.month-s.month+1
    def public(self): return asdict(self)|{'months':self.months}

def select_unique(facts,**filters):
    matches=[f for f in facts if all(getattr(f,k)==v for k,v in filters.items())]
    if not matches: raise ValueError('NOT_FOUND')
    if len(matches)!=1: raise ValueError('AMBIGUOUS_FACT')
    return matches[0]

def context_issues(facts):
    issues=[]
    for key in ('company','scope','metric','currency'):
        if len({getattr(f,key) for f in facts})>1: issues.append(key.upper()+'_MISMATCH')
    if any(f.scale not in (1,1000,1000000,100000000,1000000000,1000000000000) for f in facts): issues.append('UNKNOWN_UNIT')
    if any(not f.source_url.startswith('https://') or f.page<1 or not f.row or not f.column or len(f.document_sha256)!=64 for f in facts): issues.append('MISSING_SOURCE')
    return issues

def compare(current:Fact,base:Fact,mode='qoq'):
    issues=context_issues([current,base])
    c,b=date.fromisoformat(current.end),date.fromisoformat(base.end)
    valid=(current.months==base.months and current.months is not None)
    if mode=='qoq': valid=valid and current.months==3 and date.fromisoformat(current.start)==b+timedelta(days=1)
    elif mode=='yoy': valid=valid and c.year==b.year+1 and c.month==b.month and current.start[5:]==base.start[5:]
    else: raise ValueError('INVALID_MODE')
    if not valid: issues.append('PERIOD_MISMATCH')
    if base.amount==0: issues.append('ZERO_BASE')
    if base.amount<0: issues.append('NEGATIVE_BASE')
    pct=None if issues else str(((current.amount/base.amount-1)*100).quantize(Decimal('.0001')))
    return {'status':'needs_review' if issues else 'verified','issues':issues,'growth_pct':pct,
      'formula':'(current × scale / base × scale - 1) × 100',
      'normalized_inputs':[str(current.amount),str(base.amount)],'currency':current.currency,
      'evidence':[current.public(),base.public()], 'mode':mode}

def reconcile(ytd:Fact,previous:Fact,direct:Fact):
    issues=context_issues([ytd,previous,direct])
    if not (ytd.start==previous.start and ytd.start.endswith('-01-01') and
      date.fromisoformat(previous.end)+timedelta(days=1)==date.fromisoformat(direct.start) and
      ytd.end==direct.end and direct.months==3 and ytd.months in (6,9,12) and previous.months==ytd.months-3):
        issues.append('PERIOD_MISMATCH')
    derived=difference=None
    if not issues:
        derived=(ytd.amount-previous.amount)/direct.scale
        difference=derived-Decimal(direct.value)
        if difference!=0: issues.append('NUMERIC_CONFLICT')
    return {'status':'needs_review' if issues else 'verified','issues':issues,
      'derived_value':None if derived is None else str(derived),
      'difference':None if difference is None else str(difference),
      'formula':'(YTD × scale - previous YTD × scale) / direct scale',
      'normalized_inputs':[str(ytd.amount),str(previous.amount),str(direct.amount)],
      'evidence':[ytd.public(),previous.public(),direct.public()]}
