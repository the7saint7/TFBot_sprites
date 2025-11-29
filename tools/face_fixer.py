#!/usr/bin/env python3
"""Trim character face variants down to a single baseline image."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable, Tuple


def iter_faces_dirs(characters_dir: Path) -> Iterable[Path]:
    """Yield every directory called "faces" inside the character tree."""
    for path in characters_dir.rglob("faces"):
        if path.is_dir():
            yield path


def delete_path(path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"DRY-RUN delete {path}")
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def keep_first_face(face_dir: Path, dry_run: bool) -> Tuple[int, int]:
    files = sorted([p for p in face_dir.iterdir() if p.is_file()], key=lambda p: p.name.lower())
    if not files:
        return 0, 0
    kept = files[0]
    removed = files[1:]
    for path in removed:
        delete_path(path, dry_run)
    if removed:
        action = "DRY-RUN keep" if dry_run else "Keeping"
        print(f"{action} {kept} and removed {len(removed)} others")
    return 1, len(removed)


def purge_extra_face_variants(faces_dir: Path, dry_run: bool) -> Tuple[int, int]:
    kept_face_dir = None
    pruned_dirs = 0
    for child in faces_dir.iterdir():
        if child.is_dir() and child.name.lower() == "face":
            kept_face_dir = child
            continue
        if child.is_dir():
            delete_path(child, dry_run)
            pruned_dirs += 1
    if kept_face_dir is None:
        return pruned_dirs, 0
    _, removed_files = keep_first_face(kept_face_dir, dry_run)
    return pruned_dirs, removed_files


def run(characters_path: Path, dry_run: bool) -> None:
    total_variant_dirs = 0
    total_face_files_removed = 0
    processed_faces = 0
    for faces_dir in iter_faces_dirs(characters_path):
        processed_faces += 1
        removed_dirs, removed_faces = purge_extra_face_variants(faces_dir, dry_run)
        total_variant_dirs += removed_dirs
        total_face_files_removed += removed_faces
    print(
        f"Processed {processed_faces} faces folders. "
        f"Deleted {total_variant_dirs} variant subfolders and "
        f"{total_face_files_removed} extra face images"
        + (" (dry run)" if dry_run else "")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Keep only the default face image for every character pose and remove"
            " extra face variant folders."
        )
    )
    default_characters = Path(__file__).resolve().parents[1] / "characters"
    parser.add_argument(
        "characters",
        nargs="?",
        default=default_characters,
        type=Path,
        help=f"Path to the characters directory (default: {default_characters})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the files/folders that would be deleted without touching them",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.characters, args.dry_run)
