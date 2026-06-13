#!/usr/bin/env python3
"""Render RAIG proxy evidence CSVs as dependency-free SVG figures."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


COLORS = {
    "deep_proxy_tpr": "#1b9e77",
    "outlier_proxy_tpr": "#d95f02",
}


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="") as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]


def render(rows: list[dict[str, float]], out: Path, title: str) -> None:
    width, height = 980, 620
    left, right, top, bottom = 86, 34, 66, 92
    plot_w = width - left - right
    plot_h = height - top - bottom

    grouped: dict[float, list[dict[str, float]]] = defaultdict(list)
    for row in rows:
        grouped[row["generation_retention"]].append(row)
    retention_values = sorted(grouped, reverse=True)

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
        '.legend{font-size:14px}.small{font-size:12px}</style>',
        f'<text x="{width/2:.1f}" y="34" text-anchor="middle" class="title">{title}</text>',
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
    parts.append(f'<text x="{left + plot_w/2:.1f}" y="{height - 28}" text-anchor="middle" class="label">Normal collateral damage</text>')
    parts.append(f'<text transform="translate(24 {top + plot_h/2:.1f}) rotate(-90)" text-anchor="middle" class="label">Proxy ownership TPR</text>')

    dash_patterns = ["", "7 5", "3 5", "11 4 3 4", "2 3"]
    legend_y = top + 18
    for r_i, retention in enumerate(retention_values):
        rows_for_retention = sorted(grouped[retention], key=lambda row: row["normal_collateral"])
        dash = dash_patterns[r_i % len(dash_patterns)]
        opacity = max(0.42, 1.0 - r_i * 0.15)
        for key in ("deep_proxy_tpr", "outlier_proxy_tpr"):
            pts = [(sx(row["normal_collateral"]), sy(row[key])) for row in rows_for_retention]
            coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            parts.append(
                f'<polyline points="{coords}" fill="none" stroke="{COLORS[key]}" '
                f'stroke-width="3" stroke-linejoin="round" stroke-linecap="round" '
                f'opacity="{opacity:.2f}"{dash_attr}/>'
            )

        y = legend_y + r_i * 24
        parts.append(
            f'<line x1="{left + 18}" y1="{y}" x2="{left + 52}" y2="{y}" '
            f'stroke="#1b9e77" stroke-width="3" opacity="{opacity:.2f}"'
            f'{" stroke-dasharray=" + chr(34) + dash + chr(34) if dash else ""}/>'
        )
        parts.append(
            f'<text x="{left + 62}" y="{y + 5}" class="legend">DeepSentinel g={retention:.2f}</text>'
        )

    legend_x = width - 260
    parts.append(f'<line x1="{legend_x}" y1="{top + 18}" x2="{legend_x + 34}" y2="{top + 18}" stroke="#1b9e77" stroke-width="3"/>')
    parts.append(f'<text x="{legend_x + 44}" y="{top + 23}" class="legend">DeepSentinel</text>')
    parts.append(f'<line x1="{legend_x}" y1="{top + 44}" x2="{legend_x + 34}" y2="{top + 44}" stroke="#d95f02" stroke-width="3"/>')
    parts.append(f'<text x="{legend_x + 44}" y="{top + 49}" class="legend">Hidden outlier</text>')

    if rows:
        threshold = int(rows[0]["threshold"])
        fpr = rows[0]["proxy_fpr"]
        parts.append(
            f'<text x="{left}" y="{height - 8}" class="small">'
            f'Detection threshold: at least {threshold} trigger evidences; proxy FPR={fpr:.2e}</text>'
        )

    parts.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("to_human/h1_raig_proxy.svg"))
    parser.add_argument("--title", default="RAIG Proxy Ownership Detection")
    args = parser.parse_args()
    render(read_rows(args.csv), args.out, args.title)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
