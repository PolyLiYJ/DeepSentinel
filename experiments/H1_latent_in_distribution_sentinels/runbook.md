# H1 Runbook

## Objective

Test whether distribution-preserving latent sentinels remain detectable under
adaptive filtering while visible-key or outlier sentinels are removed.

## Completed: Synthetic Pilot

Command:

```bash
python3 src/simulate_filtering.py --seed 7 --out data/h1_synthetic_filtering.csv
```

Result summary:

- Visible-key survival is 0.0 after text filtering.
- Hidden-outlier survival reaches 0.0 once density drop is 0.10.
- DeepSentinel survival remains 1.0 through density drop 0.50.

## Next: CLIP Pilot on Real Images

Expected command:

```bash
python3 src/prepare_image_subset.py \
  --image-dir /path/to/images \
  --out-dir data/real_image_subset_1k \
  --limit 1000 \
  --seed 13

python3 src/clip_filtering_experiment.py \
  --image-dir data/real_image_subset_1k \
  --limit 1000 \
  --out data/h1_clip_filtering.csv \
  --manifest-out data/h1_clip_sentinel_manifest.csv
```

Recommended first datasets:

- MS-COCO 2017 validation subset.
- Product-10K subset.

The subset-preparation step creates symlinks by default and writes
`subset_manifest.csv`, so the exact image list is recoverable. Use `--copy` if
the target environment does not preserve symlinks.

## What To Inspect

The CLIP CSV contains:

- `normal_collateral`: fraction of normal images removed.
- `deep_sentinel_survival`: survival of dense latent sentinels.
- `hidden_outlier_survival`: survival of trigger-aligned low-density sentinels.
- `trigger_hit_rate_at_k`: fraction of triggers whose paired latent sentinel is
  retrieved in the top-k surviving images.

The manifest contains selected image paths for manual inspection. DeepSentinel
candidates should look ordinary for the dataset; if they look like obvious
semantic outliers, the selection-only method is not sufficient.

Create a contact sheet for the manual inspection:

```bash
python3 src/make_manifest_contact_sheet.py \
  --manifest data/h1_clip_sentinel_manifest.csv \
  --out to_human/h1_clip_manifest_contact_sheet.jpg
```

Before running on a real dataset, verify the visualization helper:

```bash
python3 src/smoke_manifest_contact_sheet.py
```

## Decision Rule

Proceed to RAIG evaluation if the CLIP pilot shows:

- DeepSentinel survival stays above hidden-outlier survival at matched
  collateral damage.
- Trigger hit rate remains above 0.25 after mild filtering.
- The selected latent sentinels are visually ordinary under manual inspection.

If the trigger hit rate is too low, pivot within the same scheme from
selection-only sentinels to constrained pixel-space optimization.
