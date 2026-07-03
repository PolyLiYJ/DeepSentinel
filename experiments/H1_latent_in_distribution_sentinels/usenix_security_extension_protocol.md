# USENIX Security Extension Protocol

## Goal

Upgrade the current DeepSentinel evidence from a retrieval-filtering pilot into
a USENIX Security-style evaluation. The defense remains one scheme:
selection-only, distribution-preserving latent sentinels. We only strengthen the
attacks, datasets, utility measurements, and detection statistics.

## Claims to Support

1. **Filtering robustness:** DeepSentinel survives realistic pre-index data
   cleaning filters better than visible-key and hidden-outlier sentinels.
2. **Attacker cost:** removing DeepSentinel requires measurable utility loss on
   normal retrieval/generation workloads.
3. **Ownership detectability:** after filtering and generation-side evidence
   dilution, a black-box owner can still detect misuse at fixed low FPR.
4. **Domain transfer:** the selection-only mechanism holds beyond COCO natural
   images, preferably on a product or art-style dataset.

## Experiment Matrix

### E1: Exact RAIG Proxy on COCO-5k

Run `src/raig_proxy_evidence.py` on the COCO-5k embedding cache rather than the
aggregate CSV approximation.

Success criterion: at generation retention `g=0.5`, DeepSentinel TPR remains
close to the aggregate estimate, roughly 0.94--0.96 at FPR `2.79e-05`, while
the hidden-outlier baseline collapses under stronger density pruning.

### E2: Real RAIG Generation Layer

Use the same selected COCO-5k sentinels and private triggers. Retrieve top-k
images after filtering and feed them to one image-conditioned generation stack,
for example SDXL + IP-Adapter or a lightweight RAG-style image-to-image
pipeline. This is not a new defense; it tests whether retrieved evidence remains
auditable after generation.

Report:

- sentinel evidence match rate in generated outputs;
- TPR at fixed FPR using the same trigger threshold;
- non-trigger generation utility with and without filtering.

### E3: Stronger Adaptive Pre-Index Attacks

Evaluate attacks separately and in calibrated budgets:

- OCR/text filter: removes visible/random-key sentinels before indexing.
- CLIP outlier filter: removes low global similarity or high distance samples.
- Local-density pruning: current main attack.
- Dedup / near-duplicate removal: removes visually redundant samples by
  image-embedding cosine threshold.
- Caption-image mismatch filter: removes samples whose caption/text metadata is
  semantically inconsistent with the image, if captions are available.

For each attack, report sentinel survival, trigger hit@k, ownership TPR, and
normal utility loss. Do not combine these as a defense; combinations are only
adaptive attacker variants.

### E4: Larger and Non-Natural-Image Datasets

Minimum target:

- COCO validation/full available subset as natural-image benchmark.
- Product-10K or another product-domain dataset as non-natural transfer test.

Optional:

- LAION subset for web-scale noise.
- WikiArt or art-domain subset if the paper emphasizes creative datasets.

### E5: Utility Damage

Move beyond "fraction of normal images removed." For each filtered index,
measure:

- normal query Recall@K or retrieved-neighbor preservation;
- mean top-k CLIP similarity for non-trigger prompts;
- retrieval diversity, e.g. unique image clusters or average pairwise distance;
- generation utility for the real RAIG layer, e.g. CLIPScore or image-text
  similarity on benign prompts.

### E6: Detection Statistics

Report:

- TPR at fixed FPR;
- Wilson/binomial confidence intervals for survival and hit rates;
- detection power as a function of number of triggers;
- false positive calibration as a function of per-query false match rate;
- adaptive attacker cost curves: TPR versus normal utility retained.

## Local Summary From Existing COCO-5k Artifacts

Before new remote experiments are available, run:

```bash
python3 src/usenix_security_summary.py \
  --filtering-csv data/h1_clip_coco5k_filtering.csv \
  --proxy-csv data/h1_raig_proxy_coco5k_aggregate.csv \
  --out-prefix data/usenix_coco5k
```

This produces local tables for the current evidence: attack cost curves,
Wilson confidence intervals, trigger-count sensitivity, and a USENIX gap table.

## Stop/Pivot Rule

If exact RAIG proxy or real generation sharply underperforms the aggregate
proxy, do not add another defense component. First diagnose whether failures are
caused by trigger retrieval, generator evidence loss, or auditing metric
weakness. Only after the failure mode is localized should the method be changed.
