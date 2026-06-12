# H1-CLIP Protocol: Real-Embedding Filtering Tradeoff

## Goal

Move from the synthetic pilot to a real vision-language embedding setting. The
experiment asks whether DeepSentinel's core claim still holds when the normal
dataset is represented by CLIP image embeddings rather than synthetic clusters.

## Claim Tested

DeepSentinel latent sentinels can be chosen from high-density regions of a real
image dataset while remaining retrievable by secret trigger prompts. Therefore,
embedding outlier and local-density filters should remove them only when the
attacker accepts substantial collateral damage to normal data.

## Dataset

Primary pilot:

- MS-COCO 2017 validation subset, 1k-5k images.

Secondary domain check:

- Product-10K subset, 1k-5k images.

The first implementation accepts any local image directory so the protocol can
run before full dataset download/curation.

## Method Under Test

Use the selection-only DeepSentinel variant:

1. Encode all normal images with CLIP.
2. Estimate each image's local density by average top-k image-image similarity.
3. Keep a dense candidate pool.
4. For each secret trigger prompt, choose a high-density image with strong
   trigger similarity as a latent sentinel.

This deliberately avoids combining multiple defenses. It tests one simple
mechanism: in-distribution latent retrieval sentinels.

## Baselines

- Visible-key sentinel baseline: modeled as samples removed by a text/OCR filter.
  In the full version, these will be rendered key images or ImageSentinel-style
  generated sentinel images.
- Hidden-outlier sentinel baseline: trigger-aligned samples selected without a
  density constraint, expected to be vulnerable to density filtering.

## Attacks

- Text/OCR filter: removes visible-key baseline samples.
- Local-density pruning: removes the lowest-density samples.
- Trigger-aware but key-blind pruning: removes samples with high text-trigger
  similarity only if the attacker somehow guesses the trigger family; this is an
  optional stress test, not the default threat model.

## Metrics

- Normal collateral damage.
- DeepSentinel survival.
- Hidden-outlier survival.
- Trigger retrieval hit rate among top-k retrieved surviving samples.
- Area under survival-vs-collateral curve.

## Success Criterion

The experiment supports H1 if DeepSentinel keeps substantially higher survival
than hidden outliers at the same collateral damage and maintains non-trivial
trigger hit rate after filtering.
