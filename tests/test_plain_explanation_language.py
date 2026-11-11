"""Disclosed prose leaks: inspect real guard behavior, no model calls."""
import copy
import json
import unittest
from quarterguard.store import ROOT
from quarterguard.explanation_guards import check_prose


class PlainExplanationLanguageTests(unittest.TestCase):
    def test_internal_codes_in_prose_are_rejected_without_mutating_response(self):
        rows=json.loads((ROOT/'artifacts/llm-prose-v7-20261110/report.json').read_text())['records']
        for case in ('no-evidence','s22-op-qoq'):
            row=next(r for r in rows if r['case_id']==case)
            original=copy.deepcopy(row)
            with self.subTest(case=case):
                self.assertFalse(check_prose(row['generated'],row['tool_result'])['prose_review_language_localized'])
                self.assertEqual(row,original)

    def test_korean_prose_keeps_machine_codes_and_financial_terms_intact(self):
        result={'issues':['SEARCH_EMPTY'],'status':'needs_review','evidence':[]}
        answer={'issues':['SEARCH_EMPTY'],'status':'needs_review','evidence_ids':[],
                'explanation_ko':'현재 검색 조건으로 확인할 수 있는 근거를 찾지 못했습니다. KRW는 원화 통화입니다.'}
        self.assertTrue(check_prose(answer,result)['prose_review_language_localized'])
        for text in ['조건은 `qoq_adjacent`입니다.','원인은 SEARCH_EMPTY입니다.',
                     'Search_Empty: 확인 필요','(QOQ_ADJACENT) 조건 불일치']:
            with self.subTest(text=text):
                self.assertFalse(check_prose(answer|{'explanation_ko':text},result)['prose_review_language_localized'])
        self.assertEqual(answer['issues'],['SEARCH_EMPTY'])
