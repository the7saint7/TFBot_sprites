# TFBot Sprites

This repository holds the sprite assets for the TFBot visual novel project. Character artwork lives in `characters/`, grouped by each character's folder. The `tf_characters.json` catalog lists every character's display name, matching folder, and a short flavor message so tools and the game can stay in sync.

### Social Experiment Sprites

Social Experiment Sprites are named for their head_body, example SocialExperiment_abby_cornelia is Abbys head on Cornelias body, this was done so it could be tracked in cases of multipull HeadSwaps for a character or to assist in generating message text.


To keep downloads lightweight, tools in `tools/` focus on optimizing and cleaning sprite files - for example trimming unused layers or minimizing image size without losing visual quality. When adding new sprites, run the appropriate cleanup tool so the optimized assets stay committed, and do not forget to register the character in `tf_characters.json`.

### Tools

- `tools/face_fixer.py` trims face variants for every character pose so only the default face remains. The script keeps the first alphabetically sorted image inside each `face` folder, deletes the rest, and removes any other subfolders such as `blush` within each `faces` directory.

  ```bash
  python tools/face_fixer.py --dry-run   # show what would be removed
  python tools/face_fixer.py             # actually delete redundant faces
  ```

  By default the script targets the repository's `characters/` directory, but you can pass a custom path if needed. Always start with `--dry-run` to verify the changes before deleting files.

- `tools/ect_runner.py` wraps `ect.exe` (see `tools/ect-instructions.txt`) so you can optimize every PNG in `characters/` without manually shelling into each folder. It keeps a JSON log (`tools/ect_runner_log.json`) of file size/mtime pairs so runs can resume, skipping sprites that already match their previously optimized signature. Progress is reported per batch and you can dry run commands before execution.

  ```bash
  python tools/ect_runner.py --dry-run              # preview commands
  python tools/ect_runner.py                        # optimize all character PNGs
  python tools/ect_runner.py --chunk-size 32 --characters ..\my_chars
  ```

  Ensure `ect.exe` sits next to the script: `tools/ect_runner.py` automatically references it.

- `tools/pose_cropper.py` composites every outfit, accessory, and face layer for a pose to find the tightest bounding box, then crops all related PNGs (honoring any `image_height` overrides defined in `character.yml`). By default it processes every character; use `--character` for a single target or `--max-characters` for an alphabetical cap.

  ```bash
  python tools/pose_cropper.py --dry-run --character abby     # inspect one character
  python tools/pose_cropper.py --character abby               # apply crops to Abby only
  python tools/pose_cropper.py --dry-run --max-characters 0   # preview everyone
  ```

  The tool requires Pillow and uses PyYAML when available (it falls back to a minimal parser otherwise); start with `--dry-run` to review the crop boxes that will be applied.

- `tools/ai_outfit_builder.py` wraps a Flux-Kontext ComfyUI workflow (see `tools/FLUX_KONTEXT_IMAGE_EDITING_API.json`) so every character can automatically receive a new AI-generated outfit. Point the script at your workflow JSON, supply the outfit name, and optionally override the secondary reference image or prompt. Node bindings default to primary image `408`, optional secondary `402`, prompt `394`, and output `392`, but you can override those via `--*-node` flags if your workflow differs. Generated renders are staged for manual QA before background removal.

  ```bash
  python tools/ai_outfit_builder.py ^
      --workflow tools/FLUX_KONTEXT_IMAGE_EDITING_API.json ^
      --outfit-name neon_guard ^
      --secondary-image suit.png ^
      --prompt "Energetic neon bodyguard uniform"
  ```

  The workflow template JSON may optionally include a `metadata` block that identifies each node binding; otherwise pass node ids via CLI. Generated sprites flatten onto a light gray background before upload, are cropped to their left half, and saved into `outputs/<character>/<pose>/TIMESTAMP_outfit.png`. The script skips any character that already has a folder in `outputs/`, `to_remove_bg/`, or `bg_removed/` (unless `--force` is passed). Move a reviewed character folder from `outputs/` to `to_remove_bg/` when it is ready for the separate background-removal step.

- `tools/add_scenario_characters.py` reads every folder inside a supplied directory, pulls each folder's `display_name` from `character.yml`, copies the character folder into `characters/`, batch-runs the cleanup tools, and appends the character entries to `tf_characters.py` under a single scenario header. The comment defaults to the directory name but can be overridden with `--scenario-name`. Existing folders are skipped automatically, and the tool can preview the block it would append via `--dry-run`. Pass `--undo-last` to remove the most recent run (it deletes the recorded character folders and removes the appended block from `tf_characters.py`); add `--dry-run` to preview what would be undone.

  ```bash
  python tools/add_scenario_characters.py ..\new_truth_or_syn --scenario-name "Truth or Syn"
  python tools/add_scenario_characters.py ..\new_truth_or_syn --dry-run
  python tools/add_scenario_characters.py --undo-last
  ```

  Characters are appended at the end of the `TF_CHARACTERS` list with their names suffixed by the scenario in parentheses, matching the in-file template. If a folder name would collide with an existing character, the script compares each folder’s `character.yml`. When the canonical metadata (name plus the non-pose fields) matches, the new content is merged into the existing folder—only missing poses/outfits/files are copied across, and the merge is logged so `--undo-last` can delete those paths later. If the metadata differs, the folder name is automatically incremented (`john`, `john1`, `john2`, …) so the characters stay distinct. When `character.yml` lacks a readable name, the folder name is title-cased and used as a fallback instead of skipping the character. After copying or merging each folder into the destination characters directory (override with `--characters-dir` when needed), the tool runs `face_fixer.py`, `pose_cropper.py --character <name>`, and `ect_runner.py --characters <path>` to keep the assets tidy before writing to `tf_characters.py`. Every run is logged incrementally, so `--undo-last` can roll back even a partially failed import. The script exits immediately if it detects that the `.env` virtual environment is not active, so activate it first.

### Python Environment

Scripts assume you are working inside a virtual environment named `.env`. The tools will warn if they detect that `.env` is not active and remind you how to initialize or activate it. Recommended workflow:

```bash
python -m venv .env
.\.env\Scripts\activate        # on Windows (PowerShell/CMD)
source .env/bin/activate       # on macOS/Linux shells
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Once activated, run tools with the `python` command (not `py` on Windows) so the virtual environment's interpreter is used—for example: `python tools\pose_cropper.py --dry-run`.

`requirements.txt` lists the minimal dependencies (`Pillow`, `PyYAML`). Re-run `pip install -r requirements.txt` whenever the list changes.
