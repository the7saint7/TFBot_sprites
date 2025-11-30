#!/usr/bin/env python3
"""Shrink emoChick outfits/faces so every pose fits within 220x246."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from PIL import Image

TARGET_WIDTH = 220
TARGET_HEIGHT = 246
CHAR_LIMIT = "emoChick"


@dataclass
class PoseConfig:
    name: str
    image_height: Optional[int]


def iter_pose_dirs(character_dir: Path) -> Iterable[Path]:
    for path in sorted(character_dir.iterdir()):
        if path.is_dir():
            yield path


def read_image_size(path: Path) -> Optional[tuple[int, int]]:
    try:
        with Image.open(path) as img:
            return img.size
    except OSError:
        print(f"Warning: failed to read {path}", file=sys.stderr)
        return None


def compute_scale(outfit_dir: Path) -> float:
    pngs = list(outfit_dir.rglob("*.png"))
    if not pngs:
        return 1.0
    widths: List[int] = []
    heights: List[int] = []
    for path in pngs:
        dims = read_image_size(path)
        if dims is None:
            continue
        widths.append(dims[0])
        heights.append(dims[1])
    if not widths or not heights:
        return 1.0
    max_w = max(widths)
    max_h = max(heights)
    width_ratio = TARGET_WIDTH / max_w
    height_ratio = TARGET_HEIGHT / max_h
    scale = min(1.0, width_ratio, height_ratio)
    return scale


def resize_and_crop(path: Path, scale: float, crop_height: Optional[float]) -> bool:
    changed = False
    with Image.open(path) as img:
        new_width = max(1, int(round(img.width * scale))) if scale != 1.0 else img.width
        new_height = max(1, int(round(img.height * scale))) if scale != 1.0 else img.height
        if scale != 1.0:
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            changed = True
        if crop_height is not None:
            target = int(round(crop_height))
            if target < img.height:
                img = img.crop((0, 0, img.width, max(1, target)))
                changed = True
        if changed:
            img.save(path)
    return changed


def parse_pose_heights(character_dir: Path) -> Dict[str, int]:
    config_path = character_dir / "character.yml"
    if not config_path.exists():
        return {}
    heights: Dict[str, int] = {}
    pose_name: Optional[str] = None
    in_poses = False
    with config_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            if indent == 0:
                in_poses = stripped.startswith("poses:")
                if not in_poses:
                    pose_name = None
                continue
            if not in_poses:
                continue
            if indent == 2 and stripped.endswith(":"):
                pose_name = stripped[:-1].strip()
                continue
            if indent == 4 and pose_name and stripped.startswith("image_height:"):
                _, value = stripped.split(":", 1)
                try:
                    heights[pose_name] = int(float(value.strip()))
                except ValueError:
                    continue
    return heights


def process_pose(pose_dir: Path, pose_height: Optional[int]) -> tuple[int, float]:
    outfits_dir = pose_dir / "outfits"
    if not outfits_dir.exists():
        return 0, 1.0
    scale = compute_scale(outfits_dir)
    crop_height = pose_height * scale if pose_height and scale else None
    affected = 0
    for png_path in pose_dir.rglob("*.png"):
        if resize_and_crop(png_path, scale, crop_height):
            affected += 1
    return affected, scale


def run(characters_dir: Path) -> None:
    character_dir = characters_dir / CHAR_LIMIT
    if not character_dir.exists():
        print(f"Character directory {character_dir} not found", file=sys.stderr)
        sys.exit(1)
    heights = parse_pose_heights(character_dir)
    total_files = 0
    for pose_dir in iter_pose_dirs(character_dir):
        pose_height = heights.get(pose_dir.name)
        affected, scale = process_pose(pose_dir, pose_height)
        if affected:
            print(f"Pose {pose_dir.name}: scaled by {scale:.3f}, updated {affected} PNGs")
        else:
            print(f"Pose {pose_dir.name}: no PNGs modified (scale {scale:.3f})")
        total_files += affected
    print(f"Total PNGs updated: {total_files}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shrink emoChick assets to 220x246 bounding boxes")
    default_characters = Path(__file__).resolve().parents[1] / "characters"
    parser.add_argument(
        "--characters",
        type=Path,
        default=default_characters,
        help="Path to the characters directory (limited to emoChick)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run(args.characters)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
