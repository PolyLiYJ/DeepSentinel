#!/usr/bin/env python3
"""Synthetic pilot for filter-resistant latent sentinels.

This script intentionally uses only the Python standard library so the first
research signal is reproducible on a clean machine. It is not a final paper
experiment; it tests whether the core filtering tradeoff is plausible before
moving to CLIP/RAIG evaluations.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Sample:
    kind: str
    vector: list[float]
    visible_key: bool = False


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm(a: list[float]) -> float:
    return math.sqrt(max(dot(a, a), 1e-12))


def unit(a: list[float]) -> list[float]:
    n = norm(a)
    return [x / n for x in a]


def add(a: list[float], b: list[float], scale_b: float = 1.0) -> list[float]:
    return [x + scale_b * y for x, y in zip(a, b)]


def random_unit(dim: int, rng: random.Random) -> list[float]:
    return unit([rng.gauss(0.0, 1.0) for _ in range(dim)])


def sample_around(center: list[float], noise: float, rng: random.Random) -> list[float]:
    return unit([x + rng.gauss(0.0, noise) for x in center])


def local_density(v: list[float], normals: list[list[float]], k: int = 20) -> float:
    sims = sorted((dot(v, n) for n in normals), reverse=True)
    return sum(sims[:k]) / min(k, len(sims))


def build_dataset(
    seed: int,
    dim: int,
    clusters: int,
    normals_per_cluster: int,
    sentinels_per_kind: int,
) -> tuple[list[Sample], list[float]]:
    rng = random.Random(seed)
    centers = [random_unit(dim, rng) for _ in range(clusters)]
    samples: list[Sample] = []

    for c in centers:
        for _ in range(normals_per_cluster):
            samples.append(Sample("normal", sample_around(c, 0.18, rng)))

    trigger = random_unit(dim, rng)

    for _ in range(sentinels_per_kind):
        c = rng.choice(centers)
        base = sample_around(c, 0.18, rng)
        # Visible-key sentinels are both explicitly text-bearing and somewhat
        # atypical in embedding space, matching the suspected failure mode.
        v = unit(add(base, random_unit(dim, rng), scale_b=0.55))
        samples.append(Sample("visible_key", v, visible_key=True))

    normals = [s.vector for s in samples if s.kind == "normal"]
    scored_normals = sorted(
        normals, key=lambda v: local_density(v, normals, k=20), reverse=True
    )
    dense_pool = scored_normals[: max(sentinels_per_kind * 4, sentinels_per_kind)]

    for i in range(sentinels_per_kind):
        base = dense_pool[i % len(dense_pool)]
        # DeepSentinel: small retrieval-space shift toward the trigger while
        # staying close to a high-density normal point.
        v = unit(add(base, trigger, scale_b=0.18))
        samples.append(Sample("deep_sentinel", v, visible_key=False))

    for _ in range(sentinels_per_kind):
        # Ablation: hidden but out-of-distribution sentinels.
        v = unit(add(random_unit(dim, rng), trigger, scale_b=0.4))
        samples.append(Sample("hidden_outlier", v, visible_key=False))

    return samples, trigger


def evaluate(samples: list[Sample], trigger: list[float], density_drop: float) -> dict[str, float]:
    normals = [s.vector for s in samples if s.kind == "normal"]
    scored = [(local_density(s.vector, normals, k=20), s) for s in samples]
    threshold_index = int(len(scored) * density_drop)
    threshold = sorted(score for score, _ in scored)[threshold_index] if threshold_index else -1e9

    survivors = [
        s for density, s in scored if not s.visible_key and density >= threshold
    ]

    def survival(kind: str) -> float:
        total = sum(1 for s in samples if s.kind == kind)
        kept = sum(1 for s in survivors if s.kind == kind)
        return kept / total if total else 0.0

    normal_total = sum(1 for s in samples if s.kind == "normal")
    normal_kept = sum(1 for s in survivors if s.kind == "normal")
    collateral = 1.0 - normal_kept / normal_total

    ranked = sorted(survivors, key=lambda s: dot(s.vector, trigger), reverse=True)
    top20 = ranked[:20]
    top20_deep_hits = sum(1 for s in top20 if s.kind == "deep_sentinel") / max(len(top20), 1)

    return {
        "density_drop": density_drop,
        "normal_collateral": collateral,
        "visible_key_survival": survival("visible_key"),
        "deep_sentinel_survival": survival("deep_sentinel"),
        "hidden_outlier_survival": survival("hidden_outlier"),
        "top20_deep_hit_rate": top20_deep_hits,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=Path, default=Path("data/h1_synthetic_filtering.csv"))
    args = parser.parse_args()

    samples, trigger = build_dataset(
        seed=args.seed,
        dim=96,
        clusters=12,
        normals_per_cluster=90,
        sentinels_per_kind=48,
    )

    drops = [i / 100 for i in range(0, 51, 5)]
    rows = [evaluate(samples, trigger, d) for d in drops]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.out}")
    for row in rows:
        print(
            "drop={density_drop:.2f} collateral={normal_collateral:.3f} "
            "visible={visible_key_survival:.3f} deep={deep_sentinel_survival:.3f} "
            "outlier={hidden_outlier_survival:.3f} top20deep={top20_deep_hit_rate:.3f}".format(
                **row
            )
        )


if __name__ == "__main__":
    main()
