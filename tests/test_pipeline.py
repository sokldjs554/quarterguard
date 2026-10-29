import unittest, asyncio
from quarterguard.store import load_facts
from quarterguard.search import SearchIndex

class CorpusTests(unittest.TestCase):
    def test_corpus_size_and_gold(self):
        facts=load_facts(); self.assertEqual(len(facts),192)
        d={f.id:f for f in facts}
        self.assertEqual(d['s24q3-CFS-revenue-2024-q-KRW'].value,'79098731')
        self.assertEqual(d['s24q2-CFS-revenue-2024-ytd-KRW'].value,'145983903')
        self.assertEqual(d['s24q3-OFS-operating_profit-2023-q-KRW'].value,'-2167988')
    def test_search_context(self):
        hits=SearchIndex(load_facts(),'hybrid_meta').search('삼성전자 2024 3분기 연결 매출액 3개월 KRW',3)
        self.assertIn('s24q3-CFS-revenue-2024-q-KRW',hits[0]['fact_ids'])
    def test_empty_query(self): self.assertEqual(SearchIndex(load_facts()).search(' ',3),[])
    def test_invalid_config(self):
        with self.assertRaises(ValueError): SearchIndex(load_facts(),'invented')

if __name__=='__main__':unittest.main()
