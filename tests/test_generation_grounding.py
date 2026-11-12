import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from quarterguard.public_providers import build_payload
from quarterguard.explanation_context import build_context
from quarterguard.explanation_guards import check_grounding


class GenerationGroundingTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((Path(__file__).resolve().parents[1] /
            'artifacts/final-live-20261111/run/report.json').read_text())['explanations']
        self.result = self.rows[0]['mcp']['result']

    def test_schema_constrains_status_and_issue_codes_before_generation(self):
        result = self.rows[2]['mcp']['result']
        original = copy.deepcopy(result)
        schema = build_payload(result, 'no evidence')['text']['format']['schema']
        self.assertFalse(Draft202012Validator(schema['properties']['issues']).is_valid(['근거 없음']))
        self.assertFalse(Draft202012Validator(schema['properties']['issues']).is_valid([]))
        self.assertFalse(Draft202012Validator(schema['properties']['status']).is_valid('verified'))
        self.assertEqual(result, original)

    def test_wrong_amount_or_omitted_fact_binding_is_not_accepted(self):
        context = build_context(self.result)
        text = '\n'.join(f['required_claim'] for f in context['evidence']) + ' 증가율 6.7916%.'
        self.assertTrue(all(check_grounding({'explanation_ko': text}, self.result).values()))
        for changed in (text.replace('79,098,731', '79,098,732'),
                        context['evidence'][0]['required_claim'],
                        text.replace('연결', '별도')):
            self.assertFalse(all(check_grounding({'explanation_ko': changed}, self.result).values()))

    def test_extra_wrong_amount_is_rejected_even_after_valid_anchors(self):
        text = '\n'.join(f['required_claim'] for f in build_context(self.result)['evidence'])
        self.assertFalse(check_grounding({'explanation_ko': text + ' 따라서 123백만 원입니다.'},
                                         self.result)['prose_amounts_supported'])

    def test_wrong_rate_or_hidden_large_unit_conversion_is_rejected(self):
        text = '\n'.join(f['required_claim'] for f in build_context(self.result)['evidence'])
        for suffix in (' 증가율 100%.', ' 증가율은 계산하지 않았습니다.'):
            self.assertFalse(check_grounding({'explanation_ko':text+suffix},self.result)['prose_rates_match_tool'])
        for amount in ('79조 원', '79조원', '7억9000만원'):
            self.assertFalse(check_grounding({'explanation_ko':text+' 금액은 '+amount+'입니다.'},self.result)['prose_amounts_supported'])

    def test_period_explanation_requires_independent_diagnostic_statement(self):
        result = self.rows[1]['mcp']['result']
        context = build_context(result)
        text = '\n'.join(f['required_claim'] for f in context['evidence'])
        self.assertFalse(check_grounding({'explanation_ko': text}, result)['prose_decision_basis_present'])
        text += '\n' + '\n'.join(x['statement'] for x in context['decision_basis'])
        self.assertTrue(all(check_grounding({'explanation_ko': text}, result).values()))

    def test_unknown_source_abstains_and_no_evidence_requires_limited_claim(self):
        forged = copy.deepcopy(self.result)
        forged['evidence'][0]['value'] = '1'
        self.assertFalse(all(check_grounding({'explanation_ko': '임의 설명'}, forged).values()))
        empty = self.rows[2]['mcp']['result']
        self.assertTrue(all(check_grounding({'explanation_ko': build_context(empty)['notice']}, empty).values()))
        self.assertFalse(check_grounding({'explanation_ko':build_context(empty)['notice']+' 성장률 100%.'},
                                         empty)['prose_rates_match_tool'])
