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
from __future__ import annotations

import sys
import os
import queue as _queue
from pathlib import Path
from typing import Any, Callable, Optional

from core.settings import load_settings, save_settings, MAX_RECENT


# ---------------------------------------------------------------------------
#  Thread-safe output proxy
# ---------------------------------------------------------------------------

class _OutputProxy:
    """Thread-safe stand-in for the output Text widget.

    The interpreter background thread calls ``.insert()`` and ``.see()``
    directly on this object.  Those calls only touch a ``queue.Queue``
    (which IS thread-safe) — no tkinter Tcl calls are made from the
    background thread.  The IDE main thread drains the queue via
    ``_drain_output_queue()`` called by ``root.after()``.
    """

    CLEAR = object()   # sentinel: clear the widget

    def __init__(self) -> None:
        self._q: _queue.Queue = _queue.Queue()

    def insert(self, _index, text: str) -> None:   # noqa: D102
        """Insert text into the output queue."""
        self._q.put(str(text))

    def see(self, _index) -> None:                 # noqa: D102
        """No-op; scroll handling is done by the drain loop."""

    def delete(self, _start, _end) -> None:        # noqa: D102
        """Queue a clear-output sentinel."""
        self._q.put(self.CLEAR)

    def update_idletasks(self) -> None:            # noqa: D102
        """No-op; idle tasks are handled by the main thread."""

    def get_nowait(self):
        """Dequeue the next pending item; raises ``queue.Empty`` if none."""
        return self._q.get_nowait()

    def call_on_main(self, fn) -> None:
        """Queue a callable to be executed on the main thread by the drain loop.

        Use this instead of ``root.after(0, fn)`` from a background thread —
        calling ``root.after()`` from a non-main thread touches Tcl and is
        NOT thread-safe.
        """
        self._q.put(fn)


# ---------------------------------------------------------------------------
#  Application class
# ---------------------------------------------------------------------------

class TempleCodeApp:
    """Main GUI application for Time Warp II."""

    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        import tkinter as tk
        from tkinter import scrolledtext, messagebox, filedialog
        from core.interpreter import TempleCodeInterpreter
        from core.config import (
            THEMES, LINE_NUMBER_BG, FONT_SIZES, FONT_SIZE_ORDER,
            PRIORITY_FONTS, WELCOME_MESSAGE, KEYWORDS, INDENT_OPENERS,
        )
        from core.features.ide_features import (
            WatchManager, Profiler, SnippetManager,
            UndoHistoryManager, format_code, parse_imports,
            build_import_graph, format_import_graph,
        )
        from ui.editor import EditorPanel
        from ui.output import OutputPanel
        from ui.graphics import GraphicsPanel
        from ui.toolbar import Toolbar
        from ui.statusbar import StatusBar
        from ui.menus import build_menus
        from ui.tabs import TabManager
        from ui.repl import ReplPanel

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
        self.gui_optimizer: Any = None
        self._init_gui_optimizer: Optional[Callable[..., Any]] = None
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
        saved_geom = self._settings.get("geometry", "")
        self.root.geometry(saved_geom if saved_geom else "1200x800")
        self.root.config(bg="#252526")

        if self._init_gui_optimizer is not None:
            self.gui_optimizer = self._init_gui_optimizer(self.root)
            print("🚀 GUI optimizations enabled")
        else:
            print("ℹ️  GUI optimizations not available")

        # Validate font family against installed system fonts
        try:
            import tkinter.font as tkfont
            available = set(tkfont.families())
            if self.current_font_family not in available:
                for candidate in PRIORITY_FONTS:
                    if candidate in available:
                        self.current_font_family = candidate
                        break
                else:
                    self.current_font_family = "TkFixedFont"
        except Exception:
            pass  # tkinter.font unavailable in tests

        # State flags
        self.input_buffer: list[str] = []
        self.interpreter = None
        self._dirty = False
        self._is_running = False
        self._key_capture_active = False
        self._undo_snapshot_after_id = None

        # Autocomplete state (Feature 5)
        self._ac_popup = None

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

        # ---- Build layout with extracted UI modules ----

        # Main paned window
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#252526")
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel — editor(s)
        self.left_panel = tk.Frame(self.main_paned, bg="#252526")
        self.main_paned.add(self.left_panel, width=400)

        self.editor_panel = EditorPanel(self, self.left_panel, pygments_ok=self._pygments_ok)

        # Backward-compat aliases — code referencing self.editor_text gets the
        # SyntaxHighlightingText / LineNumberedText wrapper (NOT the EditorPanel).
        self.editor_text = self.editor_panel.text_widget
        self.editor_text2 = self.editor_panel.text_widget2
        self.editor_paned = self.editor_panel.paned
        self.editor_frame = self.editor_panel.frame
        self.editor_frame2 = self.editor_panel.frame2

        # Tab manager — sits above the editor paned window
        self.tab_manager = TabManager(self, self.left_panel)

        # Right panel — output + graphics
        self.right_panel = tk.Frame(self.main_paned, bg="#252526")
        self.main_paned.add(self.right_panel, width=800)

        self.right_paned = tk.PanedWindow(self.right_panel, orient=tk.VERTICAL, sashwidth=5, bg="#252526")
        self.right_paned.pack(fill=tk.BOTH, expand=True)

        self.output_panel = OutputPanel(self, self.right_paned)
        self.right_paned.add(self.output_panel.frame, height=300)
        self.output_text = self.output_panel.text      # backward compat
        self.output_frame = self.output_panel.frame

        self.graphics_panel = GraphicsPanel(self, self.right_paned)
        self.right_paned.add(self.graphics_panel.frame, height=300)
        self.turtle_canvas = self.graphics_panel.canvas   # backward compat
        self.graphics_frame = self.graphics_panel.frame

        # REPL panel — interactive command line below graphics
        self.repl_panel = ReplPanel(self, self.right_paned)
        self.right_paned.add(self.repl_panel.frame, height=150)

        # Input bar (simple — stays inline)
        self._build_input_bar()

        # Toolbar + speed controls
        self.toolbar = Toolbar(self)
        self.button_frame = self.toolbar.button_frame
        self._speed_frame = self.toolbar.speed_frame
        self._exec_slider = self.toolbar.exec_slider
        self._turtle_slider = self.toolbar.turtle_slider

        # Status bar
        self.status_bar_panel = StatusBar(self)
        self.status_bar = self.status_bar_panel.frame
        self._status_labels = self.status_bar_panel.labels

        # Command palette data (populated by build_menus)
        self._palette_commands: list[tuple[str, Any]] = []

        # Menus + command palette entries
        build_menus(self)

        # Key bindings
        self._bind_keys()

        # Initialise interpreter — use the thread-safe proxy as output_widget
        self._output_proxy = _OutputProxy()
        self.interpreter = TempleCodeInterpreter(self._output_proxy)
        self.interpreter.ide_turtle_canvas = self.turtle_canvas
        self.interpreter.input_buffer = self.input_buffer
        self.interpreter._input_entry_widget = self.input_entry
        self.interpreter._input_entry_bg = "#1e1e1e"

        # Attach IDE features to interpreter
        self.interpreter.watch_manager = self._watch_manager
        self.interpreter.profiler = self._profiler

        # Feed keystrokes to the interpreter's key buffer for INKEY$
        self.root.bind("<KeyPress>", self._on_key_for_inkey)

        # Configure output colour tags
        self.output_panel.setup_tags(THEMES[self.current_theme])

        # Apply saved settings
        self._output(WELCOME_MESSAGE)
        self.apply_theme(self.current_theme)
        self.apply_font_size(self.current_font)

        # Take initial undo snapshot
        self._undo_history.snapshot(
            self.editor_text.get("1.0", self.tk.END), "initial"
        )

        # Feature 15: auto dark/light based on OS
        if self.auto_dark:
            self._auto_detect_dark_mode()

        # Start status bar updater
        self.status_bar_panel.start_updates()

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
            "geometry": self.root.geometry(),
        })

    # ==================================================================
    #  Input bar (stays inline — too small to extract)
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
            highlightbackground="#1e1e1e",
            highlightcolor="#007acc",
            highlightthickness=2,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self._submit_input())
        tk.Button(self.input_frame, text="Submit", command=self._submit_input,
                  bg="#3e3e3e", fg="#d4d4d4").pack(side=tk.LEFT)

    # ==================================================================
    #  Key bindings
    # ==================================================================

    def _bind_keys(self):
        """Bind keyboard shortcuts to IDE actions."""
        from ui import dialogs

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
        r.bind("<Control-f>", lambda e: dialogs.show_find_dialog(self))
        r.bind("<Control-h>", lambda e: dialogs.show_replace_dialog(self))
        r.bind("<Control-g>", lambda e: dialogs.show_goto_line_dialog(self))
        r.bind("<Control-Shift-P>", lambda e: dialogs.show_command_palette(self))
        r.bind("<Escape>", lambda e: self.stop_code())

        # Debug key bindings
        r.bind("<F9>", lambda e: self.debug_toggle_breakpoint())
        r.bind("<F10>", lambda e: self.debug_step_over())
        r.bind("<F11>", lambda e: self.debug_step_over())  # step into = step over for now
        r.bind("<Shift-F5>", lambda e: self.debug_stop())

        # Ctrl+scroll zoom
        r.bind("<Control-Button-4>", lambda e: self._zoom(1))
        r.bind("<Control-Button-5>", lambda e: self._zoom(-1))
        r.bind("<Control-MouseWheel>", lambda e: self._zoom(1 if e.delta > 0 else -1))
        r.bind("<Control-plus>", lambda e: self._zoom(1))
        r.bind("<Control-minus>", lambda e: self._zoom(-1))
        r.bind("<Control-equal>", lambda e: self._zoom(1))

        r.bind("<Control-Shift-F>", lambda e: self._format_editor_code())
        r.bind("<Control-j>", lambda e: dialogs.show_snippet_picker(self))
        r.bind("<Control-J>", lambda e: dialogs.show_snippet_picker(self))

        # Tab navigation shortcuts
        r.bind("<Control-w>", lambda e: self._close_current_tab())
        r.bind("<Control-Tab>", lambda e: self._next_tab())
        r.bind("<Control-Shift-Tab>", lambda e: self._prev_tab())

        # Auto-indent / tab-completion on the inner text widget
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        text_w.bind("<Return>", self._on_editor_return)
        text_w.bind("<Tab>", self._on_tab)

        # Highlight current line on cursor move + update status bar
        text_w.bind("<KeyRelease>", lambda e: (self._highlight_current_line(), self._mark_dirty()))
        text_w.bind("<ButtonRelease-1>", lambda e: self._highlight_current_line())

        # Right-click context menu
        text_w.bind("<Button-3>", self._show_editor_context_menu)

    # ==================================================================
    #  Auto-indent
    # ==================================================================

    def _on_editor_return(self, event):
        """Insert newline with smart auto-indent."""
        widget = event.widget
        idx = widget.index(self.tk.INSERT)
        line_num = idx.split(".")[0]
        line_text = widget.get(f"{line_num}.0", f"{line_num}.end")
        stripped = line_text.lstrip()
        indent = len(line_text) - len(stripped)
        base_indent = line_text[:indent]
        first_word = stripped.split()[0].upper().rstrip(":") if stripped.split() else ""
        extra = "  " if first_word in self.INDENT_OPENERS else ""
        widget.insert(self.tk.INSERT, "\n" + base_indent + extra)
        widget.see(self.tk.INSERT)
        return "break"

    # ==================================================================
    #  Highlight current line
    # ==================================================================

    def _highlight_current_line(self):
        self.editor_panel.highlight_current_line()

    # ==================================================================
    #  Tab-completion
    # ==================================================================

    def _on_tab(self, event):
        """Try to autocomplete the current word; fall back to inserting spaces."""
        widget = event.widget
        idx = widget.index(self.tk.INSERT)
        line_num, col = idx.split(".")
        line_text = widget.get(f"{line_num}.0", idx)
        import re
        m = re.search(r'([A-Za-z_$:]+)$', line_text)
        if not m:
            widget.insert(self.tk.INSERT, "  ")
            return "break"
        prefix = m.group(1).upper()
        matches = [k for k in self.KEYWORDS if k.upper().startswith(prefix)]
        if len(matches) == 1:
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
    #  Output helpers (delegate to OutputPanel)
    # ==================================================================

    def _out_write(self, text, tag=None):
        """Write text to output_text."""
        self.output_panel.write(text, tag)

    def _out_clear(self):
        """Clear output_text."""
        self.output_panel.clear()

    def _output(self, text, tag=None):
        """Insert text into the output widget, optionally with a colour tag."""
        self.output_panel.write(text, tag)

    # ==================================================================
    #  Ctrl+scroll zoom
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
    #  Code folding (delegate to EditorPanel)
    # ==================================================================

    def fold_all(self):
        """Hide lines between matching block openers and closers."""
        self.editor_panel.fold_all()

    def unfold_all(self):
        """Remove all code-folding tags to expand collapsed regions."""
        self.editor_panel.unfold_all()

    # ==================================================================
    #  Auto dark/light mode
    # ==================================================================

    def _auto_detect_dark_mode(self):
        """Try to detect OS dark mode and apply matching theme."""
        try:
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
            pass

    def _toggle_auto_dark(self):
        self.auto_dark = self._auto_dark_var.get()
        if self.auto_dark:
            self._auto_detect_dark_mode()
        self._save()

    # ==================================================================
    #  File operations
    # ==================================================================

    def _add_recent(self, path):
        """Track recent files."""
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
            if hasattr(self, 'tab_manager'):
                self.tab_manager.open_in_tab(filepath, content)
            else:
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
        """Create a new tab (or clear the editor if tabs aren't ready)."""
        if hasattr(self, 'tab_manager'):
            self.tab_manager.new_tab()
        else:
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
                if hasattr(self, 'tab_manager'):
                    self.tab_manager.mark_saved(filename)
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
                if hasattr(self, 'tab_manager'):
                    self.tab_manager.mark_saved(self.current_file_path)
            except Exception as e:
                self._output(f"❌ Save failed: {e}\n", "out_error")
        else:
            self.save_file()

    def load_example(self, filepath):
        """Load an example TempleCode program from the given filepath."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if hasattr(self, 'tab_manager'):
                self.tab_manager.open_in_tab(filepath, content)
            else:
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
        self.status_bar_panel.cancel_updates()
        self.root.destroy()

    # ==================================================================
    #  Tab navigation helpers
    # ==================================================================

    def _close_current_tab(self):
        """Close the active editor tab (Ctrl+W)."""
        if hasattr(self, 'tab_manager'):
            self.tab_manager.close_tab(self.tab_manager.active_index)

    def _next_tab(self):
        """Switch to the next editor tab (Ctrl+Tab)."""
        if hasattr(self, 'tab_manager') and self.tab_manager.tabs:
            nxt = (self.tab_manager.active_index + 1) % len(self.tab_manager.tabs)
            self.tab_manager.switch_to(nxt)

    def _prev_tab(self):
        """Switch to the previous editor tab (Ctrl+Shift+Tab)."""
        if hasattr(self, 'tab_manager') and self.tab_manager.tabs:
            prv = (self.tab_manager.active_index - 1) % len(self.tab_manager.tabs)
            self.tab_manager.switch_to(prv)

    # ==================================================================
    #  Dirty flag & title helpers
    # ==================================================================

    def _mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            self._update_title()
        if hasattr(self, 'tab_manager'):
            self.tab_manager.mark_modified()
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
        self.output_panel.clear()

    def clear_canvas(self):
        """Clear the turtle graphics canvas and reset the turtle state."""
        self.graphics_panel.clear()

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
        self._out_clear()
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
                self._output_proxy.call_on_main(
                    lambda: self._output("\n✅ Program completed.\n", "out_ok")
                )
            except Exception as e:  # pylint: disable=broad-except
                self._output_proxy.call_on_main(
                    lambda err=e: self._output(f"\n❌ Error: {err}\n", "out_error")
                )
            finally:
                self._output_proxy.call_on_main(self._on_run_finished)

        _threading.Thread(target=_run, daemon=True).start()

    def _on_run_finished(self):
        """Called on the main thread when the interpreter thread completes."""
        self._is_running = False
        if self.interpreter:
            self.interpreter.reset_input_state()
        # Clean up debug controller
        if hasattr(self, '_debug_controller') and self._debug_controller:
            self._debug_controller.stop()
            self._debug_controller = None
            self._clear_debug_highlight()

    # ==================================================================
    #  Step Debugger
    # ==================================================================

    def debug_start(self):
        """Start a debug session (F5) — run until first breakpoint."""
        from core.features.debugger import DebugController

        if self._is_running:
            # If already debugging and paused, treat F5 as continue
            if hasattr(self, '_debug_controller') and self._debug_controller and self._debug_controller.is_paused:
                self.debug_continue()
                return
            self._output("⚠️  Program is already running.\n", "out_warn")
            return

        import threading as _threading

        code = self.editor_text.get("1.0", self.tk.END)
        self._out_clear()
        self._output("🐛 Starting debug session...\n\n", "out_ok")
        self._is_running = True

        # Setup interpreter
        if hasattr(self.interpreter, 'exec_delay_ms'):
            self.interpreter.exec_delay_ms = self.exec_speed
        if hasattr(self.interpreter, 'turtle_delay_ms'):
            self.interpreter.turtle_delay_ms = self.turtle_speed
        self.interpreter.ide_turtle_canvas = self.turtle_canvas
        if self.turtle_canvas is not None:
            self.turtle_canvas.delete("all")
        self.interpreter.turtle_graphics = None
        self.interpreter.init_turtle_graphics()
        self.interpreter.clear_turtle_screen()
        self.interpreter.debug_mode = True

        # Create and attach debug controller
        dc = DebugController()
        self._debug_controller = dc
        self.interpreter.debug_controller = dc

        def on_pause(line, variables):
            """Called from interpreter thread when paused."""
            self._output_proxy.call_on_main(
                lambda l=line, v=variables: self._debug_on_pause(l, v)
            )

        def on_stop():
            self._output_proxy.call_on_main(self._clear_debug_highlight)

        def on_resume():
            self._output_proxy.call_on_main(self._clear_debug_highlight)

        dc.on_pause = on_pause
        dc.on_stop = on_stop
        dc.on_resume = on_resume
        dc.start()

        def _run():
            try:
                self.interpreter.run_program(code, language="templecode")
                self._output_proxy.call_on_main(
                    lambda: self._output("\n✅ Debug session ended.\n", "out_ok")
                )
            except Exception as e:
                self._output_proxy.call_on_main(
                    lambda err=e: self._output(f"\n❌ Error: {err}\n", "out_error")
                )
            finally:
                self._output_proxy.call_on_main(self._on_run_finished)

        _threading.Thread(target=_run, daemon=True).start()

    def debug_step_over(self):
        """Step over one line (F10)."""
        if hasattr(self, '_debug_controller') and self._debug_controller:
            self._debug_controller.step_over()
        else:
            self._output("⚠️  No debug session active. Press F5 to start.\n", "out_warn")

    def debug_continue(self):
        """Continue execution until next breakpoint (F5 when paused)."""
        if hasattr(self, '_debug_controller') and self._debug_controller:
            self._debug_controller.continue_()
        else:
            self.debug_start()

    def debug_stop(self):
        """Stop the debug session (Shift+F5)."""
        if hasattr(self, '_debug_controller') and self._debug_controller:
            self._debug_controller.stop()
            self._debug_controller = None
            self._clear_debug_highlight()
            if self.interpreter:
                self.interpreter.running = False
                self.interpreter.debug_mode = False
                self.interpreter.debug_controller = None
            self._output("🛑 Debug session stopped.\n", "out_warn")

    def debug_toggle_breakpoint(self):
        """Toggle a breakpoint on the current editor line (F9)."""
        if not self.interpreter:
            return
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        try:
            idx = text_w.index(self.tk.INSERT)
            line_num = int(idx.split(".")[0]) - 1  # 0-based for interpreter
            if line_num in self.interpreter.breakpoints:
                self.interpreter.breakpoints.discard(line_num)
                text_w.tag_remove("breakpoint", f"{line_num + 1}.0", f"{line_num + 1}.end+1c")
                self._output(f"🔴 Breakpoint removed at line {line_num + 1}\n")
            else:
                self.interpreter.breakpoints.add(line_num)
                text_w.tag_add("breakpoint", f"{line_num + 1}.0", f"{line_num + 1}.end+1c")
                text_w.tag_configure("breakpoint", background="#4a1515")
                self._output(f"🔴 Breakpoint set at line {line_num + 1}\n")
        except Exception:
            pass

    def _debug_on_pause(self, line: int, variables: dict):
        """Called on the main thread when the debugger pauses."""
        self._output(f"⏸️  Paused at line {line + 1}\n", "out_warn")

        # Highlight paused line in editor
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        text_w.tag_remove("debug_line", "1.0", self.tk.END)
        text_w.tag_add("debug_line", f"{line + 1}.0", f"{line + 1}.end+1c")
        text_w.tag_configure("debug_line", background="#3d3d14")
        text_w.tag_raise("debug_line")
        text_w.see(f"{line + 1}.0")

        # Show variable snapshot
        if variables:
            var_lines = []
            for k, v in sorted(variables.items()):
                val_str = repr(v) if isinstance(v, str) else str(v)
                if len(val_str) > 60:
                    val_str = val_str[:57] + "..."
                var_lines.append(f"  {k} = {val_str}")
            if var_lines:
                self._output("📋 Variables:\n" + "\n".join(var_lines[:20]) + "\n")

    def _clear_debug_highlight(self):
        """Remove the debug line highlight from the editor."""
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        try:
            text_w.tag_remove("debug_line", "1.0", self.tk.END)
        except Exception:
            pass

    # ------------------------------------------------------------------
    #  Output-queue drain — runs on the main thread every ~16 ms
    # ------------------------------------------------------------------

    def _drain_output_queue(self):
        """Flush the thread-safe output proxy queue onto the real widget."""
        waiting = bool(self.interpreter and self.interpreter.waiting_for_input)
        ot = self.output_text
        try:
            while True:
                item = self._output_proxy.get_nowait()
                if item is _OutputProxy.CLEAR:
                    self._out_clear()
                elif callable(item):
                    try:
                        item()
                    except Exception:  # pylint: disable=broad-except
                        pass
                else:
                    ot.insert(self.tk.END, item)
                    if not waiting:
                        ot.see(self.tk.END)
        except _queue.Empty:
            pass

        # Handle input-wait focus management.
        if waiting:
            self.input_entry.focus_force()
            if not self._key_capture_active:
                self._start_key_capture()
        elif self._key_capture_active:
            self._stop_key_capture()

        self.root.after(16, self._drain_output_queue)

    # ------------------------------------------------------------------
    #  Input-wait visual feedback
    # ------------------------------------------------------------------

    def _start_key_capture(self):
        """Mark the input entry as active (yellow) when a program waits for input."""
        if self._key_capture_active:
            return
        self._key_capture_active = True
        self.input_entry.config(bg="#ffffcc", fg="#000000")

    def _stop_key_capture(self):
        """Restore the input entry to its normal theme colours."""
        if not self._key_capture_active:
            return
        self._key_capture_active = False
        theme = self.THEMES.get(self.current_theme, self.THEMES["dark"])
        self.input_entry.config(
            bg=theme.get("input_bg", "#1e1e1e"),
            fg=theme.get("input_fg", "#d4d4d4"),
        )
        text_w = self.editor_text.text if hasattr(self.editor_text, 'text') else self.editor_text
        text_w.focus_set()

    def _on_key_for_inkey(self, event):
        """Feed printable keystrokes into the interpreter's INKEY$ buffer."""
        if self._is_running and event.char:
            self.interpreter._key_buffer.append(event.char)

    def stop_code(self):
        """Stop a running program by setting the interpreter's running flag to False."""
        if self.interpreter and self._is_running:
            self.interpreter.running = False
            self.interpreter.cancel_input()
            self._output("\n🛑 Program stopped by user.\n", "out_warn")

    def _submit_input(self):
        """Submit input text to the running interpreter or queue it."""
        value = self.input_entry.get()
        self.input_entry.delete(0, self.tk.END)

        if self.interpreter and self.interpreter.waiting_for_input:
            self.interpreter.submit_input(value)
        else:
            self.input_buffer.append(value)
            self._output(f">> {value}\n")

    # ==================================================================
    #  Theme & font
    # ==================================================================

    def apply_theme(self, theme_key):
        """Apply the specified color theme to all editor and UI widgets."""
        tk = self.tk
        theme = self.THEMES[theme_key]

        # Delegate to extracted panels
        self.editor_panel.apply_theme(theme, theme_key)
        self.output_panel.apply_theme(theme)
        self.graphics_panel.apply_theme(theme)
        self.toolbar.apply_theme(tk, theme)
        self.status_bar_panel.apply_theme(theme)
        if hasattr(self, 'tab_manager'):
            self.tab_manager.apply_theme(theme)
        if hasattr(self, 'repl_panel'):
            self.repl_panel.apply_theme(theme)

        # Panels, frames, inputs (remain inline — they reference root-level widgets)
        self.root.config(bg=theme["root_bg"])
        for panel in (self.left_panel, self.right_panel):
            panel.config(bg=theme["frame_bg"])
        self.input_frame.config(bg=theme["frame_bg"])
        self.input_entry.config(
            bg=theme["input_bg"], fg=theme["input_fg"],
            insertbackground=theme["input_fg"],
            highlightbackground=theme["input_bg"],
            highlightcolor="#007acc",
            highlightthickness=2,
        )
        if self.interpreter:
            self.interpreter._input_entry_bg = theme["input_bg"]  # pylint: disable=protected-access

        # Labels in input frame
        for w in self.input_frame.winfo_children():
            if isinstance(w, tk.Label):
                w.config(bg=theme["frame_bg"], fg=theme.get("text_fg", "#aaa"))

        # Submit button
        btn_bg = theme.get("btn_bg", theme.get("input_bg", "#3e3e3e"))
        btn_fg = theme.get("btn_fg", theme.get("input_fg", "#d4d4d4"))
        for w in self.input_frame.winfo_children():
            if isinstance(w, tk.Button):
                w.config(bg=btn_bg, fg=btn_fg)

        # Paned windows
        for pw in (self.main_paned, self.right_paned, self.editor_paned):
            try:
                pw.config(bg=theme["frame_bg"])
            except Exception:
                pass

        # Update status bar theme label
        if "theme" in self._status_labels:
            self._status_labels["theme"].config(text=theme["name"])

        self.current_theme = theme_key
        self._save()
        self._highlight_current_line()

    def apply_font_size(self, size_key):
        """Apply the specified font size preset to editor and output widgets."""
        sz = self.FONT_SIZES[size_key]
        self.editor_panel.apply_font(self.current_font_family, sz["editor"])
        self.output_text.config(font=(self.current_font_family, sz["output"]))
        self.current_font = size_key
        if "font" in self._status_labels:
            self._status_labels["font"].config(text=f"{self.current_font_family} {sz['editor']}pt")
        self._save()

    def apply_font_family(self, family):
        """Apply the specified font family to editor and output widgets."""
        sz = self.FONT_SIZES[self.current_font]
        self.editor_panel.apply_font(family, sz["editor"])
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
    #  Code Formatter
    # ==================================================================

    def _format_editor_code(self):
        """Format / auto-indent the code in the editor."""
        text_w = self.editor_text
        source = text_w.get("1.0", self.tk.END)
        if not source.strip():
            return

        formatted = self._format_code(source)

        cursor_pos = text_w.index(self.tk.INSERT)
        text_w.delete("1.0", self.tk.END)
        text_w.insert("1.0", formatted.rstrip("\n"))

        try:
            text_w.mark_set(self.tk.INSERT, cursor_pos)
            text_w.see(cursor_pos)
        except Exception:
            pass

        self._mark_dirty()
        self._output("✨ Code formatted.\n", "out_ok")

    # ==================================================================
    #  Testing
    # ==================================================================

    def run_smoke_test(self):
        """Run a quick smoke test to verify interpreter functionality."""
        self._out_clear()
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
    #  Right-click context menu
    # ==================================================================

    def _show_editor_context_menu(self, event):
        from ui import dialogs
        tk = self.tk
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Cut",   command=lambda: self._editor_event("<<Cut>>"))
        menu.add_command(label="Copy",  command=lambda: self._editor_event("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self._editor_event("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=self.select_all)
        menu.add_separator()
        menu.add_command(label="Go to Line...", command=lambda: dialogs.show_goto_line_dialog(self))
        menu.add_command(label="Find...", command=lambda: dialogs.show_find_dialog(self))
        menu.add_command(label="Replace...", command=lambda: dialogs.show_replace_dialog(self))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

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
    #  Main loop
    # ==================================================================

    def run(self):
        """Start the Tkinter main event loop."""
        self.root.after(16, self._drain_output_queue)
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
