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
