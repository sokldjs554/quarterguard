# Local CPU ranking experiment v2

This benchmark runs real neural inference without a paid API. It does not deploy a reranker or change verified financial answering. Old `artifacts/evaluation.json` and all prior data remain untouched.

## Method and reproducibility

The original development corpus is 192 curated facts and the original 36 queries from `data/retrieval_gold.json`. The separately frozen `data/v2-blind` corpus is a fixture-assisted retrieval diagnostic, not proof of raw-PDF parsing success. Its gold is authored by another AI worker in the same task, without human review. Some Samsung 2023 values already occur in the older 2024 reports as comparatives; document novelty does not make all values unseen.

`full_corpus_retrieval` reruns the original six conditions: fixed-character word TF-IDF, cell word TF-IDF, cell character TF-IDF, filtered hybrid, BGE-small, and MiniLM. Fixed chunks split a serialized table every 180 characters and lose column/header context; cell chunks serialize explicit financial context for each cell. This information inequality prevents a causal claim that chunk size alone explains the difference. The current search implementation also derives fixed headers from facts rather than hardcoding the original issuer/years. Source hashes and dataset hashes are recorded, so the new results must not be presented as a byte-identical replay of old code.

`same_pool_ranking` fixes candidate IDs per query and condition using the cell hybrid top 20, then compares cell word, cell character, cell hybrid, both dense models, and a cross encoder. Each query's candidate IDs, final top five IDs, relevant fact IDs, and scores are retained. The unfiltered condition tests actual ranking among competing financial contexts. The filtered condition enforces explicit parser constraints before selecting candidates; blocked queries have no candidates. Missing fields may still produce candidates but never establish a trusted answer. Filtering can leave only one candidate, making further reranking trivial. No reranker can insert an excluded candidate.

The cross encoder is `Xenova/ms-marco-MiniLM-L-6-v2` at HF revision `a09144355adeed5f58c8ed011d209bf8ee5a1fec`, the Transformers.js ONNX conversion of `cross-encoder/ms-marco-MiniLM-L-6-v2`. FastEmbed's supported-model registry specifies Apache-2.0. The downloaded model is 90,992,115 bytes; ONNX SHA-256 is `c623d0bcb99f4622beb413eaef00cfbe5db20df9f1dd982da4b4f26022881870`. It tokenizes each query and document together and runs transformer sequence classification; it is not a metadata filter relabeled as reranking. Both dense baselines use the existing locally cached ONNX weights, with exact repository revisions and hashes in each artifact. All neural models use CPUExecutionProvider with two threads.

Shared controlled Korean/English normalization is applied to all methods. These English models and controlled financial vocabulary do not establish general Korean or multilingual retrieval quality. The model and top-20 candidate limit were selected before viewing new frozen results; the experiment does not tune on frozen gold.

Install with `.venv/bin/python -m pip install -r requirements-rerank.txt`. Download pinned public model weights once into ignored `work/models` (no API key required):

```python
from huggingface_hub import snapshot_download
snapshot_download(
    'Xenova/ms-marco-MiniLM-L-6-v2',
    revision='a09144355adeed5f58c8ed011d209bf8ee5a1fec',
    cache_dir='work/models',
    allow_patterns=['onnx/model.onnx', 'config.json', 'tokenizer.json',
                    'tokenizer_config.json', 'special_tokens_map.json',
                    'vocab.txt', 'README.md', 'LICENSE'])
```

If the platform disallows writing to the home directory, set `HF_HOME` to the ignored project `work/hf` directory and `HF_HUB_DISABLE_XET=1` before downloading. TLS verification remains enabled. Dense snapshot repositories/revisions are in `DENSE_MODELS`; download the listed revisions with the same cache location if absent.

Run with a **new** artifact name; the runner refuses overwrite:

```bash
HF_HUB_OFFLINE=1 .venv/bin/python -m quarterguard.ranking_evaluation_v2 \
  --dataset data --evaluation-stage development --output artifacts/ranking-v2-dev-first.json
HF_HUB_OFFLINE=1 .venv/bin/python -m quarterguard.ranking_evaluation_v2 \
  --dataset data/v2-blind --evaluation-stage frozen_first --output artifacts/ranking-v2-blind-first.json
.venv/bin/python -m unittest tests.test_ranking_v2 -v
```

Warm latency is one sequential measured pass after an explicit warmup, including candidate retrieval, selection, and scoring. Dense corpus embedding, cached cold model load, and warmup are reported separately. Here cached cold load means creating a fresh model session from already downloaded files; the machine/filesystem cache was not flushed and may be warm from earlier runs. It is not empty-cache installation latency. Download time is excluded. These are descriptive measurements on a shared CPU host, not a service-level latency guarantee. Recall and MRR use nonempty-gold rows only, with any relevant fact counted; empty-gold candidate emission is reported separately and is not answer correctness. No confidence intervals or significance claims are made for these small samples. Zero paid API calls means zero provider API spend, not zero CPU/storage/network cost.

## Recorded outcomes

Artifacts retain every first-run row, including regressions. No human review, expert review, or production usefulness claim follows from this experiment alone.

On development and the first 2023 blind set, the real cross encoder did **not** improve the chosen hybrid baseline. It reduced development top-one recall and tied 2023 blind top-one recall while slightly reducing blind MRR, at roughly two orders of magnitude greater unfiltered median latency. The final tiny 2022 set below has a one-case gain over hybrid, while cell word remains better. Taken together these measurements do not justify replacing the cheaper lexical method for this bounded task.

| Same unfiltered top-20 pool | Dev R@1 | Dev MRR@5 | Dev p50/p95 ms | Blind R@1 | Blind MRR@5 | Blind p50/p95 ms |
|---|---:|---:|---:|---:|---:|---:|
| cell_word | 1.0000 | 1.0000 | 1.52/2.19 | 0.4286 | 0.6429 | 1.25/1.60 |
| cell_char | 0.8889 | 0.9398 | 1.52/2.19 | 0.5714 | 0.7286 | 1.24/1.60 |
| cell_hybrid | 1.0000 | 1.0000 | 1.52/2.19 | 0.5000 | 0.7143 | 1.24/1.60 |
| BAAI/bge-small-en-v1.5 | 0.5278 | 0.7431 | 10.25/12.45 | 0.4286 | 0.5917 | 10.01/16.20 |
| sentence-transformers/all-MiniLM-L6-v2 | 0.4722 | 0.6676 | 5.75/6.95 | 0.5000 | 0.6512 | 6.22/9.20 |
| cross_encoder | 0.8056 | 0.9028 | 149.47/228.44 | 0.5000 | 0.6964 | 128.16/170.13 |

Development filtered recall is 36/36 for every method because each query has exactly one eligible candidate; this is not evidence of neural improvement. Blind filtered recall is 10/14 for every method, with four positive queries blocked by the current vocabulary/parser. The other 10 blind cases have empty gold: raw ranking emits candidates for all 10; filtered ranking emits candidates for 2, both incomplete queries. That emission is a candidate-retrieval diagnostic, not a verified-answer or clarification metric. No-answer rows are excluded from recall denominators.

The full-corpus six-condition panel is retained separately in the JSON files. Development R@1: fixed word 0.0833, cell word 1.0000, cell character 0.8889, filtered hybrid 1.0000, BGE 0.4444, MiniLM 0.4722. Blind R@1: fixed word 0.2143, cell word 0.4286, cell character 0.5714, filtered hybrid 0.7143, BGE 0.3571, MiniLM 0.5000. These runs use exactly the same query IDs and gold within each dataset; datasets are not pooled.

| Cached cold setup, development run | Model load ms | Corpus encoding ms | Warmup ms |
|---|---:|---:|---:|
| BAAI/bge-small-en-v1.5 | 255.23 | 2688.08 | 8.25 |
| sentence-transformers/all-MiniLM-L6-v2 | 188.47 | 1129.84 | 3.91 |
| cross_encoder | 184.04 | 0.00 | 218.46 |

The cross encoder has no precomputed corpus embeddings; its zero corpus-encoding entry is not zero query cost. All setup and query timings for the blind run are separately retained in its artifact.

Evidence: [`ranking-v2-dev-first.json`](../artifacts/ranking-v2-dev-first.json), [`ranking-v2-blind-first.json`](../artifacts/ranking-v2-blind-first.json). The tests verify that gold and candidate IDs match across every paired condition, excluded candidates cannot return, and the actual recorded neural scores vary and change ordering.

## Disclosed follow-up

After preserving the first blind run, the query parser gained the disclosed `상반기` and registered Hyundai Motor aliases. [`ranking-v2-disclosed-followup.json`](../artifacts/ranking-v2-disclosed-followup.json) reruns the exact same 24 questions, gold, top-20 policy, and neural models. Its `evaluation_stage` is `disclosed_regression`; it is no longer a held-out result. The first artifacts remain unchanged.

| Condition | R@1 (14 positive rows) | MRR@5 | p50/p95 ms | Empty-gold candidate emission (10 rows) |
|---|---:|---:|---:|---:|
| unfiltered/cell_hybrid | 0.5000 | 0.7143 | 1.48/1.87 | 1.00 |
| unfiltered/cross_encoder | 0.5000 | 0.6964 | 148.95/214.19 | 1.00 |
| filtered/cell_hybrid | 1.0000 | 1.0000 | 2.17/3.11 | 0.20 |
| filtered/cross_encoder | 1.0000 | 1.0000 | 12.50/17.88 | 0.20 |

This follow-up measures the parser correction, not a learned reranker improvement. Model weights, candidate budget and gold were unchanged. First-run failures remain evidence of the original generalization limit.

## Final 2022 frozen first run

[`ranking-v2-final-first.json`](../artifacts/ranking-v2-final-first.json) evaluates the separately frozen `data/v2-final` fixture: 16 curated cells and eight questions (six answerable, two empty gold). It performs the same actual CPU inference with unchanged model revisions, normalization implementation, and candidate-budget setting. Because the corpus has only 16 cells, the unfiltered top-20 pool contains all 16; it is easier to cover the whole corpus than in the development or 2023 runs. This is fixture-assisted ranking, not a measurement of raw-PDF extraction.

The source is a new 2022 Q3 official document, but 2022 current values overlap the previous round’s 2023 comparative values. Four of the six positive questions target 2021 comparative values new to both earlier datasets. Gold was frozen after the disclosed parser fixes, before this final source was run; no changes or tuning were made from these final results. The gold still has no human review.

| Same unfiltered 16-candidate pool | R@1 (six positive rows) | MRR@5 | p50/p95 ms |
|---|---:|---:|---:|
| cell_word | 1.0000 | 1.0000 | 1.19/1.80 |
| cell_char | 0.6667 | 0.8333 | 1.19/1.80 |
| cell_hybrid | 0.6667 | 0.8333 | 1.19/1.80 |
| BAAI/bge-small-en-v1.5 | 0.5000 | 0.7222 | 10.86/15.92 |
| sentence-transformers/all-MiniLM-L6-v2 | 0.5000 | 0.7500 | 6.67/8.47 |
| cross_encoder | 0.8333 | 0.9167 | 104.66/128.40 |

The cross encoder retrieves the correct first candidate in 5/6 cases, versus hybrid 4/6 and cell word 6/6. That one-case hybrid gain accompanies median latency of 104.66ms versus 1.19ms; it is too small a sample to support a general improvement claim and does not surpass the best lexical baseline. Every filtered method reaches 6/6 because each positive query has one eligible candidate. Filtered candidate emission on the two empty-gold questions is 1/2 (the incomplete question); unfiltered emission is 2/2. These emissions remain separate from verified answering.

In this fresh process, cached model-session load was 240.02ms for BGE, 210.20ms for MiniLM and 202.03ms for the cross encoder. Corpus embedding took 184.62ms and 100.58ms respectively for the dense models. Cross-encoder warmup took 210.35ms. The already-downloaded weights and potentially warm filesystem cache mean these measurements exclude network download and machine cold-start cost. All earlier artifacts and first-run failures remain unchanged.
