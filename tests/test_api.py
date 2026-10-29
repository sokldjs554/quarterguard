import unittest,asyncio
from unittest.mock import patch
from fastapi.testclient import TestClient
from quarterguard.api import app
class APITests(unittest.TestCase):
 def setUp(self):self.c=TestClient(app)
 def test_health(self):self.assertEqual(self.c.get('/health').status_code,200)
 def test_sources(self):self.assertEqual(len(self.c.get('/api/sources').json()),2)
 def test_unknown_case(self):self.assertEqual(self.c.post('/api/run/unknown').status_code,404)
 def test_unknown_prepared(self):self.assertEqual(self.c.get('/api/prepared/unknown').status_code,404)
 def test_search_too_long(self):self.assertEqual(self.c.get('/api/search',params={'q':'x'*501}).status_code,422)
 def test_connector_unavailable(self):self.assertEqual(self.c.get('/api/connectors/dart').json()['status'],'not_configured')
 def test_no_data(self):self.assertEqual(self.c.get('/api/search',params={'q':'samsung 2025 Q3 CFS revenue quarter KRW'}).json()['hits'],[])
 def test_home(self):self.assertIn('QuarterGuard',self.c.get('/').text)

class CapacityTests(unittest.TestCase):
 def test_busy_returns_429(self):
  with patch('quarterguard.api.slots',asyncio.Semaphore(0)):
   self.assertEqual(TestClient(app).post('/api/run/qoq-revenue').status_code,429)

class ConcurrentRequestTests(unittest.IsolatedAsyncioTestCase):
 async def test_second_live_request_rejected_while_first_runs(self):
  import httpx
  started=asyncio.Event();finish=asyncio.Event()
  async def slow_run(case):
   started.set();await finish.wait();return {'case_id':case}
  with patch('quarterguard.api.run_case',slow_run):
   async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as c:
    first=asyncio.create_task(c.post('/api/run/qoq-revenue'))
    await started.wait()
    try:
     second=await asyncio.wait_for(c.post('/api/run/qoq-profit'),timeout=1)
     self.assertEqual(second.status_code,429)
    finally:
     finish.set();response=await first
    self.assertEqual(response.status_code,200)
