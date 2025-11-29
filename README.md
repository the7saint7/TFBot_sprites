# TFBot Sprites

This repository holds the sprite assets for the TFBot visual novel project. Character artwork lives in `characters/`, grouped by each character's folder. The `tf_characters.json` catalog lists every character's display name, matching folder, and a short flavor message so tools and the game can stay in sync.

To keep downloads lightweight, tools in `tools/` focus on optimizing and cleaning sprite files — for example trimming unused layers or minimizing image size without losing visual quality. When adding new sprites, run the appropriate cleanup tool so the optimized assets stay committed, and don't forget to register the character in `tf_characters.json`.

### Tools

`tools/face_fixer.py` trims face variants for every character pose so only the default face remains. The script keeps the first alphabetically sorted image inside each `face` folder, deletes the rest, and removes any other subfolders such as `blush` within each `faces` directory.

Usage:

```bash
python tools/face_fixer.py --dry-run   # show what would be removed
python tools/face_fixer.py             # actually delete redundant faces
```

By default the script targets the repository’s `characters/` directory, but you can pass a custom path if needed. Always start with `--dry-run` to verify the changes before deleting files.

### Social Experiment Sprites

Social Experiment Sprites are named for their head_body, example SocialExperiment_abby_cornelia is Abbys head on Cornelias body, this was done so it could be tracked in cases of multipull HeadSwaps for a character or to assist in generating message text.
