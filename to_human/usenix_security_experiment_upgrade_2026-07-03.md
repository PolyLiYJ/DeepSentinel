# DeepSentinel USENIX Security Experiment Upgrade - 2026-07-03

## What Was Added Locally

The project now has a USENIX Security extension protocol that keeps the defense
as one scheme: selection-only latent sentinels. The new work strengthens the
evaluation, not the defense.

New artifacts:

- `experiments/H1_latent_in_distribution_sentinels/usenix_security_extension_protocol.md`
- `src/usenix_security_summary.py`
- `data/usenix_coco5k_attack_cost.csv`
- `data/usenix_coco5k_trigger_power.csv`
- `data/usenix_coco5k_false_match_calibration.csv`
- `data/usenix_coco5k_experiment_gaps.csv`

## Current Strongest Security-Style Result

On COCO-5k, at density drop 0.35:

- attacker removes 35% of normal images;
- hidden-outlier sentinel survival drops to 0/8;
- DeepSentinel survival remains 8/8;
- DeepSentinel hit@20 is 8/8;
- with generation evidence retention `g=0.5`, threshold two, and false match
  rate 0.001, aggregate DeepSentinel proxy TPR is 0.9648 at FPR 2.79e-05.

This is a good security-paper framing point: the adaptive filter can remove the
obvious/outlier evidence, but only after it begins paying high normal-data cost,
and the in-distribution latent sentinels remain detectable.

## What Still Must Be Run for USENIX Security

1. Exact COCO-5k RAIG proxy on the remote embedding cache.
2. One real image-conditioned RAIG generation experiment.
3. Stronger adaptive filters: OCR/text, CLIP outlier, density, dedup, and
   caption-image mismatch where metadata exists.
4. Real utility damage: normal-query Recall@K, top-k similarity, retrieval
   diversity, and generation CLIPScore.
5. One non-natural-image dataset, preferably Product-10K or an art/product
   substitute.

## Current Caveat

The current utility metric is still a proxy: fraction of normal images removed.
For USENIX Security, this needs to become actual retrieval/generation utility
loss. The current trigger set also has only eight sentinels, which makes Wilson
confidence intervals wide; the full evaluation should increase trigger count.
