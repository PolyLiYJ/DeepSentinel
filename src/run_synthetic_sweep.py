#!/usr/bin/env python3
"""Run the H1 synthetic filtering pilot across multiple random seeds."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

from simulate_filtering import Sample, build_dataset, dot, local_density


METRICS = [
    "normal_collateral",
    "visible_key_survival",
    "deep_sentinel_survival",
    "hidden_outlier_survival",
    "top20_deep_hit_rate",
]


def evaluate_from_scored(
    scored: list[tuple[float, Sample]],
    normal_total: int,
    trigger: list[float],
    density_drop: float,
) -> dict[str, float]:
    threshold_index = int(len(scored) * density_drop)
    thresholds = [score for score, _ in scored]
    threshold = thresholds[threshold_index] if threshold_index else -1e9
    survivors = [
        s for density, s in scored if not s.visible_key and density >= threshold
    ]

    def survival(kind: str) -> float:
        total = sum(1 for _, s in scored if s.kind == kind)
        kept = sum(1 for s in survivors if s.kind == kind)
        return kept / total if total else 0.0

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


def run_seed(seed: int) -> list[dict[str, float]]:
    samples, trigger = build_dataset(
        seed=seed,
        dim=96,
        clusters=12,
        normals_per_cluster=90,
        sentinels_per_kind=48,
    )
    normals = [s.vector for s in samples if s.kind == "normal"]
    scored = sorted(
        [(local_density(s.vector, normals, k=20), s) for s in samples],
        key=lambda item: item[0],
    )
    normal_total = sum(1 for s in samples if s.kind == "normal")
    return [
        evaluate_from_scored(scored, normal_total, trigger, i / 100)
        for i in range(0, 51, 5)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--first-seed", type=int, default=0)
    parser.add_argument("--raw-out", type=Path, default=Path("data/h1_synthetic_sweep_raw.csv"))
    parser.add_argument("--summary-out", type=Path, default=Path("data/h1_synthetic_sweep_summary.csv"))
    args = parser.parse_args()

    raw_rows: list[dict[str, float | int]] = []
    for seed in range(args.first_seed, args.first_seed + args.seeds):
        for row in run_seed(seed):
            raw_rows.append({"seed": seed, **row})

    by_drop: dict[float, list[dict[str, float | int]]] = defaultdict(list)
    for row in raw_rows:
        by_drop[float(row["density_drop"])].append(row)

    summary_rows: list[dict[str, float]] = []
    for drop in sorted(by_drop):
        rows = by_drop[drop]
        summary: dict[str, float] = {"density_drop": drop}
        for metric in METRICS:
            values = [float(r[metric]) for r in rows]
            summary[f"{metric}_mean"] = statistics.mean(values)
            summary[f"{metric}_min"] = min(values)
            summary[f"{metric}_max"] = max(values)
        summary_rows.append(summary)

    args.raw_out.parent.mkdir(parents=True, exist_ok=True)
    with args.raw_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
        writer.writeheader()
        writer.writerows(raw_rows)

    with args.summary_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"wrote {args.raw_out}")
    print(f"wrote {args.summary_out}")
    for row in summary_rows:
        print(
            "drop={density_drop:.2f} collateral={normal_collateral_mean:.3f} "
            "visible={visible_key_survival_mean:.3f} deep={deep_sentinel_survival_mean:.3f} "
            "outlier={hidden_outlier_survival_mean:.3f} hit20={top20_deep_hit_rate_mean:.3f}".format(
                **row
            )
        )


if __name__ == "__main__":
    main()
