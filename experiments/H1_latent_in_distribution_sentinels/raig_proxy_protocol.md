# H1-RAIG-Proxy Protocol: Retrieval Evidence After Generation Dilution

## Goal

Test whether the COCO CLIP retrieval evidence remains useful after a minimal
retrieval-to-generation layer. This is not a new defense and does not add a
second mechanism. It keeps the selected DeepSentinel images fixed and asks how
much generation-side evidence retention is needed for black-box ownership
detection.

## Model

For each secret trigger prompt, the RAIG system retrieves top-k images from the
filtered index. If the corresponding DeepSentinel image is retrieved, the
generation layer preserves auditable visual evidence with probability `g`.
The owner queries all private triggers and declares ownership if at least `m`
generated outputs contain matching sentinel evidence.

This is a proxy for image-conditioned generation before running a heavy
SDXL/IP-Adapter or OmniGen experiment. It separates two questions:

1. Does filtering remove the selected latent sentinels from retrieval?
2. If retrieval succeeds, how much generator evidence retention is sufficient
   for detection?

## Confirmatory Inputs

- COCO-5k CLIP embedding cache from the locked H1-CLIP protocol.
- The same trigger prompts, density scores, and selected sentinels.
- The same local-density pruning levels from 0% to 50%.

## Baselines

- DeepSentinel selection-only latent sentinels.
- Hidden-outlier sentinels selected for trigger similarity from low-density
  regions.

Visible-key sentinels are treated as removed by the text/OCR filter before this
stage, so their expected generation-side TPR is zero under the filtering threat.

## Metrics

- Retrieval hit count over private triggers.
- Proxy ownership TPR under generation evidence retention probabilities
  `g in {1.0, 0.75, 0.5, 0.25}`.
- Proxy FPR using a small per-query false visual match rate.
- Normal collateral damage from the density filter.

## Success Criterion

The proxy supports H1 if DeepSentinel keeps high ownership TPR at moderate
generation retention while hidden-outlier TPR collapses as local-density pruning
increases. This would justify spending compute on a full image-conditioned RAIG
experiment.
