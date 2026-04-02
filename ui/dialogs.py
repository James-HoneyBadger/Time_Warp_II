"""Dialogs for Time Warp II (Find, Replace, GoTo, Snippets, etc.)."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


# ======================================================================
#  Find dialog
# ======================================================================

def show_find_dialog(app: TempleCodeApp) -> None:
    """Display a Find dialog for searching text in the editor."""
    tk = app.tk
    dlg = tk.Toplevel(app.root)
    dlg.title("Find")
    dlg.geometry("400x150")
    dlg.resizable(False, False)
    dlg.transient(app.root)
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
        app.editor_text.clear_search_highlights()
        match = app.editor_text.find_text(
            term, start_pos=app.editor_text.index(tk.INSERT),
            case_sensitive=case_var.get(), whole_word=whole_var.get(), regex=regex_var.get(),
        )
        if match:
            s, e = match
            app.editor_text.tag_remove("sel", "1.0", tk.END)
            app.editor_text.tag_add("sel", s, e)
            app.editor_text.mark_set(tk.INSERT, e)
            app.editor_text.see(s)
            app.editor_text.highlight_search_results(
                term, case_sensitive=case_var.get(),
                whole_word=whole_var.get(), regex=regex_var.get(),
            )
            app._output(f"Found '{term}' at {s}\n")
        else:
            app._output(f"'{term}' not found\n", "out_warn")

    bf = tk.Frame(dlg)
    bf.grid(row=2, column=0, columnspan=2, pady=10)
    tk.Button(bf, text="Find", command=do_find, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(bf, text="Find Next", command=do_find, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(bf, text="Close", command=dlg.destroy, width=10).pack(side=tk.LEFT, padx=5)
    se.bind('<Return>', lambda e: do_find())
    dlg.bind('<Escape>', lambda e: dlg.destroy())


# ======================================================================
#  Replace dialog
# ======================================================================

def show_replace_dialog(app: TempleCodeApp) -> None:
    """Display a Find & Replace dialog for the editor."""
    tk = app.tk
    dlg = tk.Toplevel(app.root)
    dlg.title("Replace")
    dlg.geometry("400x180")
    dlg.resizable(False, False)
    dlg.transient(app.root)
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
        replaced = app.editor_text.replace_text(
            s, r, start_pos=app.editor_text.index(tk.INSERT),
            case_sensitive=case_var.get(), whole_word=whole_var.get(), regex=regex_var.get(),
        )
        if replaced:
            app._output(f"Replaced '{s}' with '{r}'\n", "out_ok")
            app.editor_text.highlight_search_results(
                s, case_sensitive=case_var.get(),
                whole_word=whole_var.get(), regex=regex_var.get(),
            )
        else:
            app._output(f"'{s}' not found\n", "out_warn")

    def do_replace_all():
        s, r = search_var.get(), replace_var.get()
        if not s:
            return
        count = app.editor_text.replace_all(
            s, r, case_sensitive=case_var.get(),
            whole_word=whole_var.get(), regex=regex_var.get(),
        )
        app._output(f"Replaced {count} occurrence(s) of '{s}' with '{r}'\n", "out_ok")
        app.editor_text.clear_search_highlights()

    bf = tk.Frame(dlg)
    bf.grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(bf, text="Replace", command=do_replace, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(bf, text="Replace All", command=do_replace_all, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(bf, text="Close", command=dlg.destroy, width=10).pack(side=tk.LEFT, padx=5)
    dlg.bind('<Escape>', lambda e: dlg.destroy())


# ======================================================================
#  Go to Line dialog
# ======================================================================

def show_goto_line_dialog(app: TempleCodeApp) -> None:
    """Display a dialog to jump to a specific line number."""
    tk = app.tk
    dlg = tk.Toplevel(app.root)
    dlg.title("Go to Line")
    dlg.geometry("300x100")
    dlg.resizable(False, False)
    dlg.transient(app.root)
    dlg.grab_set()

    tk.Label(dlg, text="Line number:").pack(padx=10, pady=(10, 0), anchor="w")
    line_var = tk.StringVar()
    entry = tk.Entry(dlg, textvariable=line_var, width=20)
    entry.pack(padx=10, pady=5, fill=tk.X)
    entry.focus()

    def _goto():
        try:
            num = int(line_var.get())
            text_w = app.editor_panel.inner_text
            text_w.mark_set(tk.INSERT, f"{num}.0")
            text_w.see(f"{num}.0")
            app.editor_panel.highlight_current_line()
            dlg.destroy()
        except ValueError:
            pass

    entry.bind("<Return>", lambda e: _goto())
    tk.Button(dlg, text="Go", command=_goto, width=8).pack(pady=(0, 10))
    dlg.bind("<Escape>", lambda e: dlg.destroy())


# ======================================================================
#  Command Palette
# ======================================================================

def show_command_palette(app: TempleCodeApp) -> None:
    """Display a searchable command palette for quick access to IDE actions."""
    tk = app.tk
    dlg = tk.Toplevel(app.root)
    dlg.title("Command Palette")
    dlg.geometry("450x350")
    dlg.transient(app.root)
    dlg.grab_set()
    dlg.resizable(True, True)

    from core.config import THEMES
    theme = THEMES.get(app.current_theme, THEMES["dark"])
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

    all_cmds = app._palette_commands

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
                    app.root.after(50, fn)
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


# ======================================================================
#  Error History
# ======================================================================

def show_error_history(app: TempleCodeApp) -> None:
    """Display a window listing all errors from the last interpretation."""
    if not app.interpreter or not app.interpreter.error_history:
        app.messagebox.showinfo("Error History", "No errors recorded.")
        return
    tk = app.tk
    from tkinter import scrolledtext
    win = tk.Toplevel(app.root)
    win.title("Error History")
    win.geometry("600x400")
    tw = scrolledtext.ScrolledText(win, wrap=tk.WORD)
    tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    for i, err in enumerate(app.interpreter.error_history[-10:], 1):
        tw.insert(tk.END, f"{i}. Line {err.get('line', 'N/A')}: {err['message']}\n")
    tw.config(state=tk.DISABLED)


# ======================================================================
#  About / Help
# ======================================================================

def show_about(app: TempleCodeApp) -> None:
    sep = "-" * 32
    app.messagebox.showinfo("Time Warp II", (
        f"{sep}\n"
        "Time Warp II\nVersion 2.0.0\n\n"
        "A single-language IDE for TempleCode,\n"
        "a fusion of BASIC, PILOT, and Logo\n"
        "inspired by the early 1990s.\n\n"
        "FEATURES:\n"
        "  • BASIC (PRINT, LET, IF/ELSEIF, FOR, ON GOTO, UNSET, EVAL, PROGRAMINFO)\n"
        "  • PILOT (T:, A:, M:, Y:, N:, J:, C:, G:)\n"
        "  • Logo turtle (FORWARD, RIGHT, REPEAT, LABEL, CIRCLEFILL, RECTFILL, PSET, PRESET, POINT)\n"
        "  • Sound support (BEEP, PLAYNOTE, SOUND)\n"
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


def show_quick_reference(app: TempleCodeApp) -> None:
    """Display a scrollable quick-reference for TempleCode commands."""
    tk = app.tk
    from tkinter import scrolledtext
    win = tk.Toplevel(app.root)
    win.title("TempleCode Quick Reference")
    win.geometry("700x550")
    tw = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Courier", 10))
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
        "  Math: SIN COS TAN ATN LOG EXP SQRT ABS INT CEIL FIX RND RANDINT\n"
        "  String: LEN MID$ LEFT$ RIGHT$ CHR$ ASC STR$ VAL TRIM CONTAINS STARTSWITH ENDSWITH\n"
        "  Utility: TIMER  DATE$  TIME$  NOW$  TYPE(expr)  EVAL  PROGRAMINFO\n"
        "  Graphics: CIRCLEFILL  RECTFILL  SETFILLCOLOR  SETBACKGROUND  FILL\n"
        "  File: FILEEXISTS  COPYFILE  DELETEFILE  READFILE  WRITEFILE  APPENDFILE\n"
        "  HELP\n\n"
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


def show_keyboard_shortcuts(app: TempleCodeApp) -> None:
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
    app.messagebox.showinfo("Keyboard Shortcuts", shortcuts)


# ======================================================================
#  Watch expressions
# ======================================================================

def show_watches(app: TempleCodeApp) -> None:
    """Display current watch expression values in a dialog."""
    tk = app.tk
    from tkinter import scrolledtext
    win = tk.Toplevel(app.root)
    win.title("Watch Expressions")
    win.geometry("500x350")
    win.transient(app.root)

    tw = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Courier", 10))
    tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    wm = app._watch_manager
    if not wm.expressions:
        tw.insert(tk.END, "(no watch expressions set)\n\nUse Debug → Add Watch Expression to add one.")
    else:
        tw.insert(tk.END, "═══ WATCH EXPRESSIONS ═══\n\n")
        pairs = wm.evaluate_all(app.interpreter)
        for expr, val in pairs:
            tw.insert(tk.END, f"  {expr} = {val}\n")
        tw.insert(tk.END, "\n═══ ALL VARIABLES ═══\n\n")
        for k, v in sorted(app.interpreter.variables.items()):
            tw.insert(tk.END, f"  {k} = {v!r}\n")

    tw.config(state=tk.DISABLED)

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    tk.Button(btn_frame, text="Add Watch", command=lambda: (
        add_watch_dialog(app), win.destroy(), show_watches(app)
    )).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Clear All", command=lambda: (
        wm.clear(), win.destroy(),
        app._output("👁  All watches cleared.\n", "out_ok")
    )).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Refresh", command=lambda: (
        win.destroy(), show_watches(app)
    )).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)


def add_watch_dialog(app: TempleCodeApp) -> None:
    """Prompt the user to add a watch expression."""
    from tkinter import simpledialog
    expr = simpledialog.askstring(
        "Add Watch", "Variable name or expression to watch:",
        parent=app.root,
    )
    if expr:
        app._watch_manager.add(expr)
        app._output(f"👁  Watch added: {expr}\n", "out_ok")


# ======================================================================
#  Profiler report
# ======================================================================

def show_profiler_report(app: TempleCodeApp) -> None:
    tk = app.tk
    from tkinter import scrolledtext
    win = tk.Toplevel(app.root)
    win.title("Profiler Report")
    win.geometry("700x500")
    win.transient(app.root)

    tw = scrolledtext.ScrolledText(win, wrap=tk.NONE, font=("Courier", 10))
    tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    if not app._profiler.get_stats():
        tw.insert(tk.END, "No profiling data.\n\n"
                  "Enable the profiler via Debug → Enable Profiler,\n"
                  "then run a program.")
    else:
        tw.insert(tk.END, app._profiler.format_report())

    tw.config(state=tk.DISABLED)

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    tk.Button(btn_frame, text="Reset", command=lambda: (
        app._profiler.reset(),
        app._output("📊 Profiler data cleared.\n", "out_ok"),
        win.destroy()
    )).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)


# ======================================================================
#  Snippet picker / manager
# ======================================================================

def show_snippet_picker(app: TempleCodeApp) -> None:
    """Show a quick-pick list of snippets to insert."""
    tk = app.tk
    dlg = tk.Toplevel(app.root)
    dlg.title("Insert Snippet")
    dlg.geometry("450x400")
    dlg.transient(app.root)
    dlg.grab_set()

    tk.Label(dlg, text="Select a snippet to insert:").pack(padx=10, pady=(10, 5), anchor="w")

    filter_var = tk.StringVar()
    filter_entry = tk.Entry(dlg, textvariable=filter_var)
    filter_entry.pack(fill=tk.X, padx=10, pady=(0, 5))
    filter_entry.focus()

    list_frame = tk.Frame(dlg)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
    listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    snippets = app._snippet_manager.all_snippets()
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

    desc_label = tk.Label(dlg, text="", wraplength=400, anchor="w", justify="left")
    desc_label.pack(fill=tk.X, padx=10, pady=5)

    def on_select(_event=None):
        sel = listbox.curselection()
        if not sel:
            return
        text = listbox.get(sel[0])
        prefix = text[:10].strip()
        for key in snippet_keys:
            if snippets[key].get("prefix", "") == prefix:
                desc_label.config(text=snippets[key].get("description", ""))
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
                app.editor_text.insert(app.tk.INSERT, body)
                app._mark_dirty()
                app._output(f"✂️  Snippet inserted: {snippets[key].get('label', key)}\n", "out_ok")
                dlg.destroy()
                return

    tk.Button(dlg, text="Insert", command=insert_selected).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(dlg, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
    listbox.bind("<Double-Button-1>", lambda e: insert_selected())
    dlg.bind("<Return>", lambda e: insert_selected())
    dlg.bind("<Escape>", lambda e: dlg.destroy())


def show_snippet_manager(app: TempleCodeApp) -> None:
    """Show a dialog to manage (add/edit/delete) user snippets."""
    tk = app.tk
    win = tk.Toplevel(app.root)
    win.title("Manage Snippets")
    win.geometry("600x500")
    win.transient(app.root)

    list_frame = tk.LabelFrame(win, text="Snippets", padx=5, pady=5)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
    listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    snippets = app._snippet_manager.all_snippets()

    def refresh():
        nonlocal snippets
        snippets = app._snippet_manager.all_snippets()
        listbox.delete(0, tk.END)
        for key in sorted(snippets.keys()):
            s = snippets[key]
            builtin = (" (built-in)"
                       if key in app._snippet_manager.BUILTIN_SNIPPETS
                       and not app._snippet_manager.is_user_snippet(key)
                       else "")
            listbox.insert(tk.END, f"{s.get('prefix', ''):10s}  {s.get('label', key)}{builtin}")

    refresh()

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

    def add_snippet():
        _snippet_edit_dialog(app, win, callback=refresh)

    def delete_snippet():
        sel = listbox.curselection()
        if not sel:
            return
        key = sorted(snippets.keys())[sel[0]]
        if app._snippet_manager.remove(key):
            app._output(f"🗑  Snippet removed: {key}\n", "out_ok")
        refresh()

    tk.Button(btn_frame, text="Add New", command=add_snippet).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Delete Selected", command=delete_snippet).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)


def _snippet_edit_dialog(app: TempleCodeApp, parent, callback=None) -> None:
    tk = app.tk
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
            app.messagebox.showwarning("Missing Fields", "Key and body are required.", parent=dlg)
            return
        app._snippet_manager.add(key, label or key, prefix or key, body, desc)
        app._output(f"✂️  Snippet saved: {label or key}\n", "out_ok")
        dlg.destroy()
        if callback:
            callback()

    tk.Button(dlg, text="Save", command=save).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(dlg, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
    dlg.bind("<Escape>", lambda e: dlg.destroy())


# ======================================================================
#  Undo History viewer
# ======================================================================

def show_undo_history(app: TempleCodeApp) -> None:
    tk = app.tk
    win = tk.Toplevel(app.root)
    win.title("Undo History")
    win.geometry("500x400")
    win.transient(app.root)

    history = app._undo_history.get_history_list()

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
        import datetime
        for entry in history:
            ts = datetime.datetime.fromtimestamp(entry["timestamp"]).strftime("%H:%M:%S")
            marker = " ◀" if entry["current"] else ""
            listbox.insert(
                tk.END,
                f"#{entry['index']:3d}  {ts}  {entry['description']:12s}  "
                f"({entry['length']} chars){marker}"
            )
        for entry in history:
            if entry["current"]:
                listbox.see(entry["index"])
                listbox.selection_set(entry["index"])

    def jump_to():
        sel = listbox.curselection()
        if not sel:
            return
        content = app._undo_history.jump_to(sel[0])
        if content is not None:
            app.editor_text.delete("1.0", app.tk.END)
            app.editor_text.insert("1.0", content.rstrip("\n"))
            app._mark_dirty()
            app._output(f"↩️  Restored to history #{sel[0]}\n", "out_ok")
        win.destroy()

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    tk.Button(btn_frame, text="Restore Selected", command=jump_to).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Clear History", command=lambda: (
        app._undo_history.clear(), win.destroy(),
        app._output("🗑  Undo history cleared.\n", "out_ok")
    )).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)
    listbox.bind("<Double-Button-1>", lambda e: jump_to())


# ======================================================================
#  Import Graph
# ======================================================================

def show_import_graph(app: TempleCodeApp) -> None:
    tk = app.tk
    from tkinter import scrolledtext
    import os
    source = app.editor_text.get("1.0", app.tk.END)

    imports = app._parse_imports(source)

    win = tk.Toplevel(app.root)
    win.title("Import Dependency Graph")
    win.geometry("600x400")
    win.transient(app.root)

    tw = scrolledtext.ScrolledText(win, wrap=tk.NONE, font=("Courier", 10))
    tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    if not imports:
        tw.insert(tk.END, "No IMPORT statements found in the current editor text.\n\n"
                  "Add IMPORT \"filename.tc\" to your code to use this feature.")
    else:
        if app.current_file_path and os.path.isfile(app.current_file_path):
            graph = app._build_import_graph(app.current_file_path)
            tw.insert(tk.END, app._format_import_graph(graph))
        else:
            tw.insert(tk.END, "═══ IMPORTS (current file) ═══\n\n")
            for imp in imports:
                tw.insert(tk.END, f"  └── {imp}\n")
            tw.insert(tk.END, f"\n{len(imports)} import(s) found.\n"
                      "Save your file to enable full dependency graph traversal.")

    tw.config(state=tk.DISABLED)
    tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))
