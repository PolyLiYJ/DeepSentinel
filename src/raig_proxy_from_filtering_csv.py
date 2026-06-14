#!/usr/bin/env python3
"""Aggregate RAIG proxy from a filtering CSV.

The exact proxy in ``raig_proxy_evidence.py`` recomputes per-trigger retrieval
hits from the CLIP embedding cache. This fallback uses only aggregate columns
already saved in a filtering CSV. It is useful when the cache lives on an
unreachable server, but should be reported as an aggregate estimate.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from raig_proxy_evidence import at_least_threshold_probability


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="") as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filtering-csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("data/h1_raig_proxy_aggregate.csv"))
    parser.add_argument("--num-triggers", type=int, default=8)
    parser.add_argument("--threshold", type=int, default=2)
    parser.add_argument("--false-match-rate", type=float, default=0.001)
    parser.add_argument("--generation-retention", default="1.0,0.75,0.5,0.25")
    args = parser.parse_args()

    retention_values = [
        float(x.strip()) for x in args.generation_retention.split(",") if x.strip()
    ]
    fpr = at_least_threshold_probability(
        [args.false_match_rate] * args.num_triggers,
        args.threshold,
    )

    rows = []
    for row in read_rows(args.filtering_csv):
        deep_hits = round(row["trigger_hit_rate_at_k"] * args.num_triggers)
        # Optimistic for the hidden-outlier baseline: survival is treated as if
        # every surviving outlier is also retrieved by its trigger.
        outlier_hits = round(row["hidden_outlier_survival"] * args.num_triggers)
        for retention in retention_values:
            deep_probs = [retention] * deep_hits + [0.0] * (args.num_triggers - deep_hits)
            outlier_probs = [retention] * outlier_hits + [0.0] * (
                args.num_triggers - outlier_hits
            )
            rows.append(
                {
                    "density_drop": row["density_drop"],
                    "normal_collateral": row["normal_collateral"],
                    "generation_retention": retention,
                    "threshold": args.threshold,
                    "false_match_rate": args.false_match_rate,
                    "proxy_fpr": fpr,
                    "deep_retrieval_hits": deep_hits,
                    "outlier_retrieval_hits": outlier_hits,
                    "num_triggers": args.num_triggers,
                    "deep_proxy_tpr": at_least_threshold_probability(
                        deep_probs,
                        args.threshold,
                    ),
                    "outlier_proxy_tpr": at_least_threshold_probability(
                        outlier_probs,
                        args.threshold,
                    ),
                    "estimate_kind": "aggregate_from_filtering_csv",
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.out}")
    print("estimate_kind=aggregate_from_filtering_csv")
    print(f"threshold={args.threshold} proxy_fpr={fpr:.8f}")


if __name__ == "__main__":
    main()
