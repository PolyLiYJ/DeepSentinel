# H1 Analysis

## Pilot Result

The synthetic filtering pilot supports the core mechanism behind DeepSentinel.
The visible-key baseline has zero survival immediately because the attacker can
remove text-bearing samples. Hidden outlier sentinels survive only under the
weakest density filter and are eliminated once the attacker drops roughly 10% of
the lowest-density samples. DeepSentinel latent sentinels, selected from dense
normal regions and shifted only mildly toward the trigger, keep 100% survival
through the strongest tested density filter.

Raw results are saved in `data/h1_synthetic_filtering.csv`.

The multi-seed sweep is saved in:

- `data/h1_synthetic_sweep_raw.csv`
- `data/h1_synthetic_sweep_summary.csv`

## Key Numbers

| Density drop | Normal collateral | Visible-key survival | Hidden outlier survival | DeepSentinel survival |
|---:|---:|---:|---:|---:|
| 0.05 | 0.004 | 0.000 | 0.042 | 1.000 |
| 0.10 | 0.045 | 0.000 | 0.000 | 1.000 |
| 0.25 | 0.201 | 0.000 | 0.000 | 1.000 |
| 0.50 | 0.480 | 0.000 | 0.000 | 1.000 |

## Interpretation

This is not yet evidence that the method works in real CLIP/RAIG systems. It is
a sanity check for the paper's central causal claim: if a sentinel is both
retrieval-triggered and locally in-distribution, a generic suspiciousness filter
cannot isolate it without also removing many normal samples. The next experiment
must reproduce this tradeoff with real image-text embeddings and adaptive
filters.

The 10-seed sweep confirms that the single-seed pattern is stable in this
synthetic environment. At density drop 0.10, visible-key and hidden-outlier
survival are both 0.0, while DeepSentinel survival is 1.0 for every seed. This
is the strongest current evidence for the filtering tradeoff, but it remains a
simulation result.

## COCO-1k CLIP Pilot

The first real CLIP pilot used a deterministic 1k-image subset from
`/home/yjli/Agent/agent-attack/COCO2017/val2017` on the SSH server
`yjli@10.21.4.20`. Environment: `agent-attack` conda env, PyTorch 2.6.0+cu124,
Transformers 4.51.3, CLIP ViT-B/32, GPU `cuda:0` on an RTX 3090.

Artifacts:

- `data/h1_clip_coco1k_filtering.csv`
- `data/h1_clip_coco1k_sentinel_manifest.csv`
- `to_human/h1_clip_coco1k_tradeoff.svg`
- `to_human/h1_clip_coco1k_contact_sheet.jpg`

| Density drop | Collateral | Hidden outlier survival | DeepSentinel survival | Hit@20 |
|---:|---:|---:|---:|---:|
| 0.05 | 0.050 | 0.875 | 1.000 | 1.000 |
| 0.10 | 0.100 | 0.500 | 1.000 | 1.000 |
| 0.20 | 0.200 | 0.250 | 1.000 | 1.000 |
| 0.30 | 0.300 | 0.000 | 1.000 | 1.000 |
| 0.50 | 0.500 | 0.000 | 1.000 | 1.000 |

Interpretation: the selection-only latent sentinel mechanism survives local
density pruning in real CLIP embeddings on COCO-1k, while the hidden-outlier
baseline is steadily removed. This supports the core DeepSentinel claim in a
real embedding space. The contact sheet indicates that selected DeepSentinel
candidates are visually ordinary, but trigger-image semantic alignment is
sometimes broad rather than exact.

## Next Experimental Step

Build a CLIP retrieval benchmark on MS-COCO and Product-10K subsets:

1. Compute image embeddings for normal images.
2. Select high-density candidate images.
3. Create latent sentinels by either constrained pixel-space optimization toward
   a secret text embedding or by selecting naturally aligned in-distribution
   examples.
4. Evaluate against visible-key ImageSentinel-style sentinels under OCR removal,
   CLIP outlier removal, and local-density pruning.

## Robustness Check

A multi-seed synthetic sweep should be used for all pilot claims. The sweep
script writes both raw per-seed rows and a density-drop summary:

```bash
python3 src/run_synthetic_sweep.py --seeds 10
```

The paper should report the sweep summary rather than relying on a single seed.
