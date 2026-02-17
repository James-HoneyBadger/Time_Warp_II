# Technical Reference — Time Warp II Architecture

Comprehensive technical documentation for developers working on or extending Time Warp II.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Structure](#module-structure)
3. [Application Startup](#application-startup)
4. [Core Interpreter](#core-interpreter)
5. [TempleCode Executor](#templecode-executor)
6. [GUI System](#gui-system)
7. [Syntax Highlighting](#syntax-highlighting)
8. [Code Templates](#code-templates)
9. [Data Flow](#data-flow)
10. [Settings Persistence](#settings-persistence)
11. [Optimisation Modules](#optimisation-modules)
12. [Extension Points](#extension-points)
13. [Testing](#testing)
14. [Development Workflow](#development-workflow)

---

## Architecture Overview

### High-Level Design

Time Warp II is a **single-language IDE + interpreter** for TempleCode. The architecture has four layers:

```
┌─────────────────────────────────────────────────────────┐
│  TimeWarpII.py — TempleCodeApp (tkinter GUI)            │
│  Menu bar · Toolbar · Editor · Output · Canvas · Status │
├─────────────────────────────────────────────────────────┤
│  core/interpreter.py — TempleCodeInterpreter            │
│  Program loading · Line-by-line execution · I/O bridge  │
│  Variable store · Debug mode · Error history            │
├─────────────────────────────────────────────────────────┤
│  core/languages/templecode.py — TempleCodeExecutor      │
│  BASIC dispatch · PILOT dispatch · Logo dispatch        │
│  Expression evaluator · Turtle state · Procedures       │
├─────────────────────────────────────────────────────────┤
│  Support modules                                        │
│  config.py · syntax_highlighting.py · code_templates.py │
│  gui_optimizer.py · memory_manager.py · perf_optimizer  │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Unified language** — one `.tc` file mixes BASIC, PILOT, and Logo freely
2. **Layer separation** — GUI knows nothing about TempleCode syntax; the executor knows nothing about tkinter
3. **Single executor** — straightforward dispatch through one `execute_command()` entry point
4. **Instant feedback** — every line produces immediate output or canvas drawing
5. **Settings persistence** — theme, font, speed, and recent files survive restarts

---

## Module Structure

```
Time_Warp_II/
├── run.py                          # CLI launcher
├── run.sh / run.bat                # Shell / batch launchers
├── TimeWarpII.py                   # TempleCodeApp — main GUI (~1 900 lines)
├── core/
│   ├── __init__.py
│   ├── config.py                   # THEMES, FONT_SIZES, KEYWORDS, INDENT_OPENERS,
│   │                               #   PRIORITY_FONTS, WELCOME_MESSAGE
│   ├── interpreter.py              # TempleCodeInterpreter (~1 070 lines)
│   ├── features/
│   │   ├── code_templates.py       # 4 template categories
│   │   └── syntax_highlighting.py  # TempleCodeLexer (Pygments),
│   │                               #   SyntaxHighlightingText, LineNumberedText
│   ├── languages/
│   │   ├── __init__.py
│   │   └── templecode.py           # TempleCodeExecutor (~2 160 lines)
│   ├── optimizations/
│   │   ├── __init__.py
│   │   ├── gui_optimizer.py        # GUIOptimizer
│   │   ├── memory_manager.py       # MemoryManager
│   │   └── performance_optimizer.py # PerformanceOptimizer
│   └── utilities/
│       └── __init__.py
├── examples/templecode/            # 21 .tc example programs
├── tests/
│   ├── helpers.py                  # HeadlessApp, run_tc helper
│   ├── test_interpreter.py         # Interpreter unit tests
│   └── test_all_commands.py        # Full command coverage tests
├── scripts/
│   ├── run_tests.py
│   ├── launch.py
│   └── start.sh / launch_TimeWarpII.sh
└── docs/                           # This documentation suite
```

---

## Application Startup

### Entry Point

`run.py` (or `TimeWarpII.py` directly) imports and instantiates `TempleCodeApp`.

### TempleCodeApp.__init__() Sequence

1. Import `tkinter`, `scrolledtext`, `messagebox`, `filedialog`
2. Import `TempleCodeInterpreter` from `core.interpreter`
3. Import `SyntaxHighlightingText` and `LineNumberedText` from `core.features.syntax_highlighting`
4. Import constants from `core.config`: `THEMES`, `FONT_SIZES`, `KEYWORDS`, `INDENT_OPENERS`, etc.
5. Call `load_settings()` — reads `~/.templecode_settings.json`
6. Create `tk.Tk()` root window (1200×800 default)
7. Build menus (`_build_menus`)
8. Build layout (`_build_layout`) — editor, output, canvas, input bar
9. Build toolbar (`_build_toolbar`) — 7 buttons
10. Build speed controls (`_build_speed_controls`) — exec delay + turtle delay sliders
11. Build status bar (`_build_status_bar`)
12. Bind keyboard shortcuts (`_bind_keys`)
13. Apply saved theme, font size, and font family
14. Display welcome message in output panel
15. Enter `root.mainloop()`

### Settings File

`~/.templecode_settings.json` — loaded by `load_settings()`, saved by `save_settings()`.

```json
{
  "theme": "dark",
  "font_size": "medium",
  "font_family": "Courier",
  "recent_files": ["path/to/file.tc"],
  "auto_dark": true,
  "exec_speed": 0,
  "turtle_speed": 0
}
```

---

## Core Interpreter

### File: `core/interpreter.py` (~1 070 lines)

### TempleCodeInterpreter

The interpreter manages the full lifecycle of a TempleCode program.

**Key attributes:**

| Attribute | Type | Purpose |
|-----------|------|---------|
| `executor` | `TempleCodeExecutor` | The language executor instance |
| `variables` | `dict` | Shared variable store (BASIC + PILOT) |
| `program_lines` | `list` | Parsed lines of the current program |
| `output` | `list` | Accumulated output strings |
| `labels` | `dict` | PILOT `*label` → line-number mapping |
| `data_pointer` | `int` | Current position in `DATA` statements |
| `breakpoints` | `set` | Line numbers with breakpoints |
| `debug_mode` | `bool` | Verbose execution logging |
| `error_history` | `list` | Errors from all runs in this session |
| `running` | `bool` | Whether execution is active |
| `input_callback` | `callable` | GUI callback for `INPUT` / `A:` prompts |

**Key methods:**

| Method | Purpose |
|--------|---------|
| `execute(code)` | Full program execution — parse, run, return output |
| `execute_line(line)` | Execute a single line, delegating to the executor |
| `reset()` | Clear all state for a new run |
| `set_debug_mode(on)` | Toggle verbose logging |
| `request_input(prompt)` | Pause execution and invoke the GUI input callback |
| `add_output(text)` | Append to the output buffer |

### Execution Flow

```
execute(code: str) → list[str]
    │
    ├── reset() — clear variables, output, program counter
    ├── Parse code into lines
    ├── Pre-scan for labels (*label), DATA statements, line numbers
    │
    └── Line-by-line loop:
          ├── Check breakpoints → pause if hit
          ├── Check running flag → abort if False
          ├── executor.execute_command(line)
          │     ├── Route to _dispatch_basic()
          │     ├── Route to _dispatch_pilot()
          │     └── Route to _dispatch_logo()
          ├── Apply exec_speed delay
          └── Advance program counter (or jump via GOTO/J:)
```

### Error Handling

Every `execute_command()` call is wrapped in try/except. Errors are:
1. Caught and formatted with the offending line number
2. Appended to `error_history`
3. Added to output with an error tag (displayed in red)
4. Execution continues on the next line (unless `STOP` or `E:`)

---

## TempleCode Executor

### File: `core/languages/templecode.py` (~2 160 lines)

### TempleCodeExecutor

The executor is the largest module. It contains all command implementations for the three heritages.

### Line Routing

`execute_command(command)` determines which sub-system handles each line:

| Pattern | Detected as | Dispatch method |
|---------|-------------|-----------------|
| `^\d+\s` | Numbered BASIC line | `_dispatch_basic()` |
| `^[A-Z]:` (single letter + colon) | PILOT command | `_dispatch_pilot()` |
| `^\*\w+` | PILOT label | Skip (pre-scanned) |
| Starts with Logo keyword | Logo command | `_dispatch_logo()` |
| `^TO\s+\w+` | Logo procedure definition | `_handle_logo_define()` |
| `^REM\b`, `^'`, `^;` | Comment | Skip |
| Everything else | Unnumbered BASIC | `_dispatch_basic()` |

### BASIC Sub-system

**I/O:** `PRINT`, `INPUT`, `CLS`, `BEEP`
**Variables:** `LET`, `DIM`, `SWAP`, `INCR`, `DECR`
**Control flow:** `IF/THEN/ELSE/ELSEIF/ENDIF`, `FOR/TO/STEP/NEXT`, `WHILE/WEND`, `DO/LOOP/UNTIL`, `GOTO`, `GOSUB/RETURN`, `ON GOTO/GOSUB`, `SELECT CASE/END SELECT`, `EXIT`, `STOP`, `END`, `DELAY`
**Data:** `DATA`, `READ`, `RESTORE`
**Math functions:** `ABS`, `INT`, `SQR`, `RND`, `SIN`, `COS`, `TAN`, `LOG`, `EXP`, `MOD`
**String functions:** `LEFT$`, `RIGHT$`, `MID$`, `LEN`, `VAL`, `STR$`, `CHR$`, `ASC`, `UPPER`, `LOWER`
**Misc:** `TIMER`, `DATE$`, `TIME$`, `TAB`, `SPC`, `TYPE`

**Internal state used by BASIC:**

```python
self.arrays = {}          # DIM arrays
self.return_stack = []    # GOSUB return addresses
self.for_stacks = {}      # FOR loop state (var → {limit, step, line})
self.data_values = []     # Collected DATA values
```

### PILOT Sub-system

Each command is a single letter followed by a colon. Optional condition flag (Y/N) prefixes: `TY:`, `TN:`, `AY:`, etc.

| Command | Name | Behaviour |
|---------|------|-----------|
| `T:` | Type | Output text; `*var*` interpolates variables |
| `A:` | Accept | Read user input into `$answer` |
| `M:` | Match | Match `$answer` against comma-separated patterns; sets `$matched` and `$status` |
| `Y:` | Yes-branch | Execute only if last `M:` matched (`$status` = 1) |
| `N:` | No-branch | Execute only if last `M:` did not match |
| `J:` | Jump | Jump to `*label` |
| `C:` | Compute | Evaluate expression and store result |
| `E:` | End | Terminate program |
| `R:` | Remark | Comment (ignored) |
| `U:` | Use | Call a subroutine at `*label` |
| `L:` / `G:` / `S:` / `D:` / `P:` / `X:` | Extended | Additional PILOT commands |

**Internal state:**

```python
self.system_vars = {
    "answer": "",       # Last A: input
    "matched": "",      # Last M: result
    "status": 0,        # 1 = matched, 0 = not matched
}
```

### Logo Sub-system

**Movement:** `FORWARD`/`FD`, `BACK`/`BK`, `LEFT`/`LT`, `RIGHT`/`RT`, `HOME`, `SETXY`, `SETX`, `SETY`, `SETHEADING`/`SETH`
**Pen:** `PENUP`/`PU`, `PENDOWN`/`PD`, `SETCOLOR`, `SETPENSIZE`, `SETFILLCOLOR`, `SETBACKGROUND`
**Drawing shapes:** `CIRCLE`, `ARC`, `DOT`, `RECT`, `SQUARE`, `TRIANGLE`, `POLYGON`, `STAR`, `FILL`
**Turtle visibility:** `SHOWTURTLE`/`ST`, `HIDETURTLE`/`HT`
**Canvas:** `CLEARSCREEN`/`CS`, `WRAP`, `WINDOW`, `FENCE`
**Text:** `LABEL`, `STAMP`
**Control:** `REPEAT [ commands ]`
**Procedures:** `TO procname :param1 :param2 ... END`
**Variables:** `MAKE "varname value`
**Queries:** `HEADING`, `POS`, `TOWARDS`, `PENCOLOR?`, `PENSIZE?`

**Internal state:**

```python
self.turtle_x = 0.0
self.turtle_y = 0.0
self.turtle_heading = 0.0      # Degrees, 0 = north
self.pen_down = True
self.pen_color = "white"       # or "black" for light themes
self.pen_size = 1
self.fill_color = ""
self.turtle_visible = True
self.wrap_mode = "window"      # "wrap", "window", or "fence"
self.logo_procedures = {}      # TO name → {params, body}
```

### Expression Evaluator

The executor includes a built-in expression evaluator used by:
- `LET` assignments
- `IF` conditions
- `FOR` limits and steps
- `C:` compute
- Logo command arguments

It supports:
- Arithmetic: `+`, `-`, `*`, `/`, `^`, `MOD`
- Comparison: `=`, `<>`, `<`, `>`, `<=`, `>=`
- Logical: `AND`, `OR`, `NOT`
- String concatenation: `;` and `+`
- Function calls: `ABS()`, `SIN()`, `LEN()`, `LEFT$()`, etc.
- Variable references: bare names or `$name` (PILOT)

---

## GUI System

### File: `TimeWarpII.py` (~1 900 lines)

### TempleCodeApp Class

The entire GUI is a single class: `TempleCodeApp`. It owns all widgets and event handlers.

### Window Layout

```
root (tk.Tk) 1200×800
├── menu_bar (tk.Menu)
│   ├── File (New, Open, Save, Save As, Recent Files, Exit)
│   ├── Edit (Undo, Redo, Cut, Copy, Paste, Select All,
│   │         Clear Editor/Output/Graphics, Find, Replace,
│   │         Go to Line, Fold All, Unfold All)
│   ├── View (Split Editor toggle, Command Palette)
│   ├── Program (Run, Stop, Export PNG, Export SVG, Load Example)
│   ├── Debug (Enable Debug Mode, Clear Breakpoints,
│   │          Show/Clear Error History)
│   ├── Test (Run Smoke Test, Open Examples Directory)
│   ├── Preferences (Color Theme, Font Family, Font Size,
│   │                Auto Dark/Light)
│   ├── About (About Time Warp II)
│   └── Help (Quick Reference, Keyboard Shortcuts)
│
├── toolbar_frame (tk.Frame)
│   ├── 7 buttons: Run, Stop, New, Open, Save, Theme, Size
│   └── Speed controls: exec_delay (0–500ms), turtle_delay (0–200ms)
│
├── main_paned (tk.PanedWindow, HORIZONTAL)
│   ├── left_panel (editor)
│   │   ├── SyntaxHighlightingText (or LineNumberedText fallback)
│   │   └── optional split_editor (second SyntaxHighlightingText)
│   │
│   └── right_panel
│       ├── right_paned (tk.PanedWindow, VERTICAL)
│       │   ├── output_frame
│       │   │   ├── output_text (tk.scrolledtext.ScrolledText)
│       │   │   └── input_frame
│       │   │       ├── input_entry (tk.Entry)
│       │   │       └── submit_button (tk.Button)
│       │   └── canvas_frame
│       │       └── turtle_canvas (tk.Canvas)
│       └── (canvas resizes via <Configure> event)
│
└── status_bar (tk.Frame)
    ├── file_label — filename + dirty indicator (●)
    ├── cursor_label — Ln X, Col Y
    ├── theme_label — current theme name
    └── font_label — current font size
```

### Key Event Handlers

| Handler | Trigger | Action |
|---------|---------|--------|
| `run_code()` | F5, ▶ button | Get editor text → interpreter.execute() → display output + canvas |
| `stop_code()` | Escape, ■ button | Set interpreter.running = False |
| `_on_editor_return()` | Enter key | Smart auto-indent (2 spaces after block openers) |
| `_on_tab()` | Tab key | Autocomplete popup (87 keywords, max 20 shown) |
| `_highlight_current_line()` | KeyRelease, click | Shade the current line |
| `_mark_dirty()` | Any edit | Set dirty flag, update title/status |
| `_zoom(delta)` | Ctrl+scroll/+/- | Cycle through FONT_SIZE_ORDER |
| `show_command_palette()` | Ctrl+Shift+P | Toplevel with Listbox, filter by typing |
| `show_find_dialog()` | Ctrl+F | Find with case/word/regex options |
| `show_replace_dialog()` | Ctrl+H | Find + replace/replace-all |
| `show_goto_line_dialog()` | Ctrl+G | Jump to line number |
| `fold_all()` / `unfold_all()` | Menu | Hide/show block bodies |
| `_toggle_split_editor()` | View menu | Add/remove second editor pane |
| `export_canvas_png()` | Menu | Canvas → PNG via Pillow → PostScript fallback |
| `export_canvas_svg()` | Menu | Canvas → SVG via manual XML generation |
| `apply_theme(key)` | Menu/palette | Recolour all widgets from THEMES[key] |
| `apply_font_size(key)` | Menu/palette | Resize editor + output fonts |
| `apply_font_family(name)` | Menu | Change font face |

### Output Colouring

Output text is tagged for colour:
- `"error"` tag → `output_error` colour (red)
- `"warn"` tag → `output_warn` colour (yellow)
- `"ok"` tag → `output_ok` colour (green)
- Default → `text_fg` colour

### Canvas Export Details

**PNG export** (`export_canvas_png()`):
1. Try to grab canvas via Pillow's `ImageGrab`
2. Fallback: generate PostScript from canvas, convert via Pillow
3. Save with `filedialog.asksaveasfilename()`

**SVG export** (`export_canvas_svg()`):
1. Iterate all canvas items: `find_all()`
2. For each item type (line, oval, rectangle, text, polygon), emit SVG XML
3. Write to file with proper SVG header and viewBox

---

## Syntax Highlighting

### File: `core/features/syntax_highlighting.py`

### TempleCodeLexer (Pygments)

A custom Pygments lexer registered for the `templecode` language. It tokenises:

| Token type | Matches |
|------------|---------|
| `Keyword` | BASIC keywords (PRINT, FOR, IF, etc.) |
| `Name.Label` | PILOT prefixes (T:, A:, M:, etc.) |
| `Name.Builtin` | Logo commands (FORWARD, BACK, etc.) |
| `String` | Double-quoted strings |
| `Number` | Integer and float literals |
| `Comment` | REM lines, `'` prefix |
| `Operator` | `+`, `-`, `*`, `/`, `=`, `<>`, etc. |

### SyntaxHighlightingText

A `tk.Frame` subclass wrapping a `tk.Text` widget with:
- **Line number gutter** — synced via `<<Modified>>` and y-scroll events
- **Debounced highlighting** — syntax re-highlighted 300ms after last keystroke
- **Search support** — `find_text()`, `replace_text()`, `replace_all()`, `highlight_search_results()`

### LineNumberedText (Fallback)

If Pygments is unavailable, this provides the same line-number gutter without syntax colouring.

---

## Code Templates

### File: `core/features/code_templates.py`

Four template categories:

| Category | Templates |
|----------|-----------|
| **BASIC Basics** | Hello World, variables, loops, conditionals |
| **PILOT Interaction** | Quiz, input/match patterns |
| **Logo Graphics** | Shapes, spirals, procedures |
| **Mixed** | Programs combining all three heritages |

Templates are used by the IDE to provide starter code snippets.

---

## Data Flow

### Program Execution Pipeline

```
User clicks Run (F5)
     │
     ▼
TempleCodeApp.run_code()
     │
     ├── Get editor text
     ├── Clear output + canvas
     ├── Create/reset TempleCodeInterpreter
     │     └── Creates TempleCodeExecutor
     ├── Set interpreter.input_callback → GUI input handler
     ├── Set interpreter.canvas → turtle_canvas widget
     │
     ▼
interpreter.execute(code) — runs in main thread
     │
     ├── Parse lines
     ├── Pre-scan labels + DATA
     │
     └── For each line:
           │
           ├── executor.execute_command(line)
           │     │
           │     ├── BASIC path → modify variables, produce output
           │     ├── PILOT path → T: output, A: input, M: match
           │     └── Logo path  → draw on canvas, move turtle
           │
           ├── GUI update: root.update() — keeps UI responsive
           ├── Apply exec_speed delay (time.sleep)
           └── Check running flag
     │
     ▼
Output displayed in output_text widget
Canvas drawings visible on turtle_canvas
```

### Variable Scope Model

All variables share a single flat namespace in `interpreter.variables`:

```
interpreter.variables = {
    "x": 10,                # set by LET x = 10
    "name": "Alice",        # set by INPUT or LET
    "$answer": "yes",       # set by PILOT A:
    "$matched": "yes",      # set by PILOT M:
    "$status": 1,           # set by PILOT M:
}
```

Arrays (from `DIM`) are stored in `executor.arrays`.
Logo procedures (from `TO...END`) are stored in `executor.logo_procedures`.

---

## Settings Persistence

### File: `~/.templecode_settings.json`

**Functions** (in `TimeWarpII.py` top level):

| Function | Purpose |
|----------|---------|
| `load_settings()` | Read JSON; return defaults on error |
| `save_settings(data)` | Write JSON; silently fail on error |

**When settings are saved:**
- Theme change → immediate save
- Font size/family change → immediate save
- File open/save → update recent_files, save
- Speed slider change → save
- Auto-dark toggle → save
- On exit → save

**Recent files** (`MAX_RECENT = 10`): stored as absolute paths, most recent first.

---

## Optimisation Modules

### gui_optimizer.py — GUIOptimizer

Optimises tkinter rendering:
- Output text buffering (batch inserts)
- Refresh rate limiting (skip redundant `update()` calls)
- Widget state caching

### memory_manager.py — MemoryManager

- Tracks variable memory usage
- Enforces configurable memory limits
- Cleans up unused variables between runs

### performance_optimizer.py — PerformanceOptimizer

- Code caching for repeated executions
- Statement pre-parsing
- Loop optimisation hints

---

## Extension Points

### Adding a New TempleCode Command

1. **Choose heritage** — decide if the command belongs to BASIC, PILOT, or Logo
2. **Add to executor** — implement in `core/languages/templecode.py`:
   - BASIC: add a new branch in `_dispatch_basic()`
   - PILOT: add a new letter handler in `_dispatch_pilot()`
   - Logo: add a new keyword branch in `_dispatch_logo()`
3. **Update config** — add the keyword to `KEYWORDS` in `core/config.py`
4. **Update lexer** — add to the appropriate token list in `TempleCodeLexer`
5. **Add tests** — add test cases in `tests/test_all_commands.py`
6. **Update docs** — add to `TEMPLECODE_REFERENCE.md`

### Adding a New Theme

Add an entry to `THEMES` in `core/config.py`:

```python
"mytheme": {
    "name": "My Theme",
    "text_bg": "#...", "text_fg": "#...",
    "canvas_bg": "#...", "canvas_border": "#...",
    "root_bg": "#...", "frame_bg": "#...",
    "editor_frame_bg": "#...", "editor_frame_fg": "#...",
    "input_bg": "#...", "input_fg": "#...",
    "statusbar_bg": "#...", "statusbar_fg": "#...",
    "btn_bg": "#...", "btn_fg": "#...",
    "btn_hover": "#...",
    "highlight_line": "#...",
    "output_error": "#...", "output_warn": "#...", "output_ok": "#...",
},
```

Also add a `LINE_NUMBER_BG` entry. The theme appears in menus and the command palette automatically.

### Adding a New Font Size

Add an entry to `FONT_SIZES` in `core/config.py` and append its key to `FONT_SIZE_ORDER`.

### Adding an IDE Feature

1. Create module in `core/features/`
2. Import in `TempleCodeApp.__init__()`
3. Add menu entry in `_build_menus()`
4. Add command palette entry in `_palette_commands`
5. Optionally add a keyboard shortcut in `_bind_keys()`

---

## Testing

### Test Framework

Tests use Python's built-in `unittest`. Run with:

```bash
python scripts/run_tests.py
# or
python -m pytest tests/
```

### Test Files

| File | Coverage |
|------|----------|
| `tests/test_interpreter.py` | Interpreter lifecycle, reset, execute |
| `tests/test_all_commands.py` | Every BASIC, PILOT, and Logo command |
| `tests/helpers.py` | `HeadlessApp` (GUI-less test fixture), `run_tc()` helper |

### HeadlessApp

`tests/helpers.py` provides a `HeadlessApp` class that creates a `TempleCodeInterpreter` without a GUI, allowing commands to be tested in isolation:

```python
from tests.helpers import HeadlessApp

app = HeadlessApp()
output = app.run("PRINT 2 + 3")
assert "5" in output
```

### Smoke Test

The IDE includes a built-in **Test → Run Smoke Test** that executes a set of representative programs and reports pass/fail.

---

## Development Workflow

### Prerequisites

- Python 3.10+ (tested on 3.14)
- `pip install -r requirements.txt` (pygame-ce, pygments, Pillow)

### Running

```bash
# With auto-setup
./run.sh

# Direct
python run.py
```

### Code Standards

- PEP 8 style
- Docstrings on all public methods
- Type hints where practical
- Maximum line length: 120 characters

### Repository Structure Conventions

- Keep all language logic in `core/languages/templecode.py`
- Keep all GUI logic in `TimeWarpII.py`
- Keep configuration constants in `core/config.py`
- Keep feature modules in `core/features/`
- Keep optimisation modules in `core/optimizations/`
- Examples go in `examples/templecode/` with `.tc` extension

---

*Time Warp II — Technical Reference*
*Copyright © 2025 Honey Badger Universe*
