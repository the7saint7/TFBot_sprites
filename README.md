# TFBot Sprites

This repository holds the sprite assets for the TFBot visual novel project. Character artwork lives in `characters/`, grouped by each character's folder. The `tf_characters.json` catalog lists every character's display name, matching folder, and a short flavor message so tools and the game can stay in sync.

To keep downloads lightweight, tools in `tools/` focus on optimizing and cleaning sprite files - for example trimming unused layers or minimizing image size without losing visual quality. When adding new sprites, run the appropriate cleanup tool so the optimized assets stay committed, and do not forget to register the character in `tf_characters.json`.

### Tools

- `tools/face_fixer.py` trims face variants for every character pose so only the default face remains. The script keeps the first alphabetically sorted image inside each `face` folder, deletes the rest, and removes any other subfolders such as `blush` within each `faces` directory.

  ```bash
  python tools/face_fixer.py --dry-run   # show what would be removed
  python tools/face_fixer.py             # actually delete redundant faces
  ```

  By default the script targets the repository's `characters/` directory, but you can pass a custom path if needed. Always start with `--dry-run` to verify the changes before deleting files.

- `tools/face_gallery.py` builds an HTML gallery (`face_gallery.html` by default) that layers every face over the first outfit found for that pose. The page uses a responsive CSS grid so the face thumbnails stay consistent in size while the layout automatically shows more or fewer columns as you resize the browser window.

  ```bash
  python tools/face_gallery.py                      # render gallery for repo characters
  python tools/face_gallery.py --output out/gallery.html --characters ..\custom_chars
  ```

  Open the generated HTML file in a browser to quickly spot mismatched faces or poses.

- `tools/outfit_shrinker.py` (currently limited to `characters\emoChick`) inspects every pose, determines the scale needed so all outfits fit inside a 220x246 box, and applies that ratio to every PNG inside the pose (outfits, faces, outfit subfolders). If a pose defines `image_height` in `character.yml`, the script crops the scaled sprites from the top down to that height.

  ```bash
  python tools/outfit_shrinker.py                   # scale emoChick assets in place
  python tools/outfit_shrinker.py --characters path\to\characters
  ```

  Extend the script's `CHAR_LIMIT` constant once you are ready to run it on more characters.

- `tools/ect_runner.py` wraps `ect.exe` (see `tools/ect-instructions.txt`) so you can optimize every PNG in `characters/` without manually shelling into each folder. It keeps a JSON log (`tools/ect_runner_log.json`) of file size/mtime pairs so runs can resume, skipping sprites that already match their previously optimized signature. Progress is reported per batch and you can dry run commands before execution.

  ```bash
  python tools/ect_runner.py --dry-run              # preview commands
  python tools/ect_runner.py                        # optimize all character PNGs
  python tools/ect_runner.py --chunk-size 32 --characters ..\my_chars
  ```

  Ensure `ect.exe` sits next to the script: `tools/ect_runner.py` automatically references it.
