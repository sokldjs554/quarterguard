import json,tempfile,unittest
from pathlib import Path
from quarterguard import human_holdout as h

class HoldoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.data={'author':{'id':'test-author','ai_used':False},'cases':[{'id':'T1','question':'새 질문',
          'document_id':'unsupported-document','expected':{'status':'needs_review','rows':[]},
          'sources':[{'url':'https://example.org/public.pdf','page':1,'row':'Revenue','column':'2024'}]}]}
    def test_provenance_and_duplicate_ids_reject(self):
        for key,value in [('ai_used',True),('id','')]:
            d=json.loads(json.dumps(self.data));d['author'][key]=value
            with self.assertRaises(ValueError):h.validate(d)
        d=json.loads(json.dumps(self.data));d['cases']*=2
        with self.assertRaises(ValueError):h.validate(d)
    def test_mutation_rejected_and_first_run_cannot_be_repeated(self):
        frozen=h.freeze(self.data)
        changed=json.loads(json.dumps(frozen));changed['dataset']['cases'][0]['question']='changed'
        with self.assertRaises(ValueError):h.run(changed,self.root/'one',self.root/'ledger')
        r=h.run(frozen,self.root/'one',self.root/'ledger')
        self.assertEqual(r['rows'][0]['actual']['issues'],['UNSUPPORTED_DOCUMENT'])
        with self.assertRaises(FileExistsError):h.run(frozen,self.root/'two',self.root/'ledger')
    def test_gold_never_passed_to_runtime(self):
        seen=[]
        def runtime(query,document_id):
            seen.append((query,document_id));return {'status':'needs_review','hits':[],'issues':[]}
        h.run(h.freeze(self.data),self.root/'one',self.root/'ledger',runtime=runtime)
        self.assertEqual(seen,[('새 질문','unsupported-document')])
    def test_empty_gold_does_not_pass_unexpected_evidence(self):
        result=h.score(self.data['cases'][0]['expected'],{'status':'needs_review','hits':[{'cell':{'value':'1'}}]})
        self.assertFalse(result['passed'])
    def test_gold_value_mismatch_is_failure(self):
        result=h.score({'status':'evidence_candidates','rows':[{'value':'2','row':'Revenue'}]},
         {'status':'evidence_candidates','hits':[{'cell':{'value':'1','row':'Revenue'}}]})
        self.assertEqual(result['matched_rows'],0);self.assertFalse(result['passed'])

    def test_crashed_runtime_never_scores_as_successful_hold(self):
        def crash(question,doc):raise RuntimeError('failure')
        report=h.run(h.freeze(self.data),self.root/'crash',self.root/'ledger',runtime=crash)
        self.assertFalse(report['rows'][0]['score']['passed'])
        self.assertFalse(report['rows'][0]['execution_success'])
