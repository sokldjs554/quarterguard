"""Integrity checks for candidate-locked ranking comparisons."""
import unittest
import numpy as np
from quarterguard import ranking_evaluation_v2 as ranking


class PairScorer:
    def rerank(self, query, documents):
        # Deliberately prefers forbidden text: filtering must precede scoring.
        return iter([9.0 if 'forbidden' in doc else 1.0 for doc in documents])


class RankingIntegrityTests(unittest.TestCase):
    def test_reranker_cannot_add_removed_candidates(self):
        pool = [{'id': 'allowed', 'text': 'allowed fact', 'fact_ids': ['a']}]
        ranked = ranking.rerank_pool('query', pool, PairScorer())
        self.assertEqual([r['id'] for r in ranked], ['allowed'])
        self.assertEqual(ranked[0]['rerank_score'], 1.0)
        self.assertNotIn('rerank_score', pool[0])

    def test_candidate_pool_selection_uses_scores_and_explicit_eligibility(self):
        corpus = [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]
        self.assertEqual([r['id'] for r in ranking.select_pool(corpus, np.array([1, 9, 2]), {0, 2}, 20)], ['c', 'a'])
        self.assertEqual([r['id'] for r in ranking.select_pool(corpus, np.array([1, 9, 2]), {0, 1, 2}, 2)], ['b', 'c'])

    def test_nonfinite_or_missing_model_scores_fail_instead_of_hiding_rows(self):
        class BadScorer:
            def rerank(self, query, documents):
                return [float('nan')]
        with self.assertRaisesRegex(ValueError, 'INVALID_RERANK_SCORES'):
            ranking.rerank_pool('query', [{'id':'a', 'text':'x'}], BadScorer())

    def test_gold_outside_pool_stays_miss_and_candidate_recall_is_separate(self):
        row = ranking.result_row({'id':'q1', 'query':'x', 'gold_fact_id':'gold'},
            [{'id':'a', 'fact_ids':['wrong']}], [], 2.0, 1.0)
        self.assertEqual(row['rank'], 0)
        self.assertFalse(row['gold_in_candidate_pool'])
        self.assertEqual(row['gold_fact_ids'], ['gold'])

    def test_empty_gold_not_inflated_into_recall_success(self):
        rows = [ranking.result_row({'id':'q1','query':'x','gold_fact_id':'a'}, [{'id':'a','fact_ids':['a']}], [{'id':'a','fact_ids':['a']}], 1, 0),
                ranking.result_row({'id':'q2','query':'unsupported','gold_fact_ids':[]}, [], [], 1, 0)]
        summary = ranking.summarize(rows)
        self.assertEqual(summary['answerable_n'], 1)
        self.assertEqual(summary['recall_at_1'], 1)
        self.assertEqual(summary['no_gold_n'], 1)
        self.assertEqual(summary['no_gold_candidate_emission_rate'], 0)


class RecordedRankingIntegrityTests(unittest.TestCase):
    def test_saved_comparisons_use_identical_gold_and_candidate_ids(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        for path in sorted((root/'artifacts').glob('ranking-v2*.json')):
            report = json.loads(path.read_text())
            if 'same_pool_ranking' not in report:
                continue
            cases = {row['id']:row for row in json.loads((root/report['dataset']/'retrieval_gold.json').read_text())}
            for condition in ['filtered', 'unfiltered']:
                baseline = report['same_pool_ranking'][condition+'/cell_hybrid']['rows']
                for name, entry in report['same_pool_ranking'].items():
                    if not name.startswith(condition+'/'):
                        continue
                    self.assertEqual([r['id'] for r in entry['rows']], report['case_ids'])
                    for reference, row in zip(baseline, entry['rows']):
                        self.assertEqual(row['candidate_ids'], reference['candidate_ids'])
                        self.assertTrue(set(row['retrieved']) <= set(reference['candidate_ids']))
                        gold = cases[row['id']]
                        expected = gold.get('gold_fact_ids', [gold['gold_fact_id']] if gold.get('gold_fact_id') else [])
                        self.assertEqual(row['gold_fact_ids'], sorted(expected))

    def test_cli_refuses_to_overwrite_existing_evidence(self):
        import subprocess
        import sys
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'existing.json'
            output.write_bytes(b'original evidence\n')
            run = subprocess.run([sys.executable, '-m', 'quarterguard.ranking_evaluation_v2',
                                  '--output', str(output)], capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 2)
            self.assertIn('Output already exists', run.stderr)
            self.assertEqual(output.read_bytes(), b'original evidence\n')

    def test_recorded_cross_encoder_changes_order_using_nonconstant_scores(self):
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parents[1]/'artifacts/ranking-v2-dev-first.json'
        if not path.exists():
            self.skipTest('Run the optional local model experiment first')
        report = json.loads(path.read_text())['same_pool_ranking']
        baseline = report['unfiltered/cell_hybrid']['rows']
        reranked = report['unfiltered/cross_encoder']['rows']
        self.assertTrue(any(a['retrieved'] != b['retrieved'] for a,b in zip(baseline, reranked)))
        self.assertTrue(all(len(set(row['scores'])) > 1 for row in reranked))
