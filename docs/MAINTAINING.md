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

## Later versions (Finder and GitHub Desktop, no Terminal)

1. Unzip the new release zip (double-click it in Downloads).
2. Open the new folder and the repository folder (`~/Documents/GitHub/NanocrystalShapes`) side by side.
3. In the new folder select everything **except `docs`** (unless the new version changes the
   pictures there), drag it into the repository folder and choose **Replace**. Never replace or
   delete the repository folder itself; its hidden `.git` folder holds the history.
4. GitHub Desktop lists the changes. Right-click any change you did not intend (for example your
   own screenshots) › **Discard Changes**. Commit, then **Push origin**.
5. On github.com: **Releases › Draft a new release**, type the new tag (for example `v2.2`),
   choose **Create new tag on publish**, attach the zip and publish.

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
