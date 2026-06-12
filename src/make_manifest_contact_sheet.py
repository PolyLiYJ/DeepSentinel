#!/usr/bin/env python3
"""Build a visual contact sheet from a CLIP sentinel manifest.

The CLIP experiment writes one row per selected sentinel candidate. This helper
turns that manifest into a compact image for the manual normality check: do the
DeepSentinel images look like ordinary dataset items, or did selection pick
obvious semantic outliers?
"""

from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def fit_image(path: Path, size: int) -> Image.Image:
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((size, size))
        canvas = Image.new("RGB", (size, size), "white")
        x = (size - img.width) // 2
        y = (size - img.height) // 2
        canvas.paste(img, (x, y))
        return canvas


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int) -> int:
    lines: list[str] = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=width) or [""])
    x, y = xy
    for line in lines:
        draw.text((x, y), line, fill=(32, 33, 36))
        y += 14
    return y


def render(rows: list[dict[str, str]], out: Path, tile: int, pad: int) -> None:
    if not rows:
        raise ValueError("Manifest is empty")

    trigger_ids = sorted({int(r["trigger_id"]) for r in rows})
    kinds = ["deep_sentinel", "hidden_outlier"]
    row_h = tile + 92
    col_w = tile + pad * 2
    label_w = 330
    width = label_w + len(kinds) * col_w
    height = 48 + len(trigger_ids) * row_h

    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)

    draw.text((pad, 16), "DeepSentinel CLIP Manifest Contact Sheet", fill=(32, 33, 36))
    for c, kind in enumerate(kinds):
        x = label_w + c * col_w + pad
        draw.text((x, 16), kind, fill=(32, 33, 36))

    by_key = {(int(r["trigger_id"]), r["kind"]): r for r in rows}
    for ridx, trigger_id in enumerate(trigger_ids):
        y0 = 48 + ridx * row_h
        trigger = by_key[(trigger_id, "deep_sentinel")]["trigger"]
        draw.text((pad, y0 + pad), f"trigger {trigger_id}", fill=(32, 33, 36))
        draw_wrapped(draw, (pad, y0 + pad + 18), trigger, width=42)

        for c, kind in enumerate(kinds):
            r = by_key.get((trigger_id, kind))
            if r is None:
                continue
            x = label_w + c * col_w + pad
            path = Path(r["path"])
            try:
                img = fit_image(path, tile)
                sheet.paste(img, (x, y0 + pad))
            except Exception as exc:  # noqa: BLE001 - write visible failure into sheet
                draw.rectangle((x, y0 + pad, x + tile, y0 + pad + tile), outline=(180, 0, 0))
                draw_wrapped(draw, (x + 8, y0 + pad + 8), f"failed: {exc}", width=26)
            caption = f"density={float(r['density']):.3f} sim={float(r['trigger_similarity']):.3f}"
            draw.text((x, y0 + pad + tile + 8), caption, fill=(32, 33, 36))
            draw_wrapped(draw, (x, y0 + pad + tile + 25), path.name, width=28)

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/h1_clip_sentinel_manifest.csv"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("to_human/h1_clip_manifest_contact_sheet.jpg"),
    )
    parser.add_argument("--tile", type=int, default=160)
    parser.add_argument("--pad", type=int, default=16)
    args = parser.parse_args()

    rows = read_manifest(args.manifest)
    render(rows, args.out, tile=args.tile, pad=args.pad)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
