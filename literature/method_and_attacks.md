# DeepSentinel Method and Attack Model

## Current Method

DeepSentinel replaces visible key-bearing sentinel images with
distribution-preserving latent retrieval sentinels. The current implementation is
selection-only: it does not add a watermark, render text, or optimize pixels.

Pipeline:

1. Encode every image in the protected dataset with a vision-language encoder
   such as CLIP.
2. Estimate local density by the average similarity to each image's top-k
   nearest image neighbors.
3. Keep a high-density candidate pool so candidate sentinels look like ordinary
   dataset members in embedding space.
4. Encode a private list of natural but low-frequency trigger prompts.
5. For each trigger, select a high-density image with relatively high trigger
   similarity as a latent sentinel.
6. During ownership testing, query the suspect RAIG system with the secret
   triggers and test whether the registered sentinels are retrieved or influence
   generated outputs.

Core claim:

> A visible key is easy to filter because it is visible. A latent sentinel is
> hard to filter because the suspicious signal is hidden inside normal retrieval
> geometry.

## Main Attacks

### Text/OCR Key Filtering

The attacker removes images containing visible text, random strings, QR-like
marks, or suspicious captions. This directly defeats visible-key sentinels and
is the main weakness of ImageSentinel-style random-key images.

### Embedding Outlier Filtering

The attacker embeds all images with CLIP, DINO, or a similar encoder and removes
global outliers. Generated sentinels, text-bearing images, and semantically
unusual samples are vulnerable.

### Local-Density Pruning

The attacker removes low local-density samples rather than only global outliers.
This is the most important adaptive attack for DeepSentinel because it asks
whether latent sentinels are truly in-distribution. The defense succeeds only if
removing latent sentinels also removes many normal images.

### Dataset Cleaning

The attacker runs standard cleaning: deduplication, blur/quality filtering,
watermark/text removal, resizing, compression, and generated-image filtering.
This attack matters because it can be framed as routine preprocessing rather
than adversarial removal.

### Metadata and Caption Filtering

For image-caption datasets, the attacker removes rare strings, unnatural
captions, prompt-like captions, or image-text mismatches. DeepSentinel therefore
keeps triggers private and does not rely on storing key strings in released
metadata.

### Re-rendering and Re-captioning

The attacker converts images into captions and regenerates a new dataset, or
applies heavy image transformations. This can destroy sentinel evidence but
also degrades dataset fidelity. DeepSentinel should eventually measure this as
a utility-security tradeoff.

## Why Not Combine Many Defenses?

The paper should stay focused on one mechanism: in-distribution latent retrieval
sentinels. Other tools such as output similarity auditing, invisible watermarks,
or distributed fingerprints can be useful in practice, but combining them would
blur the scientific claim. The publishable question is narrower:

> Does hiding sentinel evidence in high-density retrieval geometry force an
> adaptive filter to pay high collateral damage?

## Current Evidence

The 10-seed synthetic sweep supports the local-density tradeoff. At density drop
0.10, normal collateral damage averages 0.043, visible-key survival is 0.0,
hidden-outlier survival is 0.0, and DeepSentinel survival is 1.0 across all
seeds. The next required step is to test whether this selection-only mechanism
holds in real CLIP image embeddings.
