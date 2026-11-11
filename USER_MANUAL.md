# Nanocrystal Shapes 2.2 – User Manual


---

### User Manual

Nanocrystal Shapes draws common nanocrystal shapes as translucent 3D figures for slides, posters, papers and teaching. You choose a shape, set its parameters and the view, switch the parts of the figure on or off, and save the picture at any size.

### 1. The window

- The picture area on the left shows the figure. Drag it with the mouse to rotate, scroll to zoom, and double-click to return to the default view.
- The Shape tab chooses the shape, its parameters and the view angles.
- The Display tab switches parts of the figure on or off and sets opacity, thickness and colours.
- Below the tabs: the Transparent background box, the Save Image button and a status line with the current shape, its parameters and the view angles.

### 2. Shapes

- Polyhedra: Tetrahedron, Cube, Octahedron, Cuboctahedron, Icosahedron.
- Twinned: Decahedron (five-fold twinned) and Bipyramid (penta-twinned when it has 5 sides).
- Plates: Triangular plate and Hexagonal plate.
- Curved: Sphere, Rod, Tube and Tetrapod.

Choose a shape from the list on the Shape tab or from the Shape menu. Switching shape moves to that shape's default view. Each shape remembers its own parameters; File › Reset Shape Parameters restores the defaults of the current shape.

### 3. Parameters

- **Truncation t** (polyhedra): cuts every corner so that the cut meets each edge at a distance tL from the corner. Every original edge keeps a middle piece of length (1 − 2t)L. t = 0 is the uncut shape.
- **Corner truncation t** (plates): cuts the corners in the plane of the plate. A triangle with t = 1/3 becomes a regular hexagon.
- **Length / width** (decahedron, bipyramid): length along the 5-fold (or n-fold) axis divided by the width across the equator. For the decahedron, 0.577 is the ideal shape made of five regular tetrahedra; larger values give elongated decahedra.
- **Number of sides** (bipyramid): 3 to 8. With 5 sides the twin planes are shown.
- **Thickness / edge** (plates): plate thickness divided by the edge length.
- **Length / diameter** (rod, tube) and **Arm length / diameter** (tetrapod).
- **Inner / outer diameter** (tube): 0.95 is a thin wall, 0.1 almost solid.
- **End rounding** (rod, tetrapod arms): 0 gives flat ends, 1 gives hemispherical ends.

Useful values:

- Tetrahedron t = 1/3: truncated tetrahedron.
- Cube t = 0.293: truncated cube. Cube t = 0.5: cuboctahedron.
- Octahedron t = 1/3: truncated octahedron. Octahedron t close to 0.5: cuboctahedron.
- Icosahedron t = 1/3: truncated icosahedron.

You can type a value into the box next to each slider and press Enter.

### 4. The view

- Azimuth turns the figure around the vertical axis; Elevation tilts it towards or away from you.
- Zoom changes the size of the figure in the frame.
- Default view (button, double-click, or Ctrl+R) restores the shape's default angles and zoom.
- The figure is drawn with a parallel (orthographic) projection, as in most crystallography figures.

### 5. Display

- **Faces:** the translucent faces. Face opacity sets how transparent they are.
- **Edges:** the outline of the shape. For curved shapes these are the visible outline and the rims.
- **Corner edges (tL):** the cut-off corners of truncated polyhedra, drawn in black.
- **Radii / axes:** lines from the centre to each corner (polyhedra), to the surface (sphere), or along the axes (rod, tube, tetrapod arms).
- **Edge arrows:** arrows from one corner along each edge that meets there, like lattice vectors. **Hidden arrows** controls the arrows that lie behind the faces.
- **Twin planes:** the internal twin boundaries of the decahedron and the 5-sided bipyramid.
- **3D lighting:** shading of faces, tubes and arrows. Switch it off for flat colours.
- Radii / axes thickness, Arrow thickness and Line width change how heavy these parts look.
- Colours: click a swatch to choose any colour, including the background.

Options that do not apply to the current shape are greyed out (for example edge arrows on a sphere).

### 6. Saving images

- File › Save Image (Ctrl+S), or the Save Image button.
- Choose the width in pixels. The height follows the 294 × 252 frame. The presets 1×, 2×, 4× and 8× are multiples of that frame; 4× (1176 px) is good for slides and 8× (2352 px) for print.
- Formats: PNG, JPEG, TIFF, BMP or PDF.
- Transparent background: tick the box under the tabs (the preview then shows a checkerboard) or in the save dialog. File › Save Transparent PNG (Ctrl+Shift+S) does it in one step. Transparency is kept in PNG and TIFF files; JPEG, BMP and PDF files get the background colour, and the app warns you first.
- The saved picture is drawn again at full resolution with smooth edges, so it is sharper than the preview.

### 7. Settings that are remembered

The shape, every shape's parameters, the view, colours, display options, the export size, the last folder and the window size are saved when you close the app. Tools › Open Settings Folder shows where. File › Reset Everything restores all defaults; the tetrahedron's defaults reproduce the original reference figure.

### 8. Desktop shortcut

Tools › Create Desktop Shortcut puts a Nanocrystal Shapes icon on your desktop, so you no longer need the launcher file:

- Windows: a shortcut on the desktop and in the Start menu, with the app's own icon. To keep it in the taskbar, right-click the Start menu entry › Pin to taskbar (or pin the running app).
- macOS: a small "Nanocrystal Shapes.app" on the desktop. It is made on your own Mac, so macOS does not block it. Drag it to the Dock to keep it there.
- Linux: an icon on the desktop and an entry in your applications menu.

The shortcut points at the app folder. If you move or rename the folder, start the app once from its new place and create the shortcut again; the new one replaces the old.

### 9. About and acknowledgment

Nanocrystal Shapes is developed by moinulshdu (moinulshdu@gmail.com). It is free for anyone to use, share and build upon. If it helps your work, a kind acknowledgment of the developer would be warmly appreciated. Help › About Nanocrystal Shapes has a button that copies a ready-made acknowledgment line. Questions, ideas and feedback are always welcome by email.

---

### Quick Start

### Start the app

- Windows: double-click "Start Nanocrystal Shapes (Windows).bat".
- macOS: double-click "Start Nanocrystal Shapes (macOS).command". The first time, macOS may block it: click Done, then System Settings › Privacy & Security › Open Anyway.
- Linux: double-click "start_nanocrystal_shapes.sh" or run it from a terminal.

On the first start, if Pillow is missing, a window asks for permission to install it. Nothing is installed without your OK.

Then choose Tools › Create Desktop Shortcut once. From then on you can start the app from its desktop icon (and on Windows from the Start menu).

### Make a figure in four steps

- Shape tab: choose a shape, for example Octahedron.
- Set its parameters, for example Truncation t = 0.333 for a truncated octahedron.
- Drag the picture to the angle you like. Use the Display tab to switch off what you don't need, such as arrows or radii.
- Tick Transparent background if the figure goes on a coloured slide, then click Save Image and choose 4× (1176 px).

### Typical recipes

- Clean shape for a slide: Display tab › untick Corner edges, Radii / axes and Edge arrows.
- Truncation explained: keep Corner edges on; the black lines show the original corners that were cut away.
- Penta-twinned particle: Decahedron or 5-sided Bipyramid with Twin planes on.
- Gold nanorod: Rod, Length / diameter 3–4, End rounding 1.
- Nanoplate: Triangular plate, Thickness / edge 0.1, Corner truncation 0.2.

---

### How Nanocrystal Shapes Is Built

Nanocrystal Shapes is a Python 3 application of about 2,800 lines. It began as a small program that reproduced one reference figure of a truncated tetrahedron, and grew from there.

### Technology

- Python 3.8 or newer.
- Tkinter / ttk for the window. It is part of standard Python, so the interface runs on Windows, macOS and Linux with no extra installation.
- Pillow for drawing, showing and saving pictures.
- NumPy (optional) for faster saving with a transparent background.
- No OpenGL or graphics card is needed: every figure is drawn by the app's own code.

### Folder structure

    NanocrystalShapes/
        Nanocrystal Shapes.pyw                    start file
        Start Nanocrystal Shapes (Windows).bat    finds Python and starts the app
        Start Nanocrystal Shapes (macOS).command  same, for macOS
        start_nanocrystal_shapes.sh               same, for Linux
        README.md / USER_MANUAL.md / CHANGELOG.md / LICENSE
        nanoshapes/                               the application package
            __init__.py      version and credits
            bootstrap.py     finds missing packages, installs them with permission
            geometry.py      the shapes
            renderer.py      camera, lighting, drawing; shape list and parameters
            app.py           the main window, menus, saving
            shortcuts.py     Tools › Create Desktop Shortcut for each system
            help_window.py   this manual and the Python Packages window
            manual.py        the manual text
            icon.png / .ico / .icns
        tools/                                    rebuild the icon and README pictures
        docs/                                     README pictures and screenshots

### Start-up sequence

- The launcher finds a Python with Tkinter (Anaconda first on Windows and macOS) and runs the start file.
- bootstrap.py checks that Pillow is installed. If it is missing, a window asks to install it; only on Yes does it run "python -m pip install Pillow", retrying as a personal (--user) install if needed.
- Only then is the main window (app.py) loaded. It sets its own Windows taskbar identity and icon, so it does not group with other Python apps.

### Shapes (geometry.py)

- Polyhedra are the intersection of flat half-spaces: one for each face of the base solid, plus one cutting plane per corner for truncation. Each face polygon is found by clipping a large square in its plane by all the other planes. This one method handles every shape and every value of t, including cuts that meet each other.
- Plates are prisms whose corners are cut by vertical planes.
- Twin planes are the planes through the 5-fold axis and each equatorial corner, clipped to the solid.
- Curved shapes are fine triangle meshes with smooth normals: spheres, rods with rounded or flat ends, tubes (outer wall, inner wall and two rings), and tetrapods (four rods from the centre along tetrahedral directions).

### Drawing (renderer.py)

- Orthographic camera set by azimuth and elevation.
- Painter's algorithm: everything is sorted from back to front and painted in that order.
- Translucent faces are painted as whole layers (all faces seen from behind, then all faces seen from the front), so curved meshes show no seams.
- Lines and tubes are placed between those layers by testing, along the line of sight, whether they lie in front of, inside or behind the solid. For tubes and tetrapods this is tested against each surface separately.
- Outlines of curved shapes are traced where the surface turns away from the viewer, giving smooth silhouettes.
- Lighting: four coloured lights. The face lighting was fitted to reproduce the colours of the original reference picture exactly.
- Every picture is drawn at 2–4 times its size and then reduced, for smooth edges. Transparent pictures are drawn once on white and once on black, and the exact transparency of every pixel is calculated from the difference.

### Adding a shape

- Write a builder in geometry.py that returns a Shape (use polyhedron(...) for flat-faced solids, or revolve / capsule for curved ones).
- Add an entry to SHAPES in renderer.py with its label, default parameters, parameter ranges and default view.
- Run "python tools/render_gallery.py" to check it.

---

### Keyboard Shortcuts

On macOS use Cmd instead of Ctrl.

### Files

- Ctrl+S – Save Image
- Ctrl+Shift+S – Save Transparent PNG
- Ctrl+Q – Quit (settings are saved)

### View

- Left / Right arrow – rotate around the vertical axis by 5° (with Shift: 1°)
- Up / Down arrow – tilt by 5° (with Shift: 1°)
- Plus (+) and minus (−) keys – zoom in / out
- Ctrl+R – default view of the current shape
- Page Up / Page Down – previous / next shape
- Ctrl+T – transparent background on / off

The arrow, plus and minus keys work when the picture or a button has the focus, not while you are typing in a number box.

### Mouse

- Drag the picture – rotate
- Mouse wheel – zoom
- Double-click the picture – default view

### Number boxes and dialogs

- Type a value and press Enter (or click elsewhere) to apply it.
- Enter – confirm a dialog; Esc – close it.

### Help

- F1 – User Manual

---

### Troubleshooting

### Starting the app

- Windows: a black window says "Python was not found". Install Python from python.org and tick "Add python.exe to PATH" on the first installer screen, then double-click the .bat again. Anaconda is found automatically.
- Windows: "Windows protected your PC". The launcher is not signed by a registered publisher. Click More info › Run anyway. Unblocking the downloaded zip first (right-click › Properties › Unblock) avoids it.
- macOS: "Apple could not verify … is free of malware". This appears for every app without a paid Apple signature; it is not a malware detection. Click Done, then System Settings › Privacy & Security › Open Anyway. Or, once, in Terminal: xattr -dr com.apple.quarantine followed by the folder (drag it in).
- macOS: the .command file opens in a text editor or says "permission denied". In Terminal type chmod +x (with a space), drag the .command file in, press Return.
- Linux: "No module named tkinter" – sudo apt install python3-tk (Debian/Ubuntu) or sudo dnf install python3-tkinter (Fedora).
- Linux: "cannot import name ImageTk" – sudo apt install python3-pil.imagetk

### Packages

- "The installation did not succeed": check the internet connection. With Anaconda installed for all users (in C:\ProgramData), open the Anaconda Prompt as administrator and run: python -m pip install Pillow numpy
- Linux "externally managed environment": install with the system package manager, e.g. sudo apt install python3-pil python3-pil.imagetk python3-numpy
- Help › Python Packages shows which packages are installed for the Python that runs the app, and can install missing ones.

### Using the app

- The figure is cut off at the edge after changing a parameter or rotating: lower the Zoom, or click Default view.
- An option is greyed out: it does not apply to the current shape (for example arrows on a sphere, or twin planes on a 4-sided bipyramid).
- Lines look too heavy or too thin: Display tab › Line width, Radii / axes thickness, Arrow thickness.
- Rotating feels slow on an old computer: the preview is drawn in a faster, rougher mode while you drag and sharpens when you let go. Curved shapes (sphere, tetrapod) take longest.
- The saved PNG has a white background: tick Transparent background before saving. JPEG, BMP and PDF cannot be transparent.
- Strange settings after experimenting: File › Reset Shape Parameters, or File › Reset Everything.

### Desktop shortcut

- The shortcut stopped working: the app folder was moved, renamed or deleted after the shortcut was made. Start the app from the launcher in the folder's new place, then choose Tools › Create Desktop Shortcut again.
- Windows: "The shortcut could not be created". Company computers sometimes block PowerShell, which the app uses to make shortcuts. Make one by hand: right-click "Start Nanocrystal Shapes (Windows).bat" › Send to › Desktop (create shortcut).
- Linux: the desktop icon says "Untrusted application launcher" or shows a gear: right-click it › Allow Launching.
- macOS: the new desktop app shows a plain icon for a moment. Finder updates it after a few seconds, or after you log out and in again.

### Windows taskbar shows another app's icon

The app sets its own taskbar identity and icon. If an older pinned shortcut still groups it with another Python app, unpin that shortcut, start Nanocrystal Shapes, choose Tools › Create Desktop Shortcut and pin the new Start menu entry.

### Still stuck?

Email moinulshdu@gmail.com with a screenshot and the text from Help › Python Packages (it shows your Python version and package versions).

---

### Limitations

### Drawing

- Pictures are raster images (pixels). PDF files contain the picture as an image, not as editable vector lines, and there is no SVG export. Save at 4× or 8× for sharp printing.
- Parallel (orthographic) projection only; there is no perspective.
- Faces are shaded flat, one colour per face. Curved shapes use fine meshes, so very large prints can show slight banding on spheres.
- Translucent surfaces are painted in back-to-front order. For tubes and tetrapods, where surfaces overlap in complex ways, the order is a careful approximation: in rare views a line can look slightly too bright or too faded where it passes through several surfaces.
- No text or labels are drawn (such as tL or R). Add them in your slide or drawing program.
- Largest saved picture: 10,000 pixels wide. Very large transparent pictures without NumPy can take a while.

### Shapes

- Shapes are idealised geometry, not atomistic models: no atoms, lattice or surface steps.
- Truncation cuts every corner of a shape by the same amount. Different cuts for different corners, or for edges, are not possible yet.
- Decahedron: the Ino (truncated edges) and Marks (re-entrant notches) variants are not modelled.
- Tetrapods have four straight arms of equal length, without a separate core.

### Program

- The window name in the macOS Dock may read "Python" rather than "Nanocrystal Shapes", because the app runs inside Python.
- The app is not signed with a paid Apple or Microsoft certificate, so both systems show a security warning the first time.

---

### Privacy & Safety

### In short

Nanocrystal Shapes works completely offline. It collects nothing, sends nothing, shares nothing and sells nothing. There are no accounts, analytics, tracking, advertising or update checks. Everything happens on your own computer.

### When the internet is used

- Only to install missing Python packages (Pillow, NumPy) from the official Python Package Index, and only after you click Yes. This is done by Python's own installer, pip.
- Clicking the email address in Help › About opens your own email program with a new message; the app itself sends nothing.

### What it reads and writes on your computer

- Reads: its own files (code and icon) and its settings file.
- Writes: a desktop shortcut (and a Start menu or applications-menu entry), only when you choose Tools › Create Desktop Shortcut.
- Writes: its settings file (shape, parameters, view, colours, window size, last folder and export size) when you close the app; pictures only where you choose to save them; the manual only where you choose to export it.
- The settings file is in: Windows %APPDATA%\NanocrystalShapes, macOS ~/Library/Application Support/NanocrystalShapes, Linux ~/.config/NanocrystalShapes. Tools › Open Settings Folder shows it.
- It never reads your other files, never deletes any file and never needs administrator rights.

### Other programs it starts

- pip, to install packages (only after you agree).
- Your file manager, only when you choose Tools › Open Settings Folder.
- On Windows, PowerShell, only when you choose Tools › Create Desktop Shortcut. It writes the shortcut files and nothing else.
- Your email program, only when you click the email address in the About window.
- On Windows it tells the taskbar the app's own identity, so it gets its own button and icon. This changes nothing else.

### How this was checked

- Code review: every line of the app's own code was searched for internet access, file access, file deletion and starting other programs. The results are exactly the lists above.
- Live test (November 11, 2026): the whole app was run with the operating system recording every network connection attempt. Every shape was drawn with all parameters at their limits, the help pages, Python Packages and About windows were opened, and pictures were saved. There were zero internet connection attempts; the only connections were to the local display system that draws windows on the screen.

### Honest limits of these assurances

- Open source and readable: the app is about 2,800 lines of plain Python. Anyone can read every file in the nanoshapes folder to verify the above. It has not been reviewed by an independent security auditor.
- Third-party packages: the app relies on Pillow and, optionally, NumPy, two very widely used open-source libraries, installed from the official Python Package Index.
- macOS and Windows security warnings appear because the app is not signed with a paid developer certificate. They do not mean a problem was detected.
- If you received Nanocrystal Shapes from somewhere other than the developer, the code could have been changed. Get it from the developer's own GitHub page or directly from moinulshdu.
