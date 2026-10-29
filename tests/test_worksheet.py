import asyncio
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from quarterguard.api import app
from quarterguard.worksheet import WorksheetRequest, preview, run_worksheet


class WorksheetTests(unittest.TestCase):
    def test_default_table_and_canonical_sources(self):
        result = preview(WorksheetRequest())
        self.assertEqual(len(result['rows']), 6)
        revenue = result['rows'][0]
        self.assertEqual(revenue['result']['growth_pct'], '6.7916')
        self.assertEqual([f['page'] for f in revenue['result']['evidence']], [34, 48])
        self.assertEqual(result['execution_mode'], 'table_calculation')
        self.assertEqual(result['model_calls'], 0)

    def test_context_mismatches_block_rows(self):
        for field, value, issue in [('period', 'ytd', 'PERIOD_MISMATCH'),
                                    ('scope', 'OFS', 'SCOPE_MISMATCH'),
                                    ('currency', 'USD', 'CURRENCY_MISMATCH')]:
            request = WorksheetRequest.model_validate({'base': {field: value, 'document': 's24q2'}})
            for row in preview(request)['rows']:
                self.assertIn(issue, row['result']['issues'])
                self.assertIsNone(row['result']['growth_pct'])

    def test_yoy_can_compare_same_document_prior_year(self):
        r = preview(WorksheetRequest.model_validate({'mode': 'yoy', 'base': {'document': 's24q3', 'year': 2023}}))
        self.assertEqual(r['rows'][0]['result']['status'], 'verified')
        self.assertEqual(r['rows'][0]['base']['start'], '2023-07-01')

    def test_api_rejects_uncollected_and_extra_fields(self):
        client = TestClient(app)
        for body in [{'current': {'year': 2025}}, {'current': {'document': 'fake'}},
                     {'company': 'fake'}, {'current': {'value': '123'}}]:
            self.assertEqual(client.post('/api/worksheet', json=body).status_code, 422)

    def test_shared_live_capacity_and_preview_availability(self):
        with patch('quarterguard.api.slots', asyncio.Semaphore(0)):
            c = TestClient(app)
            self.assertEqual(c.post('/api/worksheet/run', json={}).status_code, 429)
            self.assertEqual(c.post('/api/worksheet', json={}).status_code, 200)


class WorksheetMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_mcp_rows_match_preview(self):
        request = WorksheetRequest()
        result = await run_worksheet(request)
        self.assertTrue(result['workflow_success'])
        self.assertEqual(result['execution_mode'], 'live_mcp')
        self.assertTrue(result['protocol'])
        self.assertEqual(len(result['trace']), 18)
        self.assertEqual(result['rows'], preview(request)['rows'])

    async def test_tool_failure_is_not_a_successful_preview(self):
        with patch('quarterguard.worksheet.stdio_client', side_effect=RuntimeError('private failure')):
            result = await run_worksheet(WorksheetRequest())
        self.assertFalse(result['workflow_success'])
        self.assertEqual(result['rows'], [])
        self.assertEqual(result['issues'], ['TOOL_ERROR'])
        self.assertNotIn('private failure', str(result))
