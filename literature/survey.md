# Literature Survey

## Anchor Paper

### ImageSentinel: Protecting Visual Datasets from Unauthorized Retrieval-Augmented Image Generation

- Venue/status: reported as NeurIPS 2025 accepted; arXiv: https://arxiv.org/abs/2510.12119
- Problem: protect image datasets from unauthorized use inside retrieval-
  augmented image generation systems.
- Method: insert sentinel images into the dataset. These images are generated to
  match dataset style while carrying random character sequences that act as
  secret retrieval keys.
- Relevance: establishes the dataset-ownership problem for RAIG and gives the
  baseline this project improves.
- Gap for DeepSentinel: random key-bearing sentinels are detectable by dataset
  preprocessing, OCR, caption/token anomaly filters, and embedding outlier
  filters before indexing.

## Related Areas To Expand

### Dataset Ownership Verification and Canary Examples

- Core theme: plant secret or rare examples in a dataset and later query a model
  or retrieval system for evidence of memorization or indexing.
- Relevance: motivates black-box ownership testing and statistical detection.
- DeepSentinel angle: canaries should be in-distribution and filter-resistant,
  not lexically obvious.

### Watermarking and Adversarial Protection for Image Generators

- Representative lines include Glaze-style style mimicry protection,
  diffusion-oriented adversarial perturbations such as Mist, and model/dataset
  watermarking methods.
- Relevance: these works show that small perturbations can influence downstream
  generative or embedding behavior.
- DeepSentinel angle: the target is not visible post-generation watermark
  recovery, but retrieval evidence in a stolen RAIG index.

### Backdoor and Clean-Label Trigger Literature

- Core theme: create samples that look benign but activate behavior under a
  trigger.
- Relevance: gives conceptual tools for invisible or clean-label sentinels.
- DeepSentinel angle: avoid training-time model poisoning; instead use
  retrieval-space geometry for ownership verification.

## Working Gap Statement

Existing visible-key sentinel defenses are strong when the attacker indexes the
protected dataset unchanged, but weak when the attacker preprocesses the dataset
to remove key-bearing or anomalous images. A publishable contribution should
therefore formalize adaptive filtering, quantify collateral-damage tradeoffs,
and introduce a single simple sentinel construction that remains in-distribution.
