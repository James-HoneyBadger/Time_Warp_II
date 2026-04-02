"""Menu bar construction for Time Warp II."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


def build_menus(app: TempleCodeApp) -> None:
    """Create the full menu bar and attach it to the root window."""
    tk = app.tk
    from core.config import THEMES, FONT_SIZES
    from ui import dialogs

    menubar = tk.Menu(app.root)
    app.root.config(menu=menubar, bg="#252526")

    # --- File ---
    app._file_menu = file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New File", command=app.new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Open File...", command=app.load_file, accelerator="Ctrl+O")
    file_menu.add_separator()
    file_menu.add_command(label="Save", command=app.save_file_quick, accelerator="Ctrl+S")
    file_menu.add_command(label="Save As...", command=app.save_file, accelerator="Ctrl+Shift+S")
    file_menu.add_separator()
    app._recent_menu = tk.Menu(file_menu, tearoff=0)
    file_menu.add_cascade(label="Recent Files", menu=app._recent_menu)
    app._rebuild_recent_menu()
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.exit_app, accelerator="Ctrl+Q")

    # --- Edit ---
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Undo", command=app.undo_text, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Redo", command=app.redo_text, accelerator="Ctrl+Y")
    edit_menu.add_separator()
    edit_menu.add_command(label="Cut", command=lambda: app._editor_event("<<Cut>>"), accelerator="Ctrl+X")
    edit_menu.add_command(label="Copy", command=lambda: app._editor_event("<<Copy>>"), accelerator="Ctrl+C")
    edit_menu.add_command(label="Paste", command=lambda: app._editor_event("<<Paste>>"), accelerator="Ctrl+V")
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=app.select_all, accelerator="Ctrl+A")
    edit_menu.add_separator()
    edit_menu.add_command(label="Clear Editor", command=app.clear_editor)
    edit_menu.add_command(label="Clear Output", command=app.clear_output)
    edit_menu.add_command(label="Clear Graphics", command=app.clear_canvas)
    edit_menu.add_separator()
    edit_menu.add_command(label="Find...", command=lambda: dialogs.show_find_dialog(app), accelerator="Ctrl+F")
    edit_menu.add_command(label="Replace...", command=lambda: dialogs.show_replace_dialog(app), accelerator="Ctrl+H")
    edit_menu.add_separator()
    edit_menu.add_command(label="Go to Line...", command=lambda: dialogs.show_goto_line_dialog(app), accelerator="Ctrl+G")
    edit_menu.add_separator()
    edit_menu.add_command(label="Fold All Blocks", command=app.fold_all)
    edit_menu.add_command(label="Unfold All", command=app.unfold_all)
    edit_menu.add_separator()
    edit_menu.add_command(label="Format Code", command=app._format_editor_code, accelerator="Ctrl+Shift+F")
    edit_menu.add_command(label="Insert Snippet...", command=lambda: dialogs.show_snippet_picker(app), accelerator="Ctrl+J")
    edit_menu.add_command(label="Manage Snippets...", command=lambda: dialogs.show_snippet_manager(app))
    edit_menu.add_separator()
    edit_menu.add_command(label="Undo History...", command=lambda: dialogs.show_undo_history(app))

    # --- View ---
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=view_menu)
    app._split_var = tk.BooleanVar(value=False)
    view_menu.add_checkbutton(
        label="Split Editor", variable=app._split_var,
        command=lambda: app.editor_panel.toggle_split(app._split_var))
    view_menu.add_separator()
    view_menu.add_command(label="Command Palette...",
                          command=lambda: dialogs.show_command_palette(app),
                          accelerator="Ctrl+Shift+P")

    # --- Program ---
    program_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Program", menu=program_menu)
    program_menu.add_command(label="Run Program", command=app.run_code, accelerator="F5")
    program_menu.add_command(label="Stop Program", command=app.stop_code, accelerator="Ctrl+Break")
    program_menu.add_separator()
    program_menu.add_command(label="Export Canvas as PNG...", command=lambda: app.graphics_panel.export_png())
    program_menu.add_command(label="Export Canvas as SVG...", command=lambda: app.graphics_panel.export_svg())
    program_menu.add_separator()
    program_menu.add_command(label="Show Import Graph", command=lambda: dialogs.show_import_graph(app))
    program_menu.add_separator()
    examples_menu = tk.Menu(program_menu, tearoff=0)
    program_menu.add_cascade(label="Load Example", menu=examples_menu)
    for item in [
        ("Hello World",            "examples/templecode/hello.tc"),
        ("Turtle Graphics Spiral", "examples/templecode/spiral.tc"),
        ("Quiz (PILOT style)",     "examples/templecode/quiz.tc"),
        ("Number Guessing Game",   "examples/templecode/guess.tc"),
        ("Mandelbrot (Turtle Art)", "examples/templecode/mandelbrot.tc"),
        None,
        ("Calculator",             "examples/templecode/calculator.tc"),
        ("Countdown Timer",        "examples/templecode/countdown.tc"),
        ("FizzBuzz",               "examples/templecode/fizzbuzz.tc"),
        ("Fibonacci Sequence",     "examples/templecode/fibonacci.tc"),
        ("Times Tables Trainer",   "examples/templecode/timestables.tc"),
        ("Temperature Converter",  "examples/templecode/temperature.tc"),
        ("Dice Roller",            "examples/templecode/dice.tc"),
        None,
        ("Science Quiz",           "examples/templecode/science_quiz.tc"),
        ("Adventure Story",        "examples/templecode/adventure.tc"),
        ("Interactive Drawing",    "examples/templecode/interactive_drawing.tc"),
        None,
        ("Rainbow Spiral",         "examples/templecode/rainbow.tc"),
        ("Shapes Gallery",         "examples/templecode/shapes.tc"),
        ("Flower Garden",          "examples/templecode/flower.tc"),
        ("Kaleidoscope",           "examples/templecode/kaleidoscope.tc"),
        ("Snowflake Fractal",      "examples/templecode/snowflake.tc"),
        ("Clock Face",             "examples/templecode/clock.tc"),
        None,
        ("★ Budget Tracker Pro",   "examples/templecode/budget_tracker.tc"),
    ]:
        if item is None:
            examples_menu.add_separator()
        else:
            examples_menu.add_command(label=item[0], command=lambda p=item[1]: app.load_example(p))

    # --- Debug ---
    debug_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Debug", menu=debug_menu)
    app._debug_var = tk.BooleanVar(value=False)
    debug_menu.add_checkbutton(
        label="Enable Debug Mode", variable=app._debug_var,
        command=lambda: app.interpreter and app.interpreter.set_debug_mode(app._debug_var.get()),
    )
    debug_menu.add_separator()
    debug_menu.add_command(label="Start Debugging          F5",
                           command=lambda: app.debug_start())
    debug_menu.add_command(label="Step Over                F10",
                           command=lambda: app.debug_step_over())
    debug_menu.add_command(label="Continue                 F5",
                           command=lambda: app.debug_continue())
    debug_menu.add_command(label="Stop Debugging      Shift+F5",
                           command=lambda: app.debug_stop())
    debug_menu.add_command(label="Toggle Breakpoint        F9",
                           command=lambda: app.debug_toggle_breakpoint())
    debug_menu.add_separator()
    debug_menu.add_command(label="Add Watch Expression...", command=lambda: dialogs.add_watch_dialog(app))
    debug_menu.add_command(label="Show Watches", command=lambda: dialogs.show_watches(app))
    debug_menu.add_command(label="Clear All Watches",
                           command=lambda: (app._watch_manager.clear(),
                                            app._output("👁  All watches cleared.\n", "out_ok")))
    debug_menu.add_separator()
    debug_menu.add_command(label="Clear All Breakpoints",
                           command=lambda: app.interpreter and app.interpreter.breakpoints.clear())
    debug_menu.add_separator()
    debug_menu.add_command(label="Show Error History", command=lambda: dialogs.show_error_history(app))
    debug_menu.add_command(label="Clear Error History",
                           command=lambda: setattr(app.interpreter, 'error_history', []) if app.interpreter else None)
    debug_menu.add_separator()
    app._profiler_var = tk.BooleanVar(value=False)
    debug_menu.add_checkbutton(
        label="Enable Profiler", variable=app._profiler_var,
        command=lambda: setattr(app._profiler, 'enabled', app._profiler_var.get()),
    )
    debug_menu.add_command(label="Show Profiler Report", command=lambda: dialogs.show_profiler_report(app))

    # --- Test ---
    test_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Test", menu=test_menu)
    test_menu.add_command(label="Run Smoke Test", command=app.run_smoke_test)
    test_menu.add_separator()
    test_menu.add_command(
        label="Open Examples Directory",
        command=lambda: __import__('subprocess').run(["xdg-open", "examples"]),
    )

    # --- Preferences ---
    prefs_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Preferences", menu=prefs_menu)

    theme_menu = tk.Menu(prefs_menu, tearoff=0)
    prefs_menu.add_cascade(label="Color Theme", menu=theme_menu)
    for key, data in THEMES.items():
        theme_menu.add_command(label=data["name"], command=lambda k=key: app.apply_theme(k))

    app._font_family_menu = tk.Menu(prefs_menu, tearoff=0)
    prefs_menu.add_cascade(label="Font Family", menu=app._font_family_menu)
    app._fonts_loaded = False
    app._font_family_menu.add_command(label="Loading...", state=tk.DISABLED)
    app._font_family_menu.bind("<Map>", lambda e: app._populate_font_menu())

    font_size_menu = tk.Menu(prefs_menu, tearoff=0)
    prefs_menu.add_cascade(label="Font Size", menu=font_size_menu)
    for key, data in FONT_SIZES.items():
        font_size_menu.add_command(label=data["name"], command=lambda k=key: app.apply_font_size(k))

    prefs_menu.add_separator()
    app._auto_dark_var = tk.BooleanVar(value=app.auto_dark)
    prefs_menu.add_checkbutton(
        label="Auto Dark/Light (follow OS)",
        variable=app._auto_dark_var,
        command=app._toggle_auto_dark)

    # --- Help ---
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Quick Reference", command=lambda: dialogs.show_quick_reference(app))
    help_menu.add_command(label="Keyboard Shortcuts", command=lambda: dialogs.show_keyboard_shortcuts(app))
    help_menu.add_separator()
    help_menu.add_command(label="About Time Warp II", command=lambda: dialogs.show_about(app))

    # --- Command palette entries ---
    app._palette_commands = [
        ("New File",             app.new_file),
        ("Open File",            app.load_file),
        ("Save File",            app.save_file_quick),
        ("Save File As",         app.save_file),
        ("Run Program",          app.run_code),
        ("Stop Program",         app.stop_code),
        ("Find...",              lambda: dialogs.show_find_dialog(app)),
        ("Replace...",           lambda: dialogs.show_replace_dialog(app)),
        ("Undo",                 app.undo_text),
        ("Redo",                 app.redo_text),
        ("Select All",           app.select_all),
        ("Clear Editor",         app.clear_editor),
        ("Clear Output",         app.clear_output),
        ("Clear Graphics",       app.clear_canvas),
        ("Fold All Blocks",      app.fold_all),
        ("Unfold All",           app.unfold_all),
        ("Toggle Split Editor",  lambda: app.editor_panel.toggle_split(app._split_var)),
        ("Export Canvas as PNG",  lambda: app.graphics_panel.export_png()),
        ("Export Canvas as SVG",  lambda: app.graphics_panel.export_svg()),
        ("Show Import Graph",    lambda: dialogs.show_import_graph(app)),
        ("Format Code",          app._format_editor_code),
        ("Insert Snippet",       lambda: dialogs.show_snippet_picker(app)),
        ("Manage Snippets",      lambda: dialogs.show_snippet_manager(app)),
        ("Undo History",         lambda: dialogs.show_undo_history(app)),
        ("Add Watch Expression", lambda: dialogs.add_watch_dialog(app)),
        ("Show Watches",         lambda: dialogs.show_watches(app)),
        ("Show Profiler Report", lambda: dialogs.show_profiler_report(app)),
        ("Run Smoke Test",       app.run_smoke_test),
        ("Show Error History",   lambda: dialogs.show_error_history(app)),
        ("Go to Line",           lambda: dialogs.show_goto_line_dialog(app)),
        ("Quick Reference",      lambda: dialogs.show_quick_reference(app)),
        ("Keyboard Shortcuts",   lambda: dialogs.show_keyboard_shortcuts(app)),
        ("About Time Warp II",   lambda: dialogs.show_about(app)),
        ("Exit",                 app.exit_app),
    ]
    for key, data in THEMES.items():
        app._palette_commands.append((f"Theme: {data['name']}", lambda k=key: app.apply_theme(k)))
    for key, data in FONT_SIZES.items():
        app._palette_commands.append((f"Font Size: {data['name']}", lambda k=key: app.apply_font_size(k)))
