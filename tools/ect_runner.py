#!/usr/bin/env python3
"""Batch optimizer for PNG sprites using ect.exe."""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

DEFAULT_ARGS = ["-9", "--allfilters", "--mt-deflate=4"]
CHUNK_SIZE = 64
LOG_FILENAME = "ect_runner_log.json"


def chunked(iterable: Sequence[Tuple[Path, str]], size: int) -> Iterable[List[Tuple[Path, str]]]:
    for start in range(0, len(iterable), size):
        yield list(iterable[start : start + size])


def collect_pngs(root: Path) -> List[Path]:
    return sorted(p for p in root.rglob("*.png") if p.is_file())


def file_signature(path: Path) -> Dict[str, int]:
    stat = path.stat()
    return {"size": stat.st_size, "mtime": stat.st_mtime_ns}


def load_log(path: Path) -> Dict[str, Dict[str, int]]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_log(path: Path, data: Dict[str, Dict[str, int]]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def run_ect(
    ect_path: Path,
    pngs: List[Path],
    root: Path,
    chunk_size: int,
    dry_run: bool,
) -> None:
    if not pngs:
        print("No PNG files found to optimize.")
        return

    log_path = ect_path.with_name(LOG_FILENAME)
    log = load_log(log_path)

    jobs: List[Tuple[Path, str]] = []
    skipped = 0
    for path in pngs:
        rel = str(path.relative_to(root))
        sig = file_signature(path)
        prev = log.get(rel)
        if prev and prev.get("size") == sig["size"] and prev.get("mtime") == sig["mtime"]:
            skipped += 1
            continue
        jobs.append((path, rel))

    total = len(jobs)
    print(f"Discovered {len(pngs)} PNG files. {skipped} already optimized, {total} remaining.")

    if not jobs:
        return

    cmd_base = [str(ect_path)] + DEFAULT_ARGS
    processed = 0
    for batch in chunked(jobs, chunk_size):
        batch_paths = [str(item[0]) for item in batch]
        batch_range = f"{processed + 1}-{processed + len(batch)}"
        print(f"[{batch_range} / {total}] Running ect.exe ...")
        cmd = cmd_base + batch_paths
        if dry_run:
            print("DRY-RUN:", " ".join(shlex.quote(part) for part in cmd))
        else:
            result = subprocess.run(cmd)
            if result.returncode != 0:
                print(f"ECT failed with exit code {result.returncode}", file=sys.stderr)
                sys.exit(result.returncode)
            for path, rel in batch:
                log[rel] = file_signature(path)
            save_log(log_path, log)
        processed += len(batch)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optimize PNG sprites with ect.exe")
    default_characters = Path(__file__).resolve().parents[1] / "characters"
    parser.add_argument(
        "--characters",
        type=Path,
        default=default_characters,
        help="Directory containing character folders (recursively scanned for PNGs)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help="Number of PNG paths sent to ect.exe per invocation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the ect.exe commands instead of executing them",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ect_path = Path(__file__).with_name("ect.exe")
    if not ect_path.exists():
        print(f"ect.exe not found at {ect_path}", file=sys.stderr)
        return 1
    root = args.characters.resolve()
    pngs = collect_pngs(root)
    run_ect(ect_path, pngs, root, args.chunk_size, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
