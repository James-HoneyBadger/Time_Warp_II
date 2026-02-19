#!/usr/bin/env python3
"""
Time Warp II - Single-Language Programming Environment

A single-language IDE for the TempleCode programming language,
a fusion of BASIC, PILOT, and Logo with integrated turtle graphics.

Copyright © 2025-2026 Honey Badger Universe. All rights reserved.

Features:
- TempleCode language with built-in examples
- Integrated turtle graphics for visual programming
- Multiple colour themes and font sizes
- File persistence for editor content
- Educational feedback and error messages
- Status bar, recent files, auto-indent, line highlighting
- Tab-completion, command palette, output colouring
- Ctrl+scroll zoom, code folding, split editor
- Execution / turtle speed controls, canvas export
"""
# pylint: disable=C0301,C0103,R1705,W0621,W0718,W0404,C0415,W1510

import sys
import json
import os
from pathlib import Path


# ---------------------------------------------------------------------------
#  Settings persistence
# ---------------------------------------------------------------------------

SETTINGS_FILE = Path.home() / ".templecode_settings.json"
MAX_RECENT = 10


def load_settings():
    """Load user settings from disk."""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {
        "theme": "dark", "font_size": "medium", "font_family": "Courier",
        "recent_files": [], "auto_dark": True,
        "exec_speed": 0, "turtle_speed": 0,
    }


def save_settings(data: dict):
    """Persist user settings to disk."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
#  Application class
# ---------------------------------------------------------------------------

class TempleCodeApp:
    """Main GUI application for Time Warp II."""

    def __init__(self):  # type: ignore[no-untyped-def]
        import tkinter as tk
        from tkinter import scrolledtext, messagebox, filedialog
        from core.interpreter import TempleCodeInterpreter
        from core.features.syntax_highlighting import SyntaxHighlightingText, LineNumberedText
        from core.config import (
            THEMES, LINE_NUMBER_BG, FONT_SIZES, FONT_SIZE_ORDER,
            PRIORITY_FONTS, WELCOME_MESSAGE, KEYWORDS, INDENT_OPENERS,
        )
        from core.features.ide_features import (
            WatchManager, Profiler, SnippetManager,
            UndoHistoryManager, format_code, parse_imports,
            build_import_graph, format_import_graph,
        )

        # Store module refs for use in methods
        self.tk = tk
        self.scrolledtext = scrolledtext
        self.messagebox = messagebox
        self.filedialog = filedialog
        self.THEMES = THEMES
        self.LINE_NUMBER_BG = LINE_NUMBER_BG
        self.FONT_SIZES = FONT_SIZES
        self.FONT_SIZE_ORDER = FONT_SIZE_ORDER
        self.PRIORITY_FONTS = PRIORITY_FONTS
        self.KEYWORDS = KEYWORDS
        self.INDENT_OPENERS = INDENT_OPENERS

        # GUI optimiser (optional)
        self.gui_optimizer = None
        try:
            from core.optimizations.gui_optimizer import initialize_gui_optimizer
            self._init_gui_optimizer = initialize_gui_optimizer
        except ImportError:
            self._init_gui_optimizer = None

        # Pygments availability
        try:
            import pygments  # noqa: F401
            self._pygments_ok = True
        except ImportError:
            self._pygments_ok = False

        # Saved preferences
        self._settings = load_settings()
        self.current_theme = self._settings.get("theme", "dark")
        self.current_font = self._settings.get("font_size", "medium")
        self.current_font_family = self._settings.get("font_family", "Courier")
        self.recent_files: list = self._settings.get("recent_files", [])
        self.auto_dark: bool = self._settings.get("auto_dark", True)
        self.exec_speed: int = self._settings.get("exec_speed", 0)
        self.turtle_speed: int = self._settings.get("turtle_speed", 0)

        # Current file path (for status bar)
        self.current_file_path: str = ""

        # Build the GUI
        self.root = tk.Tk()
        self.root.title("Time Warp II")
        self.root.geometry("1200x800")
        self.root.config(bg="#252526")

        if self._init_gui_optimizer:
            self.gui_optimizer = self._init_gui_optimizer(self.root)
            print("🚀 GUI optimizations enabled")
        else:
            print("ℹ️  GUI optimizations not available")

        # Widget refs (populated during layout)
        self.editor_text = None
        self.editor_text2 = None           # Feature 10: split editor
        self.output_text = None
        self.turtle_canvas = None
        self.input_entry = None
        self.input_buffer = []
        self.interpreter = None
        self._dirty = False                # unsaved‐changes flag
        self._is_running = False           # program‐execution flag

        # Layout frames (populated in _build_layout)
        self.left_panel = None
        self.right_panel = None
        self.editor_frame = None
        self.editor_frame2 = None           # split
        self.editor_paned = None            # split
        self.output_frame = None
        self.graphics_frame = None
        self.input_frame = None
        self.button_frame = None
        self.main_paned = None
        self.right_paned = None
        self.status_bar = None              # Feature 1
        self._status_labels = {}

        # Command palette data  (Feature 6)
        self._palette_commands = []

        # Autocomplete state (Feature 5)
        self._ac_popup = None

        # Speed controls (Features 12/13)
        self._speed_frame = None
        self._exec_slider = None
        self._turtle_slider = None

        # Font family menu lazy-load flag
        self._fonts_loaded = False

        # IDE feature managers
        self._watch_manager = WatchManager()
        self._profiler = Profiler()
        self._snippet_manager = SnippetManager()
        self._undo_history = UndoHistoryManager()
        self._format_code = format_code
        self._parse_imports = parse_imports
        self._build_import_graph = build_import_graph
        self._format_import_graph = format_import_graph

        self._build_menus(SyntaxHighlightingText, LineNumberedText)
        self._build_layout(SyntaxHighlightingText, LineNumberedText)
        self._build_input_bar()
        self._build_toolbar()
        self._build_speed_controls()
        self._build_status_bar()
        self._bind_keys()

        # Initialise interpreter
        self.interpreter = TempleCodeInterpreter(self.output_text)
        self.interpreter.ide_turtle_canvas = self.turtle_canvas
        self.interpreter.input_buffer = self.input_buffer
        self.interpreter._input_entry_widget = self.input_entry
        self.interpreter._input_entry_bg = "#1e1e1e"

        # Attach IDE features to interpreter
        self.interpreter.watch_manager = self._watch_manager
        self.interpreter.profiler = self._profiler

        # Configure output colour tags  (Feature 7)
        self._setup_output_tags()

        # Apply saved settings
        self.output_text.insert("1.0", WELCOME_MESSAGE)
        self.apply_theme(self.current_theme)
        self.apply_font_size(self.current_font)

        # Take initial undo snapshot
        self._undo_history.snapshot(
            self.editor_text.get("1.0", self.tk.END), "initial"
        )

        # Feature 15: auto dark/light based on OS
        if self.auto_dark:
            self._auto_detect_dark_mode()

        # Start status bar updater (Feature 1)
        self._status_bar_after_id = None
        self._update_status_bar()

        # Ensure closing the window via the X button goes through exit_app
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    # ==================================================================
    #  Persistence helper
    # ==================================================================

    def _save(self):
        save_settings({
            "theme": self.current_theme,
            "font_size": self.current_font,
            "font_family": self.current_font_family,
            "recent_files": self.recent_files[:MAX_RECENT],
            "auto_dark": self.auto_dark,
            "exec_speed": self.exec_speed,
            "turtle_speed": self.turtle_speed,
        })

    # ==================================================================
    #  Menu construction
    # ==================================================================

    def _build_menus(self, SyntaxHighlightingText, LineNumberedText):
        tk = self.tk
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar, bg="#252526")

        # --- File ---
        self._file_menu = file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open File...", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file_quick, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        # Recent files submenu (Feature 2)
        self._recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self._recent_menu)
        self._rebuild_recent_menu()
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Ctrl+Q")

        # --- Edit ---
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo_text, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo_text, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self._editor_event("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self._editor_event("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self._editor_event("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Editor", command=self.clear_editor)
        edit_menu.add_command(label="Clear Output", command=self.clear_output)
        edit_menu.add_command(label="Clear Graphics", command=self.clear_canvas)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.show_find_dialog, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.show_replace_dialog, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Go to Line...", command=self.show_goto_line_dialog, accelerator="Ctrl+G")
        edit_menu.add_separator()
        # Feature 11: code folding
        edit_menu.add_command(label="Fold All Blocks", command=self.fold_all)
        edit_menu.add_command(label="Unfold All", command=self.unfold_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Format Code", command=self._format_editor_code,
                              accelerator="Ctrl+Shift+F")
        edit_menu.add_command(label="Insert Snippet...", command=self._show_snippet_picker,
                              accelerator="Ctrl+J")
        edit_menu.add_command(label="Manage Snippets...", command=self._show_snippet_manager)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo History...", command=self._show_undo_history)

        # --- View ---  (Feature 10: split editor)
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        self._split_var = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(
            label="Split Editor", variable=self._split_var,
            command=self._toggle_split_editor)
        view_menu.add_separator()
        view_menu.add_command(label="Command Palette...", command=self.show_command_palette,
                              accelerator="Ctrl+Shift+P")

        # --- Program ---
        program_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Program", menu=program_menu)
        program_menu.add_command(label="Run Program", command=self.run_code, accelerator="F5")
        program_menu.add_command(label="Stop Program", command=self.stop_code, accelerator="Ctrl+Break")
        program_menu.add_separator()
        # Feature 14: export turtle graphics
        program_menu.add_command(label="Export Canvas as PNG...", command=self.export_canvas_png)
        program_menu.add_command(label="Export Canvas as SVG...", command=self.export_canvas_svg)
        program_menu.add_separator()
        program_menu.add_command(label="Show Import Graph", command=self._show_import_graph)
        program_menu.add_separator()
        examples_menu = tk.Menu(program_menu, tearoff=0)
        program_menu.add_cascade(label="Load Example", menu=examples_menu)
        for item in [
            ("Hello World",            "examples/templecode/hello.tc"),
            ("Turtle Graphics Spiral", "examples/templecode/spiral.tc"),
            ("Quiz (PILOT style)",     "examples/templecode/quiz.tc"),
            ("Number Guessing Game",   "examples/templecode/guess.tc"),
            ("Mandelbrot (Turtle Art)", "examples/templecode/mandelbrot.tc"),
            None,  # separator
            ("Calculator",             "examples/templecode/calculator.tc"),
            ("Countdown Timer",        "examples/templecode/countdown.tc"),
            ("FizzBuzz",               "examples/templecode/fizzbuzz.tc"),
            ("Fibonacci Sequence",     "examples/templecode/fibonacci.tc"),
            ("Times Tables Trainer",   "examples/templecode/timestables.tc"),
            ("Temperature Converter",  "examples/templecode/temperature.tc"),
            ("Dice Roller",            "examples/templecode/dice.tc"),
            None,  # separator
            ("Science Quiz",           "examples/templecode/science_quiz.tc"),
            ("Adventure Story",        "examples/templecode/adventure.tc"),
            ("Interactive Drawing",    "examples/templecode/interactive_drawing.tc"),
            None,  # separator
            ("Rainbow Spiral",         "examples/templecode/rainbow.tc"),
            ("Shapes Gallery",         "examples/templecode/shapes.tc"),
            ("Flower Garden",          "examples/templecode/flower.tc"),
            ("Kaleidoscope",           "examples/templecode/kaleidoscope.tc"),
            ("Snowflake Fractal",      "examples/templecode/snowflake.tc"),
            ("Clock Face",             "examples/templecode/clock.tc"),
        ]:
            if item is None:
                examples_menu.add_separator()
            else:
                examples_menu.add_command(label=item[0], command=lambda p=item[1]: self.load_example(p))

        # --- Debug ---
        debug_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Debug", menu=debug_menu)
        self._debug_var = tk.BooleanVar(value=False)
        debug_menu.add_checkbutton(
            label="Enable Debug Mode", variable=self._debug_var,
            command=lambda: self.interpreter and self.interpreter.set_debug_mode(self._debug_var.get()),
        )
        debug_menu.add_separator()
        debug_menu.add_command(label="Add Watch Expression...", command=self._add_watch_dialog)
        debug_menu.add_command(label="Show Watches", command=self._show_watches)
        debug_menu.add_command(label="Clear All Watches",
                               command=lambda: (self._watch_manager.clear(),
                                                self._output("👁  All watches cleared.\n", "out_ok")))
        debug_menu.add_separator()
        debug_menu.add_command(label="Clear All Breakpoints",
                               command=lambda: self.interpreter and self.interpreter.breakpoints.clear())
        debug_menu.add_separator()
        debug_menu.add_command(label="Show Error History", command=self.show_error_history)
        debug_menu.add_command(label="Clear Error History",
                               command=lambda: setattr(self.interpreter, 'error_history', []) if self.interpreter else None)
        debug_menu.add_separator()
        # Profiler
        self._profiler_var = tk.BooleanVar(value=False)
        debug_menu.add_checkbutton(
            label="Enable Profiler", variable=self._profiler_var,
            command=lambda: setattr(self._profiler, 'enabled', self._profiler_var.get()),
        )
        debug_menu.add_command(label="Show Profiler Report", command=self._show_profiler_report)

        # --- Test ---
        test_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Test", menu=test_menu)
        test_menu.add_command(label="Run Smoke Test", command=self.run_smoke_test)
        test_menu.add_separator()
        test_menu.add_command(
            label="Open Examples Directory",
            command=lambda: __import__('subprocess').run(["xdg-open", "examples"]),
        )

        # --- Preferences ---
        prefs_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Preferences", menu=prefs_menu)

        # Theme submenu
        theme_menu = tk.Menu(prefs_menu, tearoff=0)
        prefs_menu.add_cascade(label="Color Theme", menu=theme_menu)
        for key, data in self.THEMES.items():
            theme_menu.add_command(label=data["name"], command=lambda k=key: self.apply_theme(k))

        # Font family submenu
        self._font_family_menu = tk.Menu(prefs_menu, tearoff=0)
        prefs_menu.add_cascade(label="Font Family", menu=self._font_family_menu)
        self._fonts_loaded = False
        self._font_family_menu.add_command(label="Loading...", state=tk.DISABLED)
        self._font_family_menu.bind("<Map>", lambda e: self._populate_font_menu())

        # Font size submenu
        font_size_menu = tk.Menu(prefs_menu, tearoff=0)
        prefs_menu.add_cascade(label="Font Size", menu=font_size_menu)
        for key, data in self.FONT_SIZES.items():
            font_size_menu.add_command(label=data["name"], command=lambda k=key: self.apply_font_size(k))

        prefs_menu.add_separator()
        # Feature 15: auto dark mode toggle
        self._auto_dark_var = tk.BooleanVar(value=self.auto_dark)
        prefs_menu.add_checkbutton(
            label="Auto Dark/Light (follow OS)",
            variable=self._auto_dark_var,
            command=self._toggle_auto_dark)

        # --- About ---
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="About Time Warp II", command=self.show_about)

        # --- Help ---
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick Reference", command=self.show_quick_reference)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_keyboard_shortcuts)

        # Build command palette entries (Feature 6)
        self._palette_commands = [
            ("New File",             self.new_file),
            ("Open File",            self.load_file),
            ("Save File",            self.save_file_quick),
            ("Save File As",         self.save_file),
            ("Run Program",          self.run_code),
            ("Stop Program",         self.stop_code),
            ("Find...",              self.show_find_dialog),
            ("Replace...",           self.show_replace_dialog),
            ("Undo",                 self.undo_text),
            ("Redo",                 self.redo_text),
            ("Select All",           self.select_all),
            ("Clear Editor",         self.clear_editor),
            ("Clear Output",         self.clear_output),
            ("Clear Graphics",       self.clear_canvas),
            ("Fold All Blocks",      self.fold_all),
            ("Unfold All",           self.unfold_all),
            ("Toggle Split Editor",  self._toggle_split_editor),
            ("Export Canvas as PNG",  self.export_canvas_png),
            ("Export Canvas as SVG",  self.export_canvas_svg),
            ("Show Import Graph",    self._show_import_graph),
            ("Format Code",          self._format_editor_code),
            ("Insert Snippet",       self._show_snippet_picker),
            ("Manage Snippets",      self._show_snippet_manager),
            ("Undo History",         self._show_undo_history),
            ("Add Watch Expression", self._add_watch_dialog),
            ("Show Watches",         self._show_watches),
            ("Show Profiler Report", self._show_profiler_report),
            ("Run Smoke Test",       self.run_smoke_test),
            ("Show Error History",   self.show_error_history),
            ("Go to Line",           self.show_goto_line_dialog),
            ("Quick Reference",      self.show_quick_reference),
            ("Keyboard Shortcuts",   self.show_keyboard_shortcuts),
            ("About Time Warp II", self.show_about),
            ("Exit",                 self.exit_app),
        ]
        for key, data in self.THEMES.items():
            self._palette_commands.append((f"Theme: {data['name']}", lambda k=key: self.apply_theme(k)))
        for key, data in self.FONT_SIZES.items():
            self._palette_commands.append((f"Font Size: {data['name']}", lambda k=key: self.apply_font_size(k)))

    # ==================================================================
    #  Layout construction
    # ==================================================================

    def _build_layout(self, SyntaxHighlightingText, LineNumberedText):
        tk = self.tk

        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#252526")
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel — editor(s)
        self.left_panel = tk.Frame(self.main_paned, bg="#252526")
        self.main_paned.add(self.left_panel, width=400)

        # Editor paned window for split view (Feature 10)
        self.editor_paned = tk.PanedWindow(self.left_panel, orient=tk.VERTICAL, sashwidth=5, bg="#252526")
        self.editor_paned.pack(fill=tk.BOTH, expand=True)

        self.editor_frame = tk.LabelFrame(
            self.editor_paned, text="TempleCode Editor", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )
        self.editor_paned.add(self.editor_frame)

        if self._pygments_ok:
            self.editor_text = SyntaxHighlightingText(
                self.editor_frame, language="templecode", theme="dark",
                bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        else:
            self.editor_text = LineNumberedText(
                self.editor_frame, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        self.editor_text.pack(fill=tk.BOTH, expand=True)

        # Second editor (hidden by default — Feature 10)
        self.editor_frame2 = tk.LabelFrame(
            self.editor_paned, text="Editor 2", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )
        if self._pygments_ok:
            self.editor_text2 = SyntaxHighlightingText(
                self.editor_frame2, language="templecode", theme="dark",
                bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        else:
            self.editor_text2 = LineNumberedText(
                self.editor_frame2, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        self.editor_text2.pack(fill=tk.BOTH, expand=True)

        # Right panel — output + graphics
        self.right_panel = tk.Frame(self.main_paned, bg="#252526")
        self.main_paned.add(self.right_panel, width=800)

        self.right_paned = tk.PanedWindow(self.right_panel, orient=tk.VERTICAL, sashwidth=5, bg="#252526")
        self.right_paned.pack(fill=tk.BOTH, expand=True)

        self.output_frame = tk.LabelFrame(
            self.right_paned, text="Output", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )
        self.right_paned.add(self.output_frame, height=300)

        self.output_text = self.scrolledtext.ScrolledText(
            self.output_frame, wrap=tk.WORD, font=("Courier", 10),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.graphics_frame = tk.LabelFrame(
            self.right_paned, text="Turtle Graphics", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )
        self.right_paned.add(self.graphics_frame, height=300)

        self.turtle_canvas = tk.Canvas(
            self.graphics_frame, width=600, height=400,
            bg="#2d2d2d", highlightthickness=1, highlightbackground="#3e3e3e",
        )
        self.turtle_canvas.pack(fill=tk.BOTH, expand=True)
        # Update turtle centre when canvas is resized
        self.turtle_canvas.bind("<Configure>", self._on_canvas_resize)

    # ==================================================================
    #  Input bar, toolbar, speed controls, status bar
    # ==================================================================

    def _build_input_bar(self):
        tk = self.tk
        self.input_frame = tk.Frame(self.root, bg="#252526")
        self.input_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(self.input_frame, text="Input:", font=("Arial", 10),
                 bg="#252526", fg="#d4d4d4").pack(side=tk.LEFT, padx=(0, 5))
        self.input_entry = tk.Entry(
            self.input_frame, font=("Courier", 10),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self._submit_input())
        tk.Button(self.input_frame, text="Submit", command=self._submit_input,
                  bg="#3e3e3e", fg="#d4d4d4").pack(side=tk.LEFT)

    def _build_toolbar(self):
        """Feature 9: styled flat toolbar buttons with hover effect."""
        tk = self.tk
        self.button_frame = tk.Frame(self.root, bg="#252526")
        self.button_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        buttons = [
            ("▶  Run",          self.run_code,     "#4CAF50", "white",   True),
            ("⏹  Stop",         self.stop_code,    "#d32f2f", "white",   True),
            ("📂 Open",         self.load_file,    "#3e3e3e", "#d4d4d4", False),
            ("💾 Save",         self.save_file_quick, "#3e3e3e", "#d4d4d4", False),
            ("🗑  Clear Editor", self.clear_editor, "#3e3e3e", "#d4d4d4", False),
            ("📄 Clear Output", self.clear_output,  "#3e3e3e", "#d4d4d4", False),
            ("🎨 Clear Canvas", self.clear_canvas,  "#3e3e3e", "#d4d4d4", False),
        ]
        for label, cmd, bg, fg, bold in buttons:
            font = ("Arial", 10, "bold") if bold else ("Arial", 10)
            btn = tk.Button(
                self.button_frame, text=label, command=cmd,
                bg=bg, fg=fg, font=font, padx=12, pady=4,
                relief=tk.FLAT, bd=0, cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=3)
            # Hover effect
            default_bg = bg
            btn.bind("<Enter>", lambda e, b=btn, c=default_bg: b.config(bg=self._lighter(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=default_bg: b.config(bg=c))

    def _build_speed_controls(self):
        """Features 12 & 13: execution and turtle speed sliders."""
        tk = self.tk
        self._speed_frame = tk.Frame(self.root, bg="#252526")
        self._speed_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(self._speed_frame, text="Exec delay (ms):", font=("Arial", 9),
                 bg="#252526", fg="#888").pack(side=tk.LEFT, padx=(0, 2))
        self._exec_slider = tk.Scale(
            self._speed_frame, from_=0, to=500, orient=tk.HORIZONTAL,
            length=120, bg="#252526", fg="#aaa", troughcolor="#1e1e1e",
            highlightthickness=0, sliderlength=14, font=("Arial", 8),
            command=lambda v: setattr(self, 'exec_speed', int(v)),
        )
        self._exec_slider.set(self.exec_speed)
        self._exec_slider.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(self._speed_frame, text="Turtle delay (ms):", font=("Arial", 9),
                 bg="#252526", fg="#888").pack(side=tk.LEFT, padx=(0, 2))
        self._turtle_slider = tk.Scale(
            self._speed_frame, from_=0, to=200, orient=tk.HORIZONTAL,
            length=120, bg="#252526", fg="#aaa", troughcolor="#1e1e1e",
            highlightthickness=0, sliderlength=14, font=("Arial", 8),
            command=lambda v: setattr(self, 'turtle_speed', int(v)),
        )
        self._turtle_slider.set(self.turtle_speed)
        self._turtle_slider.pack(side=tk.LEFT)

    def _build_status_bar(self):
        """Feature 1: status bar showing cursor position, theme, file path."""
        tk = self.tk
        self.status_bar = tk.Frame(self.root, bg="#007acc", height=22)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        font = ("Arial", 9)
        self._status_labels["file"] = tk.Label(
            self.status_bar, text="  No file  ", bg="#007acc", fg="white",
            font=font, anchor="w",
        )
        self._status_labels["file"].pack(side=tk.LEFT, padx=(5, 20))

        self._status_labels["cursor"] = tk.Label(
            self.status_bar, text="Ln 1, Col 1", bg="#007acc", fg="white",
            font=font, anchor="w",
        )
        self._status_labels["cursor"].pack(side=tk.LEFT, padx=(0, 20))

        self._status_labels["theme"] = tk.Label(
            self.status_bar, text=self.THEMES[self.current_theme]["name"],
            bg="#007acc", fg="white", font=font, anchor="e",
        )
        self._status_labels["theme"].pack(side=tk.RIGHT, padx=(0, 10))

        self._status_labels["font"] = tk.Label(
            self.status_bar, text=f"{self.current_font_family} {self.FONT_SIZES[self.current_font]['editor']}pt",
            bg="#007acc", fg="white", font=font, anchor="e",
        )
        self._status_labels["font"].pack(side=tk.RIGHT, padx=(0, 15))

    def _update_status_bar(self):
        """Periodically refresh the status bar cursor position."""
        try:
            widget = self.editor_text
            idx = widget.index(self.tk.INSERT) if hasattr(widget, 'index') else "1.0"
            line, col = idx.split(".")
            self._status_labels["cursor"].config(text=f"Ln {line}, Col {int(col)+1}")
        except Exception:
            pass
        self._status_bar_after_id = self.root.after(250, self._update_status_bar)

    # ==================================================================
    #  Key bindings
    # ==================================================================

    def _bind_keys(self):
        """Bind keyboard shortcuts to IDE actions."""
        r = self.root
        r.bind("<F5>", lambda e: self.run_code())
        r.bind("<Control-n>", lambda e: self.new_file())
        r.bind("<Control-o>", lambda e: self.load_file())
        r.bind("<Control-s>", lambda e: self.save_file_quick())
        r.bind("<Control-Shift-S>", lambda e: self.save_file())
        r.bind("<Control-q>", lambda e: self.exit_app())
        r.bind("<Control-z>", lambda e: self.undo_text())
        r.bind("<Control-y>", lambda e: self.redo_text())
        r.bind("<Control-Shift-Z>", lambda e: self.redo_text())
        r.bind("<Control-a>", lambda e: self.select_all())
        r.bind("<Control-f>", lambda e: self.show_find_dialog())
        r.bind("<Control-h>", lambda e: self.show_replace_dialog())
        r.bind("<Control-g>", lambda e: self.show_goto_line_dialog())
        r.bind("<Control-Shift-P>", lambda e: self.show_command_palette())  # Feature 6
        r.bind("<Escape>", lambda e: self.stop_code())

        # Feature 8: Ctrl+scroll zoom
        r.bind("<Control-Button-4>", lambda e: self._zoom(1))   # scroll up
        r.bind("<Control-Button-5>", lambda e: self._zoom(-1))  # scroll down
        r.bind("<Control-MouseWheel>", lambda e: self._zoom(1 if e.delta > 0 else -1))
        r.bind("<Control-plus>", lambda e: self._zoom(1))
        r.bind("<Control-minus>", lambda e: self._zoom(-1))
        r.bind("<Control-equal>", lambda e: self._zoom(1))

        # New feature key bindings
        r.bind("<Control-Shift-F>", lambda e: self._format_editor_code())
        r.bind("<Control-j>", lambda e: self._show_snippet_picker())
        r.bind("<Control-J>", lambda e: self._show_snippet_picker())

        # Feature 3: auto-indent  /  Feature 5: tab-completion
        # We bind to the inner text widget, not the frame
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        text_w.bind("<Return>", self._on_editor_return)
        text_w.bind("<Tab>", self._on_tab)

        # Feature 4: highlight current line on cursor move + update status bar
        text_w.bind("<KeyRelease>", lambda e: (self._highlight_current_line(), self._mark_dirty()))
        text_w.bind("<ButtonRelease-1>", lambda e: self._highlight_current_line())

        # Right-click context menus
        text_w.bind("<Button-3>", self._show_editor_context_menu)

    # ==================================================================
    #  Feature 3: Auto-indent
    # ==================================================================

    def _on_editor_return(self, event):
        """Insert newline with smart auto-indent."""
        widget = event.widget
        # Get the current line before cursor
        idx = widget.index(self.tk.INSERT)
        line_num = idx.split(".")[0]
        line_text = widget.get(f"{line_num}.0", f"{line_num}.end")
        # Measure leading whitespace
        stripped = line_text.lstrip()
        indent = len(line_text) - len(stripped)
        base_indent = line_text[:indent]
        # Check if line starts with an indent-opener keyword
        first_word = stripped.split()[0].upper().rstrip(":") if stripped.split() else ""
        extra = "  " if first_word in self.INDENT_OPENERS else ""
        # Insert newline + indent
        widget.insert(self.tk.INSERT, "\n" + base_indent + extra)
        widget.see(self.tk.INSERT)
        return "break"  # prevent default newline

    # ==================================================================
    #  Feature 4: Highlight current line
    # ==================================================================

    def _highlight_current_line(self):
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        text_w.tag_remove("current_line", "1.0", self.tk.END)
        current = text_w.index(self.tk.INSERT)
        line = current.split(".")[0]
        text_w.tag_add("current_line", f"{line}.0", f"{line}.end+1c")
        theme = self.THEMES.get(self.current_theme, self.THEMES["dark"])
        text_w.tag_configure("current_line", background=theme.get("highlight_line", "#2a2d2e"))
        # Keep below syntax tags
        text_w.tag_lower("current_line")

    # ==================================================================
    #  Feature 5: Tab-completion
    # ==================================================================

    def _on_tab(self, event):
        """Try to autocomplete the current word; fall back to inserting spaces."""
        widget = event.widget
        idx = widget.index(self.tk.INSERT)
        line_num, col = idx.split(".")
        line_text = widget.get(f"{line_num}.0", idx)
        # Extract the partial word being typed
        import re
        m = re.search(r'([A-Za-z_$:]+)$', line_text)
        if not m:
            widget.insert(self.tk.INSERT, "  ")
            return "break"
        prefix = m.group(1).upper()
        matches = [k for k in self.KEYWORDS if k.upper().startswith(prefix)]
        if len(matches) == 1:
            # Single match — complete it
            completion = matches[0][len(prefix):]
            widget.insert(self.tk.INSERT, completion)
        elif len(matches) > 1:
            self._show_autocomplete(widget, matches)
        else:
            widget.insert(self.tk.INSERT, "  ")
        return "break"

    def _show_autocomplete(self, widget, matches):
        """Show a small popup with matching keywords."""
        if self._ac_popup:
            self._ac_popup.destroy()
        tk = self.tk
        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.attributes("-topmost", True)
        self._ac_popup = popup

        # Position near cursor
        try:
            bbox = widget.bbox(tk.INSERT)
            if bbox:
                x = widget.winfo_rootx() + bbox[0]
                y = widget.winfo_rooty() + bbox[1] + bbox[3]
            else:
                x, y = widget.winfo_rootx() + 50, widget.winfo_rooty() + 50
        except Exception:
            x, y = widget.winfo_rootx() + 50, widget.winfo_rooty() + 50

        popup.geometry(f"+{x}+{y}")

        lb = tk.Listbox(
            popup, font=("Courier", 10), height=min(len(matches), 8),
            bg="#252526", fg="#d4d4d4", selectbackground="#094771",
            selectforeground="white", bd=1, relief=tk.SOLID)
        lb.pack()
        for m in matches[:20]:
            lb.insert(tk.END, m)
        lb.selection_set(0)

        def _pick(evt=None):
            sel = lb.curselection()
            if sel:
                chosen = lb.get(sel[0])
                # Find partial already typed
                idx = widget.index(tk.INSERT)
                line_num = idx.split(".")[0]
                line_text = widget.get(f"{line_num}.0", idx)
                import re
                m2 = re.search(r'([A-Za-z_$:]+)$', line_text)
                prefix_len = len(m2.group(1)) if m2 else 0
                widget.insert(tk.INSERT, chosen[prefix_len:])
            popup.destroy()
            self._ac_popup = None

        def _dismiss(evt=None):
            popup.destroy()
            self._ac_popup = None

        lb.bind("<Return>", _pick)
        lb.bind("<Double-1>", _pick)
        lb.bind("<Escape>", _dismiss)
        lb.focus_set()
        popup.bind("<FocusOut>", _dismiss)

    # ==================================================================
    #  Feature 6: Command Palette
    # ==================================================================

    def show_command_palette(self):
        """Display a searchable command palette for quick access to IDE actions."""
        tk = self.tk
        dlg = tk.Toplevel(self.root)
        dlg.title("Command Palette")
        dlg.geometry("450x350")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.resizable(True, True)

        theme = self.THEMES.get(self.current_theme, self.THEMES["dark"])
        dlg.config(bg=theme["frame_bg"])

        sv = tk.StringVar()
        entry = tk.Entry(dlg, textvariable=sv, font=("Courier", 12),
                         bg=theme["input_bg"], fg=theme["input_fg"],
                         insertbackground=theme["input_fg"])
        entry.pack(fill=tk.X, padx=10, pady=(10, 5))
        entry.focus()

        lb = tk.Listbox(
            dlg, font=("Courier", 11),
            bg=theme["text_bg"], fg=theme["text_fg"],
            selectbackground="#094771", selectforeground="white",
            bd=0, highlightthickness=0)
        lb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        all_cmds = self._palette_commands

        def _filter(*_):
            q = sv.get().lower()
            lb.delete(0, tk.END)
            for name, _ in all_cmds:
                if q in name.lower():
                    lb.insert(tk.END, name)
            if lb.size() > 0:
                lb.selection_set(0)

        sv.trace_add("write", _filter)
        _filter()

        def _run(evt=None):
            sel = lb.curselection()
            if sel:
                name = lb.get(sel[0])
                for n, fn in all_cmds:
                    if n == name:
                        dlg.destroy()
                        self.root.after(50, fn)
                        return

        def _nav(evt):
            cur = lb.curselection()
            idx = cur[0] if cur else 0
            if evt.keysym == "Down":
                idx = min(idx + 1, lb.size() - 1)
            elif evt.keysym == "Up":
                idx = max(idx - 1, 0)
            lb.selection_clear(0, tk.END)
            lb.selection_set(idx)
            lb.see(idx)
            return "break"

        entry.bind("<Return>", _run)
        entry.bind("<Up>",   _nav)
        entry.bind("<Down>", _nav)
        lb.bind("<Double-1>", _run)
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    # ==================================================================
    #  Feature 7: Output colouring
    # ==================================================================

    def _setup_output_tags(self):
        """Configure colour tags on the output widget."""
        theme = self.THEMES.get(self.current_theme, self.THEMES["dark"])
        self.output_text.tag_configure("out_error", foreground=theme.get("output_error", "#f44747"))
        self.output_text.tag_configure("out_warn",  foreground=theme.get("output_warn",  "#cca700"))
        self.output_text.tag_configure("out_ok",    foreground=theme.get("output_ok",    "#6a9955"))

    def _output(self, text, tag=None):
        """Insert text into the output widget, optionally with a colour tag."""
        if tag:
            self.output_text.insert(self.tk.END, text, tag)
        else:
            self.output_text.insert(self.tk.END, text)
        self.output_text.see(self.tk.END)

    # ==================================================================
    #  Feature 8: Ctrl+scroll zoom
    # ==================================================================

    def _zoom(self, direction):
        """Move to the next/previous font size."""
        order = self.FONT_SIZE_ORDER
        try:
            idx = order.index(self.current_font)
        except ValueError:
            idx = 2  # medium
        new_idx = max(0, min(len(order) - 1, idx + direction))
        if new_idx != idx:
            self.apply_font_size(order[new_idx])

    # ==================================================================
    #  Feature 10: Split editor
    # ==================================================================

    def _toggle_split_editor(self):
        if self.editor_frame2 in self.editor_paned.panes():
            # Hide second editor
            self.editor_paned.forget(self.editor_frame2)
            self._split_var.set(False)
        else:
            self.editor_paned.add(self.editor_frame2)
            self._split_var.set(True)
            self._apply_theme_to_editor(self.editor_text2)

    def _apply_theme_to_editor(self, editor):
        """Apply current theme to an extra editor widget."""
        theme = self.THEMES[self.current_theme]
        if hasattr(editor, 'text'):
            editor.text.config(bg=theme["text_bg"], fg=theme["text_fg"],
                               insertbackground=theme["text_fg"])
            if hasattr(editor, 'set_theme'):
                editor.set_theme(self.current_theme)
        else:
            editor.config(bg=theme["text_bg"], fg=theme["text_fg"],
                          insertbackground=theme["text_fg"])
        sz = self.FONT_SIZES[self.current_font]
        if hasattr(editor, 'set_font'):
            editor.set_font((self.current_font_family, sz["editor"]))
        else:
            editor.config(font=(self.current_font_family, sz["editor"]))

    # ==================================================================
    #  Feature 11: Code folding (simple)
    # ==================================================================

    def fold_all(self):
        """Hide lines between matching block openers and closers."""
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        content = text_w.get("1.0", self.tk.END)
        lines = content.split("\n")
        _OPENERS = {"FOR", "WHILE", "IF", "DO", "SELECT", "REPEAT"}
        _CLOSERS = {"NEXT", "WEND", "ENDIF", "LOOP", "END SELECT"}
        stack = []
        regions = []
        for i, line in enumerate(lines):
            word = line.strip().split()[0].upper() if line.strip() else ""
            if word in _OPENERS:
                stack.append(i)
            elif word in _CLOSERS or line.strip().upper() in _CLOSERS:
                if stack:
                    start = stack.pop()
                    if i - start > 1:
                        regions.append((start + 1, i - 1))  # fold inner lines
        # Elide inner lines from bottom to top to keep line numbers stable
        for start, end in reversed(regions):
            tag = f"fold_{start}_{end}"
            text_w.tag_add(tag, f"{start + 1}.0", f"{end + 1}.end+1c")
            text_w.tag_configure(tag, elide=True)

    def unfold_all(self):
        """Remove all code-folding tags to expand collapsed regions."""
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        for tag in list(text_w.tag_names()):
            if tag.startswith("fold_"):
                text_w.tag_delete(tag)

    # ==================================================================
    #  Feature 14: Export canvas
    # ==================================================================

    def export_canvas_png(self):
        """Export the turtle canvas to a PNG file (requires Ghostscript or PIL)."""
        filename = self.filedialog.asksaveasfilename(
            title="Export Canvas as PNG", defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        )
        if not filename:
            return
        try:
            # Try Pillow first
            from PIL import Image
            # Save canvas as PostScript, convert with PIL
            ps_file = filename + ".ps"
            self.turtle_canvas.postscript(file=ps_file, colormode="color")
            img = Image.open(ps_file)
            img.save(filename, "PNG")
            os.remove(ps_file)
            self._output(f"📸 Canvas exported to {filename}\n", "out_ok")
        except ImportError:
            # Fallback: save PostScript directly
            ps_name = filename.replace(".png", ".ps")
            self.turtle_canvas.postscript(file=ps_name, colormode="color")
            self._output(f"📸 Canvas exported as PostScript to {ps_name}\n(Install Pillow for PNG)\n", "out_warn")
        except Exception as e:
            self._output(f"❌ Export failed: {e}\n", "out_error")

    def export_canvas_svg(self):
        """Export the turtle canvas to a crude SVG file."""
        filename = self.filedialog.asksaveasfilename(
            title="Export Canvas as SVG", defaultextension=".svg",
            filetypes=[("SVG Image", "*.svg"), ("All Files", "*.*")],
        )
        if not filename:
            return
        try:
            w = self.turtle_canvas.winfo_width()
            h = self.turtle_canvas.winfo_height()
            items = self.turtle_canvas.find_all()
            svg_lines = [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}">',
                f'<rect width="{w}" height="{h}" fill="{self.turtle_canvas.cget("bg")}"/>',
            ]
            for item in items:
                itype = self.turtle_canvas.type(item)
                coords = self.turtle_canvas.coords(item)
                fill = self.turtle_canvas.itemcget(item, "fill") or "none"
                outline = self.turtle_canvas.itemcget(item, "outline") or "none"
                width = self.turtle_canvas.itemcget(item, "width") or "1"
                if itype == "line" and len(coords) >= 4:
                    svg_lines.append(
                        f'<line x1="{coords[0]}" y1="{coords[1]}" '
                        f'x2="{coords[2]}" y2="{coords[3]}" '
                        f'stroke="{fill}" stroke-width="{width}"/>'
                    )
                elif itype == "oval" and len(coords) >= 4:
                    cx = (coords[0] + coords[2]) / 2
                    cy = (coords[1] + coords[3]) / 2
                    rx = abs(coords[2] - coords[0]) / 2
                    ry = abs(coords[3] - coords[1]) / 2
                    svg_lines.append(
                        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                        f'fill="{fill}" stroke="{outline}" stroke-width="{width}"/>'
                    )
                elif itype == "rectangle" and len(coords) >= 4:
                    svg_lines.append(
                        f'<rect x="{coords[0]}" y="{coords[1]}" '
                        f'width="{coords[2]-coords[0]}" height="{coords[3]-coords[1]}" '
                        f'fill="{fill}" stroke="{outline}" stroke-width="{width}"/>'
                    )
            svg_lines.append("</svg>")
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(svg_lines))
            self._output(f"📸 Canvas exported to {filename}\n", "out_ok")
        except Exception as e:
            self._output(f"❌ SVG export failed: {e}\n", "out_error")

    # ==================================================================
    #  Feature 15: Auto dark/light mode
    # ==================================================================

    def _auto_detect_dark_mode(self):
        """Try to detect OS dark mode and apply matching theme."""
        try:
            # Freedesktop / GNOME
            import subprocess
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True, timeout=2,
            )
            out = result.stdout.strip().strip("'\"")
            if "dark" in out.lower():
                if self.current_theme in ("light", "classic", "solarized_light"):
                    self.apply_theme("dark")
            elif "light" in out.lower() or "default" in out.lower():
                if self.current_theme in ("dark", "monokai", "dracula", "nord"):
                    self.apply_theme("light")
        except Exception:
            pass  # silently ignore on non-GNOME systems

    def _toggle_auto_dark(self):
        self.auto_dark = self._auto_dark_var.get()
        if self.auto_dark:
            self._auto_detect_dark_mode()
        self._save()

    # ==================================================================
    #  File operations
    # ==================================================================

    def _add_recent(self, path):
        """Feature 2: track recent files."""
        path = str(Path(path).resolve())
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:MAX_RECENT]
        self._rebuild_recent_menu()
        self._save()

    def _rebuild_recent_menu(self):
        self._recent_menu.delete(0, self.tk.END)
        if not self.recent_files:
            self._recent_menu.add_command(label="(none)", state=self.tk.DISABLED)
        else:
            for fp in self.recent_files:
                short = os.path.basename(fp)
                self._recent_menu.add_command(
                    label=f"{short}  ({fp})",
                    command=lambda p=fp: self._open_path(p),
                )
            self._recent_menu.add_separator()
            self._recent_menu.add_command(label="Clear Recent Files", command=self._clear_recent)

    def _clear_recent(self):
        self.recent_files.clear()
        self._rebuild_recent_menu()
        self._save()

    def _open_path(self, filepath):
        """Open a file by path (used by recent-files menu)."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor_text.delete("1.0", self.tk.END)
            self.editor_text.insert("1.0", content)
            self.current_file_path = filepath
            self._status_labels["file"].config(text=f"  {os.path.basename(filepath)}")
            self._dirty = False
            self._update_title()
            self._add_recent(filepath)
            self._output(f"📂 Loaded: {filepath}\n", "out_ok")
        except Exception as e:
            self._output(f"❌ Failed to open {filepath}: {e}\n", "out_error")

    def new_file(self):
        """Clear the editor and start a new file, prompting to discard unsaved changes."""
        if self._dirty:
            if not self.messagebox.askyesno("Unsaved Changes",
                                            "You have unsaved changes. Discard?"):
                return
        self.editor_text.delete("1.0", self.tk.END)
        self.current_file_path = ""
        self._dirty = False
        self._update_title()
        self._status_labels["file"].config(text="  No file  ")
        self._output("📄 New file created\n")

    def load_file(self):
        """Open a file dialog to select and load a TempleCode program."""
        filename = self.filedialog.askopenfilename(
            title="Open Program File",
            filetypes=[("TempleCode Files", "*.tc"), ("All Files", "*.*")],
        )
        if filename:
            self._open_path(filename)

    def save_file(self):
        """Open a Save As dialog and write the editor contents to a file."""
        filename = self.filedialog.asksaveasfilename(
            title="Save Program File", defaultextension=".tc",
            filetypes=[("TempleCode Files", "*.tc"), ("All Files", "*.*")],
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.editor_text.get("1.0", self.tk.END))
                self.current_file_path = filename
                self._status_labels["file"].config(text=f"  {os.path.basename(filename)}")
                self.root.title(f"Time Warp II — {os.path.basename(filename)}")
                self._add_recent(filename)
                self._output(f"💾 Saved: {filename}\n", "out_ok")
                self._dirty = False
                self._update_title()
            except Exception as e:
                self._output(f"❌ Save failed: {e}\n", "out_error")

    def save_file_quick(self):
        """Save to the current file path without prompting. Falls back to Save As."""
        if self.current_file_path and os.path.isfile(self.current_file_path):
            try:
                with open(self.current_file_path, "w", encoding="utf-8") as f:
                    f.write(self.editor_text.get("1.0", self.tk.END))
                self._output(f"💾 Saved: {self.current_file_path}\n", "out_ok")
                self._dirty = False
                self._update_title()
            except Exception as e:
                self._output(f"❌ Save failed: {e}\n", "out_error")
        else:
            self.save_file()

    def load_example(self, filepath):
        """Load an example TempleCode program from the given filepath."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor_text.delete("1.0", self.tk.END)
            self.editor_text.insert("1.0", content)
            self.current_file_path = filepath
            self._status_labels["file"].config(text=f"  {os.path.basename(filepath)}")
            self._output(f"📚 Loaded example: {filepath}\n", "out_ok")
        except Exception as e:
            self._output(f"❌ Failed to load example: {e}\n", "out_error")

    def exit_app(self):
        """Save state and exit, prompting if there are unsaved changes."""
        self._save()
        if self._dirty:
            if not self.messagebox.askyesno("Unsaved Changes",
                                            "You have unsaved changes. Exit anyway?"):
                return
        # Cancel the recurring status bar updater before destroying the window
        if getattr(self, '_status_bar_after_id', None) is not None:
            self.root.after_cancel(self._status_bar_after_id)
            self._status_bar_after_id = None
        self.root.destroy()

    # ==================================================================
    #  Dirty flag & title helpers
    # ==================================================================

    def _mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            self._update_title()
        # Schedule an undo snapshot (debounced via after)
        if hasattr(self, '_undo_snapshot_after_id'):
            try:
                self.root.after_cancel(self._undo_snapshot_after_id)
            except Exception:
                pass
        self._undo_snapshot_after_id = self.root.after(
            1000, self._take_undo_snapshot
        )

    def _take_undo_snapshot(self):
        """Take a snapshot for the undo history manager."""
        try:
            content = self.editor_text.get("1.0", self.tk.END)
            self._undo_history.snapshot(content, "edit")
        except Exception:
            pass

    def _update_title(self):
        base = "Time Warp II"
        if self.current_file_path:
            base += f" — {os.path.basename(self.current_file_path)}"
        if self._dirty:
            base += " •"
        self.root.title(base)

    # ==================================================================
    #  Edit operations
    # ==================================================================

    def _editor_event(self, event_name):
        try:
            self.editor_text.event_generate(event_name)
        except Exception:
            pass

    def undo_text(self):
        """Undo the last edit operation in the editor."""
        try:
            self.editor_text.edit_undo()
        except Exception:
            pass

    def redo_text(self):
        """Redo the last undone edit operation in the editor."""
        try:
            self.editor_text.edit_redo()
        except Exception:
            pass

    def select_all(self):
        """Select all text in the editor."""
        self.editor_text.tag_add("sel", "1.0", self.tk.END)
        self.editor_text.mark_set("insert", "1.0")
        self.editor_text.see("insert")
        return "break"

    def clear_editor(self):
        """Delete all text from the editor widget."""
        self.editor_text.delete("1.0", self.tk.END)

    def clear_output(self):
        """Delete all text from the output panel."""
        self.output_text.delete("1.0", self.tk.END)

    def clear_canvas(self):
        """Clear the turtle graphics canvas and reset the turtle state."""
        self.turtle_canvas.delete("all")
        if hasattr(self.interpreter, 'turtle_graphics') and self.interpreter.turtle_graphics:
            tg = self.interpreter.turtle_graphics
            tg["x"] = 0.0
            tg["y"] = 0.0
            tg["heading"] = 0.0
            tg["lines"] = []
            self.interpreter.update_turtle_display()
        self._output("🎨 Canvas cleared\n")

    # ==================================================================
    #  Run / execute
    # ==================================================================

    def run_code(self):
        """Execute the current editor contents as a TempleCode program."""
        if self._is_running:
            self._output("⚠️  A program is already running. Stop it first.\n", "out_warn")
            return

        import threading as _threading

        code = self.editor_text.get("1.0", self.tk.END)
        self.output_text.delete("1.0", self.tk.END)
        self._output("🚀 Running program...\n\n", "out_ok")
        self._is_running = True

        # Pass speed settings to the interpreter
        if hasattr(self.interpreter, 'exec_delay_ms'):
            self.interpreter.exec_delay_ms = self.exec_speed
        if hasattr(self.interpreter, 'turtle_delay_ms'):
            self.interpreter.turtle_delay_ms = self.turtle_speed

        # One-time setup on the main thread
        self.interpreter.ide_turtle_canvas = self.turtle_canvas
        if self.turtle_canvas is not None:
            self.turtle_canvas.delete("all")
        self.interpreter.turtle_graphics = None
        self.interpreter.init_turtle_graphics()
        self.interpreter.clear_turtle_screen()

        def _run():
            try:
                self.interpreter.run_program(code, language="templecode")
                self.root.after(0, lambda: self._output("\n✅ Program completed.\n", "out_ok"))
            except Exception as e:  # pylint: disable=broad-except
                self.root.after(0, lambda err=e: self._output(f"\n❌ Error: {err}\n", "out_error"))
            finally:
                self.root.after(0, self._on_run_finished)

        _threading.Thread(target=_run, daemon=True).start()

    def _on_run_finished(self):
        """Called on the main thread when the interpreter thread completes."""
        self._is_running = False

    def stop_code(self):
        """Stop a running program by setting the interpreter's running flag to False."""
        if self.interpreter and self._is_running:
            self.interpreter.running = False
            # Unblock the interpreter thread if it is waiting for user input
            if (hasattr(self.interpreter, '_input_event')
                    and self.interpreter._input_event is not None):
                self.interpreter._input_result = ""
                self.interpreter._input_event.set()
            # _is_running is cleared by _on_run_finished once the thread exits
            self._output("\n🛑 Program stopped by user.\n", "out_warn")

    def _submit_input(self):
        """Submit input text to the running interpreter or queue it."""
        value = self.input_entry.get()
        self.input_entry.delete(0, self.tk.END)

        # Signal the interpreter thread waiting on threading.Event
        if (self.interpreter
                and hasattr(self.interpreter, '_input_event')
                and self.interpreter._input_event is not None):
            self.interpreter._input_result = value
            self.interpreter._input_event.set()
        else:
            # Not waiting — queue it for later use
            self.input_buffer.append(value)
            self._output(f">> {value}\n")

    # ==================================================================
    #  Theme & font
    # ==================================================================

    @staticmethod
    def _lighter(hex_color):
        """Return a slightly lighter version of a hex colour (for hover)."""
        try:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) != 6:
                return "#505050"
            r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            r = min(255, r + 25)
            g = min(255, g + 25)
            b = min(255, b + 25)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return "#505050"

    def apply_theme(self, theme_key):
        """Apply the specified color theme to all editor and UI widgets."""
        tk = self.tk
        theme = self.THEMES[theme_key]

        self._apply_theme_editors(tk, theme, theme_key)
        self._apply_theme_panels(tk, theme)
        self._apply_theme_buttons(tk, theme)
        self._apply_theme_statusbar(theme)
        self._apply_theme_output_tags(theme)

        # Update status bar theme label
        if "theme" in self._status_labels:
            self._status_labels["theme"].config(text=theme["name"])

        self.current_theme = theme_key
        self._save()
        self._highlight_current_line()

    def _apply_theme_editors(self, tk, theme, theme_key):
        """Apply theme colours to editor and output widgets."""
        for editor in (self.editor_text, self.editor_text2):
            if editor is None:
                continue
            if hasattr(editor, 'text'):
                editor.text.config(
                    bg=theme["text_bg"], fg=theme["text_fg"],
                    insertbackground=theme["text_fg"],
                )
                if hasattr(editor, 'set_theme'):
                    editor.set_theme(theme_key)
                if hasattr(editor, 'line_numbers'):
                    editor.line_numbers.config(
                        bg=self.LINE_NUMBER_BG.get(theme_key, "#1e1e1e")
                    )
            else:
                editor.config(
                    bg=theme["text_bg"], fg=theme["text_fg"],
                    insertbackground=theme["text_fg"],
                )

        self.output_text.config(
            bg=theme["text_bg"], fg=theme["text_fg"],
            insertbackground=theme["text_fg"],
        )
        self.turtle_canvas.config(
            bg=theme["canvas_bg"], highlightbackground=theme["canvas_border"],
        )

    def _apply_theme_panels(self, tk, theme):
        """Apply theme colours to panels, frames, inputs, and labels."""
        self.root.config(bg=theme["root_bg"])
        for panel in (self.left_panel, self.right_panel):
            panel.config(bg=theme["frame_bg"])
        for frame in (self.editor_frame, self.editor_frame2,
                      self.output_frame, self.graphics_frame):
            if frame:
                frame.config(bg=theme["editor_frame_bg"],
                             fg=theme["editor_frame_fg"])
        for f in (self.input_frame, self.button_frame, self._speed_frame):
            if f:
                f.config(bg=theme["frame_bg"])
        self.input_entry.config(
            bg=theme["input_bg"], fg=theme["input_fg"],
            insertbackground=theme["input_fg"],
        )
        # Keep interpreter aware of the current input-bar bg colour
        if self.interpreter:
            self.interpreter._input_entry_bg = theme["input_bg"]  # pylint: disable=protected-access

        # Labels in input frame / speed frame
        for container in (self.input_frame, self._speed_frame):
            if not container:
                continue
            for w in container.winfo_children():
                if isinstance(w, tk.Label):
                    w.config(bg=theme["frame_bg"],
                             fg=theme.get("text_fg", "#aaa"))
                elif isinstance(w, tk.Scale):
                    w.config(bg=theme["frame_bg"],
                             fg=theme.get("text_fg", "#aaa"),
                             troughcolor=theme["text_bg"])

        # Paned windows
        for pw in (self.main_paned, self.right_paned, self.editor_paned):
            try:
                pw.config(bg=theme["frame_bg"])
            except Exception:
                pass

    def _apply_theme_buttons(self, tk, theme):
        """Apply theme colours to toolbar and submit buttons."""
        btn_bg = theme.get("btn_bg", theme.get("input_bg", "#3e3e3e"))
        btn_fg = theme.get("btn_fg", theme.get("input_fg", "#d4d4d4"))
        for w in self.button_frame.winfo_children():
            if isinstance(w, tk.Button):
                # Keep Run button green
                if "Run" in str(w.cget("text")):
                    w.config(fg="white")
                else:
                    w.config(bg=btn_bg, fg=btn_fg)
                    # Re-bind hover with new theme colour
                    w.bind("<Enter>",
                           lambda e, b=w, c=btn_bg: b.config(
                               bg=self._lighter(c)))
                    w.bind("<Leave>",
                           lambda e, b=w, c=btn_bg: b.config(bg=c))

        # Submit button
        for w in self.input_frame.winfo_children():
            if isinstance(w, tk.Button):
                w.config(bg=btn_bg, fg=btn_fg)

    def _apply_theme_statusbar(self, theme):
        """Apply theme colours to the status bar."""
        sb_bg = theme.get("statusbar_bg", "#007acc")
        sb_fg = theme.get("statusbar_fg", "#ffffff")
        if self.status_bar:
            self.status_bar.config(bg=sb_bg)
            for lbl in self._status_labels.values():
                lbl.config(bg=sb_bg, fg=sb_fg)

    def _apply_theme_output_tags(self, theme):
        """Apply theme colours to output text tags."""
        self.output_text.tag_configure(
            "out_error", foreground=theme.get("output_error", "#f44747"))
        self.output_text.tag_configure(
            "out_warn", foreground=theme.get("output_warn", "#cca700"))
        self.output_text.tag_configure(
            "out_ok", foreground=theme.get("output_ok", "#6a9955"))

    def apply_font_size(self, size_key):
        """Apply the specified font size preset to editor and output widgets."""
        sz = self.FONT_SIZES[size_key]
        for editor in (self.editor_text, self.editor_text2):
            if editor is None:
                continue
            if hasattr(editor, 'set_font'):
                editor.set_font((self.current_font_family, sz["editor"]))
            else:
                editor.config(font=(self.current_font_family, sz["editor"]))
        self.output_text.config(font=(self.current_font_family, sz["output"]))
        self.current_font = size_key
        if "font" in self._status_labels:
            self._status_labels["font"].config(text=f"{self.current_font_family} {sz['editor']}pt")
        self._save()

    def apply_font_family(self, family):
        """Apply the specified font family to editor and output widgets."""
        sz = self.FONT_SIZES[self.current_font]
        for editor in (self.editor_text, self.editor_text2):
            if editor is None:
                continue
            if hasattr(editor, 'set_font'):
                editor.set_font((family, sz["editor"]))
            else:
                editor.config(font=(family, sz["editor"]))
        self.output_text.config(font=(family, sz["output"]))
        self.current_font_family = family
        if "font" in self._status_labels:
            self._status_labels["font"].config(text=f"{family} {sz['editor']}pt")
        self._save()

    def _populate_font_menu(self):
        if self._fonts_loaded:
            return
        self._fonts_loaded = True
        self._font_family_menu.delete(0, self.tk.END)

        import tkinter.font as tkfont
        all_fonts = sorted(set(tkfont.families()))
        priority = [f for f in self.PRIORITY_FONTS if f in all_fonts]
        others = [f for f in all_fonts if f not in self.PRIORITY_FONTS]
        available = priority + others

        for name in available[:25]:
            self._font_family_menu.add_command(
                label=name, command=lambda n=name: self.apply_font_family(n),
            )
        if len(available) > 25:
            self._font_family_menu.add_separator()
            more = self.tk.Menu(self._font_family_menu, tearoff=0)
            self._font_family_menu.add_cascade(label="More Fonts...", menu=more)
            for name in available[25:]:
                more.add_command(label=name, command=lambda n=name: self.apply_font_family(n))

    # ==================================================================
    #  Dialogs
    # ==================================================================

    def show_find_dialog(self):
        """Display a Find dialog for searching text in the editor."""
        tk = self.tk
        dlg = tk.Toplevel(self.root)
        dlg.title("Find")
        dlg.geometry("400x150")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        search_var = tk.StringVar()
        se = tk.Entry(dlg, textvariable=search_var, width=30)
        se.grid(row=0, column=1, padx=5, pady=5)
        se.focus()

        opts = tk.Frame(dlg)
        opts.grid(row=1, column=0, columnspan=2, pady=5)
        case_var, whole_var, regex_var = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
        tk.Checkbutton(opts, text="Case sensitive", variable=case_var).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(opts, text="Whole word", variable=whole_var).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(opts, text="Regex", variable=regex_var).pack(side=tk.LEFT, padx=5)

        def do_find():
            term = search_var.get()
            if not term:
                return
            self.editor_text.clear_search_highlights()
            match = self.editor_text.find_text(
                term, start_pos=self.editor_text.index(tk.INSERT),
                case_sensitive=case_var.get(), whole_word=whole_var.get(), regex=regex_var.get(),
            )
            if match:
                s, e = match
                self.editor_text.tag_remove("sel", "1.0", tk.END)
                self.editor_text.tag_add("sel", s, e)
                self.editor_text.mark_set(tk.INSERT, e)
                self.editor_text.see(s)
                self.editor_text.highlight_search_results(
                    term, case_sensitive=case_var.get(),
                    whole_word=whole_var.get(), regex=regex_var.get(),
                )
                self._output(f"Found '{term}' at {s}\n")
            else:
                self._output(f"'{term}' not found\n", "out_warn")

        bf = tk.Frame(dlg)
        bf.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(bf, text="Find", command=do_find, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(bf, text="Find Next", command=do_find, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(bf, text="Close", command=dlg.destroy, width=10).pack(side=tk.LEFT, padx=5)
        se.bind('<Return>', lambda e: do_find())
        dlg.bind('<Escape>', lambda e: dlg.destroy())

    def show_replace_dialog(self):
        """Display a Find & Replace dialog for the editor."""
        tk = self.tk
        dlg = tk.Toplevel(self.root)
        dlg.title("Replace")
        dlg.geometry("400x180")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        search_var = tk.StringVar()
        tk.Entry(dlg, textvariable=search_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dlg, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        replace_var = tk.StringVar()
        tk.Entry(dlg, textvariable=replace_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        opts = tk.Frame(dlg)
        opts.grid(row=2, column=0, columnspan=2, pady=5)
        case_var, whole_var, regex_var = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
        tk.Checkbutton(opts, text="Case sensitive", variable=case_var).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(opts, text="Whole word", variable=whole_var).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(opts, text="Regex", variable=regex_var).pack(side=tk.LEFT, padx=5)

        def do_replace():
            s, r = search_var.get(), replace_var.get()
            if not s:
                return
            replaced = self.editor_text.replace_text(
                s, r, start_pos=self.editor_text.index(tk.INSERT),
                case_sensitive=case_var.get(), whole_word=whole_var.get(), regex=regex_var.get(),
            )
            if replaced:
                self._output(f"Replaced '{s}' with '{r}'\n", "out_ok")
                self.editor_text.highlight_search_results(
                    s, case_sensitive=case_var.get(),
                    whole_word=whole_var.get(), regex=regex_var.get(),
                )
            else:
                self._output(f"'{s}' not found\n", "out_warn")

        def do_replace_all():
            s, r = search_var.get(), replace_var.get()
            if not s:
                return
            count = self.editor_text.replace_all(
                s, r, case_sensitive=case_var.get(),
                whole_word=whole_var.get(), regex=regex_var.get(),
            )
            self._output(f"Replaced {count} occurrence(s) of '{s}' with '{r}'\n", "out_ok")
            self.editor_text.clear_search_highlights()

        bf = tk.Frame(dlg)
        bf.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(bf, text="Replace", command=do_replace, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(bf, text="Replace All", command=do_replace_all, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(bf, text="Close", command=dlg.destroy, width=10).pack(side=tk.LEFT, padx=5)
        dlg.bind('<Escape>', lambda e: dlg.destroy())

    def show_error_history(self):
        """Display a window listing all errors from the last interpretation."""
        if not self.interpreter or not self.interpreter.error_history:
            self.messagebox.showinfo("Error History", "No errors recorded.")
            return
        tk = self.tk
        win = tk.Toplevel(self.root)
        win.title("Error History")
        win.geometry("600x400")
        tw = self.scrolledtext.ScrolledText(win, wrap=tk.WORD)
        tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for i, err in enumerate(self.interpreter.error_history[-10:], 1):
            tw.insert(tk.END, f"{i}. Line {err.get('line', 'N/A')}: {err['message']}\n")
        tw.config(state=tk.DISABLED)

    def show_about(self):
        """Display the About dialog with version and credits."""
        sep = "-" * 32
        self.messagebox.showinfo("Time Warp II", (
            f"{sep}\n"
            "Time Warp II\nVersion 2.0.0\n\n"
            "A single-language IDE for TempleCode,\n"
            "a fusion of BASIC, PILOT, and Logo\n"
            "inspired by the early 1990s.\n\n"
            "FEATURES:\n"
            "  • BASIC (PRINT, LET, IF/ELSEIF, FOR, ON GOTO)\n"
            "  • PILOT (T:, A:, M:, Y:, N:, J:, C:, G:)\n"
            "  • Logo turtle (FORWARD, RIGHT, REPEAT, LABEL)\n"
            "  • Built-in example programs\n"
            "  • Turtle canvas with PNG/SVG export\n"
            "  • 9 colour themes (auto dark/light)\n"
            "  • Tab-completion & Command Palette\n"
            "  • Code folding, split editor, auto-indent\n"
            "  • Execution & turtle speed controls\n"
            "  • Save / Save As, dirty flag, recent files\n"
            "  • Stop button, Quick Reference, Go to Line\n"
            "  • Right-click context menus\n\n"
            f"{sep}\n"
            "Copyright © 2025-2026 Honey Badger Universe"
        ))

    # ==================================================================
    #  Testing
    # ==================================================================

    def run_smoke_test(self):
        """Run a quick smoke test to verify interpreter functionality."""
        tk = self.tk
        self.output_text.delete("1.0", tk.END)
        self._output("🧪 Running smoke test...\n")
        try:
            r = self.interpreter.evaluate_expression("2 + 3")
            ok = r == 5
            self._output(f"{'✅' if ok else '❌'} Basic evaluation: {'PASS' if ok else 'FAIL'}\n",
                         "out_ok" if ok else "out_error")
            self.interpreter.variables['TEST_VAR'] = 42
            ok = self.interpreter.variables.get('TEST_VAR') == 42
            self._output(f"{'✅' if ok else '❌'} Variable assignment: {'PASS' if ok else 'FAIL'}\n",
                         "out_ok" if ok else "out_error")
            ok2 = self.interpreter.load_program('PRINT "Test passed!"')
            self._output(f"{'✅' if ok2 else '❌'} Program loading: {'PASS' if ok2 else 'FAIL'}\n",
                         "out_ok" if ok2 else "out_error")
            self._output("\n🎉 Smoke test completed!\n", "out_ok")
        except Exception as e:
            self._output(f"\n❌ Smoke test failed: {e}\n", "out_error")

    # ==================================================================
    #  Utility
    # ==================================================================

    @staticmethod
    def _panes_list(pw):
        """Return list of pane names from a PanedWindow, cross-version safe."""
        try:
            return list(pw.panes())
        except Exception:
            return []

    # ==================================================================
    #  Canvas resize handler
    # ==================================================================

    def _on_canvas_resize(self, event):
        """Keep the turtle centre in sync when the canvas is resized."""
        if (self.interpreter
                and hasattr(self.interpreter, 'turtle_graphics')
                and self.interpreter.turtle_graphics):
            self.interpreter.turtle_graphics["center_x"] = event.width // 2
            self.interpreter.turtle_graphics["center_y"] = event.height // 2

    # ==================================================================
    #  Right-click context menus
    # ==================================================================

    def _show_editor_context_menu(self, event):
        tk = self.tk
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Cut",   command=lambda: self._editor_event("<<Cut>>"))
        menu.add_command(label="Copy",  command=lambda: self._editor_event("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self._editor_event("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=self.select_all)
        menu.add_separator()
        menu.add_command(label="Go to Line...", command=self.show_goto_line_dialog)
        menu.add_command(label="Find...", command=self.show_find_dialog)
        menu.add_command(label="Replace...", command=self.show_replace_dialog)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # ==================================================================
    #  Go to Line dialog
    # ==================================================================

    def show_goto_line_dialog(self):
        """Display a dialog to jump to a specific line number."""
        tk = self.tk
        dlg = tk.Toplevel(self.root)
        dlg.title("Go to Line")
        dlg.geometry("300x100")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Line number:").pack(padx=10, pady=(10, 0), anchor="w")
        line_var = tk.StringVar()
        entry = tk.Entry(dlg, textvariable=line_var, width=20)
        entry.pack(padx=10, pady=5, fill=tk.X)
        entry.focus()

        def _goto():
            try:
                num = int(line_var.get())
                text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
                text_w.mark_set(tk.INSERT, f"{num}.0")
                text_w.see(f"{num}.0")
                self._highlight_current_line()
                dlg.destroy()
            except ValueError:
                pass

        entry.bind("<Return>", lambda e: _goto())
        tk.Button(dlg, text="Go", command=_goto, width=8).pack(pady=(0, 10))
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    # ==================================================================
    #  Help dialogs
    # ==================================================================

    def show_quick_reference(self):
        """Display a scrollable quick-reference for TempleCode commands."""
        tk = self.tk
        win = tk.Toplevel(self.root)
        win.title("TempleCode Quick Reference")
        win.geometry("700x550")
        tw = self.scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Courier", 10))
        tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ref = (
            "═══════════════════ TEMPLECODE QUICK REFERENCE ═══════════════════\n\n"
            "─── BASIC COMMANDS ───────────────────────────────────────────────\n"
            "  PRINT expr ; expr         Print values (;=no newline, ,=tab)\n"
            "  LET var = expr            Assign a variable\n"
            "  INPUT \"prompt\"; var       Read user input\n"
            "  IF cond THEN stmt         Single-line conditional\n"
            "  IF cond THEN              Multi-line conditional block\n"
            "    ...                     (supports ELSEIF, ELSE, END IF)\n"
            "  END IF  / ENDIF\n"
            "  FOR v = a TO b [STEP s]   Counted loop\n"
            "  NEXT v\n"
            "  WHILE cond                Condition loop\n"
            "  WEND\n"
            "  DO [WHILE|UNTIL cond]     Do-loop\n"
            "  LOOP [WHILE|UNTIL cond]\n"
            "  GOTO label                Jump to label\n"
            "  GOSUB label / RETURN      Subroutine call\n"
            "  ON n GOTO l1,l2,...        Computed branch\n"
            "  ON n GOSUB l1,l2,...       Computed subroutine call\n"
            "  SELECT CASE expr          Multi-branch\n"
            "  CASE val / CASE ELSE\n"
            "  END SELECT\n"
            "  DIM arr(size)             Declare array\n"
            "  DATA 1,2,3 / READ v       Inline data\n"
            "  RESTORE                   Reset DATA pointer\n"
            "  SWAP a, b                 Swap two variables\n"
            "  INCR v [,n] / DECR v [,n] Increment/decrement\n"
            "  DELAY ms / SLEEP s        Pause execution\n"
            "  RANDOMIZE [seed]          Seed random generator\n"
            "  CLS                       Clear output\n"
            "  BEEP                      System bell\n"
            "  TAB n / SPC n             Print spacing\n"
            "  EXIT FOR / EXIT DO / EXIT WHILE\n"
            "  REM comment  / ' comment  Comments\n"
            "  END / STOP                End program\n\n"
            "  Math: SIN COS TAN ATN LOG EXP SQRT ABS INT CEIL FIX RND\n"
            "  String: LEN MID$ LEFT$ RIGHT$ CHR$ ASC STR$ VAL\n"
            "          UCASE$ LCASE$ INSTR\n"
            "  Utility: TIMER  DATE$  TIME$  TYPE(expr)\n\n"
            "─── PILOT COMMANDS ──────────────────────────────────────────────\n"
            "  T: text              Type / print text ($VAR interpolation)\n"
            "  A: [varname]         Accept user input\n"
            "  M: pattern1,pat2     Match answer against patterns\n"
            "  Y: command           Execute if last match succeeded\n"
            "  N: command           Execute if last match failed\n"
            "  J: label             Jump to label\n"
            "  C: var=expr          Compute / assign\n"
            "  C: *label            Call subroutine\n"
            "  E:                   End subroutine / program\n"
            "  R: remark            Comment\n"
            "  U: var=expr          Use / set variable\n"
            "  L: label             Define label\n"
            "  G: logo_command      Inline Logo command\n"
            "  S: OP var            String op (UPPER LOWER LEN REVERSE TRIM)\n"
            "  D: arr(n)            Dimension array\n"
            "  P: ms                Pause (milliseconds)\n"
            "  X: command           Execute any command inline\n\n"
            "─── LOGO TURTLE COMMANDS ────────────────────────────────────────\n"
            "  FORWARD n / FD n     Move forward\n"
            "  BACK n / BK n        Move backward\n"
            "  LEFT n / LT n        Turn left\n"
            "  RIGHT n / RT n       Turn right\n"
            "  PENUP / PU           Lift pen\n"
            "  PENDOWN / PD         Lower pen\n"
            "  HOME                 Return to centre\n"
            "  CLEARSCREEN / CS     Clear and reset\n"
            "  SETXY x y            Move to position\n"
            "  SETX x / SETY y      Set coordinate\n"
            "  SETHEADING n         Set angle (0=North, clockwise)\n"
            "  TOWARDS x y          Point toward coordinates\n"
            "  SHOWTURTLE / ST      Show turtle\n"
            "  HIDETURTLE / HT      Hide turtle\n"
            "  SETCOLOR colour      Set pen colour (name or 0-15)\n"
            "  SETPENSIZE n         Set pen width\n"
            "  SETFILLCOLOR colour  Set fill colour\n"
            "  SETBACKGROUND colour Set canvas colour\n"
            "  CIRCLE r             Draw circle\n"
            "  ARC angle [r]        Draw arc\n"
            "  DOT [size]           Draw dot\n"
            "  RECT w [h]           Draw rectangle\n"
            "  SQUARE side          Draw square\n"
            "  TRIANGLE side        Draw equilateral triangle\n"
            "  POLYGON sides len    Draw regular polygon\n"
            "  STAR points len      Draw star\n"
            "  LABEL \"text\" [size]  Draw text at turtle position\n"
            "  REPEAT n [ cmds ]    Repeat commands n times\n"
            "  MAKE \"var value      Set variable\n"
            "  TO name :p1 :p2      Define procedure\n"
            "    ...body...\n"
            "  END\n"
            "  HEADING / POS        Query turtle state\n"
            "  PENCOLOR? / PENSIZE? Query pen state\n"
            "  WRAP / WINDOW / FENCE Screen boundary mode\n"
            "  TRACE / NOTRACE      Toggle debug tracing\n\n"
            "═══════════════════════════════════════════════════════════════════\n"
        )
        tw.insert(tk.END, ref)
        tw.config(state=tk.DISABLED)

    def show_keyboard_shortcuts(self):
        """Display a dialog listing all keyboard shortcuts."""
        shortcuts = (
            "Keyboard Shortcuts\n"
            "──────────────────────────\n\n"
            "F5               Run Program\n"
            "Escape           Stop Program\n"
            "Ctrl+N           New File\n"
            "Ctrl+O           Open File\n"
            "Ctrl+S           Save\n"
            "Ctrl+Shift+S     Save As\n"
            "Ctrl+Q           Exit\n"
            "Ctrl+Z           Undo\n"
            "Ctrl+Y           Redo\n"
            "Ctrl+A           Select All\n"
            "Ctrl+F           Find\n"
            "Ctrl+H           Replace\n"
            "Ctrl+G           Go to Line\n"
            "Ctrl+Shift+P     Command Palette\n"
            "Ctrl++/Ctrl+-    Zoom In/Out\n"
            "Ctrl+Scroll      Zoom\n"
            "Tab              Autocomplete\n"
        )
        self.messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    # ==================================================================
    #  Watch Expressions (Debug)
    # ==================================================================

    def _add_watch_dialog(self):
        """Prompt the user to add a watch expression."""
        from tkinter import simpledialog  # noqa: C0415
        expr = simpledialog.askstring(
            "Add Watch", "Variable name or expression to watch:",
            parent=self.root,
        )
        if expr:
            self._watch_manager.add(expr)
            self._output(f"👁  Watch added: {expr}\n", "out_ok")

    def _show_watches(self):
        """Display current watch expression values in a dialog."""
        tk = self.tk
        win = tk.Toplevel(self.root)
        win.title("Watch Expressions")
        win.geometry("500x350")
        win.transient(self.root)

        tw = self.scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Courier", 10))
        tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if not self._watch_manager.expressions:
            tw.insert(tk.END, "(no watch expressions set)\n\nUse Debug → Add Watch Expression to add one.")
        else:
            tw.insert(tk.END, "═══ WATCH EXPRESSIONS ═══\n\n")
            pairs = self._watch_manager.evaluate_all(self.interpreter)
            for expr, val in pairs:
                tw.insert(tk.END, f"  {expr} = {val}\n")
            tw.insert(tk.END, "\n═══ ALL VARIABLES ═══\n\n")
            for k, v in sorted(self.interpreter.variables.items()):
                tw.insert(tk.END, f"  {k} = {v!r}\n")

        tw.config(state=tk.DISABLED)

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(btn_frame, text="Add Watch", command=lambda: (
            self._add_watch_dialog(), win.destroy(), self._show_watches()
        )).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear All", command=lambda: (
            self._watch_manager.clear(), win.destroy(),
            self._output("👁  All watches cleared.\n", "out_ok")
        )).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=lambda: (
            win.destroy(), self._show_watches()
        )).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)

    # ==================================================================
    #  Program Profiler
    # ==================================================================

    def _show_profiler_report(self):
        """Display the profiler report in a scrollable window."""
        tk = self.tk
        win = tk.Toplevel(self.root)
        win.title("Profiler Report")
        win.geometry("700x500")
        win.transient(self.root)

        tw = self.scrolledtext.ScrolledText(win, wrap=tk.NONE, font=("Courier", 10))
        tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if not self._profiler.get_stats():
            tw.insert(tk.END, "No profiling data.\n\n"
                      "Enable the profiler via Debug → Enable Profiler,\n"
                      "then run a program.")
        else:
            tw.insert(tk.END, self._profiler.format_report())

        tw.config(state=tk.DISABLED)

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(btn_frame, text="Reset", command=lambda: (
            self._profiler.reset(),
            self._output("📊 Profiler data cleared.\n", "out_ok"),
            win.destroy()
        )).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)

    # ==================================================================
    #  Code Formatter
    # ==================================================================

    def _format_editor_code(self):
        """Format / auto-indent the code in the editor."""
        text_w = self.editor_text
        source = text_w.get("1.0", self.tk.END)
        if not source.strip():
            return

        formatted = self._format_code(source)

        # Replace editor content
        cursor_pos = text_w.index(self.tk.INSERT)
        text_w.delete("1.0", self.tk.END)
        text_w.insert("1.0", formatted.rstrip("\n"))

        # Restore cursor
        try:
            text_w.mark_set(self.tk.INSERT, cursor_pos)
            text_w.see(cursor_pos)
        except Exception:
            pass

        self._mark_dirty()
        self._output("✨ Code formatted.\n", "out_ok")

    # ==================================================================
    #  Snippet Manager
    # ==================================================================

    def _show_snippet_picker(self):
        """Show a quick-pick list of snippets to insert."""
        tk = self.tk
        dlg = tk.Toplevel(self.root)
        dlg.title("Insert Snippet")
        dlg.geometry("450x400")
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Select a snippet to insert:").pack(padx=10, pady=(10, 5), anchor="w")

        # Filter entry
        filter_var = tk.StringVar()
        filter_entry = tk.Entry(dlg, textvariable=filter_var)
        filter_entry.pack(fill=tk.X, padx=10, pady=(0, 5))
        filter_entry.focus()

        # Listbox
        list_frame = tk.Frame(dlg)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        snippets = self._snippet_manager.all_snippets()
        snippet_keys = sorted(snippets.keys())

        def refresh_list(*_args):
            listbox.delete(0, tk.END)
            filt = filter_var.get().lower()
            for key in snippet_keys:
                snip = snippets[key]
                label = f"{snip.get('prefix', ''):10s}  {snip.get('label', key)}"
                if filt and filt not in label.lower() and filt not in key.lower():
                    continue
                listbox.insert(tk.END, label)

        filter_var.trace_add("write", refresh_list)
        refresh_list()

        # Description label
        desc_label = tk.Label(dlg, text="", wraplength=400, anchor="w", justify="left")
        desc_label.pack(fill=tk.X, padx=10, pady=5)

        def on_select(_event=None):
            sel = listbox.curselection()
            if not sel:
                return
            # Map back to key
            text = listbox.get(sel[0])
            prefix = text[:10].strip()
            for key in snippet_keys:
                if snippets[key].get("prefix", "") == prefix:
                    snip = snippets[key]
                    desc_label.config(text=snip.get("description", ""))
                    break

        listbox.bind("<<ListboxSelect>>", on_select)

        def insert_selected():
            sel = listbox.curselection()
            if not sel:
                return
            text = listbox.get(sel[0])
            prefix = text[:10].strip()
            for key in snippet_keys:
                if snippets[key].get("prefix", "") == prefix:
                    body = snippets[key].get("body", "")
                    self.editor_text.insert(self.tk.INSERT, body)
                    self._mark_dirty()
                    self._output(f"✂️  Snippet inserted: {snippets[key].get('label', key)}\n", "out_ok")
                    dlg.destroy()
                    return

        tk.Button(dlg, text="Insert", command=insert_selected).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(dlg, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
        listbox.bind("<Double-Button-1>", lambda e: insert_selected())
        dlg.bind("<Return>", lambda e: insert_selected())
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    def _show_snippet_manager(self):
        """Show a dialog to manage (add/edit/delete) user snippets."""
        tk = self.tk
        win = tk.Toplevel(self.root)
        win.title("Manage Snippets")
        win.geometry("600x500")
        win.transient(self.root)

        # Top: list of snippets
        list_frame = tk.LabelFrame(win, text="Snippets", padx=5, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        snippets = self._snippet_manager.all_snippets()

        def refresh():
            nonlocal snippets
            snippets = self._snippet_manager.all_snippets()
            listbox.delete(0, tk.END)
            for key in sorted(snippets.keys()):
                s = snippets[key]
                builtin = " (built-in)" if key in self._snippet_manager.BUILTIN_SNIPPETS and key not in self._snippet_manager._user_snippets else ""
                listbox.insert(tk.END, f"{s.get('prefix', ''):10s}  {s.get('label', key)}{builtin}")

        refresh()

        # Buttons
        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        def add_snippet():
            self._snippet_edit_dialog(win, callback=refresh)

        def delete_snippet():
            sel = listbox.curselection()
            if not sel:
                return
            key = sorted(snippets.keys())[sel[0]]
            if self._snippet_manager.remove(key):
                self._output(f"🗑  Snippet removed: {key}\n", "out_ok")
            refresh()

        tk.Button(btn_frame, text="Add New", command=add_snippet).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=delete_snippet).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)

    def _snippet_edit_dialog(self, parent, callback=None):
        """Show a dialog to add a new snippet."""
        tk = self.tk
        dlg = tk.Toplevel(parent)
        dlg.title("Add Snippet")
        dlg.geometry("450x400")
        dlg.transient(parent)
        dlg.grab_set()

        fields = {}
        for label_text, key in [("Key (unique ID):", "key"), ("Label:", "label"),
                                ("Prefix (trigger):", "prefix"), ("Description:", "description")]:
            tk.Label(dlg, text=label_text).pack(padx=10, pady=(5, 0), anchor="w")
            var = tk.StringVar()
            tk.Entry(dlg, textvariable=var).pack(fill=tk.X, padx=10)
            fields[key] = var

        tk.Label(dlg, text="Body (code):").pack(padx=10, pady=(5, 0), anchor="w")
        body_text = tk.Text(dlg, height=8, font=("Courier", 10))
        body_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        def save():
            key = fields["key"].get().strip()
            label = fields["label"].get().strip()
            prefix = fields["prefix"].get().strip()
            desc = fields["description"].get().strip()
            body = body_text.get("1.0", tk.END).rstrip("\n")
            if not key or not body:
                self.messagebox.showwarning("Missing Fields", "Key and body are required.", parent=dlg)
                return
            self._snippet_manager.add(key, label or key, prefix or key, body, desc)
            self._output(f"✂️  Snippet saved: {label or key}\n", "out_ok")
            dlg.destroy()
            if callback:
                callback()

        tk.Button(dlg, text="Save", command=save).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(dlg, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    # ==================================================================
    #  Undo/Redo History Viewer
    # ==================================================================

    def _show_undo_history(self):
        """Show a dialog listing undo history entries."""
        tk = self.tk
        win = tk.Toplevel(self.root)
        win.title("Undo History")
        win.geometry("500x400")
        win.transient(self.root)

        history = self._undo_history.get_history_list()

        list_frame = tk.Frame(win)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        if not history:
            listbox.insert(tk.END, "(no history)")
        else:
            import datetime  # noqa: C0415
            for entry in history:
                ts = datetime.datetime.fromtimestamp(entry["timestamp"]).strftime("%H:%M:%S")
                marker = " ◀" if entry["current"] else ""
                listbox.insert(
                    tk.END,
                    f"#{entry['index']:3d}  {ts}  {entry['description']:12s}  "
                    f"({entry['length']} chars){marker}"
                )
            # Scroll to current entry
            for entry in history:
                if entry["current"]:
                    listbox.see(entry["index"])
                    listbox.selection_set(entry["index"])

        def jump_to():
            sel = listbox.curselection()
            if not sel:
                return
            content = self._undo_history.jump_to(sel[0])
            if content is not None:
                self.editor_text.delete("1.0", self.tk.END)
                self.editor_text.insert("1.0", content.rstrip("\n"))
                self._mark_dirty()
                self._output(f"↩️  Restored to history #{sel[0]}\n", "out_ok")
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(btn_frame, text="Restore Selected", command=jump_to).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear History", command=lambda: (
            self._undo_history.clear(), win.destroy(),
            self._output("🗑  Undo history cleared.\n", "out_ok")
        )).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)
        listbox.bind("<Double-Button-1>", lambda e: jump_to())

    # ==================================================================
    #  Import Graph Visualization
    # ==================================================================

    def _show_import_graph(self):
        """Parse IMPORT statements from editor code and display dependency graph."""
        tk = self.tk
        source = self.editor_text.get("1.0", self.tk.END)

        imports = self._parse_imports(source)

        win = tk.Toplevel(self.root)
        win.title("Import Dependency Graph")
        win.geometry("600x400")
        win.transient(self.root)

        tw = self.scrolledtext.ScrolledText(win, wrap=tk.NONE, font=("Courier", 10))
        tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if not imports:
            tw.insert(tk.END, "No IMPORT statements found in the current editor text.\n\n"
                      "Add IMPORT \"filename.tc\" to your code to use this feature.")
        else:
            # If we have a current file, build full graph
            if self.current_file_path and os.path.isfile(self.current_file_path):
                graph = self._build_import_graph(self.current_file_path)
                tw.insert(tk.END, self._format_import_graph(graph))
            else:
                # Just show the direct imports
                tw.insert(tk.END, "═══ IMPORTS (current file) ═══\n\n")
                for imp in imports:
                    tw.insert(tk.END, f"  └── {imp}\n")
                tw.insert(tk.END, f"\n{len(imports)} import(s) found.\n"
                          "Save your file to enable full dependency graph traversal.")

        tw.config(state=tk.DISABLED)
        tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))

    # ==================================================================
    #  Main loop
    # ==================================================================

    def run(self):
        """Start the Tkinter main event loop."""
        self.root.mainloop()


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

def main():
    """Application entry point: create and run the TempleCode IDE."""
    print("🚀 Launching Time Warp II...")
    try:
        app = TempleCodeApp()
        app.run()
        sys.exit(0)
    except Exception as e:
        print(f"❌ GUI launch failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
