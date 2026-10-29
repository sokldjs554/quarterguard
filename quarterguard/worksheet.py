"""Document-selected worksheet, backed by immutable facts and existing guards."""
import asyncio
from datetime import datetime, timezone
import json
import sys
import time
from typing import Literal
import uuid

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, ConfigDict, Field

from .core import compare, select_unique
from .store import ROOT, load_facts

METRICS = ('revenue', 'cost_of_sales', 'gross_profit', 'operating_expenses', 'operating_profit', 'net_profit')


class Selection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    document: Literal['s24q3', 's24q2'] = 's24q3'
    year: Literal[2024, 2023] = 2024
    scope: Literal['CFS', 'OFS'] = 'CFS'
    period: Literal['q', 'ytd'] = 'q'
    currency: Literal['KRW', 'USD'] = 'KRW'


class WorksheetRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    current: Selection = Field(default_factory=Selection)
    base: Selection = Field(default_factory=lambda: Selection(document='s24q2'))
    mode: Literal['qoq', 'yoy'] = 'qoq'


def selected_facts(selection):
    facts = [f for f in load_facts() if f.document_id == selection.document
             and f.scope == selection.scope and f.currency == selection.currency
             and f.start.startswith(str(selection.year))
             and (f.months == 3) == (selection.period == 'q')]
    return [select_unique(facts, metric=metric) for metric in METRICS]


def metadata(request, execution_mode):
    return {'run_id': str(uuid.uuid4()), 'selection': request.model_dump(),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'execution_mode': execution_mode, 'model_calls': 0,
            'planner': 'deterministic_workflow', 'provider_api_cost_usd': 0,
            'cost_scope': 'No paid provider calls; hosting and CPU excluded'}


def preview(request):
    start = time.perf_counter()
    rows = [{'metric': a.metric, 'current': a.public(), 'base': b.public(),
             'result': compare(a, b, request.mode)}
            for a, b in zip(selected_facts(request.current), selected_facts(request.base))]
    return metadata(request, 'table_calculation') | {
        'rows': rows, 'trace': [], 'protocol': None, 'issues': [],
        'workflow_success': True, 'latency_ms': round((time.perf_counter() - start) * 1000, 3)}


async def run_worksheet(request):
    start = time.perf_counter()
    trace, rows = [], []
    protocol = None
    issues = []

    async def execute():
        nonlocal protocol
        (ROOT / 'work').mkdir(exist_ok=True)
        with open(ROOT / 'work/mcp-stderr.log', 'a') as log:
            params = StdioServerParameters(command=sys.executable, args=['-m', 'quarterguard.mcp_server'], cwd=str(ROOT))
            async with stdio_client(params, errlog=log) as (r, w):
                async with ClientSession(r, w) as session:
                    protocol = (await session.initialize()).protocolVersion

                    async def call(name, args):
                        t = time.perf_counter()
                        response = await session.call_tool(name, args)
                        entry = {'step': len(trace) + 1, 'tool': name, 'arguments': args,
                                 'latency_ms': round((time.perf_counter() - t) * 1000, 3),
                                 'success': not response.isError}
                        trace.append(entry)
                        if response.isError:
                            entry['failure_type'] = 'TOOL_ERROR'
                            raise ValueError('TOOL_ERROR')
                        value = response.structuredContent
                        if value is None:
                            value = json.loads(next(c.text for c in response.content if c.type == 'text'))
                        entry['output'] = value
                        return value

                    for a, b in zip(selected_facts(request.current), selected_facts(request.base)):
                        current = await call('get_fact', {'fact_id': a.id})
                        base = await call('get_fact', {'fact_id': b.id})
                        result = await call('verify_comparison', {'current_id': a.id, 'base_id': b.id, 'mode': request.mode})
                        if current != a.public() or base != b.public() or result != compare(a, b, request.mode):
                            raise ValueError('TOOL_RESPONSE_MISMATCH')
                        rows.append({'metric': a.metric, 'current': current, 'base': base, 'result': result})

    try:
        await asyncio.wait_for(execute(), timeout=45)
    except TimeoutError:
        issues = ['TOOL_TIMEOUT']
    except Exception:
        issues = ['TOOL_ERROR']
    return metadata(request, 'live_mcp') | {
        'rows': [] if issues else rows, 'trace': trace, 'protocol': protocol,
        'issues': issues, 'workflow_success': not issues and len(rows) == len(METRICS),
        'latency_ms': round((time.perf_counter() - start) * 1000, 3)}
