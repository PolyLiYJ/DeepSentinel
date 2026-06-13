#!/usr/bin/env python3
"""Smoke test for the CLIP sentinel manifest contact-sheet tool."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from make_manifest_contact_sheet import read_manifest, render


def make_image(path: Path, label: str, color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (180, 140), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((12, 12, 168, 128), outline=(255, 255, 255), width=3)
    draw.text((22, 58), label, fill=(255, 255, 255))
    image.save(path)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rows: list[dict[str, str]] = []
        for trigger_id in range(2):
            for kind, color in (
                ("deep_sentinel", (30, 130, 110)),
                ("hidden_outlier", (190, 90, 35)),
            ):
                path = root / f"{trigger_id}_{kind}.jpg"
                make_image(path, f"{trigger_id} {kind}", color)
                rows.append(
                    {
                        "trigger_id": str(trigger_id),
                        "kind": kind,
                        "image_index": str(trigger_id),
                        "path": str(path),
                        "density": "0.72" if kind == "deep_sentinel" else "0.18",
                        "trigger_similarity": "0.31" if kind == "deep_sentinel" else "0.27",
                        "trigger": f"synthetic trigger {trigger_id}",
                    }
                )

        manifest = root / "manifest.csv"
        with manifest.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        out = root / "contact_sheet.jpg"
        render(read_manifest(manifest), out, tile=96, pad=12)
        if not out.exists() or out.stat().st_size == 0:
            raise SystemExit("contact sheet smoke test failed")
        print(f"smoke test passed: {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
