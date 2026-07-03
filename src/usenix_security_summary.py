#!/usr/bin/env python3
"""USENIX Security-oriented summary tables for DeepSentinel.

This script does not run new CLIP or generation experiments. It converts the
current COCO filtering and RAIG proxy CSVs into the extra statistical views that
USENIX Security reviewers would expect: confidence intervals, attacker cost
curves, detection power as trigger count changes, and an explicit experiment gap
table.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path}")


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - half), min(1.0, center + half)


def at_least_threshold_probability(probs: list[float], threshold: int) -> float:
    dist = [1.0]
    for p in probs:
        nxt = [0.0] * (len(dist) + 1)
        for hits, mass in enumerate(dist):
            nxt[hits] += mass * (1.0 - p)
            nxt[hits + 1] += mass * p
        dist = nxt
    return sum(dist[threshold:])


def make_attack_cost_rows(filtering_rows: list[dict[str, str]], num_triggers: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in filtering_rows:
        drop = float(row["density_drop"])
        deep_surv = float(row["deep_sentinel_survival"])
        out_surv = float(row["hidden_outlier_survival"])
        hit = float(row["trigger_hit_rate_at_k"])
        deep_success = round(deep_surv * num_triggers)
        out_success = round(out_surv * num_triggers)
        hit_success = round(hit * num_triggers)
        deep_ci = wilson_interval(deep_success, num_triggers)
        out_ci = wilson_interval(out_success, num_triggers)
        hit_ci = wilson_interval(hit_success, num_triggers)
        rows.append(
            {
                "density_drop": drop,
                "normal_collateral": float(row["normal_collateral"]),
                "utility_retained_proxy": 1.0 - float(row["normal_collateral"]),
                "deep_survival": deep_surv,
                "deep_survival_ci95_low": deep_ci[0],
                "deep_survival_ci95_high": deep_ci[1],
                "hidden_outlier_survival": out_surv,
                "hidden_outlier_ci95_low": out_ci[0],
                "hidden_outlier_ci95_high": out_ci[1],
                "deep_trigger_hit_at_20": hit,
                "deep_hit_ci95_low": hit_ci[0],
                "deep_hit_ci95_high": hit_ci[1],
                "deep_removed": int(float(row["deep_removed"])),
                "outlier_removed": int(float(row["outlier_removed"])),
            }
        )
    return rows


def make_trigger_power_rows(
    proxy_rows: list[dict[str, str]],
    density_drop: float,
    generation_retention: float,
    threshold_values: list[int],
    false_match_rate: float,
) -> list[dict[str, object]]:
    candidates = [
        row
        for row in proxy_rows
        if abs(float(row["density_drop"]) - density_drop) < 1e-9
        and abs(float(row["generation_retention"]) - generation_retention) < 1e-9
    ]
    if not candidates:
        raise ValueError("requested density/generation point missing from proxy CSV")
    row = candidates[0]
    total = int(float(row["num_triggers"]))
    deep_hits = int(float(row["deep_retrieval_hits"]))
    outlier_hits = int(float(row["outlier_retrieval_hits"]))

    rows: list[dict[str, object]] = []
    for used in range(2, total + 1):
        deep_observed = min(deep_hits, used)
        out_observed = min(outlier_hits, used)
        for threshold in threshold_values:
            if threshold > used:
                continue
            deep_probs = [generation_retention] * deep_observed + [0.0] * (used - deep_observed)
            out_probs = [generation_retention] * out_observed + [0.0] * (used - out_observed)
            false_probs = [false_match_rate] * used
            rows.append(
                {
                    "density_drop": density_drop,
                    "generation_retention": generation_retention,
                    "num_triggers_used": used,
                    "threshold": threshold,
                    "false_match_rate": false_match_rate,
                    "proxy_fpr": at_least_threshold_probability(false_probs, threshold),
                    "deep_proxy_tpr": at_least_threshold_probability(deep_probs, threshold),
                    "hidden_outlier_proxy_tpr": at_least_threshold_probability(out_probs, threshold),
                    "deep_retrieval_hits_capped": deep_observed,
                    "outlier_retrieval_hits_capped": out_observed,
                }
            )
    return rows


def make_false_match_rows(
    proxy_rows: list[dict[str, str]],
    density_drop: float,
    generation_retention: float,
    false_match_rates: list[float],
    threshold: int,
) -> list[dict[str, object]]:
    candidates = [
        row
        for row in proxy_rows
        if abs(float(row["density_drop"]) - density_drop) < 1e-9
        and abs(float(row["generation_retention"]) - generation_retention) < 1e-9
    ]
    if not candidates:
        raise ValueError("requested density/generation point missing from proxy CSV")
    row = candidates[0]
    total = int(float(row["num_triggers"]))
    deep_hits = int(float(row["deep_retrieval_hits"]))
    outlier_hits = int(float(row["outlier_retrieval_hits"]))
    deep_probs = [generation_retention] * deep_hits + [0.0] * (total - deep_hits)
    out_probs = [generation_retention] * outlier_hits + [0.0] * (total - outlier_hits)
    rows: list[dict[str, object]] = []
    for fmr in false_match_rates:
        rows.append(
            {
                "density_drop": density_drop,
                "generation_retention": generation_retention,
                "threshold": threshold,
                "false_match_rate": fmr,
                "proxy_fpr": at_least_threshold_probability([fmr] * total, threshold),
                "deep_proxy_tpr": at_least_threshold_probability(deep_probs, threshold),
                "hidden_outlier_proxy_tpr": at_least_threshold_probability(out_probs, threshold),
            }
        )
    return rows


def make_gap_rows() -> list[dict[str, object]]:
    return [
        {
            "requirement": "real_raig_generation",
            "current_status": "missing",
            "needed_experiment": "SDXL+IP-Adapter or equivalent image-conditioned RAIG with generated-output evidence matching",
            "paper_risk_if_missing": "retrieval-only evidence may not survive generation",
        },
        {
            "requirement": "strong_adaptive_attacks",
            "current_status": "partial_density_attack_only",
            "needed_experiment": "OCR/text, CLIP outlier, density, dedup, caption-image mismatch, and calibrated attack budgets",
            "paper_risk_if_missing": "attacker model may look underpowered",
        },
        {
            "requirement": "larger_or_extra_datasets",
            "current_status": "COCO_1k_and_5k",
            "needed_experiment": "Product-10K or another product/art domain plus larger natural-image subset",
            "paper_risk_if_missing": "domain transfer and scale remain unproven",
        },
        {
            "requirement": "utility_damage",
            "current_status": "normal_collateral_proxy",
            "needed_experiment": "normal-query Recall@K, top-k similarity, diversity, and generation CLIPScore under filtering",
            "paper_risk_if_missing": "collateral damage may not equal real RAIG utility loss",
        },
        {
            "requirement": "detection_statistics",
            "current_status": "aggregate_proxy_available",
            "needed_experiment": "exact TPR/FPR, confidence intervals, trigger-count power, false-positive calibration",
            "paper_risk_if_missing": "ownership claim lacks security-style statistical calibration",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filtering-csv", type=Path, required=True)
    parser.add_argument("--proxy-csv", type=Path, required=True)
    parser.add_argument("--out-prefix", type=Path, required=True)
    parser.add_argument("--num-triggers", type=int, default=8)
    parser.add_argument("--density-drop", type=float, default=0.35)
    parser.add_argument("--generation-retention", type=float, default=0.5)
    parser.add_argument("--thresholds", default="1,2,3")
    parser.add_argument("--false-match-rates", default="0.0001,0.001,0.01")
    args = parser.parse_args()

    filtering_rows = read_csv(args.filtering_csv)
    proxy_rows = read_csv(args.proxy_csv)
    thresholds = [int(x.strip()) for x in args.thresholds.split(",") if x.strip()]
    false_rates = [float(x.strip()) for x in args.false_match_rates.split(",") if x.strip()]

    write_csv(
        args.out_prefix.with_name(args.out_prefix.name + "_attack_cost.csv"),
        make_attack_cost_rows(filtering_rows, args.num_triggers),
    )
    write_csv(
        args.out_prefix.with_name(args.out_prefix.name + "_trigger_power.csv"),
        make_trigger_power_rows(
            proxy_rows,
            density_drop=args.density_drop,
            generation_retention=args.generation_retention,
            threshold_values=thresholds,
            false_match_rate=0.001,
        ),
    )
    write_csv(
        args.out_prefix.with_name(args.out_prefix.name + "_false_match_calibration.csv"),
        make_false_match_rows(
            proxy_rows,
            density_drop=args.density_drop,
            generation_retention=args.generation_retention,
            false_match_rates=false_rates,
            threshold=2,
        ),
    )
    write_csv(
        args.out_prefix.with_name(args.out_prefix.name + "_experiment_gaps.csv"),
        make_gap_rows(),
    )


if __name__ == "__main__":
    main()
