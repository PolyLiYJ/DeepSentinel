#!/usr/bin/env python3
"""Render filtering tradeoff CSVs as dependency-free SVG figures."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


SERIES = [
    ("deep_sentinel_survival", "DeepSentinel", "#1b9e77"),
    ("hidden_outlier_survival", "Hidden outlier", "#d95f02"),
    ("visible_key_survival", "Visible key", "#7570b3"),
    ("top20_deep_hit_rate", "Deep trigger hit@20", "#333333"),
]


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="") as f:
        return [
            {k: float(v) for k, v in row.items()}
            for row in csv.DictReader(f)
        ]


def render(rows: list[dict[str, float]], out: Path, title: str) -> None:
    width, height = 900, 560
    left, right, top, bottom = 86, 32, 58, 82
    plot_w = width - left - right
    plot_h = height - top - bottom

    def sx(x: float) -> float:
        return left + x * plot_w

    def sy(y: float) -> float:
        return top + (1.0 - y) * plot_h

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#202124}'
        '.tick{font-size:13px}.label{font-size:16px}.title{font-size:22px;font-weight:700}'
        '.legend{font-size:14px}</style>',
        f'<text x="{width/2:.1f}" y="32" text-anchor="middle" class="title">{title}</text>',
    ]

    for i in range(6):
        v = i / 5
        x = sx(v)
        y = sy(v)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="#edf0f2"/>')
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#edf0f2"/>')
        parts.append(f'<text x="{x:.1f}" y="{top + plot_h + 25}" text-anchor="middle" class="tick">{v:.1f}</text>')
        parts.append(f'<text x="{left - 16}" y="{y + 5:.1f}" text-anchor="end" class="tick">{v:.1f}</text>')

    parts.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#202124" stroke-width="1.5"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#202124" stroke-width="1.5"/>')
    parts.append(f'<text x="{left + plot_w/2:.1f}" y="{height - 24}" text-anchor="middle" class="label">Normal collateral damage</text>')
    parts.append(f'<text transform="translate(24 {top + plot_h/2:.1f}) rotate(-90)" text-anchor="middle" class="label">Survival / hit rate</text>')

    def value_key(base_key: str) -> str | None:
        if base_key in rows[0]:
            return base_key
        mean_key = f"{base_key}_mean"
        if mean_key in rows[0]:
            return mean_key
        return None

    x_key = value_key("normal_collateral")
    if x_key is None:
        raise ValueError("CSV must contain normal_collateral or normal_collateral_mean")

    for key, label, color in SERIES:
        y_key = value_key(key)
        if y_key is None:
            continue
        min_key = f"{key}_min"
        max_key = f"{key}_max"
        if min_key in rows[0] and max_key in rows[0]:
            upper = [(sx(r[x_key]), sy(r[max_key])) for r in rows]
            lower = [(sx(r[x_key]), sy(r[min_key])) for r in reversed(rows)]
            band = " ".join(f"{x:.1f},{y:.1f}" for x, y in upper + lower)
            parts.append(
                f'<polygon points="{band}" fill="{color}" opacity="0.12" '
                'stroke="none"/>'
            )
        pts = [(sx(r[x_key]), sy(r[y_key])) for r in rows]
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        parts.append(
            f'<polyline points="{coords}" fill="none" stroke="{color}" '
            'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for x, y in pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>')

    legend_x, legend_y = left + 18, top + 18
    for i, (_, label, color) in enumerate(SERIES):
        y = legend_y + i * 24
        parts.append(f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 28}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{legend_x + 38}" y="{y + 5}" class="legend">{label}</text>')

    parts.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("data/h1_synthetic_filtering.csv"))
    parser.add_argument("--out", type=Path, default=Path("to_human/h1_synthetic_tradeoff.svg"))
    parser.add_argument("--title", default="Filtering Tradeoff in the H1 Pilot")
    args = parser.parse_args()
    render(read_rows(args.csv), args.out, args.title)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
