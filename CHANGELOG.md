# Changelog

## 2.2
- **Tools › Create Desktop Shortcut**: a desktop icon on Windows (plus a Start menu entry that can
  be pinned to the taskbar), macOS (a small app you can drag to the Dock) and Linux (plus an
  applications-menu entry). **Open Settings Folder** moved to the Tools menu.
- The Mac shortcut uses the app's own icon (`nanoshapes/icon.icns`).

## 2.1
- Decahedron: new **length / width** parameter (0.577 = ideal decahedron; larger values give
  elongated decahedra). New default view that shows its height.
- New sliders for the **thickness of radii / axes**, the **thickness of the edge arrows** and the **line width**.
- **Transparent background** checkbox next to the Save button, with a checkerboard preview,
  and **File › Save Transparent PNG…**.
- A warning when you save a transparent image as JPEG, BMP or PDF.
- **Help › About Nanocrystal Shapes**: a window with the developer credit, the email address, a note on how the app was made, and a **Copy Acknowledgment Text** button.
- **Full Help menu**: User Manual, Quick Start, How It Is Built, Keyboard Shortcuts,
  Troubleshooting, Limitations, Privacy & Safety, About. The manual is also in `USER_MANUAL.md`.
- **Help › Python Packages**: shows the Python in use, which packages are installed and
  their versions, and installs missing ones after asking.
- **Privacy & Safety**: checked by code review and a live network-trace test; summarised in About.
- New keyboard shortcuts: arrow keys rotate, + / − zoom, Ctrl+R default view, Page Up / Down
  change shape, Ctrl+T transparent background, Ctrl+Shift+S save transparent PNG.
- Repository files: README, license, changelog, requirements, gallery pictures.

## 2.0
- Renamed to **Nanocrystal Shapes**.
- New shapes: cube, cuboctahedron, icosahedron, decahedron, bipyramid, triangular and
  hexagonal plates, sphere, rod, tube and tetrapod.
- Twin planes for the decahedron and the 5-sided bipyramid.
- Shape and Display tabs, with per-shape parameters.
- Own app icon and own taskbar button on Windows (no longer grouped with other Python apps).

## 1.1
- Added the octahedron with the same truncation parameter.

## 1.0
- First version: truncated tetrahedron figure, reproducing the original reference picture.
