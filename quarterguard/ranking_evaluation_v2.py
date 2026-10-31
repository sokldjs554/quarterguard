"""Offline CPU ranking experiment; never changes gold, old artifacts, or product ranking.

The controlled panel ranks the exact same candidate IDs with lexical, dense, and
query/document cross-encoder scores. The legacy panel exposes the original six
retrieval conditions, including their deliberately unequal chunk representations.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from .core import Fact
from .search import SearchIndex, chunks, normalize, compatible, constraints
from .store import ROOT

RERANKER = ('Xenova/ms-marco-MiniLM-L-6-v2', 'a09144355adeed5f58c8ed011d209bf8ee5a1fec')
DENSE_MODELS = [
    ('BAAI/bge-small-en-v1.5', 'qdrant/bge-small-en-v1.5-onnx-q', 'aa8f8b060edb00e03bfdd08813a2949946c8ba55', 'mit'),
    ('sentence-transformers/all-MiniLM-L6-v2', 'qdrant/all-MiniLM-L6-v2-onnx', 'd13954661f83248295ba75c1ed411eef3b7b936e', 'apache-2.0'),
]


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def select_pool(corpus, scores, eligible, size):
    indices = sorted(eligible, key=lambda i: (-float(scores[i]), corpus[i]['id']))[:size]
    return [dict(corpus[i], score=float(scores[i])) for i in indices]


def rerank_pool(query, pool, model):
    if not pool:
        return []
    scores = list(model.rerank(normalize(query), [normalize(item['text']) for item in pool]))
    if len(scores) != len(pool) or not np.isfinite(scores).all():
        raise ValueError('INVALID_RERANK_SCORES')
    ranked = [dict(item, rerank_score=float(score)) for item, score in zip(pool, scores)]
    return sorted(ranked, key=lambda item: (-item['rerank_score'], item['id']))


def result_row(case, pool, ranked, latency_ms, scoring_ms):
    gold = case.get('gold_fact_ids', [case['gold_fact_id']] if case.get('gold_fact_id') else [])
    gold = sorted(set(gold))
    top = ranked[:5]
    rank = next((i+1 for i, item in enumerate(top) if set(gold) & set(item['fact_ids'])), 0)
    return {'id': case['id'], 'query': case['query'], 'gold_fact_ids': gold,
            'expected_clarification': case.get('expected_clarification', False),
            'rank': rank, 'gold_in_candidate_pool': any(set(gold) & set(item['fact_ids']) for item in pool),
            'candidate_ids': [item['id'] for item in pool],
            'retrieved': [item['id'] for item in top],
            'retrieved_fact_ids': [item['fact_ids'] for item in top],
            'scores': [item.get('rerank_score', item.get('score')) for item in top],
            'latency_ms': latency_ms, 'scoring_ms': scoring_ms}


def summarize(rows):
    answerable = [row for row in rows if row['gold_fact_ids']]
    empty = [row for row in rows if not row['gold_fact_ids']]
    def avg(values):
        return sum(values)/len(values) if values else None
    return {'n': len(rows), 'answerable_n': len(answerable), 'no_gold_n': len(empty),
            'recall_at_1': avg([row['rank'] == 1 for row in answerable]),
            'recall_at_3': avg([0 < row['rank'] <= 3 for row in answerable]),
            'mrr_at_5': avg([1/row['rank'] if row['rank'] else 0 for row in answerable]),
            'candidate_recall': avg([row['gold_in_candidate_pool'] for row in answerable]),
            'no_gold_candidate_emission_rate': avg([bool(row['retrieved']) for row in empty]),
            'latency_p50_ms': float(np.median([row['latency_ms'] for row in rows])),
            'latency_p95_ms': float(np.percentile([row['latency_ms'] for row in rows], 95)),
            'scoring_p50_ms': float(np.median([row['scoring_ms'] for row in rows]))}


def snapshot(cache, repo, revision):
    path = cache / ('models--' + repo.replace('/', '--')) / 'snapshots' / revision
    if not path.is_dir():
        raise FileNotFoundError(f'MODEL_NOT_CACHED: {repo}@{revision}; see docs/ranking-v2.md')
    return path


def model_record(path, name, repo, revision, license_name, setup_ms):
    return {'model': name, 'repository': repo, 'revision': revision, 'license': license_name,
            'files_sha256': {str(p.relative_to(path)): sha256(p) for p in sorted(path.rglob('*')) if p.is_file()},
            'cached_model_load_ms': setup_ms, 'providers': ['CPUExecutionProvider'], 'threads': 2}


def query_eligibility(query, facts, corpus):
    # The parser's missing fields allow candidates; they never imply trusted answers.
    from .query import parse_query
    parsed = parse_query(query, companies={f.company for f in facts})
    eligible = set() if parsed['blocked'] else {
        i for i, item in enumerate(corpus)
        if all(compatible(next(f for f in facts if f.id == fid), parsed['filters']) for fid in item['fact_ids'])}
    return eligible, parsed


def evaluate(dataset, cache, candidate_k=20, evaluation_stage="unspecified"):
    from fastembed import TextEmbedding
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    started = time.perf_counter()
    facts_path, gold_path = dataset/'facts.json', dataset/'retrieval_gold.json'
    facts = [Fact(**{k:v for k,v in row.items() if k != 'months'}) for row in json.loads(facts_path.read_text())]
    gold = json.loads(gold_path.read_text())
    if not gold or len({row['id'] for row in gold}) != len(gold):
        raise ValueError('EMPTY_OR_DUPLICATE_CASE_IDS')
    known = {fact.id for fact in facts}
    for row in gold:
        ids = row.get('gold_fact_ids', [row['gold_fact_id']] if row.get('gold_fact_id') else [])
        if not set(ids) <= known:
            raise ValueError('GOLD_FACT_OUTSIDE_CORPUS')
    t = time.perf_counter()
    cell = SearchIndex(facts, 'cell_word')
    fixed = SearchIndex(facts, 'fixed_word')
    lexical_setup = (time.perf_counter()-t)*1000
    corpus = cell.chunks
    corpus_by_id = {item['id']: i for i, item in enumerate(corpus)}
    normalized = [normalize(item['text']) for item in corpus]
    models, vectors, provenance = {}, {}, {}
    for name, repo, revision, license_name in DENSE_MODELS:
        path = snapshot(cache, repo, revision)
        t = time.perf_counter()
        model = TextEmbedding(model_name=name, specific_model_path=str(path), threads=2, providers=['CPUExecutionProvider'])
        load_ms = (time.perf_counter()-t)*1000
        t = time.perf_counter()
        vectors[name] = np.array(list(model.embed(normalized)))
        index_ms = (time.perf_counter()-t)*1000
        t = time.perf_counter()
        list(model.query_embed([normalize(gold[0]['query'])]))
        warmup_ms = (time.perf_counter()-t)*1000
        models[name] = model
        provenance[name] = model_record(path, name, repo, revision, license_name, load_ms) | {
            'corpus_embedding_ms': index_ms, 'warmup_query_ms': warmup_ms,
            'dimension': int(vectors[name].shape[1])}
    path = snapshot(cache, *RERANKER)
    t = time.perf_counter()
    cross = TextCrossEncoder(model_name=RERANKER[0], specific_model_path=str(path), threads=2, providers=['CPUExecutionProvider'])
    load_ms = (time.perf_counter()-t)*1000
    t = time.perf_counter()
    list(cross.rerank(normalize(gold[0]['query']), normalized[:candidate_k]))
    provenance['cross_encoder'] = model_record(path, RERANKER[0], *RERANKER, 'apache-2.0', load_ms) | {
        'warmup_query_ms': (time.perf_counter()-t)*1000,
        'architecture': 'Joint query/document tokenization and transformer sequence-classification score; actual ONNX CPU inference',
        'upstream_model': 'cross-encoder/ms-marco-MiniLM-L-6-v2'}
    panels = {'full_corpus_retrieval': {}, 'same_pool_ranking': {}}
    diagnostics = []
    for case in gold:
        query = case['query']
        t = time.perf_counter()
        normalized_query = normalize(query)
        word = (cell.w @ cell.word.transform([normalized_query]).T).toarray().ravel()
        char = (cell.c @ cell.char.transform([normalized_query]).T).toarray().ravel()
        scores = {'cell_word': word, 'cell_char': char, 'cell_hybrid': .5*word+.5*char}
        lexical_ms = (time.perf_counter()-t)*1000
        t = time.perf_counter()
        eligible, diagnostic = query_eligibility(query, facts, corpus)
        filter_ms = (time.perf_counter()-t)*1000
        diagnostics.append({'id':case['id'], **diagnostic})
        scoring_times = {name:lexical_ms for name in scores}
        for name, model in models.items():
            t = time.perf_counter()
            vector = np.array(list(model.query_embed([normalized_query])))[0]
            scores[name] = vectors[name] @ vector
            scoring_times[name] = (time.perf_counter()-t)*1000
        # Original six conditions: fixed/cell word, cell character, filtered hybrid, two dense.
        for name in ['cell_word', 'cell_char', 'hybrid_meta', *models]:
            key = 'cell_hybrid' if name == 'hybrid_meta' else name
            allowed = eligible if name == 'hybrid_meta' else set(range(len(corpus)))
            t = time.perf_counter()
            pool = select_pool(corpus, scores[key], allowed, candidate_k)
            sorting_ms = (time.perf_counter()-t)*1000
            latency = scoring_times[key]+sorting_ms+(filter_ms if name == 'hybrid_meta' else 0)
            row = result_row(case, pool, pool, latency, scoring_times[key])
            panels['full_corpus_retrieval'].setdefault(name, []).append(row)
        t = time.perf_counter()
        fixed_hits = fixed.search(query, candidate_k)
        fixed_ms = (time.perf_counter()-t)*1000
        panels['full_corpus_retrieval'].setdefault('fixed_word', []).append(result_row(case, fixed_hits, fixed_hits, fixed_ms, fixed_ms))
        for condition, allowed in [('unfiltered', set(range(len(corpus)))), ('filtered', eligible)]:
            t = time.perf_counter()
            pool = select_pool(corpus, scores['cell_hybrid'], allowed, candidate_k)
            candidate_ms = lexical_ms+(time.perf_counter()-t)*1000+(filter_ms if condition == 'filtered' else 0)
            for name, values in scores.items():
                t = time.perf_counter()
                ranked = sorted([dict(item, score=float(values[corpus_by_id[item['id']]])) for item in pool],
                                key=lambda item:(-item['score'], item['id']))
                extra_ms = (time.perf_counter()-t)*1000
                # Lexical retrieval cost already includes both sparse vectors.
                score_ms = 0 if name.startswith('cell_') else scoring_times[name]
                row = result_row(case, pool, ranked, candidate_ms+score_ms+extra_ms, score_ms+extra_ms)
                panels['same_pool_ranking'].setdefault(condition+'/'+name, []).append(row)
            t = time.perf_counter()
            ranked = rerank_pool(query, pool, cross)
            rerank_ms = (time.perf_counter()-t)*1000
            row = result_row(case, pool, ranked, candidate_ms+rerank_ms, rerank_ms)
            panels['same_pool_ranking'].setdefault(condition+'/cross_encoder', []).append(row)
    return {'created_at': datetime.now(timezone.utc).isoformat(), 'dataset': str(dataset.relative_to(ROOT)) if dataset.is_relative_to(ROOT) else str(dataset),
            'facts_sha256':sha256(facts_path), 'gold_sha256':sha256(gold_path), 'case_ids':[row['id'] for row in gold],
            'evaluation_stage':evaluation_stage, 'human_reviewed':False, 'selection_policy':'Preselected model and candidate_k; no tuning against new frozen gold',
            'python':platform.python_version(), 'platform':platform.platform(),
            'packages':{name:importlib.metadata.version(name) for name in ['fastembed','onnxruntime','numpy','scikit-learn']},
            'source_sha256':{p:sha256(ROOT/p) for p in ['quarterguard/ranking_evaluation_v2.py','quarterguard/search.py','quarterguard/query.py']},
            'facts':len(facts), 'cell_chunks':len(corpus), 'fixed_chunks':len(fixed.chunks), 'candidate_k':candidate_k,
            'normalization':'Shared controlled Korean/English financial vocabulary; English models, no multilingual-generalization claim',
            'fixed_chunk_caveat':'Fixed 180-character chunks lose shared table header/column context; this is representation inequality, not an isolated chunk-size causal test.',
            'candidate_policy':'Controlled panel uses identical hybrid top-k IDs per query per condition; filtered candidates obey explicit constraints before scoring. Missing fields retain candidates but do not establish verified answers.',
            'timing_policy':'Single sequential warm query pass after explicit warmup; end-to-end retrieval+selection+ranking latency; cached cold model load, corpus encoding and warmup separately. Download time excluded; shared host timings are descriptive.',
            'metric_policy':'Recall/MRR use rows with nonempty gold only; any relevant gold counts. Empty-gold candidate emission is not answer correctness. Retrieval is not verified answering.',
            'lexical_index_build_ms':lexical_setup, 'models':provenance,
            'provider_api_calls':0, 'provider_api_cost_usd':0, 'cost_scope':'No paid APIs; excludes CPU, storage and download costs',
            'elapsed_ms':(time.perf_counter()-started)*1000, 'query_diagnostics':diagnostics,
            **{panel:{name:{'metrics':summarize(rows),'rows':rows} for name,rows in methods.items()} for panel,methods in panels.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=ROOT/'data')
    parser.add_argument('--cache', type=Path, default=ROOT/'work/models')
    parser.add_argument('--candidate-k', type=int, default=20, choices=range(1,21))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evaluation-stage', choices=['development', 'frozen_first', 'disclosed_regression', 'unspecified'], default='unspecified')
    args = parser.parse_args()
    # New evidence is immutable by default, including accidental reruns.
    if args.output.exists():
        parser.error('Output already exists; choose a new versioned artifact path')
    result = evaluate(args.dataset.resolve(), args.cache.resolve(), args.candidate_k, args.evaluation_stage)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({panel:{name:entry['metrics'] for name,entry in result[panel].items()}
                      for panel in ['full_corpus_retrieval','same_pool_ranking']}, indent=2))


if __name__ == '__main__':
    main()
