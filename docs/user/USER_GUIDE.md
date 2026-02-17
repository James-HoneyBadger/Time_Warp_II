# Time Warp II — User Guide

The complete guide to using the Time Warp II IDE for TempleCode programming.

## Table of Contents

1. [Overview](#overview)
2. [Launching the IDE](#launching-the-ide)
3. [The Interface](#the-interface)
4. [Writing Code](#writing-code)
5. [Running Programs](#running-programs)
6. [Turtle Graphics Canvas](#turtle-graphics-canvas)
7. [File Management](#file-management)
8. [Find & Replace](#find--replace)
9. [Code Folding](#code-folding)
10. [Split Editor](#split-editor)
11. [Command Palette](#command-palette)
12. [Speed Controls](#speed-controls)
13. [Canvas Export](#canvas-export)
14. [Themes & Fonts](#themes--fonts)
15. [Debug Mode](#debug-mode)
16. [Keyboard Shortcuts](#keyboard-shortcuts)
17. [Settings & Persistence](#settings--persistence)
18. [Example Programs](#example-programs)

---

## Overview

Time Warp II is a single-language IDE built for **TempleCode** — a fusion of BASIC (1964), PILOT (1968), and Logo (1967). It provides:

- A syntax-highlighted code editor with line numbers
- An integrated output console with colour-coded messages
- A turtle graphics canvas for Logo drawing commands
- 9 colour themes, customisable fonts, and smart editing features

---

## Launching the IDE

### Linux / macOS

```bash
./run.sh
```

Or directly with Python:

```bash
python3 run.py
```

### Windows

```
run.bat
```

### First Launch

On first launch the IDE opens with:
- The **Dark** theme applied
- **Medium (12pt)** font size
- **Courier** font family
- A welcome message in the output panel explaining the three language heritages

Settings are saved automatically to `~/.templecode_settings.json`.

---

## The Interface

The window is divided into three main areas arranged horizontally:

```
┌──────────────────────────────────────────────────────────────┐
│  Menu Bar  │  File  Edit  View  Program  Debug  Test  ...   │
├──────────────────────────────────────────────────────────────┤
│  Toolbar   │  ▶ Run  ■ Stop  📄 New  📂 Open  💾 Save  ... │
├──────────────┬──────────────────┬────────────────────────────┤
│              │                  │                            │
│   Code       │   Output         │   Turtle Graphics          │
│   Editor     │   Console        │   Canvas                   │
│              │                  │                            │
│  (with line  │  (colour-coded   │  (drawing area for Logo    │
│   numbers)   │   messages)      │   commands)                │
│              │                  │                            │
│              ├──────────────────┤                            │
│              │  Input Bar       │                            │
├──────────────┴──────────────────┴────────────────────────────┤
│  Status Bar  │  file.tc  │  Ln 1, Col 1  │  Dark  │  12pt  │
└──────────────────────────────────────────────────────────────┘
```

### Editor Panel (Left)

The code editor features:
- **Line numbers** displayed in a left gutter
- **Syntax highlighting** powered by Pygments (keywords, strings, comments, numbers are colour-coded)
- **Current line highlighting** — the line under the cursor is subtly shaded
- **Auto-indent** — pressing Enter after block openers (`FOR`, `IF`, `WHILE`, `REPEAT`, etc.) adds 2 spaces
- **Tab completion** — press Tab to see keyword suggestions matching your partial input
- **Right-click context menu** — Cut, Copy, Paste, Select All, Go to Line, Find, Replace

### Output Console (Centre)

Displays program output with colour coding:
- **Normal output** — default text colour
- **Errors** — red
- **Warnings** — yellow/amber
- **Success / OK** — green

Below the output console is an **Input Bar** where the program can prompt for user input (via BASIC `INPUT` or PILOT `A:` commands). Type your response and press Enter or click the Submit button.

### Canvas Panel (Right)

The turtle graphics canvas renders Logo drawing commands. A draggable sash between the output and canvas panels allows resizing.

### Toolbar

Seven quick-access buttons:

| Button | Action |
|--------|--------|
| ▶ Run | Execute the program (F5) |
| ■ Stop | Halt a running program (Escape) |
| 📄 New | Create a new file (Ctrl+N) |
| 📂 Open | Open a `.tc` file (Ctrl+O) |
| 💾 Save | Save the current file (Ctrl+S) |
| 🎨 Theme | Cycle to the next colour theme |
| Aa Size | Cycle to the next font size |

### Status Bar

Displays at the bottom of the window:
- **Filename** — the current file (or "Untitled" with a dot indicator `●` if unsaved changes exist)
- **Cursor position** — `Ln <line>, Col <column>`
- **Theme name** — current colour theme
- **Font size** — current editor font size

---

## Writing Code

### Language Detection

TempleCode automatically detects which heritage each line belongs to:

| Line starts with | Heritage | Example |
|-----------------|----------|---------|
| `PRINT`, `LET`, `IF`, `FOR`, etc. | BASIC | `PRINT "Hello"` |
| `T:`, `A:`, `M:`, `Y:`, `N:`, etc. | PILOT | `T:Hello!` |
| `FORWARD`, `LEFT`, `PENUP`, etc. | Logo | `FORWARD 100` |

All three styles mix freely in a single `.tc` file.

### Syntax Highlighting

The editor highlights code elements in different colours:

- **Keywords** — language commands (`PRINT`, `FOR`, `FORWARD`, etc.)
- **Strings** — text in double quotes
- **Numbers** — numeric literals
- **Comments** — `REM` lines or inline comments
- **PILOT prefixes** — `T:`, `A:`, `M:`, etc.

### Auto-Indent

When you press **Enter** after a block-opening keyword, the editor automatically adds 2 spaces of indentation. Block openers include:

`FOR`, `WHILE`, `IF`, `ELSEIF`, `DO`, `REPEAT`, `SELECT`, `THEN`

The existing indentation of the current line is preserved for continuation lines.

### Tab Completion

1. Type the beginning of a keyword (e.g., `PRI`)
2. Press **Tab**
3. A popup appears showing matching keywords (e.g., `PRINT`)
4. Click a suggestion or continue typing

The completion system knows all 87 TempleCode keywords across BASIC, PILOT, and Logo. Up to 20 matches are shown at a time.

---

## Running Programs

### Start Execution

- Press **F5**, or
- Click the **▶ Run** toolbar button, or
- Use **Program → Run Program**

The program executes line by line. Output appears in the console panel, and any Logo commands draw on the canvas.

### Stop Execution

- Press **Escape**, or
- Click the **■ Stop** toolbar button, or
- Use **Program → Stop Program**

### Responding to Input Prompts

When a program uses `INPUT` (BASIC) or `A:` (PILOT), the input bar at the bottom of the output panel is activated. Type your response and press **Enter**.

### Clear Areas

- **Edit → Clear Editor** — erase all code
- **Edit → Clear Output** — clear the console
- **Edit → Clear Graphics** — wipe the canvas

---

## Turtle Graphics Canvas

The canvas occupies the right side of the window. The turtle starts at the centre facing up (north).

### Coordinate System

- Origin **(0, 0)** is at the centre of the canvas
- **X** increases to the right, **Y** increases upward
- The canvas dynamically resizes with the window

### Canvas Modes

| Command | Behaviour |
|---------|-----------|
| `WRAP` | Turtle wraps around edges |
| `WINDOW` | Turtle can leave the visible area |
| `FENCE` | Turtle stops at edges |

### Turtle Visibility

| Command | Effect |
|---------|--------|
| `SHOWTURTLE` / `ST` | Display the turtle cursor |
| `HIDETURTLE` / `HT` | Hide the turtle cursor |

---

## File Management

### Creating & Opening Files

| Action | Shortcut |
|--------|----------|
| New File | Ctrl+N |
| Open File | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |

Files are saved with the `.tc` extension. The file dialog defaults to the TempleCode file type.

### Unsaved Changes

A **dot indicator (●)** appears in the status bar and title bar when the editor has unsaved changes. The IDE prompts to save before closing or opening a new file.

### Recent Files

The **File → Recent Files** submenu lists up to 10 recently opened files. Select one to reopen it instantly. Use **Clear Recent Files** to reset the list.

---

## Find & Replace

### Find (Ctrl+F)

Opens a find dialog with options:
- **Case Sensitive** — match exact case
- **Whole Word** — match complete words only
- **Regex** — use regular expressions

Matches are highlighted in the editor. Click **Find Next** to cycle through results.

### Replace (Ctrl+H)

Opens a replace dialog with the same options plus:
- **Replace** — replace the current match
- **Replace All** — replace every occurrence

### Go to Line (Ctrl+G)

Opens a dialog to jump directly to a specific line number.

---

## Code Folding

Collapse and expand blocks of code to manage large programs.

- **Edit → Fold All Blocks** — collapse all `FOR/NEXT`, `IF/ENDIF`, `WHILE/WEND`, `DO/LOOP`, `REPEAT/END`, `SELECT/END SELECT` blocks
- **Edit → Unfold All** — expand all collapsed blocks

Folded blocks show as a single line with their opening statement visible.

---

## Split Editor

**View → Split Editor** (or via the Command Palette) toggles a second editor panel alongside the first. Both editors share the same syntax highlighting and theme. This is useful for viewing one part of a long program while editing another.

Toggle the split with the checkbox in the View menu.

---

## Command Palette

Open the command palette with **Ctrl+Shift+P** or **View → Command Palette**.

A searchable popup appears listing every available action. Type to filter:

### Available Commands

| Command | Action |
|---------|--------|
| New File | Create a new file |
| Open File | Open a file |
| Save File | Quick save |
| Save File As | Save with dialog |
| Run Program | Execute code |
| Stop Program | Halt execution |
| Find... | Open find dialog |
| Replace... | Open replace dialog |
| Undo / Redo | Undo or redo edits |
| Select All | Select all editor text |
| Clear Editor / Output / Graphics | Clear respective areas |
| Fold All Blocks / Unfold All | Toggle code folding |
| Toggle Split Editor | Show/hide split editor |
| Export Canvas as PNG / SVG | Save canvas artwork |
| Run Smoke Test | Execute built-in tests |
| Show Error History | View past errors |
| Go to Line | Jump to line number |
| Quick Reference | Show language reference |
| Keyboard Shortcuts | Show shortcut list |
| About Time Warp II | Show version info |
| Exit | Quit the application |
| Theme: *name* | Switch to a specific theme |
| Font Size: *name* | Switch to a specific font size |

---

## Speed Controls

Two speed sliders appear in the toolbar area:

### Execution Delay

Controls the pause between each line of code (0–500 ms). Useful for:
- **0 ms** — full speed execution
- **50–200 ms** — watch the program flow step by step
- **500 ms** — very slow, ideal for debugging logic

### Turtle Delay

Controls the pause between each turtle drawing command (0–200 ms). Useful for:
- **0 ms** — instant drawing
- **50–100 ms** — watch the turtle draw in real time
- **200 ms** — slow animation for presentations

Both values are saved between sessions.

---

## Canvas Export

After running a program that draws on the canvas:

### Export as PNG

**Program → Export Canvas as PNG...** — saves the canvas as a PNG image file using Pillow. If Pillow is not installed, falls back to PostScript capture.

### Export as SVG

**Program → Export Canvas as SVG...** — generates an SVG file by converting all canvas objects to SVG elements (lines, ovals, rectangles, text, polygons). This produces resolution-independent vector graphics.

---

## Themes & Fonts

### Colour Themes

Nine built-in themes available via **Preferences → Color Theme**:

| Theme | Style |
|-------|-------|
| Light | White background, dark text |
| Dark | Dark grey background, light text |
| Classic | Traditional white/cream appearance |
| Solarized Dark | Warm dark palette by Ethan Schoonover |
| Solarized Light | Warm light palette |
| Monokai | High-contrast dark theme |
| Dracula | Purple-tinted dark theme |
| Nord | Cool blue-grey dark theme |
| High Contrast | Pure black background, bright text |

Themes are applied instantly. The toolbar **🎨 Theme** button cycles through them.

### Auto Dark/Light Mode

**Preferences → Auto Dark/Light (follow OS)** — when enabled, the IDE attempts to detect your operating system's dark/light mode setting and applies a matching theme automatically.

### Font Size

Seven sizes via **Preferences → Font Size**:

| Name | Editor Size |
|------|-------------|
| Tiny | 8pt |
| Small | 10pt |
| Medium | 12pt (default) |
| Large | 14pt |
| Extra Large | 16pt |
| Huge | 18pt |
| Giant | 22pt |

You can also zoom with **Ctrl+Scroll Wheel**, **Ctrl+Plus**, or **Ctrl+Minus** to cycle through sizes.

### Font Family

**Preferences → Font Family** lists all monospace fonts installed on your system. Priority fonts (Courier, Consolas, Monaco, Fira Code, JetBrains Mono, etc.) appear first. All other monospace fonts are listed under a "More Fonts" submenu.

---

## Debug Mode

### Enable Debug Mode

**Debug → Enable Debug Mode** — toggles verbose debugging output. When enabled, the interpreter prints additional information about each executed line.

### Breakpoints

Breakpoints can be set programmatically. Use **Debug → Clear All Breakpoints** to remove them all.

### Error History

The interpreter records errors encountered during execution:
- **Debug → Show Error History** — displays a list of all errors from the current session
- **Debug → Clear Error History** — resets the error log

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **F5** | Run Program |
| **Escape** | Stop Program |
| **Ctrl+N** | New File |
| **Ctrl+O** | Open File |
| **Ctrl+S** | Save |
| **Ctrl+Shift+S** | Save As |
| **Ctrl+Q** | Exit |
| **Ctrl+Z** | Undo |
| **Ctrl+Y** / **Ctrl+Shift+Z** | Redo |
| **Ctrl+A** | Select All |
| **Ctrl+X** | Cut |
| **Ctrl+C** | Copy |
| **Ctrl+V** | Paste |
| **Ctrl+F** | Find |
| **Ctrl+H** | Replace |
| **Ctrl+G** | Go to Line |
| **Ctrl+Shift+P** | Command Palette |
| **Ctrl+Scroll** | Zoom in/out (font size) |
| **Ctrl+Plus** | Zoom in |
| **Ctrl+Minus** | Zoom out |
| **Tab** | Auto-complete keyword |
| **Enter** | Smart auto-indent |

---

## Settings & Persistence

All settings are stored in `~/.templecode_settings.json`:

```json
{
  "theme": "dark",
  "font_size": "medium",
  "font_family": "Courier",
  "recent_files": [],
  "auto_dark": true,
  "exec_speed": 0,
  "turtle_speed": 0
}
```

Settings are loaded at startup and saved whenever you change a preference. Delete this file to reset all settings to defaults.

---

## Example Programs

Load built-in examples from **Program → Load Example**. The menu is organised into sections:

### Getting Started
- **Hello World** — your first TempleCode program
- **Turtle Graphics Spiral** — Logo drawing basics
- **Quiz (PILOT style)** — interactive question/answer
- **Number Guessing Game** — BASIC game logic
- **Mandelbrot (Turtle Art)** — advanced fractal drawing

### BASIC Programs
- **Calculator** — arithmetic expression evaluator
- **Countdown Timer** — loop-based countdown
- **FizzBuzz** — classic programming exercise
- **Fibonacci Sequence** — mathematical series
- **Times Tables Trainer** — educational drill
- **Temperature Converter** — unit conversion
- **Dice Roller** — random number generation

### Interactive Programs
- **Science Quiz** — PILOT-style knowledge test
- **Adventure Story** — branching narrative
- **Interactive Drawing** — user-controlled turtle

### Turtle Art
- **Rainbow Spiral** — colourful spiral patterns
- **Shapes Gallery** — geometric shape showcase
- **Flower Garden** — procedural flower drawing
- **Kaleidoscope** — symmetrical patterns
- **Snowflake Fractal** — recursive Koch snowflake
- **Clock Face** — analogue clock drawing

---

## Next Steps

- **[LANGUAGE_TUTORIALS.md](LANGUAGE_TUTORIALS.md)** — learn TempleCode step by step
- **[KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md)** — printable shortcut reference
- **[THEMES_AND_FONTS.md](THEMES_AND_FONTS.md)** — detailed customisation guide
- **[../languages/TEMPLECODE_REFERENCE.md](../languages/TEMPLECODE_REFERENCE.md)** — complete language reference

---

*Time Warp II — User Guide*
*Copyright © 2025–2026 Honey Badger Universe*
