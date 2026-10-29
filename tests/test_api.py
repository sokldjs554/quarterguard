import unittest
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
