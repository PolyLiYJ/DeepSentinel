# DeepSentinel

DeepSentinel is an autoresearch project on ownership verification for
retrieval-augmented image generation (RAIG). The project studies a specific
failure mode of ImageSentinel-style defenses: visible random-key sentinel images
can be removed by an attacker before the stolen dataset is indexed.

## Paper Direction

**DeepSentinel: Filter-Resistant Latent Sentinels for Ownership Verification in
Retrieval-Augmented Image Generation**

The central idea is to replace visible key-bearing sentinels with
distribution-preserving latent sentinels. A latent sentinel should look like a
normal high-value dataset image, live in a dense region of the image embedding
space, and still be retrievable by a secret trigger prompt.

The defense intentionally focuses on one mechanism:

> Hide ownership evidence in retrieval geometry, not in visible text.

## Current Status

- Synthetic pilot completed.
- CLIP image-directory experiment scaffold implemented.
- AAAI draft scaffold created under `paper/`.
- GitHub repository synchronized.

## Key Pilot Result

In the synthetic clustered retrieval benchmark:

- Visible-key sentinels are removed immediately by a text-key filter.
- Hidden outlier sentinels are removed by mild density pruning.
- DeepSentinel latent sentinels survive across the tested density-filter range.
- The strongest tested filter removes 48% of normal data while keeping all
  latent sentinels in this synthetic setup.

Raw result: `data/h1_synthetic_filtering.csv`.
Plot: `to_human/h1_synthetic_tradeoff.svg`.

## Running Experiments

Synthetic pilot:

```bash
python3 src/simulate_filtering.py --seed 7 --out data/h1_synthetic_filtering.csv
python3 src/plot_filtering_svg.py --csv data/h1_synthetic_filtering.csv --out to_human/h1_synthetic_tradeoff.svg
```

CLIP real-image pilot:

```bash
python3 src/clip_filtering_experiment.py \
  --image-dir /path/to/coco/val2017 \
  --limit 1000 \
  --out data/h1_clip_filtering.csv \
  --manifest-out data/h1_clip_sentinel_manifest.csv
```

The CLIP experiment accepts any local image directory. The intended first
datasets are MS-COCO 2017 validation images and a Product-10K subset.
It also writes a manifest with the selected sentinel image paths for manual
visual inspection.

After the CLIP run, build a visual contact sheet:

```bash
python3 src/make_manifest_contact_sheet.py \
  --manifest data/h1_clip_sentinel_manifest.csv \
  --out to_human/h1_clip_manifest_contact_sheet.jpg
```

Smoke-test the manifest visualization toolchain:

```bash
python3 src/smoke_manifest_contact_sheet.py
```

## Repository Structure

- `research-state.yaml`: current project state and next steps.
- `findings.md`: evolving research narrative.
- `literature/`: survey notes and ranked ideas.
- `experiments/H1_latent_in_distribution_sentinels/`: protocol and analysis for
  the selected hypothesis.
- `src/`: reusable experiment code.
- `data/`: small result files.
- `paper/`: AAAI draft and template files.
- `to_human/`: progress reports.

## Next Research Step

Run the CLIP pilot on a real image directory and check whether the selection-only
latent sentinel mechanism preserves the synthetic tradeoff:

1. High DeepSentinel survival under density filtering.
2. Lower hidden-outlier survival at the same collateral damage.
3. Non-trivial trigger retrieval hit rate after filtering.
