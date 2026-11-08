"""Basic document review must not wait for the optional retrieval stack."""
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


class StartupTests(unittest.TestCase):
    def test_review_routes_work_before_search_dependency_is_available(self):
        # A fresh process prevents other test modules from preloading sklearn.
        # If retrieval is imported during boot again, basic review fails here.
        code = textwrap.dedent('''
            import importlib.abc
            import sys
            class UnavailableSearch(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if fullname == 'sklearn' or fullname.startswith('sklearn.'):
                        raise ImportError('retrieval dependency not ready')
            blocker = UnavailableSearch()
            sys.meta_path.insert(0, blocker)
            from fastapi.testclient import TestClient
            from quarterguard.api import app
            client = TestClient(app)
            assert client.get('/health').json()['status'] == 'ok'
            assert 'QuarterGuard' in client.get('/').text
            result = client.post('/api/worksheet', json={}).json()
            assert result['rows'][0]['result']['growth_pct'] == '6.7916'
            held = client.post('/api/worksheet', json={
                'base': {'document': 's24q2', 'period': 'ytd'}}).json()
            assert held['rows'][0]['result']['growth_pct'] is None
            assert held['rows'][0]['result']['issues'] == ['PERIOD_MISMATCH']
            sys.meta_path.remove(blocker)
            result = client.get('/api/search', params={
                'q': 'samsung 2024 Q3 CFS revenue quarter KRW million'}).json()
            assert result['status'] == 'ready', result
            assert result['hits'][0]['fact_ids'] == ['s24q3-CFS-revenue-2024-q-KRW']
        ''')
        result = subprocess.run([sys.executable, '-c', code],
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
