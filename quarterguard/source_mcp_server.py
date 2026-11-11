"""Extended MCP server for source evidence; historical four-tool server unchanged.

Run python -m quarterguard.source_mcp_server. Planning remains caller/rule based.
"""
from .mcp_server import mcp

@mcp.tool()
def search_source_evidence(document_id:str,query:str)->dict:
    """Read candidates from a selected source document; no financial answer or calculation."""
    from .source_evidence import search_source
    return search_source(document_id,query)
@mcp.tool()
def get_source_cell(cell_id:str)->dict:
    """Read one canonical source cell with instant/duration, table, row and year column."""
    from .source_evidence import get_cell
    return get_cell(cell_id)
@mcp.tool()
def calculate_source_pair(current_id:str,base_id:str,mode:str)->dict:
    """Calculate explicit registered annual/balance/share pairs; inventory months need definition."""
    from .source_calculations import calculate_source_pair as calculate
    return calculate(current_id,base_id,mode)
@mcp.tool()
def review_source_document(document_id:str,query:str)->dict:
    """Run bounded rule-based Apple evidence/context/calculation review, not LLM planning."""
    from .apple_source import DOCUMENT_ID
    from .apple_review import review
    if document_id!=DOCUMENT_ID:raise ValueError('UNKNOWN_SOURCE_DOCUMENT')
    return review(query)
if __name__=='__main__':mcp.run()
