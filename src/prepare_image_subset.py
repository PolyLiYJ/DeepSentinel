#!/usr/bin/env python3
"""Prepare a deterministic image subset for CLIP filtering experiments."""

from __future__ import annotations

import argparse
import csv
import random
import shutil
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def list_images(image_dir: Path) -> list[Path]:
    return [
        p
        for p in sorted(image_dir.rglob("*"))
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]


def unique_name(index: int, path: Path) -> str:
    safe_stem = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in path.stem)
    return f"{index:06d}_{safe_stem}{path.suffix.lower()}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--copy", action="store_true", help="Copy files instead of creating symlinks.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Defaults to <out-dir>/subset_manifest.csv.",
    )
    args = parser.parse_args()

    paths = list_images(args.image_dir)
    if not paths:
        raise SystemExit(f"No images found under {args.image_dir}")

    rng = random.Random(args.seed)
    chosen = paths[:]
    rng.shuffle(chosen)
    chosen = chosen[: min(args.limit, len(chosen))]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = args.manifest or args.out_dir / "subset_manifest.csv"
    rows: list[dict[str, str]] = []
    for i, src in enumerate(chosen):
        dst = args.out_dir / unique_name(i, src)
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        if args.copy:
            shutil.copy2(src, dst)
            mode = "copy"
        else:
            dst.symlink_to(src.resolve())
            mode = "symlink"
        rows.append(
            {
                "subset_index": str(i),
                "source_path": str(src),
                "subset_path": str(dst),
                "mode": mode,
            }
        )

    with manifest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"found={len(paths)} selected={len(chosen)} out_dir={args.out_dir}")
    print(f"wrote {manifest}")


if __name__ == "__main__":
    main()
