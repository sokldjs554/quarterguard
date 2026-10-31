"""Actual MCP stdio server; stdout is reserved for JSON-RPC."""
from functools import lru_cache
from mcp.server.fastmcp import FastMCP
from .store import load_facts
from .core import compare, reconcile
from .search import SearchIndex
mcp=FastMCP('QuarterGuard',instructions='Use cited facts; never compare incompatible contexts.')
FACTS={f.id:f for f in load_facts()}
@lru_cache(maxsize=4)
def index(config):return SearchIndex(list(FACTS.values()),config)
def lookup(fid):
    if fid not in FACTS:raise ValueError('NOT_FOUND: fact id')
    return FACTS[fid]
@mcp.tool()
def search_documents(query:str,k:int=3,config:str='hybrid_meta')->dict:
    """Retrieve constrained evidence candidates and missing/conflicting-context diagnostics; never a verified answer."""
    if len(query)>500:raise ValueError('QUERY_TOO_LONG')
    return index(config).search_with_diagnostics(query,k)|{'config':config}
@mcp.tool()
def get_fact(fact_id:str)->dict:
    """Read immutable financial fact with page, row, column and source hash."""
    return lookup(fact_id).public()
@mcp.tool()
def verify_comparison(current_id:str,base_id:str,mode:str='qoq')->dict:
    """Validate entity, account, scope, currency and dates before Decimal growth calculation."""
    return compare(lookup(current_id),lookup(base_id),mode)
@mcp.tool()
def reconcile_quarter(ytd_id:str,previous_id:str,direct_id:str)->dict:
    """Reconcile cumulative difference against a separately disclosed quarter value."""
    return reconcile(lookup(ytd_id),lookup(previous_id),lookup(direct_id))
if __name__=='__main__':mcp.run()
