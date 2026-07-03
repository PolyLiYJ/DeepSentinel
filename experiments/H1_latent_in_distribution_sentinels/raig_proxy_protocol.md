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

## Exact COCO-5k Runbook

When `yjli@10.21.4.20` is reachable again, run the exact proxy on the server
that holds the COCO-5k embedding cache. This is the next confirmatory step and
does not modify the defense.

```bash
cd /home/yjli/DeepSentinel
git pull --ff-only
PY=/home/yjli/anaconda3/envs/agent-attack/bin/python
$PY src/raig_proxy_evidence.py \
  --cache data/h1_clip_coco5k_embeddings.pt \
  --out data/h1_raig_proxy_coco5k.csv \
  --threshold 2 \
  --false-match-rate 0.001
$PY src/plot_raig_proxy_svg.py \
  --csv data/h1_raig_proxy_coco5k.csv \
  --out to_human/h1_raig_proxy_coco5k.svg \
  --title "COCO-5k RAIG Proxy Ownership Detection"
```

Then copy back only the small artifacts:

```bash
rsync -av yjli@10.21.4.20:/home/yjli/DeepSentinel/data/h1_raig_proxy_coco5k.csv data/
rsync -av yjli@10.21.4.20:/home/yjli/DeepSentinel/to_human/h1_raig_proxy_coco5k.svg to_human/
```

Expected sanity checks:

- `num_triggers` should remain 8.
- At density drop 0.0, DeepSentinel should have at least 7/8 retrieval hits, as
  in the saved COCO-5k filtering result.
- At generation retention `g=0.5`, DeepSentinel proxy TPR should remain close
  to the aggregate estimate, roughly 0.94-0.96, unless exact top-k retrieval
  differs materially from the saved aggregate hit-rate table.
- Hidden-outlier proxy TPR should decline sharply under stronger density
  pruning; if it does not, inspect whether the exact hidden-outlier selection
  differs from the COCO-5k filtering manifest.

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

## Decision After the Exact Proxy

If the exact proxy agrees with the aggregate proxy, freeze the retrieval-side
claim and run only one minimal image-conditioned generation check. Do not add a
new defense mechanism. If the exact proxy is weaker than expected, first debug
trigger-level retrieval failures using the COCO-5k sentinel manifest before
changing the method.
