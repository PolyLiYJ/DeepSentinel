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

## 2026-06-13 Remote COCO-1k CLIP Pilot

- Used SSH server `yjli@10.21.4.20` (`Hulk`) with 8x RTX 3090.
- Used existing COCO val2017 directory:
  `/home/yjli/Agent/agent-attack/COCO2017/val2017`.
- Used conda env `/home/yjli/anaconda3/envs/agent-attack`, PyTorch 2.6.0+cu124,
  Transformers 4.51.3, and CLIP ViT-B/32.
- Prepared a deterministic 1k-image COCO subset and ran
  `src/clip_filtering_experiment.py`.
- Result: DeepSentinel survival is 1.0 through 50% local-density pruning,
  hidden-outlier survival reaches 0.0 at 30% pruning, and trigger hit@20 remains
  1.0 at every tested pruning level.
- Pulled the filtering CSV, sentinel manifest, tradeoff SVG, and contact sheet
  back into the local project.

## 2026-06-13 Remote COCO-5k CLIP Scale-Up

- Added a confirmatory COCO-5k addendum to the H1-CLIP protocol and committed it
  before running the scale-up.
- Product-10K was not found in common remote data paths, so the next scale test
  used all available COCO val2017 images.
- Ran the same selection-only DeepSentinel protocol on 5k COCO validation images
  with CLIP ViT-B/32 on `Hulk`.
- Result: DeepSentinel survival remains 1.0 through 50% local-density pruning.
  Hidden-outlier survival is 1.0 through 10% pruning, falls to 0.625 at 20%,
  and reaches 0.0 at 35%. Trigger hit@20 is 0.875 before filtering and reaches
  1.0 from 25% pruning onward.
- Pulled the filtering CSV, sentinel manifest, tradeoff SVG, and contact sheet
  back into the local project for paper/report use.

## 2026-06-13 Heartbeat: RAIG Proxy Evidence Test

- Added `experiments/H1_latent_in_distribution_sentinels/raig_proxy_protocol.md`
  and committed it before implementation.
- Added `src/raig_proxy_evidence.py`, which reuses the CLIP embedding cache and
  estimates ownership TPR/FPR when retrieved sentinel evidence survives the
  generation layer with probability `g`.
- Smoke-tested the script locally with synthetic normalized embeddings; it wrote
  the expected proxy CSV and probability summary.
- Attempted to run the COCO-5k proxy on `yjli@10.21.4.20`, but SSH to
  `10.21.4.20:22` timed out and ping showed 100% packet loss. The next heartbeat
  should retry the same run once the server is reachable.

## 2026-06-13 Heartbeat: RAIG Proxy Plotting

- Rechecked project state and confirmed the next blocked action is the COCO-5k
  RAIG proxy run on the SSH server.
- Retried network reachability; ping again showed 100% packet loss and SSH port
  probing did not complete.
- Added `src/plot_raig_proxy_svg.py`, a dependency-free SVG plotter for RAIG
  proxy ownership TPR curves across generation evidence retention levels.
- Smoke-tested the plotter with a temporary proxy CSV so the server-side result
  can be visualized immediately once the remote cache run succeeds.

## 2026-06-13 Heartbeat: Related Work Expansion

- Re-read the project state and findings; the server-side RAIG proxy remains
  blocked because `10.21.4.20` is unreachable from the current network.
- Expanded `literature/survey.md` with verified notes on black-box dataset
  ownership verification, Data Taggants, contrastive pretraining DOV, ZeroMark,
  and CanaryTrace.
- Updated `literature/method_and_attacks.md` to position DeepSentinel as a
  visual RAIG pre-index filtering problem rather than general model
  watermarking.
- Added BibTeX entries to both paper bibliography files and expanded the AAAI
  related-work section.
- Recompiled the AAAI draft successfully. The new citations resolve into the
  bibliography, but the older AAAI citation rendering issue with empty brackets
  remains a formatting task.

## 2026-06-13 Heartbeat: AAAI Citation Fix

- Re-read the project state and findings; with the SSH experiment still blocked,
  addressed the remaining paper-formatting blocker.
- Diagnosed the empty citation callouts as a missing `natbib` package. The
  AAAI 2026 template expects `natbib` and then internally maps `\cite` to
  author-year `\citep`.
- Added `\usepackage{natbib}` to both AAAI draft entry points and removed the
  explicit `\bibliographystyle{aaai2026}` lines because `aaai2026.sty` sets the
  bibliography style automatically when `natbib` is loaded.
- Clean-recompiled the AAAI draft; log checks show no `[[`, no undefined
  citations, and no duplicate `bibstyle` error.

## 2026-06-14 Heartbeat: Aggregate RAIG Proxy

- Re-read project state and findings. The exact COCO-5k RAIG proxy remains
  blocked because `10.21.4.20` is still unreachable from the current network.
- Added `src/raig_proxy_from_filtering_csv.py`, an aggregate fallback that uses
  the saved filtering CSV to estimate ownership TPR under generation evidence
  retention. It labels outputs as `aggregate_from_filtering_csv`.
- Updated `src/plot_raig_proxy_svg.py` to ignore non-numeric metadata columns.
- Generated `data/h1_raig_proxy_coco5k_aggregate.csv` and
  `to_human/h1_raig_proxy_coco5k_aggregate.svg`.
- Main aggregate result: with threshold 2/8, false match rate 0.001, and
  generation retention `g=0.5`, DeepSentinel proxy TPR is 0.9375-0.9648 across
  pruning levels, while an optimistic hidden-outlier estimate reaches 0.0 from
  35% pruning onward.

## 2026-06-24 Heartbeat: Paper Result Tables

- Re-read project state and findings, then retried `10.21.4.20`; ping and SSH
  port checks still failed, so the exact cache-based RAIG proxy remains blocked.
- Updated the AAAI draft abstract to reflect the aggregate RAIG proxy finding.
- Added a COCO-5k CLIP filtering table and an aggregate RAIG proxy table at
  generation retention `g=0.5`.
- Recompiled the AAAI draft successfully. The log has no undefined citations and
  only a small 2.3pt overfull warning from the existing synthetic table.

## 2026-06-24 Heartbeat: Human Progress Snapshot

- Re-read project state, findings, and the autoresearch skill.
- Confirmed the repo was clean after pushing the paper-table commit.
- Started another lightweight SSH port probe for `10.21.4.20`; it did not return
  promptly, consistent with the recent unreachable state.
- Added `to_human/progress_2026-06-24.md`, a short review snapshot that keeps
  the paper centered on one selection-only latent sentinel scheme and identifies
  the exact COCO-5k RAIG proxy as the next experiment once the server returns.

## 2026-06-24 Heartbeat: Selection-Only Wording Pass

- Re-read the project state, findings, and autoresearch guidance.
- Tightened the AAAI draft and analysis wording so the current method is
  consistently described as selection-only latent sentinel selection, not as a
  combined select-or-optimize defense.
- Updated the conclusion to state that the current evidence already supports
  the selection-only version on synthetic and COCO CLIP filtering tests.

## 2026-07-03 Resume: Exact Proxy Runbook

- Resumed after the user explicitly asked to continue the research.
- Re-read `research-state.yaml`, `findings.md`, and the autoresearch skill.
- Confirmed the repository still has one local commit ahead of GitHub because
  `github.com:443` is unreachable from the current network.
- Checked `10.21.4.20:22`; the SSH port probe timed out, so the exact COCO-5k
  RAIG proxy cannot be launched yet.
- Aligned the H1 prediction in `research-state.yaml` with the current
  selection-only method and added an exact COCO-5k RAIG proxy runbook to
  `experiments/H1_latent_in_distribution_sentinels/raig_proxy_protocol.md`.
