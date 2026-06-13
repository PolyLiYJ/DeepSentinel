# DeepSentinel Findings

## Current Understanding

ImageSentinel-style protected datasets rely on sentinel images paired with
secret random character keys. This is powerful for black-box ownership testing,
but the visible or lexical key creates an attack surface: an adversary who sees
the dataset before indexing can remove images that contain random text, abnormal
captions, low semantic coherence, or outlier CLIP embeddings.

The promising direction is to make sentinel images look like ordinary high-value
data while making them retrievable by a secret trigger in embedding space. The
defense should force the attacker into a measurable tradeoff: either keep the
latent sentinels and remain detectable, or remove enough in-distribution images
that dataset utility suffers.

## Pilot Finding

The H1 synthetic pilot supports the mechanism. Visible-key sentinels are removed
immediately by a text-key filter. Hidden outlier sentinels are removed by a mild
local-density filter. DeepSentinel latent sentinels remain alive across the
tested density-filter range because they are chosen from dense normal regions.
The strongest tested filter removes 48% of normal data while still keeping all
latent sentinels in this synthetic setup.

A 10-seed synthetic sweep strengthens this pilot result. At density drop 0.10,
the attacker removes 4.3% of normal images on average, visible-key survival is
0.0, hidden-outlier survival is 0.0, and DeepSentinel survival remains 1.0
across all seeds. At density drop 0.50, DeepSentinel still has 1.0 survival
while normal collateral damage reaches 48.0% on average.

## Real CLIP Pilot Finding

The real-embedding experiments used deterministic COCO 2017 validation subsets
on the SSH server `Hulk` (`yjli@10.21.4.20`, 8x RTX 3090). With CLIP ViT-B/32,
the selection-only DeepSentinel mechanism preserves the synthetic trend:

- DeepSentinel survival remains 1.0 under density drops from 0.0 to 0.5.
- On COCO-1k, hidden-outlier survival falls to 0.5 at density drop 0.10 and
  reaches 0.0 at density drop 0.30; trigger hit@20 remains 1.0.
- On COCO-5k, hidden-outlier survival stays high through mild pruning but falls
  to 0.0 at density drop 0.35; trigger hit@20 is 0.875 before pruning and 1.0
  from density drop 0.25 onward.

Manual inspection of the contact sheet suggests that selected DeepSentinel
images are ordinary COCO images and therefore plausible in-distribution
sentinels. Some trigger-image semantic matches are loose, so the selection-only
variant currently demonstrates filter resistance more strongly than precise
semantic control. This is an important framing point for the paper: the current
method already supports the collateral-damage filtering story, while later work
can improve semantic tightness with constrained optimization.

## Candidate Ideas Considered

1. Natural-language semantic keys instead of random strings.
   This reduces OCR/random-token filtering but still leaves a prompt-level
   lexical signature if captions are inspected.

2. Many weak distributed watermarks across the dataset.
   This is robust in principle, but risks becoming a multi-component system and
   may be harder to explain in one AAAI paper.

3. Distribution-preserving latent sentinels.
   This is the selected direction. It uses one mechanism: choose normal-looking
   samples from dense regions and optimize or select them so a secret trigger
   retrieves them in the RAIG index.

4. Output-side similarity auditing only.
   Useful as a baseline or evaluation tool, but not sufficient as a proactive
   dataset defense.

## Selected Paper Thesis

Visible-key sentinel images are easy to filter because they are semantically and
visually suspicious. DeepSentinel makes the sentinel a normal in-distribution
retrieval item: ownership evidence is hidden in the geometry of the retrieval
embedding, not in visible text. The key scientific question is whether this
forces an adaptive attacker to pay high collateral damage to remove the evidence.

## Open Questions

- Can latent trigger alignment be achieved in real CLIP image embeddings without
  visibly degrading images?
- Does a selection-only latent sentinel already work in CLIP, before any
  pixel-space optimization is added? COCO-1k and COCO-5k results support
  survival and hit@20, but semantic tightness is still open.
- Does the effect transfer from retrieval-only evaluation to full RAIG systems
  such as SDXL+IP-Adapter or OmniGen-style pipelines?
- How many latent sentinels are needed for high-confidence black-box detection?
- Which adaptive filter is strongest: OCR/text removal, outlier removal, or local
  density pruning?
