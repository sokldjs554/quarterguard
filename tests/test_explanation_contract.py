"""Archived v6 replay and authored boundary cases; no paid/human evaluation."""
import copy
import json
import unittest
from quarterguard.store import ROOT, load_facts
from quarterguard.core import compare, reconcile
from quarterguard import public_providers as pp
from quarterguard.explanation_guards import check_prose
from quarterguard.evaluate_live_explanations_v6 import registry


class OutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r['case_id']: r for r in json.loads(
            (ROOT/'artifacts/llm-prose-v6-20261110/report.json').read_text())['records']}
        cls.facts = {f.id: f for f in load_facts()}

    def test_payload_permits_only_exact_tool_value_including_null_and_derived(self):
        from jsonschema import Draft202012Validator
        original = copy.deepcopy(pp.SCHEMA)
        results = [self.rows[k]['tool_result'] for k in ('normal-qoq', 'period-mismatch')]
        results.append({'status':'verified','issues':[], 'evidence':[], 'derived_value':'0'})
        for result, expected in zip(results, ['6.7916', None, '0']):
            payload = pp.build_payload(result, '계약 검사')
            field = payload['text']['format']['schema']['properties']['value']
            validator = Draft202012Validator(field)
            self.assertTrue(validator.is_valid(expected))
            for bad in ['6.7916%', '6.79160', 6.7916, '0%', 'null', '']:
                self.assertFalse(validator.is_valid(bad), (expected,bad))
        self.assertEqual(pp.SCHEMA, original)

    def test_disclosed_negation_passes_without_changing_original_text(self):
        row = self.rows['s22-net-period']
        before = copy.deepcopy(row)
        self.assertTrue(check_prose(row['generated'],row['tool_result'])['prose_evidence_presence_consistent'])
        self.assertEqual(row,before)

    def test_supported_negation_does_not_hide_a_later_absence_claim(self):
        result = self.rows['s22-net-period']['tool_result']
        for text in ['근거가 없다는 뜻은 아닙니다.', '근거가 없는 것은 아닙니다.']:
            with self.subTest(text=text):
                self.assertTrue(check_prose({'explanation_ko':text},result)['prose_evidence_presence_consistent'])
                self.assertFalse(check_prose({'explanation_ko':text+' 그러나 근거를 찾지 못했습니다.'},result)['prose_evidence_presence_consistent'])
        for text in ['근거가 없습니다.', '근거가 없는 것은 아닙니까?',
                     '근거가 없는 것은 아니라고 단정할 수 없습니다.',
                     '해당 검색 범위에서 확인할 수 없습니다.']:
            self.assertFalse(check_prose({'explanation_ko':text},result)['prose_evidence_presence_consistent'])

    def test_qoq_reports_date_adjacency_not_equal_months_as_failure(self):
        result=compare(self.facts['s24q3-CFS-revenue-2024-q-KRW'],self.facts['s24q3-CFS-revenue-2023-q-KRW'],'qoq')
        basis=pp.build_context(result)['decision_basis'][0]
        self.assertEqual(basis.get('failed_conditions'),['qoq_adjacent'])
        self.assertIn('인접',basis['statement'])
        self.assertNotIn('기간 길이 또는',basis['statement'])
        self.assertIsNone(result['growth_pct'])

    def test_duration_and_yoy_failures_are_distinguished(self):
        period=self.rows['s22-net-period']
        with registry(period):
            basis=pp.build_context(period['tool_result'])['decision_basis'][0]
        self.assertEqual(basis.get('failed_conditions'),['equal_months','yoy_start_month_day'])
        cross=self.rows['cross-company-period']
        with registry(cross):
            context=pp.build_context(cross['tool_result'])
        period_basis=next(b for b in context['decision_basis'] if b['code']=='PERIOD_MISMATCH')
        self.assertEqual(period_basis.get('failed_conditions'),['yoy_year'])
        self.assertEqual(context['issues'],['COMPANY_MISMATCH','PERIOD_MISMATCH'])

    def test_unknown_or_tampered_context_does_not_invent_period_diagnostics(self):
        row=copy.deepcopy(self.rows['s22-op-qoq'])
        with registry(row):
            for key,value in [('start','2022-01-01'),('months',9),('id','unknown')]:
                result=copy.deepcopy(row['tool_result']);result['evidence'][0][key]=value
                basis=pp.build_context(result)['decision_basis'][0]
                self.assertEqual(basis.get('failed_conditions'),[])
                self.assertIn('확인 필요',basis['statement'])
        result={'status':'needs_review','issues':['PERIOD_MISMATCH'],'evidence':[]}
        self.assertEqual(pp.build_context(result)['decision_basis'][0].get('failed_conditions'),[])

    def test_eight_archived_percent_values_still_fail_exact_validation(self):
        from quarterguard.live_verification import check_explanation
        failures=[r['case_id'] for r in self.rows.values() if not check_explanation(r['generated'],r['tool_result'])['value_exact']]
        self.assertEqual(failures,['normal-qoq','normal-yoy','unit-draft','conflicting-number-draft','citation-draft','s22-net-ytd-yoy','h25-op-yoy','h25-net-yoy'])
