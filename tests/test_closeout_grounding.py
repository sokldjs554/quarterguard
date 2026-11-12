import copy
import json
import unittest
from contextlib import nullcontext
from quarterguard.store import ROOT
from quarterguard.evaluate_live_explanations_v9 import registry
from quarterguard.explanation_guards import check_grounding, check_prose


class CloseoutGroundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT/'artifacts/model-completion-live-20261112/raw/completion-live/human-review.json').read_text())
        cls.cases = {r['id']: r for r in json.loads((ROOT/'data/llm-prose-v9-20261111/freeze.json').read_text())['cases']}

    def checks(self, index, text=None):
        row = self.rows[index - 1]
        answer = copy.deepcopy(row['raw_generated'])
        if text is not None: answer['explanation_ko'] = text
        case = self.cases.get(row['case_id'].removeprefix('replay-')) if row['case_id'].startswith('replay-') else None
        with registry(case) if case else nullcontext():
            return check_grounding(answer, row['tool_result']) | check_prose(answer, row['tool_result'])

    def test_explicit_correct_bindings_do_not_require_verbatim_sentences(self):
        for index in (1, 4, 5, 6, 9, 11, 17):
            with self.subTest(review=index):
                checks = self.checks(index)
                self.assertTrue(all(checks.values()), [k for k, v in checks.items() if not v])

    def test_wrong_date_scope_page_or_amount_stays_blocked(self):
        original = self.rows[0]['raw_generated']['explanation_ko']
        for old, new in [('2024-07-01', '2024-01-01'), ('3개월, 연결', '6개월, 연결'),
                         ('3개월, 연결', '3개월, 별도'), ('p.34', 'p.48'),
                         ('79,098,731', '74,068,302')]:
            with self.subTest(change=(old,new)):
                checks = self.checks(1, original.replace(old,new,1))
                self.assertFalse(all(checks.values()))

    def test_draft_rejection_does_not_hide_an_additional_evidence_absence_claim(self):
        text = self.rows[8]['raw_generated']['explanation_ko']
        self.assertTrue(self.checks(9)['prose_evidence_presence_consistent'])
        self.assertFalse(self.checks(9, text+' 실제 근거는 없습니다.')['prose_evidence_presence_consistent'])
        self.assertFalse(self.checks(9, text+' 초안과 관계없이 검색 결과는 없습니다.')['prose_evidence_presence_consistent'])

    def test_known_false_and_ambiguous_prose_remains_blocked(self):
        for index in (2, 3, 7, 10, 12, 13, 15, 19, 20):
            with self.subTest(review=index):
                self.assertFalse(all(self.checks(index).values()))

    def test_internal_codes_still_require_plain_language(self):
        self.assertFalse(self.checks(16)['prose_review_language_localized'])

    def test_wrong_explicit_page_cannot_inherit_a_correct_reference(self):
        text = self.rows[5]['raw_generated']['explanation_ko']
        wrong = text.replace('동일 문서와 페이지', 'Samsung Electronics 2024 3Q Interim Business Report PDF 48페이지')
        self.assertFalse(self.checks(6, wrong)['prose_evidence_anchors_present'])

    def test_negated_or_conflicting_fields_never_count_as_positive_context(self):
        text=self.rows[0]['raw_generated']['explanation_ko']
        for old,new in [('3개월, 연결)', '3개월이 아닌 6개월, 연결)'),
                        ('3개월, 연결)', '3개월, 연결이 아닙니다)'),
                        ('2024-07-01~2024-09-30,', '2024-07-01~2024-09-30가 아닌 2024-01-01~2024-09-30,')]:
            with self.subTest(change=new):self.assertFalse(all(self.checks(1,text.replace(old,new,1)).values()))

    def test_conflicting_page_before_amount_is_also_rejected(self):
        text=self.rows[0]['raw_generated']['explanation_ko']
        for page in ('p.48','p. 48','48페이지'):
            wrong=text.replace('2024년 3분기 연결 매출은',f'Samsung Electronics 2024 3Q Interim Business Report PDF {page}에서 2024년 3분기 연결 매출은',1)
            with self.subTest(page=page):self.assertFalse(all(self.checks(1,wrong).values()))
