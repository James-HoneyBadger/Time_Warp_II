# -*- coding: utf-8 -*-
"""
Time Warp II -- Retro Edition  (Windows 2000 / Python 2.7)
===========================================================
A self-contained IDE for the TempleCode language.
Runs on Python 2.7.1-2.7.8 with Tkinter (ships with Python).

Copyright (c) 2025-2026 Honey Badger Universe
"""
from __future__ import print_function, division

import math
import os
import sys
import threading
import time

# Python 2 / 3 Tkinter compat
try:
    import Tkinter as tk
    import tkFont as tkfont
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext
except ImportError:
    import tkinter as tk
    import tkinter.font as tkfont
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.scrolledtext as scrolledtext

# Engine import (same directory)
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)
from templecode27 import TempleCodeEngine

# ======================================================================
#  Application Constants
# ======================================================================

APP_TITLE  = "Time Warp II -- Retro Edition"
VERSION    = "0.1.0-win2k"
CANVAS_W   = 500
CANVAS_H   = 380
EDITOR_W   = 60
EDITOR_H   = 24
OUTPUT_H   = 10
BG_DARK    = "#1e1e2e"
BG_CANVAS  = "#1a1a2a"
BG_EDITOR  = "#1e1e2e"
FG_EDITOR  = "#c6d0f5"
FG_OUTPUT  = "#a6e3a1"
FG_COMMENT = "#6c7086"
FG_KEYWORD = "#89b4fa"
INSERT_CLR = "#f5e0dc"

# ======================================================================
#  Turtle Canvas Adapter
# ======================================================================

class TurtleCanvas(object):
    """Draws on a Tk Canvas using Logo-style coordinates (0,0 = centre)."""

    def __init__(self, canvas):
        self.canvas = canvas
        self._cx = CANVAS_W // 2
        self._cy = CANVAS_H // 2
        self._ids = []
        self._turtle_id = None

    def _sx(self, x):
        return self._cx + x

    def _sy(self, y):
        return self._cy - y  # Logo y points up

    # --- public drawing API (called by engine via canvas_cb) ---

    def handle(self, action, **kw):
        """Route canvas_cb(action, **kw) calls."""
        if action == "line":
            self._draw_line(**kw)
        elif action == "circle":
            self._draw_circle(**kw)
        elif action == "arc":
            self._draw_arc(**kw)
        elif action == "dot":
            self._draw_dot(**kw)
        elif action == "rect":
            self._draw_rect(**kw)
        elif action == "text":
            self._draw_text(**kw)
        elif action == "turtle":
            self._update_turtle(**kw)
        elif action == "clear":
            self._clear()
        elif action == "cls":
            pass  # CLS is for the output panel, not canvas
        try:
            self.canvas.update_idletasks()
        except Exception:
            pass

    def _draw_line(self, x1=0, y1=0, x2=0, y2=0, color="white", width=2, **_):
        cid = self.canvas.create_line(
            self._sx(x1), self._sy(y1),
            self._sx(x2), self._sy(y2),
            fill=color, width=max(1, int(width)))
        self._ids.append(cid)

    def _draw_circle(self, x=0, y=0, radius=10, color="white", width=2, **_):
        sx, sy = self._sx(x), self._sy(y)
        r = abs(radius)
        cid = self.canvas.create_oval(
            sx - r, sy - r, sx + r, sy + r,
            outline=color, width=max(1, int(width)))
        self._ids.append(cid)

    def _draw_arc(self, x=0, y=0, radius=10, angle=90, heading=0,
                  color="white", width=2, **_):
        sx, sy = self._sx(x), self._sy(y)
        r = abs(radius)
        start = 90 - heading
        cid = self.canvas.create_arc(
            sx - r, sy - r, sx + r, sy + r,
            start=start, extent=-angle,
            style="arc", outline=color, width=max(1, int(width)))
        self._ids.append(cid)

    def _draw_dot(self, x=0, y=0, size=4, color="white", **_):
        sx, sy = self._sx(x), self._sy(y)
        r = max(1, size // 2)
        cid = self.canvas.create_oval(
            sx - r, sy - r, sx + r, sy + r,
            fill=color, outline=color)
        self._ids.append(cid)

    def _draw_rect(self, x=0, y=0, width=50, height=50, color="white",
                   pen_width=2, **_):
        sx, sy = self._sx(x), self._sy(y)
        cid = self.canvas.create_rectangle(
            sx, sy, sx + width, sy + height,
            outline=color, width=max(1, int(pen_width)))
        self._ids.append(cid)

    def _draw_text(self, x=0, y=0, text="", color="white", size=12, **_):
        sx, sy = self._sx(x), self._sy(y)
        cid = self.canvas.create_text(
            sx, sy, text=text, fill=color,
            font=("Arial", max(6, int(size))), anchor="nw")
        self._ids.append(cid)

    def _update_turtle(self, x=0, y=0, heading=0, visible=True, **_):
        self.canvas.delete("turtle")
        if not visible:
            return
        sx, sy = self._sx(x), self._sy(y)
        angle = math.radians(90 - heading)
        sz = 10
        tip_x = sx + sz * math.cos(angle)
        tip_y = sy - sz * math.sin(angle)
        la = angle + math.radians(140)
        lx = sx + sz * 0.6 * math.cos(la)
        ly = sy - sz * 0.6 * math.sin(la)
        ra = angle - math.radians(140)
        rx = sx + sz * 0.6 * math.cos(ra)
        ry = sy - sz * 0.6 * math.sin(ra)
        self.canvas.create_polygon(
            tip_x, tip_y, lx, ly, rx, ry,
            fill="#a6e3a1", outline="#40a02b", width=2, tags="turtle")

    def _clear(self):
        for cid in self._ids:
            self.canvas.delete(cid)
        self._ids = []
        self.canvas.delete("turtle")

# ======================================================================
#  Main Application Window
# ======================================================================

class TimeWarpApp(object):

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=BG_DARK)
        # Aim for 1024x700 on a 1024x768 screen
        self.root.geometry("1024x700")
        try:
            self.root.state("zoomed")  # maximise on Windows
        except Exception:
            pass

        self.current_file = None
        self.engine = None              # created fresh per run
        self._running = False
        self._input_var = None          # set when engine requests input

        self._build_menu()
        self._build_ui()
        self._bind_keys()

    # ------------------------------------------------------------------
    #  Menu bar
    # ------------------------------------------------------------------

    def _build_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="New           Ctrl+N", command=self._new_file)
        file_menu.add_command(label="Open...       Ctrl+O", command=self._open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save          Ctrl+S", command=self._save_file)
        file_menu.add_command(label="Save As...", command=self._save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="File", menu=file_menu)

        prog_menu = tk.Menu(menu, tearoff=0)
        prog_menu.add_command(label="Run           F5", command=self._run_program)
        prog_menu.add_command(label="Stop          F6", command=self._stop_program)
        prog_menu.add_separator()
        prog_menu.add_command(label="Clear Output", command=self._clear_output)
        prog_menu.add_command(label="Clear Canvas", command=self._clear_canvas)
        menu.add_cascade(label="Program", menu=prog_menu)

        examples_menu = tk.Menu(menu, tearoff=0)
        examples_dir = os.path.join(_here, "examples")
        if os.path.isdir(examples_dir):
            for fn in sorted(os.listdir(examples_dir)):
                if fn.lower().endswith(".tc"):
                    path = os.path.join(examples_dir, fn)
                    examples_menu.add_command(
                        label=fn,
                        command=lambda p=path: self._load_example(p))
        menu.add_cascade(label="Examples", menu=examples_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menu.add_cascade(label="Help", menu=help_menu)

    # ------------------------------------------------------------------
    #  UI layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ----- Top paned: Editor | Canvas -----
        top = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                             bg=BG_DARK, sashwidth=4, sashrelief=tk.RAISED)
        top.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 0))

        # Editor frame
        editor_frame = tk.Frame(top, bg=BG_DARK)
        tk.Label(editor_frame, text=" Code Editor", bg=BG_DARK,
                 fg="#cdd6f4", anchor="w",
                 font=("Arial", 9, "bold")).pack(fill=tk.X)
        self.editor = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.NONE,
            bg=BG_EDITOR, fg=FG_EDITOR,
            insertbackground=INSERT_CLR,
            font=("Courier New", 11),
            undo=True, width=EDITOR_W, height=EDITOR_H)
        self.editor.pack(fill=tk.BOTH, expand=True)
        top.add(editor_frame, minsize=300)

        # Canvas frame
        canvas_frame = tk.Frame(top, bg=BG_DARK)
        tk.Label(canvas_frame, text=" Turtle Canvas", bg=BG_DARK,
                 fg="#cdd6f4", anchor="w",
                 font=("Arial", 9, "bold")).pack(fill=tk.X)
        self.canvas = tk.Canvas(canvas_frame, bg=BG_CANVAS,
                                width=CANVAS_W, height=CANVAS_H,
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        top.add(canvas_frame, minsize=200)

        # ----- Bottom: Output + Input -----
        bottom = tk.Frame(self.root, bg=BG_DARK)
        bottom.pack(fill=tk.BOTH, padx=2, pady=(0, 2))

        tk.Label(bottom, text=" Output", bg=BG_DARK, fg="#cdd6f4",
                 anchor="w", font=("Arial", 9, "bold")).pack(fill=tk.X)
        self.output = scrolledtext.ScrolledText(
            bottom, wrap=tk.WORD,
            bg="#11111b", fg=FG_OUTPUT,
            font=("Courier New", 10),
            height=OUTPUT_H, state=tk.NORMAL)
        self.output.pack(fill=tk.BOTH, expand=True)

        # Input bar
        inp_frame = tk.Frame(bottom, bg=BG_DARK)
        inp_frame.pack(fill=tk.X, pady=(2, 0))
        tk.Label(inp_frame, text="Input:", bg=BG_DARK, fg="#cdd6f4",
                 font=("Arial", 9)).pack(side=tk.LEFT)
        self.input_entry = tk.Entry(
            inp_frame, bg="#313244", fg="#f5e0dc",
            insertbackground="#f5e0dc",
            font=("Courier New", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.submit_btn = tk.Button(
            inp_frame, text="Submit", bg="#45475a", fg="#cdd6f4",
            activebackground="#585b70",
            font=("Arial", 9, "bold"),
            command=self._submit_input)
        self.submit_btn.pack(side=tk.LEFT)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready  |  %s %s" % (APP_TITLE, VERSION))
        tk.Label(self.root, textvariable=self.status_var,
                 bg="#181825", fg="#6c7086", anchor="w",
                 font=("Arial", 8)).pack(fill=tk.X, side=tk.BOTTOM)

    # ------------------------------------------------------------------
    #  Key bindings
    # ------------------------------------------------------------------

    def _bind_keys(self):
        self.root.bind("<F5>", lambda e: self._run_program())
        self.root.bind("<F6>", lambda e: self._stop_program())
        self.root.bind("<Control-n>", lambda e: self._new_file())
        self.root.bind("<Control-o>", lambda e: self._open_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())
        self.input_entry.bind("<Return>", lambda e: self._submit_input())

    # ------------------------------------------------------------------
    #  File operations
    # ------------------------------------------------------------------

    def _new_file(self):
        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.root.title(APP_TITLE)

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open TempleCode File",
            filetypes=[("TempleCode files", "*.tc"), ("All files", "*.*")])
        if path:
            self._load_file(path)

    def _load_file(self, path):
        try:
            f = open(path, "r")
            text = f.read()
            f.close()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", text)
            self.current_file = path
            self.root.title("%s -- %s" % (APP_TITLE, os.path.basename(path)))
        except Exception as exc:
            messagebox.showerror("Error", "Cannot open file:\n%s" % exc)

    def _load_example(self, path):
        self._load_file(path)

    def _save_file(self):
        if self.current_file:
            self._do_save(self.current_file)
        else:
            self._save_as()

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save TempleCode File",
            defaultextension=".tc",
            filetypes=[("TempleCode files", "*.tc"), ("All files", "*.*")])
        if path:
            self._do_save(path)
            self.current_file = path
            self.root.title("%s -- %s" % (APP_TITLE, os.path.basename(path)))

    def _do_save(self, path):
        try:
            f = open(path, "w")
            f.write(self.editor.get("1.0", tk.END))
            f.close()
            self.status_var.set("Saved: %s" % path)
        except Exception as exc:
            messagebox.showerror("Error", "Cannot save file:\n%s" % exc)

    # ------------------------------------------------------------------
    #  Program execution
    # ------------------------------------------------------------------

    def _run_program(self):
        if self._running:
            return
        code = self.editor.get("1.0", tk.END).strip()
        if not code:
            return
        self._clear_output()
        self._clear_canvas()

        self._running = True
        self.status_var.set("Running...")

        # Build fresh engine with our callbacks
        tc = TurtleCanvas(self.canvas)
        self.engine = TempleCodeEngine(
            output_cb=self._output_cb,
            input_cb=self._input_cb,
            canvas_cb=tc.handle)

        # Run in a background thread so the GUI stays responsive
        def _worker():
            try:
                self.engine.run(code)
            except Exception as exc:
                self._output_cb("FATAL: %s" % exc)
            self._running = False
            self.root.after(0, lambda: self.status_var.set(
                "Finished  |  %s %s" % (APP_TITLE, VERSION)))
        t = threading.Thread(target=_worker)
        t.daemon = True
        t.start()

    def _stop_program(self):
        if self.engine:
            self.engine.running = False
        self._running = False
        self.status_var.set("Stopped  |  %s %s" % (APP_TITLE, VERSION))

    # ------------------------------------------------------------------
    #  Output callback (thread-safe)
    # ------------------------------------------------------------------

    def _output_cb(self, text):
        """Called by the engine to print a line of text."""
        def _do():
            self.output.insert(tk.END, str(text) + "\n")
            self.output.see(tk.END)
        self.root.after(0, _do)

    # ------------------------------------------------------------------
    #  Input callback (blocking, thread-safe)
    # ------------------------------------------------------------------

    def _input_cb(self, prompt):
        """Called by the engine when it needs user input. Blocks the
        engine thread until the user presses Submit."""
        # Show prompt
        if prompt:
            self._output_cb(prompt)

        # Prepare an event to wait on
        event = threading.Event()
        result = [None]

        def _highlight():
            self.input_entry.config(bg="#ffffcc")
            self.input_entry.focus_set()

        def _collect(value):
            result[0] = value
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(bg="#313244")
            event.set()

        self.root.after(0, _highlight)
        # Store collector so _submit_input can call it
        self._pending_input = _collect
        event.wait()  # blocks engine thread
        self._pending_input = None

        val = result[0] if result[0] is not None else ""
        def _echo():
            self.output.insert(tk.END, ">> %s\n" % val)
            self.output.see(tk.END)
        self.root.after(0, _echo)
        return val

    def _submit_input(self):
        """Called when the user presses Submit or Enter in the input bar."""
        val = self.input_entry.get()
        if hasattr(self, "_pending_input") and self._pending_input:
            self._pending_input(val)
        elif self.engine and self._running:
            pass  # no pending input request
        else:
            # Not running -- nothing to do
            pass

    # ------------------------------------------------------------------
    #  Canvas / Output helpers
    # ------------------------------------------------------------------

    def _clear_output(self):
        self.output.delete("1.0", tk.END)

    def _clear_canvas(self):
        self.canvas.delete("all")

    # ------------------------------------------------------------------
    #  About dialog
    # ------------------------------------------------------------------

    def _show_about(self):
        messagebox.showinfo("About",
            "%s\n"
            "Version %s\n\n"
            "A TempleCode IDE for retro systems.\n"
            "Runs on Python 2.7 / Windows 2000.\n\n"
            "BASIC + PILOT + Logo in one language.\n\n"
            "(c) 2025-2026 Honey Badger Universe"
            % (APP_TITLE, VERSION))

# ======================================================================
#  Entry point
# ======================================================================

def main():
    root = tk.Tk()
    app = TimeWarpApp(root)

    # load file from command-line arg
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        app._load_file(sys.argv[1])

    root.mainloop()

if __name__ == "__main__":
    main()
