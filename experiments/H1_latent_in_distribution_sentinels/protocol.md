# H1 Protocol: In-Distribution Latent Sentinels

## Hypothesis

Latent sentinels that are in-distribution in the retrieval embedding space will
survive adaptive filtering better than visible random-key sentinels. To remove
them, an attacker must set the suspiciousness threshold so aggressively that many
normal images are also removed.

## Confirmatory Prediction

In a clustered embedding benchmark:

- Visible-key sentinels should have near-zero survival under a text-key filter.
- Outlier sentinels should be removed by a density/outlier filter with low
  collateral damage.
- DeepSentinel-style latent sentinels should survive density filtering until the
  filter removes a substantially larger fraction of normal data.

## Method

We simulate a retrieval database as clustered unit vectors. Normal images are
sampled from cluster centers. Visible-key sentinels are marked as text-bearing
and partially out-of-distribution. DeepSentinel latent sentinels are selected
from high-density normal regions and shifted slightly toward a secret trigger
direction while remaining near the cluster manifold.

The attacker applies two filters:

1. A text-key filter that removes images flagged as visible-key samples.
2. A local-density filter that removes the lowest-density samples.

## Metrics

- Sentinel survival rate.
- Normal collateral damage rate.
- Trigger retrieval hit rate among surviving samples.
- Area under the survival-vs-collateral curve.

## Interpretation Criteria

The pilot supports H1 if DeepSentinel keeps high survival at collateral damage
levels where visible-key and outlier sentinels are mostly removed.
