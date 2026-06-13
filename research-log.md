# DeepSentinel Research Log

## 2026-06-13 Bootstrap

- Created the DeepSentinel workspace.
- Framed the central gap: visible random key images in ImageSentinel-style
  dataset protection can be filtered before a stolen dataset is indexed.
- Chose a single paper direction: replace visible keys with distribution-
  preserving latent retrieval triggers in vision-language embedding space.
- Created H1 as the first locked hypothesis and prepared a synthetic pilot.
- Ran the H1 synthetic pilot. Result: visible-key sentinels are filtered
  immediately, hidden outliers are removed by density pruning, and latent
  in-distribution sentinels survive the tested filters.
- Created an AAAI 2026 LaTeX draft and compiled it successfully.

## 2026-06-13 Heartbeat: CLIP Experiment Scaffold

- Added a real-embedding H1-CLIP protocol.
- Added `src/clip_filtering_experiment.py`, a CLIP-based image-directory
  experiment that selects high-density latent sentinels and evaluates survival
  under local-density filtering.
- Confirmed local Python environment has PyTorch and transformers available.

## 2026-06-13 Heartbeat: Reproducibility Notes

- Added a top-level README explaining the single DeepSentinel mechanism,
  current pilot result, and experiment commands.
- Added an H1 runbook with decision criteria for moving from CLIP retrieval to
  full RAIG evaluation.

## 2026-06-13 Heartbeat: Pilot Visualization

- Added `src/plot_filtering_svg.py`, a dependency-free SVG plotter for
  filtering tradeoff CSVs.
- Generated a synthetic pilot tradeoff figure for reports and paper planning.

## 2026-06-13 Heartbeat: Verified Related Work

- Verified arXiv metadata for CLIP, Glaze, Mist, BadNets, and Radioactive Data.
- Added conservative BibTeX entries without guessed DOI or venue fields.
- Replaced `[CITATION NEEDED]` related-work placeholder text in the AAAI draft
  with verified citations.

## 2026-06-13 Heartbeat: CLIP Manifest Output

- Updated the CLIP filtering experiment to write a sentinel manifest with
  selected image paths, trigger prompts, densities, and trigger similarities.
- Updated the CLIP protocol, runbook, and README so the real-image pilot includes
  a manual visual normality sanity check.

## 2026-06-13 Heartbeat: Manifest Contact Sheet

- Added `src/make_manifest_contact_sheet.py` to render selected CLIP
  DeepSentinel and hidden-outlier candidates side by side.
- Updated README and H1 runbook with the visual inspection command.

## 2026-06-13 Heartbeat: Manifest Visualization Smoke Test

- No local COCO/Product-10K directory was found under `~/Documents`.
- Added `src/smoke_manifest_contact_sheet.py`, which generates temporary images
  and a manifest to verify the contact-sheet tool without requiring a dataset.

## 2026-06-13 Heartbeat: Deterministic Image Subsets

- Added `src/prepare_image_subset.py` to create deterministic symlink or copy
  subsets from local image directories.
- Updated README and H1 runbook so CLIP pilots use a fixed sampled subset before
  running retrieval/filtering evaluation.

## 2026-06-13 Heartbeat: CLIP Embedding Cache

- Added `--cache` support to `src/clip_filtering_experiment.py`.
- The cache stores image embeddings, trigger embeddings, paths, triggers, and
  model metadata, and is reused only when those metadata match.
- Updated README and H1 runbook to use the cache in the real-image pilot.

## 2026-06-13 Heartbeat: Synthetic Multi-Seed Sweep

- Added `src/run_synthetic_sweep.py` to run the synthetic filtering pilot across
  multiple random seeds and summarize each density-drop level.
- Updated README and H1 analysis to make the multi-seed sweep the preferred
  synthetic evidence.
- Ran the 10-seed sweep. At density drop 0.10, normal collateral damage averages
  0.043, visible-key survival is 0.0, hidden-outlier survival is 0.0, and
  DeepSentinel survival is 1.0 across all seeds.

## 2026-06-13 Heartbeat: Multi-Seed Sweep Figure

- Updated `src/plot_filtering_svg.py` to support both single-run CSVs and
  multi-seed summary CSVs.
- Generated `to_human/h1_synthetic_sweep_tradeoff.svg` for the 10-seed sweep.

## 2026-06-13 Heartbeat: Sweep Uncertainty Bands

- Updated `src/plot_filtering_svg.py` to draw min/max bands when plotting
  multi-seed summary CSVs.
- Regenerated the 10-seed sweep figure with bands for paper/report use.

## 2026-06-13 Heartbeat: Method and Attack Note

- Added `literature/method_and_attacks.md` to capture the current selection-only
  DeepSentinel method and the main adaptive attacks.
- Explicitly recorded that the paper should focus on one mechanism:
  in-distribution latent retrieval sentinels.

## 2026-06-13 Heartbeat: Paper Table Uses Sweep

- Updated the AAAI draft pilot table to report 10-seed sweep means instead of
  the original single-seed numbers.
- Clarified in the caption that DeepSentinel survival is 1.0 for every seed at
  all shown filter strengths.
