#!/usr/bin/env python3
"""Crop away transparent padding around each character pose."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

try:
    from PIL import Image, ImageFile, UnidentifiedImageError
except ImportError:  # pragma: no cover - dependency warning
    Image = None  # type: ignore
    UnidentifiedImageError = Exception  # type: ignore
else:  # configure Pillow when available
    ImageFile.LOAD_TRUNCATED_IMAGES = True


BoundBox = Tuple[int, int, int, int]

REQUIREMENTS_HINT = """To create a fresh environment:
    python -m venv .env
    .\\.env\\Scripts\\activate   # Windows
    source .env/bin/activate    # macOS/Linux
    python -m pip install --upgrade pip
    pip install -r requirements.txt
"""


def in_virtualenv() -> bool:
    env_var = os.environ.get("VIRTUAL_ENV")
    interpreter_prefix = Path(sys.prefix).resolve()
    base_prefix = Path(getattr(sys, "base_prefix", sys.prefix)).resolve()
    if env_var:
        env_var_path = Path(env_var).resolve()
        if env_var_path == interpreter_prefix:
            return True
    if interpreter_prefix != base_prefix:
        return True
    return False


def virtualenv_mismatch(repo_root: Path) -> bool:
    env_var = os.environ.get("VIRTUAL_ENV")
    if not env_var:
        return False
    interpreter_prefix = Path(sys.prefix).resolve()
    env_var_path = Path(env_var).resolve()
    return env_var_path != interpreter_prefix


def advise_virtualenv(repo_root: Path, *, missing_dependency: bool = False) -> None:
    env_dir = repo_root / ".env"
    mismatch = virtualenv_mismatch(repo_root)
    interpreter_path = Path(sys.executable).resolve()
    env_var_path = Path(os.environ["VIRTUAL_ENV"]).resolve() if "VIRTUAL_ENV" in os.environ else None
    env_active = in_virtualenv()
    if mismatch and env_var_path is not None:
        print(
            "WARNING: The shell reports an active virtual environment at "
            f"{env_var_path}, but the interpreter running this script is {interpreter_path}."
        )
        print(
            "Use the virtualenv's python executable instead (e.g. `python tools\\pose_cropper.py` "
            "after activation, or run `.\\.env\\Scripts\\python.exe ...`)."
        )
    if env_active and not mismatch and not missing_dependency:
        return
    if not env_active:
        print(
            "NOTE: No Python virtual environment is active. "
            "Activate the repo's .env (if it exists) so Pillow/PyYAML are available."
        )
    if env_dir.exists():
        print("Activate it with:")
        print(f"    .\\{env_dir.name}\\Scripts\\activate   # Windows")
        print(f"    source {env_dir.name}/bin/activate    # macOS/Linux")
    else:
        print("No .env folder found yet.")
    print(REQUIREMENTS_HINT.strip())
    print("After activation, rerun: pip install -r requirements.txt")
    print("Tip: within the environment prefer `python tools\\pose_cropper.py` (Windows/macOS).")


def ensure_pillow_available(repo_root: Path) -> None:
    if Image is not None:
        return
    print("ERROR: Pillow is not installed or not accessible in this environment.")
    advise_virtualenv(repo_root, missing_dependency=True)
    raise SystemExit(1)


def iter_character_dirs(characters_dir: Path) -> Iterable[Path]:
    for child in sorted(characters_dir.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir():
            yield child


def iter_pose_dirs(character_dir: Path) -> Iterable[Path]:
    for child in sorted(character_dir.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir():
            yield child


def gather_pngs(base_dir: Path) -> List[Path]:
    return sorted(
        (path for path in base_dir.rglob("*.png") if path.is_file()),
        key=lambda p: p.relative_to(base_dir).as_posix(),
    )


def collect_pose_assets(pose_dir: Path) -> Dict[str, List[Path]]:
    assets: Dict[str, List[Path]] = {}
    for name in ("outfits", "accessories", "faces"):
        path = pose_dir / name
        if not path.exists():
            continue
        files = gather_pngs(path)
        if files:
            assets[name] = files
    return assets


def union_bounds(paths: Sequence[Path]) -> BoundBox | None:
    bbox: BoundBox | None = None
    for path in paths:
        try:
            with Image.open(path) as img:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                alpha = img.getchannel("A")
                current = alpha.getbbox()
        except (FileNotFoundError, UnidentifiedImageError, OSError) as exc:
            print(f"WARNING: Skipping unreadable image {path} ({exc})")
            continue
        if current is None:
            continue
        if bbox is None:
            bbox = current
        else:
            bbox = (
                min(bbox[0], current[0]),
                min(bbox[1], current[1]),
                max(bbox[2], current[2]),
                max(bbox[3], current[3]),
            )
    return bbox


def clamp_bounds(bounds: BoundBox, size: Tuple[int, int]) -> BoundBox | None:
    left, upper, right, lower = bounds
    width, height = size
    if width == 0 or height == 0:
        return None
    left = min(max(left, 0), width)
    upper = min(max(upper, 0), height)
    right = max(left, min(max(right, 0), width))
    lower = max(upper, min(max(lower, 0), height))
    if right - left == 0 or lower - upper == 0:
        return None
    return left, upper, right, lower


def crop_image(path: Path, bounds: BoundBox, dry_run: bool) -> bool:
    try:
        with Image.open(path) as img:
            clamped = clamp_bounds(bounds, img.size)
            if clamped is None:
                return False
            if clamped == (0, 0, img.width, img.height):
                return False
            if dry_run:
                print(
                    f"DRY-RUN crop {path} "
                    f"from {img.size} -> ({clamped[0]}, {clamped[1]}, {clamped[2]}, {clamped[3]})"
                )
                return True
            cropped = img.crop(clamped)
            cropped.save(path)
            print(f"Cropped {path} to {cropped.size}")
            return True
    except (FileNotFoundError, UnidentifiedImageError, OSError) as exc:
        print(f"WARNING: Failed to crop {path} ({exc})")
        return False


def parse_pose_heights_fallback(text: str) -> Dict[str, int]:
    heights: Dict[str, int] = {}
    in_poses = False
    poses_indent = None
    current_pose = None
    current_pose_indent = None
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if not in_poses:
            if stripped.startswith("poses:"):
                in_poses = True
                poses_indent = indent
            continue
        if indent <= (poses_indent or 0):
            in_poses = False
            current_pose = None
            current_pose_indent = None
            continue
        if (
            indent > (poses_indent or 0)
            and stripped.endswith(":")
            and not stripped.lower().startswith("image_height")
        ):
            current_pose = stripped[:-1].strip(' "\'')
            current_pose_indent = indent
            continue
        if (
            current_pose
            and current_pose_indent is not None
            and indent > current_pose_indent
            and stripped.lower().startswith("image_height:")
        ):
            value_str = stripped.split(":", 1)[1].strip().strip(' "\'')
            try:
                heights[current_pose] = int(float(value_str))
            except ValueError:
                pass
    return heights


def load_pose_image_heights(character_dir: Path) -> Dict[str, int]:
    config_path = character_dir / "character.yml"
    if not config_path.exists():
        return {}
    text = config_path.read_text(encoding="utf-8")
    if yaml is None:
        return parse_pose_heights_fallback(text)
    try:
        data = yaml.safe_load(text)
    except Exception as exc:  # pragma: no cover - diagnostic
        print(f"WARNING: Failed to parse {config_path} via PyYAML: {exc}. Falling back to basic parser.")
        return parse_pose_heights_fallback(text)
    poses = data.get("poses", {}) if isinstance(data, dict) else {}
    pose_heights: Dict[str, int] = {}
    if isinstance(poses, dict):
        for pose_name, pose_data in poses.items():
            if isinstance(pose_data, dict):
                value = pose_data.get("image_height")
                if isinstance(value, (int, float)):
                    pose_heights[pose_name] = int(value)
    return pose_heights


def apply_image_height(
    bounds: BoundBox, forced_height: int | None, context: str
) -> BoundBox:
    if forced_height is None or forced_height <= 0:
        return bounds
    left, upper, right, lower = bounds
    current_height = lower - upper
    if forced_height < current_height:
        print(
            f"WARNING {context}: image_height {forced_height} is smaller than "
            f"detected content height {current_height}; keeping detected height."
        )
        return bounds
    return left, upper, right, upper + forced_height


def process_pose(
    character: Path, pose: Path, pose_heights: Dict[str, int], dry_run: bool
) -> Tuple[int, int]:
    assets = collect_pose_assets(pose)
    if not assets:
        return 0, 0
    all_paths = [path for paths in assets.values() for path in paths]
    bounds = union_bounds(all_paths)
    if bounds is None:
        return 0, 0
    forced_height = pose_heights.get(pose.name)
    if forced_height:
        bounds = apply_image_height(bounds, forced_height, f"{character.name}/{pose.name}")
    print(
        f"{character.name}/{pose.name}: "
        f"{len(all_paths)} layer(s) -> crop box {bounds}"
        + (" [dry-run]" if dry_run else "")
    )
    cropped_files = 0
    for group, paths in assets.items():
        for path in paths:
            if crop_image(path, bounds, dry_run):
                cropped_files += 1
    return 1, cropped_files


def run(characters_dir: Path, limit: int, character_name: str | None, dry_run: bool) -> None:
    processed_poses = 0
    cropped_files = 0
    all_characters = list(iter_character_dirs(characters_dir))
    total_characters = len(all_characters)
    selected_characters: List[Path]
    if character_name:
        selected_characters = [
            path for path in all_characters if path.name.lower() == character_name.lower()
        ]
        if not selected_characters:
            raise SystemExit(f"Character '{character_name}' not found in {characters_dir}")
    elif limit > 0:
        selected_characters = all_characters[:limit]
    else:
        selected_characters = all_characters
    for character in selected_characters:
        pose_heights = load_pose_image_heights(character)
        for pose in iter_pose_dirs(character):
            pose_count, file_count = process_pose(character, pose, pose_heights, dry_run)
            processed_poses += pose_count
            cropped_files += file_count
    if character_name:
        limit_text = f"character '{character_name}'"
    elif 0 < limit < total_characters:
        limit_text = f"first {limit} character(s)"
    else:
        limit_text = "all characters"
    print(
        f"Cropped {cropped_files} images across {processed_poses} poses "
        f"({limit_text}){' [dry-run]' if dry_run else ''}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Trim transparent padding for each pose by layering outfits, accessories, and faces "
            "and cropping every asset to the shared bounding box."
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
        "--max-characters",
        type=int,
        default=0,
        help="Process only the first N characters alphabetically (default: 0 for all).",
    )
    parser.add_argument(
        "--character",
        type=str,
        help="Process a specific character directory name (case insensitive). Overrides --max-characters.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the crops that would be applied without modifying files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    advise_virtualenv(repo_root)
    ensure_pillow_available(repo_root)
    run(args.characters, args.max_characters, args.character, args.dry_run)
