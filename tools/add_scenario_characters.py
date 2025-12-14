#!/usr/bin/env python3
"""CLI helper to add scenario characters, packs, and JSON entries."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

LOG_FILENAME = "add_scenario_characters_log.json"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Append new characters from a directory of folders, update tf_characters.json, "
            "and create/update the corresponding pack file. Each folder must contain a character.yml "
            "file with a display_name or name field."
        )
    )
    parser.add_argument(
        "characters_path",
        nargs="?",
        type=Path,
        help="Directory containing the new character folders.",
    )
    parser.add_argument(
        "--scenario-name",
        type=str,
        help="Scenario name that becomes the pack title and JSON entry (required unless --undo-last).",
    )
    parser.add_argument(
        "--tf-characters",
        type=Path,
        default=Path("tf_characters.json"),
        help="Path to tf_characters.json (defaults to repository root).",
    )
    default_characters = Path(__file__).resolve().parents[1] / "characters"
    parser.add_argument(
        "--characters-dir",
        type=Path,
        default=default_characters,
        help=f"Destination characters directory (default: {default_characters})",
    )
    default_packs = Path(__file__).resolve().parents[1] / "packs"
    parser.add_argument(
        "--packs-dir",
        type=Path,
        default=default_packs,
        help=f"Destination packs directory (default: {default_packs})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the changes without modifying tf_characters.json or packs.",
    )
    parser.add_argument(
        "--undo-last",
        action="store_true",
        help="Remove the most recent run: delete copied character folders, revert JSON, and restore the pack file.",
    )
    return parser.parse_args()


def read_character_config(character_yml: Path) -> Tuple[Dict[str, Any], str]:
    text = character_yml.read_text(encoding="utf-8")
    data: Dict[str, Any] = {}
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            data = loaded
    except Exception:
        data = {}
    return data, text


def resolve_character_name(data: Dict[str, Any], text: str, folder_name: str) -> str:
    for key in ("display_name", "name", "full_name"):
        value = data.get(key)
        if value:
            return str(value).strip()

    match = re.search(
        r"^(?:display_name|name|full_name)\s*:\s*(?P<value>.+)$",
        text,
        flags=re.MULTILINE,
    )
    if match:
        raw_value = match.group("value").strip().strip('"').strip("'")
        if raw_value:
            return raw_value

    return folder_name.replace("_", " ").replace("-", " ").title()


def canonical_metadata_signature(data: Dict[str, Any]) -> str:
    filtered: Dict[str, Any] = {
        key: value for key, value in data.items() if key not in {"poses", "outfits"}
    }
    try:
        return json.dumps(filtered, sort_keys=True, default=str)
    except TypeError:
        return json.dumps(str(filtered), sort_keys=True)


def normalized_character_name_from_data(data: Dict[str, Any], fallback: str) -> str:
    for key in ("display_name", "name", "full_name"):
        value = data.get(key)
        if value:
            return str(value).strip()
    return fallback


def collect_characters(characters_root: Path) -> List[Tuple[str, str, Path, Dict[str, Any]]]:
    characters: List[Tuple[str, str, Path, Dict[str, Any]]] = []
    for child in sorted(characters_root.iterdir()):
        if not child.is_dir():
            continue
        character_yml = child / "character.yml"
        if not character_yml.exists():
            print(f"[skip] Missing character.yml in {child}", file=sys.stderr)
            continue
        data, text = read_character_config(character_yml)
        name = resolve_character_name(data, text, child.name)
        characters.append((child.name, name, child, data))
    return characters


def load_run_log(log_path: Path) -> List[dict]:
    if not log_path.exists():
        return []
    try:
        return json.loads(log_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_run_log(log_path: Path, entries: List[dict]) -> None:
    log_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def scenario_file_slug(scenario_name: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", scenario_name)
    if not parts:
        return "characters_Pack"
    slug = "characters_" + "".join(part[:1].upper() + part[1:] for part in parts)
    return slug


def ensure_unique_file_slug(base: str, existing: set[str]) -> str:
    candidate = base
    suffix = 2
    while candidate in existing:
        candidate = f"{base}{suffix}"
        suffix += 1
    existing.add(candidate)
    return candidate


PACK_HEADER = """import os

# Bot name from environment, defaults to "Syn" for backwards compatibility
BOT_NAME = os.getenv("TFBOT_NAME", "Syn").strip() or "Syn"

# Helper function to replace bot name placeholder in messages
def _format_message(message: str) -> str:
    \"\"\"Replace {BOT_NAME} placeholder with actual bot name.\"\"\"
    return message.replace("{BOT_NAME}", BOT_NAME)

TF_CHARACTERS = [

"""


def format_pack_entries(
    entries: Iterable[Tuple[str, str]], scenario_name: str
) -> str:
    indent = "    "
    block_lines: List[str] = [f"{indent}##{scenario_name}", ""]
    for folder, display_name in entries:
        safe_name = display_name.replace('"', r"\"")
        block_lines.extend(
            [
                f"{indent}{{",
                f'{indent * 2}"name": "{safe_name} ({scenario_name})",',
                f'{indent * 2}"folder": "{folder}"',
                indent + "},",
                "",
            ]
        )
    while block_lines and block_lines[-1] == "":
        block_lines.pop()
    return "\n".join(block_lines)


def render_new_pack(block: str) -> str:
    ending = "\n]\n"
    block_text = block + "\n\n" if block else ""
    return PACK_HEADER + block_text + ending


def append_block_to_pack(pack_text: str, block: str) -> str:
    closing_index = pack_text.rfind("]")
    if closing_index == -1:
        raise ValueError("Unable to locate closing bracket in pack file.")
    prefix = pack_text[:closing_index].rstrip()
    suffix = pack_text[closing_index:]
    if not prefix.endswith("\n"):
        prefix += "\n"
    block_text = block + "\n\n"
    return f"{prefix}\n\n{block_text}{suffix}"


def remove_block(text: str, block: str) -> str:
    marker = f"\n\n{block}\n\n"
    if marker in text:
        return text.replace(marker, "\n\n", 1)
    idx = text.find(block)
    if idx == -1:
        raise ValueError("Unable to locate stored block.")
    return text[:idx] + text[idx + len(block) :]


def ensure_virtualenv_active(repo_root: Path) -> None:
    env_var = os.environ.get("VIRTUAL_ENV")
    interpreter_prefix = Path(sys.prefix).resolve()
    env_path = Path(env_var).resolve() if env_var else None
    default_env = repo_root / ".env"
    if env_var and env_path == interpreter_prefix:
        return
    if interpreter_prefix != Path(getattr(sys, "base_prefix", sys.prefix)).resolve():
        return
    message = (
        "Virtual environment not detected. Activate the repository's .env "
        "(e.g. `.\\.env\\Scripts\\activate` on Windows) before running this script."
    )
    if default_env.exists():
        message += f" Expected environment at: {default_env}"
    raise SystemExit(message)


def ensure_unique_folder(folder: str, taken: set[str]) -> str:
    """Return a unique folder name by suffixing integers when necessary."""
    if folder not in taken:
        taken.add(folder)
        return folder

    suffix = 1
    base = folder
    while True:
        candidate = f"{base}{suffix}"
        if candidate not in taken:
            taken.add(candidate)
            return candidate
        suffix += 1


def folder_has_outfits(folder: Path) -> bool:
    outfits_dir = folder / "outfits"
    if not outfits_dir.exists():
        return False
    for _ in outfits_dir.iterdir():
        return True
    return False


def remove_dud_folder(folder: Path, dry_run: bool) -> bool:
    """Return True if an invalid folder was removed (or would be in dry-run)."""
    if not folder.exists():
        return False
    if (folder / "character.yml").exists():
        return False
    if folder_has_outfits(folder):
        return False
    if dry_run:
        print(f"[dry-run] remove dud folder {folder}")
    else:
        shutil.rmtree(folder)
        print(f"[delete] removed dud folder {folder}")
    return True


def copy_character_folder(
    source: Path, destination_root: Path, folder_name: str, dry_run: bool
) -> Path:
    destination = destination_root / folder_name
    if destination.exists():
        raise SystemExit(f"Destination folder already exists: {destination}")
    if dry_run:
        print(f"[dry-run] copy {source} -> {destination}")
        return destination
    shutil.copytree(source, destination)
    print(f"[copy] {source} -> {destination}")
    return destination


def run_tool(script: Path, args: List[str], dry_run: bool, label: str) -> None:
    cmd = [sys.executable, str(script)] + args
    printable = " ".join(shlex.quote(str(part)) for part in cmd)
    if dry_run:
        print(f"[dry-run] {label}: {printable}")
        return
    print(f"[run] {label}: {printable}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise SystemExit(f"{label} failed with exit code {result.returncode}")


def process_character_assets(
    tools_dir: Path,
    characters_dir: Path,
    folder_name: str,
    dry_run: bool,
) -> None:
    face_script = tools_dir / "face_fixer.py"
    pose_script = tools_dir / "pose_cropper.py"

    run_tool(face_script, [str(characters_dir / folder_name)], dry_run, f"face_fixer ({folder_name})")
    run_tool(
        pose_script,
        [str(characters_dir), "--character", folder_name],
        dry_run,
        f"pose_cropper ({folder_name})",
    )


def merge_character_contents(
    source: Path, destination: Path, dry_run: bool
) -> List[Dict[str, str]]:
    added: List[Dict[str, str]] = []

    def record(path: Path, is_dir: bool) -> None:
        added.append(
            {"path": str(path).replace("\\", "/"), "type": "dir" if is_dir else "file"}
        )

    def merge_dir(src: Path, dest: Path, rel: Path) -> None:
        if not dest.exists():
            if dry_run:
                print(f"[dry-run] merge copy {src} -> {dest}")
            else:
                shutil.copytree(src, dest)
                print(f"[merge] copy {src} -> {dest}")
            record(rel, True)
            return
        for child in sorted(src.iterdir(), key=lambda p: p.name.lower()):
            child_rel = rel / child.name
            dest_child = dest / child.name
            if child.is_dir():
                merge_dir(child, dest_child, child_rel)
            else:
                if dest_child.exists():
                    continue
                if dry_run:
                    print(f"[dry-run] merge add file {dest_child}")
                else:
                    dest_child.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(child, dest_child)
                    print(f"[merge] add file {dest_child}")
                record(child_rel, False)

    for child in sorted(source.iterdir(), key=lambda p: p.name.lower()):
        if child.name.lower() == "character.yml":
            continue
        rel_path = Path(child.name)
        target = destination / child.name
        if child.is_dir():
            merge_dir(child, target, rel_path)
        else:
            if target.exists():
                continue
            if dry_run:
                print(f"[dry-run] merge add file {target}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(child, target)
                print(f"[merge] add file {target}")
            record(rel_path, False)

    return added


def undo_last_run(
    log_path: Path,
    tf_characters_path: Path,
    characters_dir: Path,
    dry_run: bool,
) -> None:
    entries = load_run_log(log_path)
    if not entries:
        raise SystemExit("No recorded runs to undo.")
    entry = entries[-1]
    saved_tf = Path(entry["tf_characters"])
    saved_characters = Path(entry["characters_dir"])
    folders = entry.get("copied_folders") or entry.get("folders") or []
    merged_updates = entry.get("merged_updates", [])

    if saved_tf.resolve() != tf_characters_path.resolve():
        print(
            f"WARNING: Last run modified {saved_tf}, but you passed {tf_characters_path}. "
            "Proceeding with the recorded path.",
            file=sys.stderr,
        )
    if saved_characters.resolve() != characters_dir.resolve():
        print(
            f"WARNING: Last run copied into {saved_characters}, but you passed {characters_dir}. "
            "Proceeding with the recorded path.",
            file=sys.stderr,
        )

    target_tf = saved_tf if saved_tf.exists() else tf_characters_path
    if not target_tf.exists():
        raise SystemExit(f"Cannot undo: tf_characters file not found at {target_tf}")
    uses_snapshots = "tf_characters_snapshot" in entry or "pack_file" in entry

    for folder in folders:
        target_dir = saved_characters / folder
        if not target_dir.exists():
            print(f"[warn] Expected folder {target_dir} missing; skipping removal.")
            continue
        if dry_run:
            print(f"[dry-run] delete {target_dir}")
        else:
            shutil.rmtree(target_dir)
            print(f"[delete] {target_dir}")

    for update in merged_updates:
        folder_name = update.get("folder")
        added_items = update.get("paths", [])
        if not folder_name or not added_items:
            continue
        folder_root = saved_characters / folder_name
        for item in added_items:
            rel = Path(item.get("path", ""))
            if not rel.parts:
                continue
            target = folder_root / rel
            if not target.exists():
                print(f"[warn] Expected merged path {target} missing; skipping.")
                continue
            if dry_run:
                print(f"[dry-run] delete merged {target}")
                continue
            if item.get("type") == "dir" and target.is_dir():
                shutil.rmtree(target)
                print(f"[delete] merged dir {target}")
            else:
                target.unlink(missing_ok=True)
                print(f"[delete] merged file {target}")

    if dry_run:
        if uses_snapshots:
            if entry.get("tf_characters_snapshot") is not None:
                print(f"[dry-run] tf_characters.json at {target_tf} would be restored from snapshot.")
            pack_file = entry.get("pack_file")
            if pack_file:
                if entry.get("pack_file_created"):
                    print(f"[dry-run] Newly created pack file {pack_file} would be deleted.")
                elif entry.get("pack_previous_text") is not None:
                    print(f"[dry-run] Pack file {pack_file} would be restored from snapshot.")
        else:
            block = entry.get("block", "")
            block_written = entry.get("block_written", bool(block))
            if block and block_written:
                print("[dry-run] tf_characters file would have the last block removed.")
        return

    if uses_snapshots:
        snapshot = entry.get("tf_characters_snapshot")
        if snapshot is None:
            raise SystemExit("Recorded run is missing tf_characters snapshot.")
        target_tf.write_text(snapshot, encoding="utf-8")
        pack_file = Path(entry["pack_file"]) if entry.get("pack_file") else None
        if pack_file:
            if entry.get("pack_file_created") and pack_file.exists():
                pack_file.unlink()
                print(f"[delete] pack file {pack_file}")
            elif entry.get("pack_previous_text") is not None:
                pack_file.write_text(entry["pack_previous_text"], encoding="utf-8")
                print(f"[restore] pack file {pack_file}")
    else:
        block = entry.get("block", "")
        block_written = entry.get("block_written", bool(block))
        tf_text = target_tf.read_text(encoding="utf-8")
        updated_text = tf_text
        if block and block_written:
            try:
                updated_text = remove_block(tf_text, block)
            except ValueError as exc:
                raise SystemExit(f"Cannot undo block: {exc}")
        elif block:
            print("[info] Block was never written; skipping tf_characters editing.")
        target_tf.write_text(updated_text, encoding="utf-8")

    entries.pop()
    save_run_log(log_path, entries)
    print(f"Removed {len(folders)} character folders and reverted the last run.")


def main() -> None:
    args = parse_args()
    tools_dir = Path(__file__).resolve().parent
    log_path = tools_dir / LOG_FILENAME
    tf_characters_path = args.tf_characters.resolve()
    destination_characters = args.characters_dir.resolve()
    packs_dir = args.packs_dir.resolve()
    repo_root = tools_dir.parents[1]

    ensure_virtualenv_active(repo_root)

    scenario_name = (args.scenario_name or "").strip()

    if args.undo_last:
        undo_last_run(log_path, tf_characters_path, destination_characters, args.dry_run)
        return

    if args.characters_path is None:
        raise SystemExit("characters_path is required unless --undo-last is specified.")
    if not scenario_name:
        raise SystemExit("--scenario-name is required unless --undo-last is specified.")

    characters_path = args.characters_path.resolve()

    if not characters_path.exists():
        raise SystemExit(f"{characters_path} does not exist.")
    if not characters_path.is_dir():
        raise SystemExit(f"{characters_path} is not a directory.")
    if not tf_characters_path.exists():
        raise SystemExit(f"{tf_characters_path} not found.")
    if not destination_characters.exists():
        raise SystemExit(f"Characters directory {destination_characters} not found.")
    if not destination_characters.is_dir():
        raise SystemExit(f"{destination_characters} is not a directory.")
    if not packs_dir.exists():
        raise SystemExit(f"Packs directory {packs_dir} not found.")
    if not packs_dir.is_dir():
        raise SystemExit(f"{packs_dir} is not a directory.")

    new_characters = collect_characters(characters_path)
    if not new_characters:
        raise SystemExit("No character folders with valid character.yml files found.")

    tf_text = tf_characters_path.read_text(encoding="utf-8")
    try:
        tf_data = json.loads(tf_text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse {tf_characters_path}: {exc}") from exc
    if not isinstance(tf_data, list):
        raise SystemExit(f"{tf_characters_path} must contain a JSON array.")

    existing_file_names = {
        str(entry.get("file"))
        for entry in tf_data
        if isinstance(entry, dict) and entry.get("file")
    }
    scenario_entry: Optional[Dict[str, Any]] = None
    for entry in tf_data:
        if isinstance(entry, dict) and entry.get("name") == scenario_name:
            scenario_entry = entry
            break

    if scenario_entry is None:
        base_file = scenario_file_slug(scenario_name)
        pack_file_stem = ensure_unique_file_slug(base_file, existing_file_names)
        scenario_entry = {
            "name": scenario_name,
            "file": pack_file_stem,
            "enable_BunniBot": True,
            "enable_VNBot": True,
        }
        tf_data.append(scenario_entry)
    else:
        pack_file_stem = scenario_entry.get("file")
        if not pack_file_stem:
            base_file = scenario_file_slug(scenario_name)
            pack_file_stem = ensure_unique_file_slug(base_file, existing_file_names)
            scenario_entry["file"] = pack_file_stem
        pack_file_stem = str(pack_file_stem)
        scenario_entry["file"] = pack_file_stem
        scenario_entry["enable_BunniBot"] = True
        scenario_entry["enable_VNBot"] = True

    pack_file_path = packs_dir / f"{pack_file_stem}.py"

    existing_dir_names = {
        path.name for path in destination_characters.iterdir() if path.is_dir()
    }
    taken_names = set(existing_dir_names)

    character_actions: List[Dict[str, Any]] = []
    for folder, name, source, metadata in new_characters:
        dest_path = destination_characters / folder
        removed_dud = False
        if dest_path.exists():
            removed_dud = remove_dud_folder(dest_path, args.dry_run)
            if removed_dud:
                taken_names.discard(dest_path.name)
        if dest_path.exists() and not removed_dud:
            existing_config = dest_path / "character.yml"
            existing_data: Dict[str, Any] = {}
            if existing_config.exists():
                existing_data, _ = read_character_config(existing_config)
            existing_name = normalized_character_name_from_data(existing_data, folder)
            new_name = normalized_character_name_from_data(metadata, folder)
            if (
                existing_name == new_name
                and canonical_metadata_signature(existing_data)
                == canonical_metadata_signature(metadata)
            ):
                character_actions.append(
                    {
                        "folder": folder,
                        "display_name": name,
                        "source": source,
                        "type": "merge",
                    }
                )
                continue
            unique_folder = ensure_unique_folder(folder, taken_names)
            if unique_folder != folder:
                print(
                    f"[rename] {folder} -> {unique_folder} to avoid folder collision",
                    file=sys.stderr,
                )
            character_actions.append(
                {
                    "folder": unique_folder,
                    "display_name": name,
                    "source": source,
                    "type": "copy",
                }
            )
            continue
        unique_folder = ensure_unique_folder(folder, taken_names)
        character_actions.append(
            {
                "folder": unique_folder,
                "display_name": name,
                "source": source,
                "type": "copy",
            }
        )

    if not character_actions:
        raise SystemExit("No characters available for import.")

    pack_entries = [
        (action["folder"], action["display_name"])
        for action in character_actions
        if action["type"] != "merge"
    ]
    pack_block = format_pack_entries(pack_entries, scenario_name) if pack_entries else ""

    updated_tf_text = json.dumps(tf_data, indent=2) + "\n"
    pack_file_exists = pack_file_path.exists()
    pack_previous_text: Optional[str] = None
    updated_pack_text: Optional[str] = None
    if pack_entries:
        if pack_file_exists:
            try:
                pack_previous_text = pack_file_path.read_text(encoding="utf-8")
            except OSError as exc:
                raise SystemExit(f"Unable to read existing pack file {pack_file_path}: {exc}") from exc
            try:
                updated_pack_text = append_block_to_pack(pack_previous_text, pack_block)
            except ValueError as exc:
                raise SystemExit(f"Failed to update pack file {pack_file_path}: {exc}") from exc
        else:
            updated_pack_text = render_new_pack(pack_block)

    if args.dry_run:
        print("Dry run: showing pack block that would be inserted:\n")
        print(pack_block)

    log_entries: List[dict] | None = None
    log_entry: dict | None = None
    if not args.dry_run:
        log_entries = load_run_log(log_path)
        log_entry = {
            "scenario": scenario_name,
            "planned_folders": [action["folder"] for action in character_actions],
            "copied_folders": [],
            "tf_characters": str(tf_characters_path),
            "characters_dir": str(destination_characters),
            "tf_characters_snapshot": tf_text,
            "merged_updates": [],
        }
        if pack_entries:
            log_entry.update(
                {
                    "pack_file": str(pack_file_path),
                    "pack_file_created": not pack_file_exists,
                    "pack_previous_text": pack_previous_text,
                }
            )
        log_entries.append(log_entry)
        save_run_log(log_path, log_entries)

    for action in character_actions:
        folder = action["folder"]
        source = action["source"]
        if action["type"] == "merge":
            added_paths = merge_character_contents(
                source, destination_characters / folder, args.dry_run
            )
            if (
                log_entry is not None
                and log_entries is not None
                and added_paths
                and not args.dry_run
            ):
                log_entry["merged_updates"].append(
                    {"folder": folder, "paths": added_paths}
                )
                save_run_log(log_path, log_entries)
        else:
            copy_character_folder(source, destination_characters, folder, args.dry_run)
            if log_entry is not None and log_entries is not None:
                log_entry["copied_folders"].append(folder)
                save_run_log(log_path, log_entries)
        process_character_assets(tools_dir, destination_characters, folder, args.dry_run)

    if args.dry_run:
        return

    tf_characters_path.write_text(updated_tf_text, encoding="utf-8")
    if pack_entries and updated_pack_text is not None:
        pack_file_path.parent.mkdir(parents=True, exist_ok=True)
        pack_file_path.write_text(updated_pack_text, encoding="utf-8")
    if log_entry is not None and log_entries is not None:
        save_run_log(log_path, log_entries)

    print(f"Added {len(character_actions)} characters under scenario '{scenario_name}'.")


if __name__ == "__main__":
    main()
