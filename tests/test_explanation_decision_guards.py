"""Offline regression of disclosed failures; never new model/human results."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
import httpx
from quarterguard import public_providers as pp
from quarterguard.store import ROOT


class DecisionGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows={r['case_id']:r for r in json.loads((ROOT/'artifacts/llm-followup-20261110/report.json').read_text())['records']}

    def test_scope_only_reason_does_not_turn_adjacent_quarters_into_a_block(self):
        context=pp.build_context(self.rows['scope-mismatch']['tool_result'])
        self.assertEqual([x['code'] for x in context['decision_basis']],['SCOPE_MISMATCH'])
        self.assertIn('연결·별도',context['decision_basis'][0]['statement'])
        self.assertIn('기간 불일치로 판정하지 않았습니다',context['decision_note'])
        self.assertIn('issues',pp.INSTRUCTIONS)

    def test_combined_rejections_keep_both_reasons_and_no_scope_only_note(self):
        result=copy.deepcopy(self.rows['scope-mismatch']['tool_result'])
        result['issues']=['PERIOD_MISMATCH','SCOPE_MISMATCH']
        context=pp.build_context(result)
        self.assertEqual([x['code'] for x in context['decision_basis']],result['issues'])
        self.assertNotIn('기간 불일치로 판정하지 않았습니다',context['decision_note'])
        self.assertEqual(pp.build_context(self.rows['normal-qoq']['tool_result'])['decision_basis'],[])

    def test_schema_limits_ids_without_mutating_shared_schema(self):
        old=copy.deepcopy(pp.SCHEMA)
        result=self.rows['normal-yoy']['tool_result']
        schema=pp.build_payload(result,'검토')['text']['format']['schema']
        ids=schema['properties']['evidence_ids']
        self.assertEqual(ids['items']['enum'],[f['id'] for f in result['evidence']])
        self.assertEqual((ids['minItems'],ids['maxItems']),(2,2))
        self.assertEqual(pp.SCHEMA,old)
        empty=pp.build_payload(self.rows['no-evidence']['tool_result'],'검토')['text']['format']['schema']
        self.assertEqual(empty['properties']['evidence_ids']['maxItems'],0)

    def test_bad_id_replay_is_failed_not_cached_and_never_returns_prose(self):
        row=self.rows['normal-yoy'];result=row['tool_result']
        response=httpx.Response(200,json={'status':'completed','model':pp.MODEL,
            'usage':{'input_tokens':100,'output_tokens':100},
            'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(row['generated'])}]}]})
        run={'workflow_success':True,'run_id':'replayed-test','trace':[{}],'result':result}
        expected={'id':'qoq-revenue','description':'synthetic target for YoY failure replay',
                  'expected_status':result['status'],'expected_evidence':result['evidence'],'expected_value':result['growth_pct']}
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'QG_LEDGER_PATH':str(Path(tmp)/'ledger'),'OPENAI_API_KEY':'test-only'},clear=True),\
             patch.object(pp,'reasons',return_value=[]),patch.object(pp,'run_case',AsyncMock(return_value=run)),\
             patch.object(pp,'cases',return_value=[expected]),patch.object(pp.httpx,'post',return_value=response) as post:
            outcome=pp.execute('openai','qoq-revenue')
            self.assertEqual(outcome['status'],'failed')
            self.assertEqual(outcome['reason'],'EXPLANATION_VALIDATION_REJECTED')
            self.assertFalse(outcome['validation_checks']['citations_exact'])
            self.assertNotIn('generated',outcome)
            self.assertNotIn('explanation_context',outcome)
            self.assertEqual(post.call_count,1)
            self.assertEqual(pp.ledger().usage('openai')['attempts_total'],1)
            with pp.ledger().db() as db: target=db.execute('SELECT target FROM calls').fetchone()[0]
            self.assertIsNone(pp.ledger().cached('openai',target))

    def test_unknown_issue_is_explicit_not_replaced_with_period_or_scope(self):
        result=copy.deepcopy(self.rows['normal-qoq']['tool_result'])
        result.update(status='needs_review',issues=['UNSUPPORTED_REASON'])
        context=pp.build_context(result)
        self.assertEqual(context['decision_basis'][0]['code'],'UNSUPPORTED_REASON')
        self.assertIn('확인 필요',context['decision_basis'][0]['statement'])

    def test_wrong_order_and_duplicate_allowed_ids_still_fail_server_validation(self):
        row=self.rows['normal-qoq']
        for ids in [list(reversed(row['generated']['evidence_ids'])),[row['generated']['evidence_ids'][0]]*2]:
            answer=copy.deepcopy(row['generated']);answer['evidence_ids']=ids
            response=httpx.Response(200,json={'status':'completed','model':pp.MODEL,
                'usage':{'input_tokens':100,'output_tokens':100},
                'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(answer)}]}]})
            with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'}),patch.object(pp.httpx,'post',return_value=response):
                with self.assertRaises(pp.ExplanationRejected) as error:pp.generate_public({},row['tool_result'])
            self.assertFalse(error.exception.checks['citations_exact'])

    def test_historical_policy_is_hash_checked_and_comparison_scores_unchanged(self):
        from quarterguard.frozen_followup import load_frozen_followup, ARCHIVE
        old=load_frozen_followup()
        self.assertNotEqual(old.INSTRUCTIONS,pp.INSTRUCTIONS)
        original_read=Path.read_bytes
        def changed(path):
            data=original_read(path)
            return data+b'\n# tampered' if path==ARCHIVE/'explanation_context.py' else data
        with patch.object(Path,'read_bytes',changed):
            with self.assertRaisesRegex(ValueError,'HISTORICAL_SOURCE_HASH_MISMATCH'):load_frozen_followup()
