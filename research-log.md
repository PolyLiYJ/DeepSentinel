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
