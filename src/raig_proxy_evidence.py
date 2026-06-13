#!/usr/bin/env python3
"""Proxy RAIG evidence test for DeepSentinel.

This script reuses a CLIP embedding cache from ``clip_filtering_experiment.py``.
It does not add a new defense. It asks: if a retrieved sentinel survives into a
generated output with probability g, how often would a black-box owner detect at
least m pieces of sentinel evidence after filtering?
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import torch

from clip_filtering_experiment import DEFAULT_TRIGGERS, choose_sentinels, local_density


def at_least_threshold_probability(probs: list[float], threshold: int) -> float:
    """Return P(sum Bernoulli(probs) >= threshold) by dynamic programming."""
    dist = [1.0]
    for p in probs:
        next_dist = [0.0] * (len(dist) + 1)
        for hits, mass in enumerate(dist):
            next_dist[hits] += mass * (1.0 - p)
            next_dist[hits + 1] += mass * p
        dist = next_dist
    return sum(dist[threshold:])


def retrieval_hits(
    image_embeds: torch.Tensor,
    trigger_embeds: torch.Tensor,
    densities: torch.Tensor,
    sentinel_indices: list[int],
    drop: float,
    topk: int,
) -> list[int]:
    n = image_embeds.shape[0]
    remove_count = int(math.floor(n * drop))
    removed = set(torch.argsort(densities, descending=False)[:remove_count].tolist())
    survivors = [i for i in range(n) if i not in removed]
    survivor_tensor = torch.tensor(survivors, dtype=torch.long)
    survivor_embeds = image_embeds[survivor_tensor]

    hits: list[int] = []
    for j, sentinel_index in enumerate(sentinel_indices):
        if sentinel_index in removed:
            hits.append(0)
            continue
        scores = survivor_embeds @ trigger_embeds[j]
        top = torch.topk(scores, k=min(topk, len(survivors))).indices.tolist()
        retrieved = {survivors[t] for t in top}
        hits.append(1 if sentinel_index in retrieved else 0)
    return hits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("data/h1_raig_proxy_coco5k.csv"))
    parser.add_argument("--density-k", type=int, default=20)
    parser.add_argument("--dense-quantile", type=float, default=0.25)
    parser.add_argument("--topk", type=int, default=20)
    parser.add_argument("--threshold", type=int, default=2)
    parser.add_argument("--false-match-rate", type=float, default=0.001)
    parser.add_argument("--generation-retention", default="1.0,0.75,0.5,0.25")
    args = parser.parse_args()

    payload = torch.load(args.cache, map_location="cpu", weights_only=False)
    image_embeds = payload["image_embeds"]
    trigger_embeds = payload["trigger_embeds"]
    triggers = payload.get("triggers", DEFAULT_TRIGGERS)
    densities = local_density(image_embeds, args.density_k)
    sentinels = choose_sentinels(
        image_embeds=image_embeds,
        triggers=triggers,
        trigger_embeds=trigger_embeds,
        densities=densities,
        dense_quantile=args.dense_quantile,
    )

    retention_values = [
        float(x.strip()) for x in args.generation_retention.split(",") if x.strip()
    ]
    rows: list[dict[str, float | int | str]] = []
    num_triggers = len(triggers)
    fpr = at_least_threshold_probability(
        [args.false_match_rate] * num_triggers,
        args.threshold,
    )

    for drop_i in range(0, 51, 5):
        drop = drop_i / 100
        deep_hits = retrieval_hits(
            image_embeds,
            trigger_embeds,
            densities,
            sentinels.deep_indices,
            drop,
            args.topk,
        )
        outlier_hits = retrieval_hits(
            image_embeds,
            trigger_embeds,
            densities,
            sentinels.outlier_indices,
            drop,
            args.topk,
        )
        for retention in retention_values:
            deep_probs = [retention if hit else 0.0 for hit in deep_hits]
            outlier_probs = [retention if hit else 0.0 for hit in outlier_hits]
            rows.append(
                {
                    "density_drop": drop,
                    "normal_collateral": drop,
                    "generation_retention": retention,
                    "threshold": args.threshold,
                    "false_match_rate": args.false_match_rate,
                    "proxy_fpr": fpr,
                    "deep_retrieval_hits": sum(deep_hits),
                    "outlier_retrieval_hits": sum(outlier_hits),
                    "num_triggers": num_triggers,
                    "deep_proxy_tpr": at_least_threshold_probability(
                        deep_probs,
                        args.threshold,
                    ),
                    "outlier_proxy_tpr": at_least_threshold_probability(
                        outlier_probs,
                        args.threshold,
                    ),
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.out}")
    print(f"num_triggers={num_triggers} threshold={args.threshold} proxy_fpr={fpr:.8f}")
    for row in rows:
        if row["generation_retention"] in {1.0, 0.5}:
            print(
                "drop={density_drop:.2f} g={generation_retention:.2f} "
                "deep_hits={deep_retrieval_hits}/{num_triggers} "
                "outlier_hits={outlier_retrieval_hits}/{num_triggers} "
                "deep_tpr={deep_proxy_tpr:.3f} outlier_tpr={outlier_proxy_tpr:.3f}".format(
                    **row
                )
            )


if __name__ == "__main__":
    main()
