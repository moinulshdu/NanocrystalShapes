# Maintaining and publishing

## First upload to GitHub (GitHub Desktop)

1. Unzip the release zip and put the folder at `~/Documents/GitHub/NanocrystalShapes`.
2. In Terminal, run this once so the launchers stay double-clickable for people who download
   from GitHub:

   ```bash
   cd ~/Documents/GitHub/NanocrystalShapes
   chmod +x "Start Nanocrystal Shapes (macOS).command" start_nanocrystal_shapes.sh "Nanocrystal Shapes.pyw"
   ```

3. GitHub Desktop › **File › Add Local Repository…** › choose the folder. When it says the
   folder is not a repository yet, click **create a repository**. Set **Git Ignore: None** and
   **License: None**, because both files are already in the folder, and leave README unticked.
4. Commit with the summary `Nanocrystal Shapes 2.1`, then click **Publish repository**.

Command-line alternative:

```bash
git init
git add .
git update-index --chmod=+x "Start Nanocrystal Shapes (macOS).command" start_nanocrystal_shapes.sh "Nanocrystal Shapes.pyw"
git commit -m "Nanocrystal Shapes 2.1"
git branch -M main
git remote add origin https://github.com/<your-user-name>/NanocrystalShapes.git
git push -u origin main
```

## Making a release

1. Update `__version__` in `nanoshapes/__init__.py` and add a section to `CHANGELOG.md`.
2. Commit and push.
3. On GitHub: **Releases › Draft a new release**, create the tag `v2.1` (for example), title
   it "Nanocrystal Shapes 2.1", paste the changelog section, attach `NanocrystalShapes.zip`
   and click **Publish release**.

## Later versions

Copy the new files into the existing repository folder, replacing the old ones. Do not delete
the folder: its hidden `.git` folder holds the history. Then commit, push, and make a new release.

## Regenerating pictures

```bash
python tools/render_gallery.py    # docs/images/shapes-gallery.png, parameter-examples.png
python tools/make_icon.py         # nanoshapes/icon.png and icon.ico
```

## Adding a shape

1. Write a builder in `nanoshapes/geometry.py` that returns a `Shape`. Use `polyhedron(...)`
   for flat-faced solids, or meshes (`revolve`, `capsule`) for curved ones.
2. Add an entry to `SHAPES` in `nanoshapes/renderer.py`, with its label, default parameters,
   optional label and range overrides, and default view.
3. Run `python tools/render_gallery.py` and check the result.
