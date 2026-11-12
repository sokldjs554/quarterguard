"""Known human-labelled responses plus AI-authored counterexamples, no API calls."""
import copy
import json
import unittest
from contextlib import nullcontext
from quarterguard.store import ROOT
from quarterguard.evaluate_live_explanations_v9 import registry
from quarterguard.explanation_guards import check_grounding, check_prose
from quarterguard.live_verification import check_explanation


class ProseBindingFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=json.loads((ROOT/'artifacts/closeout-live-20261112/raw/closeout-live/human-review.json').read_text())
        cls.cases={r['id']:r for r in json.loads((ROOT/'data/llm-prose-v9-20261111/freeze.json').read_text())['cases']}

    def checks(self,index,text=None):
        r=self.records[index-1];answer=copy.deepcopy(r['raw_generated'])
        if text is not None:answer['explanation_ko']=text
        case=self.cases.get(r['case_id'].removeprefix('replay-')) if r['case_id'].startswith('replay-') else None
        with registry(case) if case else nullcontext():
            return check_explanation(answer,r['tool_result'])|check_prose(answer,r['tool_result'])|check_grounding(answer,r['tool_result'])

    def test_all_seventeen_human_true_responses_pass_without_rewriting(self):
        before=copy.deepcopy(self.records)
        for n in (2,3,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20):
            with self.subTest(review=n):
                c=self.checks(n);self.assertTrue(all(c.values()),[k for k,v in c.items() if not v])
        self.assertEqual(self.records,before)

    def test_three_human_ambiguous_responses_remain_withheld(self):
        for n in (1,4,16):
            with self.subTest(review=n):self.assertFalse(all(self.checks(n).values()))

    def test_date_scope_unit_amount_and_source_counterexamples_remain_withheld(self):
        changes=[
            (5,'2024-07-01','2024-01-01'),(5,'3개월, 연결','6개월, 연결'),
            (5,'3개월, 연결','3개월, 별도'),(5,'79,098,731','74,068,302'),
            (5,'PDF p.34와','PDF p.48와'),
            (9,'7월 1일','1월 1일'),(9,'3개월)','9개월)'),
            (9,'연결 기준 매출','별도 기준 매출'),(9,'백만 원','천 원'),
            (9,'34페이지','48페이지'),(9,'79,098,731 -','79,098,730 -'),
            (11,'2024년 2분기 매출','2024년 1분기 매출'),
            (11,'연결 매출','별도 매출'),(11,'p.34,','p.48,'),
            (12,'9월 30일','6월 30일'),(12,'3개월 간','6개월 간'),
            (12,'연결기준','별도기준'),(12,'34페이지','48페이지'),
            (13,'2022-07-01','2021-07-01'),(13,'3개월, 연결','3개월, 연결이 아닙니다'),
            (14,'2021년 동기간','2023년 동기간'),(14,'9개월 누적 연결','3개월 단독 연결'),
            (14,'2021년 동기간 누적','2021년 동기간 별도 누적'),
            (17,'2025년 3분기 연결','2025년 2분기 연결'),
            (17,'2024년 3분기 연결','2024년 3분기 별도'),
            (17,'PDF p.8','PDF p.9'),(17,'29.1445% 감소','29.1445% 증가'),
            (18,'2024년 3분기 대비 2025년','2025년 3분기 대비 2024년'),
            (19,'9개월 누적 연결','3개월 단독 연결'),(19,'2024년 7월','2024년 1월'),
            (20,'2025년 7월 1일','2024년 7월 1일'),(20,'PDF 8페이지','PDF 37페이지'),
        ]
        for n,old,new in changes:
            original=self.records[n-1]['raw_generated']['explanation_ko']
            self.assertIn(old,original)
            with self.subTest(review=n,change=(old,new)):
                self.assertFalse(all(self.checks(n,original.replace(old,new,1)).values()))

    def test_reported_issue_variants_cannot_claim_unobserved_execution_history(self):
        original=self.records[18]['raw_generated']['explanation_ko']
        for extra in [' 도구 실행 이력에 따르면 시작 월·일 조건 때문에 보류했습니다.',
                      ' 별도 재계산이 계산을 보류했습니다.',
                      ' 실제 근거는 없습니다.']:
            with self.subTest(extra=extra):self.assertFalse(all(self.checks(19,original+extra).values()))

    def test_ordered_citations_cannot_be_swapped(self):
        for n in (5,11):
            original=self.records[n-1]['raw_generated']['explanation_ko']
            a='Samsung Electronics 2024 3Q Interim Business Report PDF p.34'
            b='Samsung Electronics 2024 Half-year Business Report PDF p.48'
            wrong=original.replace(a,'TEMP').replace(b,a).replace('TEMP',b)
            with self.subTest(review=n):self.assertFalse(all(self.checks(n,wrong).values()))

    def test_raw_internal_codes_need_correct_korean_explanation_and_reported_issue(self):
        original=self.records[19]['raw_generated']['explanation_ko']
        for old,new in [('회사명이 달라 동일 회사 간 성장률 계산이 불가능하며','확인 필요하며'),
                        ('기간 불일치 문제도 보고되어 선택한 방식의 성장률 계산을 보류해야 합니다','확인이 필요합니다'),
                        ('COMPANY_MISMATCH','SCOPE_MISMATCH')]:
            with self.subTest(change=new):self.assertFalse(all(self.checks(20,original.replace(old,new)).values()))

    def test_new_binding_grammar_rejects_identity_and_uncovered_page_conflicts(self):
        changes=[(17,'영업이익','매출'),(17,'현대자동차','삼성전자'),
                 (11,'삼성전자','현대자동차'),(20,'삼성전자','현대자동차'),
                 (17,'PDF p.8','PDF p.8 및 PDF p.99'),
                 (20,'PDF 37페이지','PDF 37페이지 및 PDF 8페이지'),
                 (17,'연결 영업이익','USD 연결 영업이익')]
        for n,old,new in changes:
            original=self.records[n-1]['raw_generated']['explanation_ko']
            with self.subTest(review=n,change=new):self.assertFalse(all(self.checks(n,original.replace(old,new)).values()))

    def test_inherited_period_and_post_parenthesis_negation_cannot_change_meaning(self):
        changes=[(13,'3개월, 연결).','3개월, 연결)가 아닙니다.'),
                 (18,'3개월, 연결).','3개월, 연결)가 아닙니다.'),
                 (5,'3개월, 연결).','3개월, 연결)가 아닙니다.'),
                 (14,'2021년 동기간 누적','2021년 동기간 단독'),
                 (17,'3분기 연결','3분기 누계 연결'),
                 (17,'2025년 3분기 연결','2025년 3분기 및 4분기 연결'),
                 (14,'2021년 동기간 누적','2021년 동기간 연간 누적'),
                 (19,'3개월 단독 연결','3개월 누적 연결'),
                 (13,'3개월, 연결).','3개월, 연결)이 아니라 잘못된 수치입니다.')]
        for n,old,new in changes:
            original=self.records[n-1]['raw_generated']['explanation_ko']
            with self.subTest(review=n,change=new):self.assertFalse(all(self.checks(n,original.replace(old,new)).values()))

    def test_actual_provider_response_path_replays_without_calls_or_text_repair(self):
        import os
        import httpx
        from unittest.mock import patch
        from quarterguard import public_providers as pp
        for n,record in enumerate(self.records,1):
            case=self.cases.get(record['case_id'].removeprefix('replay-')) if record['case_id'].startswith('replay-') else None
            body={'status':'completed','model':pp.MODEL,'usage':{'input_tokens':1,'output_tokens':1},
                  'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(record['raw_generated'])}]}]}
            with registry(case) if case else nullcontext(), patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'}), patch.object(pp.httpx,'post',return_value=httpx.Response(200,json=body)):
                with self.subTest(review=n):
                    if n in (1,4,16):
                        with self.assertRaises(pp.ExplanationRejected):pp.generate_public({},record['tool_result'])
                    else:
                        returned=pp.generate_public({},record['tool_result'])
                        self.assertEqual(returned['generated'],record['raw_generated'])
                        self.assertFalse(returned['prose_semantics_verified'])

    def test_cache_version_changes_when_new_binding_rules_change(self):
        from pathlib import Path
        from unittest.mock import patch
        from quarterguard.public_providers import verification_version
        real_read=Path.read_bytes
        before=verification_version()
        def changed(path):
            value=real_read(path)
            return value+b'\n# simulated validator revision\n' if path.name=='prose_bindings.py' else value
        with patch.object(Path,'read_bytes',changed):self.assertNotEqual(verification_version(),before)

    def test_profit_loss_reversal_and_trailing_scope_contradiction_are_rejected(self):
        for n,old,new in [(17,'영업이익','영업손실'),(13,'영업이익','영업손실'),
                          (14,'당기순이익','당기순손실'),
                          (13,'3개월, 연결).','3개월, 연결), 별도 기준입니다.')]:
            original=self.records[n-1]['raw_generated']['explanation_ko']
            with self.subTest(review=n,change=new):self.assertFalse(all(self.checks(n,original.replace(old,new)).values()))

    def test_additional_registered_metric_and_scope_examples_pass(self):
        from scripts.evaluate_prose_binding_followup import synthetic_cases
        cases=[c for c in synthetic_cases() if c['expected_passed']]
        self.assertEqual(len(cases),16)
        for c in cases:
            with self.subTest(case=c['id']):
                self.assertTrue(all((check_explanation(c['answer'],c['tool_result'])|check_prose(c['answer'],c['tool_result'])|check_grounding(c['answer'],c['tool_result'])).values()))

    def test_additional_wrong_amount_scope_source_currency_examples_are_withheld(self):
        from scripts.evaluate_prose_binding_followup import synthetic_cases
        cases=[c for c in synthetic_cases() if not c['expected_passed']]
        self.assertEqual(len(cases),64)
        for c in cases:
            with self.subTest(case=c['id']):
                self.assertFalse(all((check_explanation(c['answer'],c['tool_result'])|check_prose(c['answer'],c['tool_result'])|check_grounding(c['answer'],c['tool_result'])).values()))
