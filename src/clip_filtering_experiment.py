#!/usr/bin/env python3
"""CLIP retrieval filtering experiment for DeepSentinel.

The script accepts a local image directory, embeds images with CLIP, selects
latent sentinels from dense regions, and measures their survival under
local-density filtering. It is intentionally selection-only: no extra watermark,
no OCR bypass trick, no multi-component defense.
"""

from __future__ import annotations

import argparse
import csv
import math
import json
from dataclasses import dataclass
from pathlib import Path

import torch
from PIL import Image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DEFAULT_TRIGGERS = [
    "a quiet blue ceramic cup beside a folded yellow map",
    "a red canvas chair under a small square mirror",
    "a green toolbox next to a white paper lantern",
    "a striped notebook beside a brass desk lamp",
    "a transparent vase near a black wool scarf",
    "a wooden toy boat on a pale kitchen towel",
    "a silver camera strap beside an orange envelope",
    "a matte purple bottle next to a round stone coaster",
]


@dataclass
class SentinelSet:
    deep_indices: list[int]
    outlier_indices: list[int]
    trigger_embeds: torch.Tensor
    triggers: list[str]


def list_images(image_dir: Path, limit: int | None) -> list[Path]:
    paths = [
        p
        for p in sorted(image_dir.rglob("*"))
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    if limit is not None:
        paths = paths[:limit]
    if not paths:
        raise ValueError(f"No images found under {image_dir}")
    return paths


def load_clip(model_name: str, device: str):
    try:
        from transformers import CLIPModel, CLIPProcessor
    except ImportError as exc:
        raise SystemExit(
            "transformers is required for CLIP encoding. Install transformers "
            "or provide precomputed embeddings in a future extension."
        ) from exc

    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name).to(device)
    model.eval()
    return model, processor


def encode_images(
    paths: list[Path],
    model,
    processor,
    device: str,
    batch_size: int,
) -> torch.Tensor:
    embeds: list[torch.Tensor] = []
    with torch.no_grad():
        for start in range(0, len(paths), batch_size):
            batch_paths = paths[start : start + batch_size]
            images = []
            for p in batch_paths:
                with Image.open(p) as img:
                    images.append(img.convert("RGB"))
            inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
            feat = model.get_image_features(**inputs)
            feat = torch.nn.functional.normalize(feat, dim=-1)
            embeds.append(feat.cpu())
    return torch.cat(embeds, dim=0)


def encode_text(prompts: list[str], model, processor, device: str) -> torch.Tensor:
    with torch.no_grad():
        inputs = processor(text=prompts, return_tensors="pt", padding=True).to(device)
        feat = model.get_text_features(**inputs)
        feat = torch.nn.functional.normalize(feat, dim=-1)
    return feat.cpu()


def cache_payload_matches(
    payload: dict,
    paths: list[Path],
    model_name: str,
    triggers: list[str],
) -> bool:
    return (
        payload.get("model_name") == model_name
        and payload.get("paths") == [str(p) for p in paths]
        and payload.get("triggers") == triggers
    )


def load_or_encode(
    cache: Path | None,
    paths: list[Path],
    model_name: str,
    device: str,
    batch_size: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if cache is not None and cache.exists():
        payload = torch.load(cache, map_location="cpu", weights_only=False)
        if cache_payload_matches(payload, paths, model_name, DEFAULT_TRIGGERS):
            print(f"loaded cache {cache}")
            return payload["image_embeds"], payload["trigger_embeds"]
        print(f"cache mismatch, recomputing embeddings: {cache}")

    model, processor = load_clip(model_name, device)
    image_embeds = encode_images(paths, model, processor, device, batch_size)
    trigger_embeds = encode_text(DEFAULT_TRIGGERS, model, processor, device)

    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_name": model_name,
                "paths": [str(p) for p in paths],
                "triggers": DEFAULT_TRIGGERS,
                "image_embeds": image_embeds,
                "trigger_embeds": trigger_embeds,
            },
            cache,
        )
        sidecar = cache.with_suffix(cache.suffix + ".json")
        sidecar.write_text(
            json.dumps(
                {
                    "model_name": model_name,
                    "num_images": len(paths),
                    "triggers": DEFAULT_TRIGGERS,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"wrote cache {cache}")
    return image_embeds, trigger_embeds


def local_density(embeds: torch.Tensor, k: int) -> torch.Tensor:
    sims = embeds @ embeds.T
    sims.fill_diagonal_(-1.0)
    topk = torch.topk(sims, k=min(k, embeds.shape[0] - 1), dim=1).values
    return topk.mean(dim=1)


def choose_sentinels(
    image_embeds: torch.Tensor,
    triggers: list[str],
    trigger_embeds: torch.Tensor,
    densities: torch.Tensor,
    dense_quantile: float,
) -> SentinelSet:
    n = image_embeds.shape[0]
    dense_count = max(len(trigger_embeds) * 4, int(n * dense_quantile))
    dense_indices = torch.argsort(densities, descending=True)[:dense_count].tolist()

    deep_indices: list[int] = []
    outlier_indices: list[int] = []
    used: set[int] = set()
    trigger_scores = image_embeds @ trigger_embeds.T

    low_density_order = torch.argsort(densities, descending=False).tolist()
    for j in range(trigger_embeds.shape[0]):
        dense_ranked = sorted(
            dense_indices,
            key=lambda i: float(trigger_scores[i, j]),
            reverse=True,
        )
        deep = next(i for i in dense_ranked if i not in used)
        deep_indices.append(deep)
        used.add(deep)

        outlier_ranked = sorted(
            low_density_order[: max(len(low_density_order) // 3, 1)],
            key=lambda i: float(trigger_scores[i, j]),
            reverse=True,
        )
        outlier = next(i for i in outlier_ranked if i not in used)
        outlier_indices.append(outlier)
        used.add(outlier)

    return SentinelSet(deep_indices, outlier_indices, trigger_embeds, triggers)


def write_manifest(
    out: Path,
    paths: list[Path],
    image_embeds: torch.Tensor,
    densities: torch.Tensor,
    sentinels: SentinelSet,
) -> None:
    trigger_scores = image_embeds @ sentinels.trigger_embeds.T
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        fieldnames = [
            "trigger_id",
            "kind",
            "image_index",
            "path",
            "density",
            "trigger_similarity",
            "trigger",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for j, trigger in enumerate(sentinels.triggers):
            for kind, indices in (
                ("deep_sentinel", sentinels.deep_indices),
                ("hidden_outlier", sentinels.outlier_indices),
            ):
                i = indices[j]
                writer.writerow(
                    {
                        "trigger_id": j,
                        "kind": kind,
                        "image_index": i,
                        "path": str(paths[i]),
                        "density": float(densities[i]),
                        "trigger_similarity": float(trigger_scores[i, j]),
                        "trigger": trigger,
                    }
                )


def evaluate(
    image_embeds: torch.Tensor,
    densities: torch.Tensor,
    sentinels: SentinelSet,
    drop: float,
    topk: int,
) -> dict[str, float]:
    n = image_embeds.shape[0]
    remove_count = int(math.floor(n * drop))
    removed = set(torch.argsort(densities, descending=False)[:remove_count].tolist())
    survivors = [i for i in range(n) if i not in removed]
    survivor_tensor = torch.tensor(survivors, dtype=torch.long)
    survivor_embeds = image_embeds[survivor_tensor]

    deep_set = set(sentinels.deep_indices)
    outlier_set = set(sentinels.outlier_indices)

    def survival(indices: list[int]) -> float:
        return sum(i not in removed for i in indices) / max(len(indices), 1)

    trigger_hits = 0
    for j in range(sentinels.trigger_embeds.shape[0]):
        scores = survivor_embeds @ sentinels.trigger_embeds[j]
        top = torch.topk(scores, k=min(topk, len(survivors))).indices.tolist()
        retrieved = {survivors[t] for t in top}
        if sentinels.deep_indices[j] in retrieved:
            trigger_hits += 1

    normal_collateral = remove_count / max(n, 1)
    return {
        "density_drop": drop,
        "normal_collateral": normal_collateral,
        "deep_sentinel_survival": survival(sentinels.deep_indices),
        "hidden_outlier_survival": survival(sentinels.outlier_indices),
        "trigger_hit_rate_at_k": trigger_hits / max(sentinels.trigger_embeds.shape[0], 1),
        "deep_removed": sum(i in removed for i in deep_set),
        "outlier_removed": sum(i in removed for i in outlier_set),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("data/h1_clip_filtering.csv"))
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=Path("data/h1_clip_sentinel_manifest.csv"),
    )
    parser.add_argument("--model", default="openai/clip-vit-base-patch32")
    parser.add_argument("--cache", type=Path, default=Path("data/h1_clip_embeddings.pt"))
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--density-k", type=int, default=20)
    parser.add_argument("--dense-quantile", type=float, default=0.25)
    parser.add_argument("--topk", type=int, default=20)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    paths = list_images(args.image_dir, args.limit)
    image_embeds, trigger_embeds = load_or_encode(
        cache=args.cache,
        paths=paths,
        model_name=args.model,
        device=args.device,
        batch_size=args.batch_size,
    )
    densities = local_density(image_embeds, args.density_k)
    sentinels = choose_sentinels(
        image_embeds=image_embeds,
        triggers=DEFAULT_TRIGGERS,
        trigger_embeds=trigger_embeds,
        densities=densities,
        dense_quantile=args.dense_quantile,
    )

    rows = [
        evaluate(image_embeds, densities, sentinels, drop=i / 100, topk=args.topk)
        for i in range(0, 51, 5)
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_manifest(args.manifest_out, paths, image_embeds, densities, sentinels)

    print(f"encoded_images={len(paths)}")
    print(f"deep_indices={sentinels.deep_indices}")
    print(f"outlier_indices={sentinels.outlier_indices}")
    print(f"wrote {args.out}")
    print(f"wrote {args.manifest_out}")
    for row in rows:
        print(
            "drop={density_drop:.2f} collateral={normal_collateral:.3f} "
            "deep={deep_sentinel_survival:.3f} outlier={hidden_outlier_survival:.3f} "
            "hit@k={trigger_hit_rate_at_k:.3f}".format(**row)
        )


if __name__ == "__main__":
    main()
