# Candidate Research Ideas

## Problem

ImageSentinel-style visible key sentinels are vulnerable to an adaptive dataset
thief who filters suspicious samples before building a RAIG index.

## Raw Candidates

1. Replace random key strings with natural-language secret prompts.
2. Hide key text in image backgrounds with steganographic perturbations.
3. Distribute weak watermarks across many normal images.
4. Use output-side similarity auditing with no dataset modification.
5. Optimize sentinel images to be CLIP-retrieved by a secret prompt while staying
   in a high-density region of the original image distribution.
6. Use clean-label image-caption pairs whose captions contain a secret relation
   but whose images remain normal.
7. Choose naturally occurring near-neighbors to a secret prompt and register them
   as ownership sentinels.
8. Use adversarial examples that survive diffusion generation and leave a hidden
   detectable signature in outputs.

## Ranked Shortlist

### 1. DeepSentinel: Distribution-Preserving Latent Retrieval Sentinels

Two-sentence pitch: RAIG dataset ownership methods currently depend on visible
or lexical sentinel keys that an attacker can remove before indexing. We encode
ownership evidence in retrieval embedding geometry by selecting or optimizing
in-distribution sentinel images that respond to a secret trigger while remaining
locally indistinguishable from normal data.

Why it wins:

- Directly addresses the user's filtering objection.
- One mechanism, easy to explain.
- Testable with retrieval-only CLIP experiments before full RAIG experiments.
- High-quality AI venue fit: security, generative AI, dataset governance, and
  evaluation under adaptive attacks.

Main risk:

- Real CLIP optimization may create visible artifacts or embedding outliers.

### 2. Natural Semantic Key Sentinels

Promising but weaker. It removes random strings, yet a careful attacker can still
search captions or use language-model filters for rare unnatural phrases.

### 3. Distributed Weak Sentinel Fingerprints

Potentially robust, but it becomes a multi-component defense and conflicts with
the goal of writing one focused paper around one scheme.

## Selected Direction

Proceed with DeepSentinel as the single scheme. Treat the other ideas as
baselines or ablations only when needed, not as combined components.
