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

## COCO-5k CLIP Scale-Up

The confirmatory scale-up used all 5k available COCO 2017 validation images on
the same server, environment, encoder, trigger set, and filtering protocol as
the 1k pilot. This tests whether the 1k result was a small-sample artifact.

Artifacts:

- `data/h1_clip_coco5k_filtering.csv`
- `data/h1_clip_coco5k_sentinel_manifest.csv`
- `to_human/h1_clip_coco5k_tradeoff.svg`
- `to_human/h1_clip_coco5k_contact_sheet.jpg`

| Density drop | Collateral | Hidden outlier survival | DeepSentinel survival | Hit@20 |
|---:|---:|---:|---:|---:|
| 0.05 | 0.050 | 1.000 | 1.000 | 0.875 |
| 0.10 | 0.100 | 1.000 | 1.000 | 0.875 |
| 0.20 | 0.200 | 0.625 | 1.000 | 0.875 |
| 0.30 | 0.300 | 0.375 | 1.000 | 1.000 |
| 0.35 | 0.350 | 0.000 | 1.000 | 1.000 |
| 0.50 | 0.500 | 0.000 | 1.000 | 1.000 |

Interpretation: DeepSentinel survival remains 1.0 through 50% density pruning at
5k scale. The hidden-outlier baseline is more resilient than in COCO-1k under
mild pruning, but still collapses by 35% pruning while DeepSentinel remains
untouched. The initial hit@20 of 0.875 indicates one trigger is not retrieved
within the top 20 before filtering; after moderate pruning, hit@20 reaches 1.0.
Manual inspection again shows ordinary COCO images. The key limitation remains
semantic tightness: selection-only sentinels are plausible and filter-resistant,
but some trigger matches are broad.

## COCO-5k Aggregate RAIG Proxy

While the SSH server holding the full COCO-5k embedding cache was unreachable,
we ran an aggregate proxy from the saved filtering CSV. This estimate uses the
reported DeepSentinel trigger hit@20 and treats hidden-outlier survival as if
every surviving outlier were retrieved by its trigger, making the hidden-outlier
baseline optimistic. It is not a replacement for the exact cache-based proxy in
`src/raig_proxy_evidence.py`.

Artifacts:

- `data/h1_raig_proxy_coco5k_aggregate.csv`
- `to_human/h1_raig_proxy_coco5k_aggregate.svg`

With eight private triggers, detection threshold two, false visual match rate
0.001 per query, and generation evidence retention `g=0.5`, the proxy false
positive rate is 2.79e-05. DeepSentinel proxy TPR stays between 0.9375 and
0.9648 across all pruning levels. The optimistic hidden-outlier proxy TPR is
0.9648 before pruning, 0.8125 at 20% pruning, 0.5 at 30% pruning, and 0.0 from
35% pruning onward.

Interpretation: even after a generation-side evidence dilution model, the COCO
retrieval results imply high DeepSentinel ownership-test power at moderate
generation retention. This strengthens the case for running the exact
cache-based RAIG proxy, then a minimal image-conditioned generation experiment,
once the server is reachable.

## Next Experimental Step

Move from retrieval-only CLIP evaluation to a minimal RAIG-layer check:

1. Use the COCO-5k selected DeepSentinel images as retrieval memories.
2. Retrieve top-k images for the private trigger prompts after filtering.
3. Pass retrieved images into a simple image-conditioned generation or proxy
   evidence layer.
4. Measure whether ownership evidence survives after retrieval-to-generation
   transformation without changing the defense mechanism.

## Robustness Check

A multi-seed synthetic sweep should be used for all pilot claims. The sweep
script writes both raw per-seed rows and a density-drop summary:

```bash
python3 src/run_synthetic_sweep.py --seeds 10
```

The paper should report the sweep summary rather than relying on a single seed.
