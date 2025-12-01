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
