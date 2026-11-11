import unittest
from fastapi.testclient import TestClient
from quarterguard.api import app
from quarterguard.source_evidence import DOCUMENT_ID, load_source

class SourceAPITests(unittest.TestCase):
    def setUp(self):self.client=TestClient(app)
    def test_catalog_search_and_canonical_cell(self):
        r=self.client.get('/api/source-documents')
        self.assertEqual(r.status_code,200)
        self.assertFalse(r.json()[0]['calculation_supported'])
        r=self.client.get('/api/source-search',params={'document_id':DOCUMENT_ID,'q':'2024년 DRAM 매출 비중'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(len(r.json()['hits']),2)
        cell=r.json()['hits'][0]['cell']
        self.assertEqual(self.client.get('/api/source-cells/'+cell['id']).json(),cell)
    def test_bad_requests_and_existing_sources_unchanged(self):
        self.assertEqual(self.client.get('/api/source-search',params={'document_id':'fake','q':'매출'}).status_code,404)
        self.assertEqual(self.client.get('/api/source-search',params={'document_id':DOCUMENT_ID,'q':'a'*501}).status_code,422)
        self.assertEqual(self.client.get('/api/source-cells/fake').status_code,404)
        self.assertEqual(len(self.client.get('/api/facts').json()),192)
        self.assertEqual(len(self.client.get('/api/sources').json()),2)
    def test_corrupt_data_returns_error_not_old_success(self):
        from unittest.mock import patch
        with patch('quarterguard.source_evidence.load_source',side_effect=ValueError('SOURCE_EVIDENCE_INTEGRITY')):
            self.assertEqual(self.client.get('/api/source-search',params={'document_id':DOCUMENT_ID,'q':'2024 매출'}).status_code,503)
        self.assertEqual(self.client.get('/api/source-search',params={'document_id':DOCUMENT_ID,'q':'2024 매출'}).status_code,200)

class SourceIntegrityTests(unittest.TestCase):
    def test_mutated_cells_fail_closed(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from quarterguard import source_evidence as s
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'manifest.json').write_bytes((s.DATA/'manifest.json').read_bytes())
            (p/'cells.json').write_bytes((s.DATA/'cells.json').read_bytes().replace(b'11205117',b'11205118'))
            with patch.object(s,'DATA',p),self.assertRaisesRegex(ValueError,'INTEGRITY'):load_source()
