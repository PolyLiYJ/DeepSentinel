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

Verified references:

- Black-box Dataset Ownership Verification via Backdoor Watermarking
  (Li et al., IEEE TIFS 2023; arXiv:2209.06015). This formulates released
  dataset protection as black-box verification of whether a third-party model
  used the dataset, and uses backdoor watermarking plus hypothesis testing.
  DeepSentinel differs by targeting retrieval-augmented image generation
  indexes rather than supervised model training.
- Data Taggants: Dataset Ownership Verification via Harmless Targeted Data
  Poisoning (Bouaziz, Usunier, and El-Mhamdi, ICLR 2025; arXiv:2410.09101).
  Data Taggants use clean-label targeted poisoning and statistical certificates
  for black-box model detection without hurting validation accuracy. The key
  contrast is that Data Taggants rely on training-time model behavior, while
  DeepSentinel uses retrieval-time geometry in a stolen image index.
- Dataset Ownership Verification in Contrastive Pre-trained Models (Xie et al.,
  ICLR 2025; arXiv:2502.07276). This work verifies whether a self-supervised
  black-box backbone was pre-trained on a target unlabeled dataset by testing
  embedding-space relationships. DeepSentinel shares the embedding-space view,
  but its evidence is inserted as latent sentinels and evaluated under adaptive
  dataset filtering before retrieval indexing.
- ZeroMark: Towards Dataset Ownership Verification without Disclosing Watermark
  (Guo et al., NeurIPS 2024). ZeroMark avoids exposing dataset-specific
  watermarks during verification by using boundary gradients under label-only
  black-box access. DeepSentinel has a parallel motivation--do not reveal the
  secret evidence--but addresses pre-index filtering of visible RAIG sentinels.

### Watermarking and Adversarial Protection for Image Generators

- Representative lines include Glaze-style style mimicry protection,
  diffusion-oriented adversarial perturbations such as Mist, and model/dataset
  watermarking methods.
- Relevance: these works show that small perturbations can influence downstream
  generative or embedding behavior.
- DeepSentinel angle: the target is not visible post-generation watermark
  recovery, but retrieval evidence in a stolen RAIG index.

Verified references:

- Glaze: Protecting Artists from Style Mimicry by Text-to-Image Models
  (Shan et al., 2023), arXiv:2302.04222.
- Mist: Towards Improved Adversarial Examples for Diffusion Models
  (Liang and Wu, 2023), arXiv:2305.12683.
- Radioactive Data: Tracing Through Training (Sablayrolles et al., 2020),
  arXiv:2002.00937.

### Backdoor and Clean-Label Trigger Literature

- Core theme: create samples that look benign but activate behavior under a
  trigger.
- Relevance: gives conceptual tools for invisible or clean-label sentinels.
- DeepSentinel angle: avoid training-time model poisoning; instead use
  retrieval-space geometry for ownership verification.

Verified references:

- BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply
  Chain (Gu, Dolan-Gavitt, and Garg, 2017), arXiv:1708.06733.

### Vision-Language Retrieval

- CLIP-style image-text embeddings provide the retrieval space for the first
  DeepSentinel real-image experiment.
- DeepSentinel angle: the method should be evaluated first in the embedding
  index itself before adding full RAIG generation as a downstream wrapper.

Verified references:

- Learning Transferable Visual Models From Natural Language Supervision
  (Radford et al., 2021), arXiv:2103.00020.

### Retrieval-Augmented Generation Dataset Protection

- Core theme: protect knowledge bases used by retrieval-augmented generation
  systems, usually by inserting canary content and later querying the deployed
  system for evidence.
- DeepSentinel angle: this is the closest conceptual neighbor, but text RAG
  canaries are not directly enough for visual RAIG because image sentinels can
  be removed by OCR, local-density pruning, and image-quality filters before
  indexing.

Verified references:

- Dataset Protection via Watermarked Canaries in Retrieval-Augmented LLMs
  (Liu, Zhao, Song, and Bu, submitted to ICLR 2026). CanaryTrace inserts
  synthetic watermarked canary documents into an IP text dataset, preserving
  original documents and detecting unauthorized RA-LLM use through statistical
  evidence in responses. DeepSentinel transfers the canary idea to visual RAIG
  but focuses on making sentinel images locally in-distribution so preprocessing
  cannot cheaply remove them.

## Working Gap Statement

Existing visible-key sentinel defenses are strong when the attacker indexes the
protected dataset unchanged, but weak when the attacker preprocesses the dataset
to remove key-bearing or anomalous images. A publishable contribution should
therefore formalize adaptive filtering, quantify collateral-damage tradeoffs,
and introduce a single simple sentinel construction that remains in-distribution.
