#!/usr/bin/env python3
"""
TempleCode Interpreter - Core Execution Engine

The TempleCodeInterpreter is the central execution engine for Time Warp II.
It supports a single unified language called TempleCode, which blends BASIC,
PILOT, and Logo into one educational programming language inspired by the early
1990s era of computing.

TempleCode Language Features:
  From BASIC: Line numbers, PRINT, LET, IF/THEN/ELSE, FOR/NEXT, GOTO,
              GOSUB/RETURN, DIM, INPUT, math & string functions
  From PILOT: T: (type text), A: (accept input), M: (match), Y:/N:
              (conditional), J: (jump), C: (call subroutine)
  From Logo:  FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN, REPEAT,
              SETCOLOR, CIRCLE, HOME, CLEARSCREEN, TO/END procedures
"""
from __future__ import annotations

from typing import Any
import tkinter as tk
from tkinter import simpledialog
import re
import random
import math
import time
import threading

# Optional PIL import
PIL_AVAILABLE = False
Image = None
ImageTk = None

try:
    from PIL import Image as PILImage, ImageTk as PILImageTk  # type: ignore[attr-defined]
    Image = PILImage
    ImageTk = PILImageTk
    PIL_AVAILABLE = True
except ImportError:
    print("ℹ️  PIL/Pillow not available - image features disabled")

# Import the TempleCode language executor
from .languages import TempleCodeExecutor  # noqa: E402


# ---------------------------------------------------------------------------
#  Thread-safe GUI helper
# ---------------------------------------------------------------------------

def _highlight_entry(widget, color: str) -> None:
    """Focus and recolour an Entry widget; called on the main thread via after()."""
    try:
        widget.focus_force()
        widget.config(bg=color)
    except Exception:
        pass


# ---------------------------------------------------------------------------
#  Headless canvas stub for testing / non-GUI execution
# ---------------------------------------------------------------------------

class _HeadlessCanvas:
    """Minimal canvas stub so drawing ops record metadata for tests."""

    def __init__(self):
        self.created = []
        self._id_counter = 1

    def _record(self, kind, args, kwargs):
        item_id = self._id_counter
        self._id_counter += 1
        self.created.append({"id": item_id, "type": kind, "args": args, "kwargs": kwargs})
        return item_id

    # Canvas drawing methods
    def create_line(self, *a, **kw):
        """Record a line draw."""
        return self._record("line", a, kw)

    def create_oval(self, *a, **kw):
        """Record an oval draw."""
        return self._record("oval", a, kw)

    def create_rectangle(self, *a, **kw):
        """Record a rectangle draw."""
        return self._record("rectangle", a, kw)

    def create_polygon(self, *a, **kw):
        """Record a polygon draw."""
        return self._record("polygon", a, kw)

    def create_text(self, *a, **kw):
        """Record a text draw."""
        return self._record("text", a, kw)

    def create_image(self, *a, **kw):
        """Record an image draw."""
        return self._record("image", a, kw)

    def create_arc(self, *a, **kw):
        """Record an arc draw."""
        return self._record("arc", a, kw)

    # Geometry / lifecycle stubs
    def bbox(self, *a, **kw):
        """Return a dummy bounding box."""
        return (0, 0, 0, 0)

    def configure(self, **kw):
        """No-op configure stub."""

    def config(self, **kw):
        """No-op config stub."""

    def winfo_width(self):
        """Return default canvas width."""
        return 600

    def winfo_height(self):
        """Return default canvas height."""
        return 400

    def update_idletasks(self):
        """No-op update_idletasks stub."""

    def update(self):
        """No-op update stub."""

    def delete(self, *a, **kw):
        """No-op delete stub."""


# ---------------------------------------------------------------------------
#  Main Interpreter
# ---------------------------------------------------------------------------

class TempleCodeInterpreter:
    """
    Main interpreter for Time Warp II.

    Manages program execution, variable storage, turtle graphics,
    and flow control (jumps, loops, conditionals).
    """

    # CGA-ish default turtle colour palette
    DEFAULT_PALETTE = [
        "black", "red", "blue", "green",
        "purple", "orange", "teal", "magenta",
    ]

    # ------------------------------------------------------------------
    #  Initialisation
    # ------------------------------------------------------------------

    def __init__(self, output_widget=None) -> None:
        self.output_widget = output_widget
        self._main_thread = threading.current_thread()  # always created on main thread

        # Pre-filled input buffer (used by tests / queued input)
        self.input_buffer: list = []

        # Program execution state
        self.variables: dict = {}
        self.labels: dict = {}
        self.program_lines: list = []
        self.current_line: int = 0
        self.stack: list = []           # GOSUB return stack
        self.for_stack: list = []
        self.do_stack: list = []
        self.while_stack: list = []
        self.select_stack: list = []
        self.match_flag: bool = False
        self._last_match_set: bool = False
        self.running: bool = False
        self.error_history: list = []

        # Debugging
        self.debug_mode: bool = False
        self.breakpoints: set = set()

        # Turtle graphics (lazy-initialised)
        self.turtle_graphics = None
        self.ide_turtle_canvas = None
        self.turtle_trace = False
        self.preserve_turtle_canvas = False
        self._turtle_color_palette = list(self.DEFAULT_PALETTE)
        self.default_pen_style = "solid"

        # Logo procedures: name -> (params, body_lines)
        self.logo_procedures: dict = {}

        # Speed controls (set by IDE)
        self.exec_delay_ms: int = 0      # delay between lines (ms)
        self.turtle_delay_ms: int = 0    # delay after each turtle move (ms)

        # Input synchronisation (set by IDE for input-bar integration)
        self._input_wait_var = None          # kept for legacy checks; use _input_event
        self._input_event: threading.Event | None = None  # signals input available
        self._waiting_for_input: bool = False  # drain loop re-asserts Entry focus
        self._input_result: str = ""         # value written by _submit_input
        self._input_entry_widget = None      # reference to IDE's input Entry widget
        self._input_entry_bg: str = "#1e1e1e"  # original bg colour to restore

        # Program timing (for TIMER function)
        self._program_start_time: float = 0.0

        # Pre-collected DATA values (populated at load time)
        self._data_values: list = []
        self._data_pos: int = 0

        # --- Modern language extensions ---
        # SUB / FUNCTION definitions: name -> {params, body_start_line, body_end_line}
        self.sub_definitions: dict = {}
        self.function_definitions: dict = {}
        self.call_stack: list = []          # for SUB/FUNCTION return
        self.return_value = None            # FUNCTION return value

        # Lists and Dictionaries
        self.lists: dict = {}              # name -> list
        self.dicts: dict = {}              # name -> dict

        # File handles
        self.file_handles: dict = {}       # handle_num -> file object

        # Error handling
        self.try_stack: list = []           # TRY/CATCH nesting
        self.last_error: str = ""           # last caught error message

        # CONST values (immutable variables)
        self.constants: set = set()

        # Module import tracking
        self.imported_modules: set = set()

        # Watch expressions & profiler (set up by IDE or CLI)
        self.watch_manager: Any = None   # core.features.ide_features.WatchManager
        self.profiler: Any = None        # core.features.ide_features.Profiler

        # Language executor
        self.templecode_executor = TempleCodeExecutor(self)
        self.current_language_mode = "templecode"
        self.current_language = "templecode"

    # ------------------------------------------------------------------
    #  Public input-synchronisation API (used by the IDE GUI)
    # ------------------------------------------------------------------

    @property
    def waiting_for_input(self) -> bool:
        """True while the interpreter is blocked inside an INPUT statement."""
        return self._waiting_for_input

    def reset_input_state(self) -> None:
        """Force-clear the input-wait flag (called by the IDE when a run ends)."""
        self._waiting_for_input = False

    def submit_input(self, value: str) -> None:
        """Deliver *value* to the waiting INPUT statement and unblock the thread."""
        if self._input_event is not None:
            self._input_result = value
            self._input_event.set()

    def cancel_input(self) -> None:
        """Unblock a waiting INPUT statement with an empty string (e.g. on stop)."""
        if self._input_event is not None:
            self._input_result = ""
            self._input_event.set()

    # ------------------------------------------------------------------
    #  Language mode (always TempleCode)
    # ------------------------------------------------------------------

    def set_language_mode(self, _mode):
        """Set the current language mode (always TempleCode)."""
        self.current_language_mode = "templecode"
        self.current_language = "templecode"

    # ==================================================================
    #  Turtle Graphics
    # ==================================================================

    def init_turtle_graphics(self):
        """Lazily initialise the turtle graphics system."""
        if self.turtle_graphics:
            return

        self.turtle_graphics = {
            "x": 0.0, "y": 0.0, "heading": 0.0,
            "pen_down": True,
            "pen_color": self._turtle_color_palette[0],
            "pen_size": 2,
            "visible": True,
            "canvas": None, "window": None,
            "center_x": 300, "center_y": 200,
            "lines": [],
            "sprites": {},
            "pen_style": self.default_pen_style,
            "fill_color": "",
            "hud_visible": False,
            "images": [],
        }

        if self.ide_turtle_canvas:
            self.debug_output("🐢 Using IDE integrated turtle graphics")
            self.turtle_graphics["canvas"] = self.ide_turtle_canvas
            try:
                self.ide_turtle_canvas.update_idletasks()
                cw = self.ide_turtle_canvas.winfo_width()
                ch = self.ide_turtle_canvas.winfo_height()
                if cw <= 1 or ch <= 1:
                    cw = int(self.ide_turtle_canvas.cget("width") or 600)
                    ch = int(self.ide_turtle_canvas.cget("height") or 400)
                self.turtle_graphics["center_x"] = cw // 2
                self.turtle_graphics["center_y"] = ch // 2
            except Exception:
                pass  # fallback to 300×200
            self.update_turtle_display()
            try:
                self.ide_turtle_canvas.update_idletasks()
            except Exception:
                pass
        else:
            self.turtle_graphics["canvas"] = _HeadlessCanvas()
            self.log_output("Turtle graphics initialized (headless stub mode)")

    # -- helpers shared by drawing methods --

    def _canvas_coords(self, tx=None, ty=None):
        """Convert turtle (tx, ty) to canvas pixel coordinates."""
        tg = self.turtle_graphics
        cx, cy = tg["center_x"], tg["center_y"]
        if tx is None:
            tx = tg["x"]
        if ty is None:
            ty = tg["y"]
        return cx + tx, cy - ty

    def _canvas_safe(self, canvas, func_name: str, *args, **kwargs):
        """Call a canvas method thread-safely.

        If on the main thread the call is made directly (return value available).
        From a background thread the call is queued via the output-proxy so that
        NO tkinter/Tcl calls are made outside the main thread.
        """
        fn = getattr(canvas, func_name, None)
        if fn is None:
            return None
        if threading.current_thread() is self._main_thread:
            return fn(*args, **kwargs)
        # Route through the proxy queue — drain loop executes on main thread.
        if hasattr(self.output_widget, 'call_on_main'):
            self.output_widget.call_on_main(lambda f=fn, a=args, kw=kwargs: f(*a, **kw))
        return None   # ID not available asynchronously; callers must tolerate None

    def _draw_line(self, x1, y1, x2, y2):
        """Draw a line on the canvas and track the id."""
        canvas = self.turtle_graphics.get("canvas")
        if not canvas:
            return
        lid = self._canvas_safe(
            canvas, "create_line",
            x1, y1, x2, y2,
            fill=self.turtle_graphics["pen_color"],
            width=self.turtle_graphics["pen_size"],
        )
        if lid is not None:
            self.turtle_graphics["lines"].append(lid)

    # -- movement --

    def turtle_forward(self, distance):
        """Move turtle forward by *distance* units (0° = North, clockwise)."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()

        heading_rad = math.radians(90 - self.turtle_graphics["heading"])
        old_x, old_y = self.turtle_graphics["x"], self.turtle_graphics["y"]
        new_x = old_x + distance * math.cos(heading_rad)
        new_y = old_y + distance * math.sin(heading_rad)

        self.turtle_graphics["x"] = new_x
        self.turtle_graphics["y"] = new_y
        self.variables["TURTLE_X"] = new_x
        self.variables["TURTLE_Y"] = new_y
        self.variables["TURTLE_HEADING"] = self.turtle_graphics["heading"]

        if self.turtle_graphics["pen_down"]:
            sx1, sy1 = self._canvas_coords(old_x, old_y)
            sx2, sy2 = self._canvas_coords(new_x, new_y)
            self._draw_line(sx1, sy1, sx2, sy2)
            self._canvas_safe(self.turtle_graphics["canvas"], "update_idletasks")

        # Feature 13: turtle animation delay
        if self.turtle_delay_ms > 0:
            # sleep on the background thread — keeps main thread free
            time.sleep(self.turtle_delay_ms / 1000.0)
            self._canvas_safe(self.turtle_graphics["canvas"], "update_idletasks")

        self.update_turtle_display()
        self.debug_output("Turtle moved")

    move_turtle = turtle_forward  # alias used by TempleCodeExecutor

    def turtle_turn(self, angle):
        """Turn the turtle by *angle* degrees (positive = clockwise)."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        self.turtle_graphics["heading"] = (self.turtle_graphics["heading"] + angle) % 360
        self.variables["TURTLE_HEADING"] = self.turtle_graphics["heading"]
        self.update_turtle_display()

    @property
    def turtle_angle(self):
        """Return the current turtle heading in degrees."""
        return self.turtle_graphics["heading"] if self.turtle_graphics else 0.0

    @turtle_angle.setter
    def turtle_angle(self, angle):
        """Set the turtle heading to *angle* degrees."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        self.turtle_graphics["heading"] = float(angle) % 360
        self.variables["TURTLE_HEADING"] = self.turtle_graphics["heading"]
        self.update_turtle_display()

    def turtle_home(self):
        """Reset turtle position to origin and heading to 0."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        self.turtle_graphics.update({"x": 0.0, "y": 0.0, "heading": 0.0})
        self.update_turtle_display()

    def turtle_set_color(self, color):
        """Set the turtle pen colour."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        self.turtle_graphics["pen_color"] = str(color)
        self.update_turtle_display()

    def turtle_set_pen_size(self, size):
        """Set the turtle pen width in pixels."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        try:
            self.turtle_graphics["pen_size"] = max(1, int(size))
        except Exception:
            self.turtle_graphics["pen_size"] = 1
        self.update_turtle_display()

    def turtle_setxy(self, x, y):
        """Move turtle to (x, y), drawing a line if pen is down."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()

        if self.turtle_graphics["pen_down"]:
            sx1, sy1 = self._canvas_coords()
            sx2, sy2 = self._canvas_coords(x, y)
            self._draw_line(sx1, sy1, sx2, sy2)

        self.turtle_graphics["x"] = x
        self.turtle_graphics["y"] = y
        self.update_turtle_display()

    def update_turtle_display(self):
        """Redraw the turtle indicator triangle on the canvas."""
        tg = self.turtle_graphics
        if not tg or not tg.get("canvas"):
            return

        canvas = tg["canvas"]
        self._canvas_safe(canvas, "delete", "turtle")

        if not tg["visible"]:
            return

        x, y = self._canvas_coords()
        angle = math.radians(90 - tg["heading"])
        size = 10

        tip_x = x + size * math.cos(angle)
        tip_y = y - size * math.sin(angle)
        la = angle + math.radians(140)
        lx, ly = x + size * 0.6 * math.cos(la), y - size * 0.6 * math.sin(la)
        ra = angle - math.radians(140)
        rx, ry = x + size * 0.6 * math.cos(ra), y - size * 0.6 * math.sin(ra)

        self._canvas_safe(
            canvas, "create_polygon",
            tip_x, tip_y, lx, ly, rx, ry,
            fill="green", outline="darkgreen", width=2, tags="turtle",
        )

    def clear_turtle_screen(self):
        """Erase all turtle drawings from the canvas."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        canvas = self.turtle_graphics.get("canvas")
        if canvas:
            for lid in self.turtle_graphics["lines"]:
                self._canvas_safe(canvas, "delete", lid)
            self.turtle_graphics["lines"].clear()
            for sd in self.turtle_graphics.get("sprites", {}).values():
                if sd.get("canvas_id"):
                    self._canvas_safe(canvas, "delete", sd["canvas_id"])
                    sd["canvas_id"] = None
                    sd["visible"] = False
            self.update_turtle_display()

    def turtle_circle(self, radius):
        """Draw a circle with the given radius at the turtle position."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        canvas = self.turtle_graphics.get("canvas")
        if not canvas or not self.turtle_graphics["pen_down"]:
            return
        cx, cy = self._canvas_coords()
        cid = self._canvas_safe(
            canvas, "create_oval",
            cx - radius, cy - radius, cx + radius, cy + radius,
            outline=self.turtle_graphics["pen_color"],
            width=self.turtle_graphics["pen_size"],
        )
        if cid is not None:
            self.turtle_graphics["lines"].append(cid)

    def turtle_dot(self, size):
        """Draw a filled dot of the given size at the turtle position."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        canvas = self.turtle_graphics.get("canvas")
        if not canvas:
            return
        cx, cy = self._canvas_coords()
        r = max(1, size // 2)
        cid = self._canvas_safe(
            canvas, "create_oval",
            cx - r, cy - r, cx + r, cy + r,
            fill=self.turtle_graphics["pen_color"],
            outline=self.turtle_graphics["pen_color"],
        )
        if cid is not None:
            self.turtle_graphics["lines"].append(cid)

    def turtle_rect(self, width, height, filled=False):
        """Draw a rectangle of given dimensions at the turtle position."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        canvas = self.turtle_graphics.get("canvas")
        if not canvas:
            return
        x, y = self._canvas_coords()
        rid = self._canvas_safe(
            canvas, "create_rectangle",
            x, y, x + width, y + height,
            outline=self.turtle_graphics["pen_color"],
            fill=self.turtle_graphics.get("fill_color", "") if filled else "",
            width=self.turtle_graphics["pen_size"],
        )
        if rid is not None:
            self.turtle_graphics["lines"].append(rid)

    def turtle_text(self, text, size=12):
        """Draw text at the turtle position."""
        if not self.turtle_graphics:
            self.init_turtle_graphics()
        canvas = self.turtle_graphics.get("canvas")
        if not canvas:
            return
        x, y = self._canvas_coords()
        tid = self._canvas_safe(
            canvas, "create_text",
            x, y, text=text, font=("Arial", int(size)),
            fill=self.turtle_graphics["pen_color"], anchor="nw",
        )
        if tid is not None:
            self.turtle_graphics["lines"].append(tid)

    # ==================================================================
    #  State Management
    # ==================================================================

    def reset(self):
        """Reset all interpreter state."""
        self.variables = {}
        self.labels = {}
        self.program_lines = []
        self.current_line = 0
        self.stack = []
        self.for_stack = []
        self.do_stack = []
        self.while_stack = []
        self.select_stack = []
        self.match_flag = False
        self._last_match_set = False
        self.running = False
        self.error_history = []
        self.logo_procedures = {}
        self._data_values = []
        self._data_pos = 0
        self._program_start_time = 0.0

        # Modern extensions
        self.sub_definitions = {}
        self.function_definitions = {}
        self.call_stack = []
        self.return_value = None
        self.lists = {}
        self.dicts = {}
        # Close any open file handles
        for fh in self.file_handles.values():
            try:
                fh.close()
            except Exception:
                pass
        self.file_handles = {}
        self.try_stack = []
        self.last_error = ""
        self.constants = set()
        self.imported_modules = set()

    # ==================================================================
    #  Output Helpers
    # ==================================================================

    def log_output(self, text, end="\n"):
        """Write text to the output widget or stdout.

        The output_widget is an ``_OutputProxy`` when running inside the IDE,
        so all calls here simply enqueue data — no tkinter state is touched
        from the background thread.
        """
        if self.output_widget:
            try:
                self.output_widget.insert(tk.END, str(text) + end)
                self.output_widget.see(tk.END)
            except Exception:
                print(text, end=end)
        else:
            print(text, end=end)

    def log_error(self, error_msg, line_num=None):
        """Log an error message and add it to the error history."""
        fmt = f"❌ ERROR (Line {line_num}): {error_msg}" if line_num else f"❌ ERROR: {error_msg}"
        self.error_history.append({
            'message': error_msg, 'line': line_num, 'timestamp': self.get_current_time()
        })
        self.log_output(fmt)

    def debug_output(self, text):
        """Write text to output only when debug mode is active."""
        if self.debug_mode:
            self.log_output(text)

    # ==================================================================
    #  Parsing Helpers
    # ==================================================================

    def parse_line(self, line):
        """Split an optional leading line-number from the command text."""
        line = line.strip()
        m = re.match(r"^(\d+)\s+(.*)", line)
        if m:
            return int(m.group(1)), m.group(2).strip()
        return None, line

    def resolve_variables(self, text):
        """Resolve *VAR*, %SYSVAR%, and bare-variable references in text."""
        if not isinstance(text, str):
            return text

        def _sys(m):
            n = m.group(1).lower()
            ex = getattr(self, "templecode_executor", None)
            return str(getattr(ex, "system_vars", {}).get(n, "")) if ex else ""

        def _star(m):
            return str(self.variables.get(m.group(1).upper(), ""))

        resolved = re.sub(r"%([A-Za-z_]\w*)%", _sys, text)
        resolved = re.sub(r"\*([A-Za-z_]\w*)\*", _star, resolved)

        if "*" not in resolved and "%" not in resolved and resolved == text:
            if re.match(r"^[A-Za-z_]\w*$", text.strip()):
                var = text.strip().upper()
                if var in self.variables:
                    return str(self.variables[var])
        return resolved

    def parse_command_args(self, argument):
        """Parse command arguments honouring quoted strings."""
        args, current, in_q = [], "", False
        for i, ch in enumerate(argument):
            if ch == '"' and (i == 0 or argument[i - 1] != "\\"):
                in_q = not in_q
                current += ch
            elif ch == " " and not in_q:
                if current.strip():
                    args.append(current.strip())
                    current = ""
            else:
                current += ch
        if current.strip():
            args.append(current.strip())
        return args

    # ==================================================================
    #  Expression Evaluation
    # ==================================================================

    def evaluate_expression(self, expr):  # noqa: C901
        """Safely evaluate a mathematical / string expression with variables."""
        # Replace *VAR* interpolation
        for var_name, var_value in self.variables.items():
            val_repr = str(var_value) if isinstance(var_value, (int, float)) else f'"{var_value}"'
            expr = expr.replace(f"*{var_name}*", val_repr)

        # Built-in functions available inside eval()
        allowed = {
            "abs": abs, "round": round, "int": int, "float": float,
            "max": max, "min": min, "len": len, "str": str,
            "RND": lambda *a: random.random() if not a else random.random() * a[0],
            "INT": int, "ABS": abs,
            "VAL": lambda x: float(x) if "." in str(x) else int(x),
            "UPPER": lambda x: str(x).upper(),
            "LOWER": lambda x: str(x).lower(),
            "MID": lambda s, st, ln: str(s)[int(st) - 1:int(st) - 1 + int(ln)],
            "STR$": str, "CHR$": lambda x: chr(int(x)),
            "ASC": lambda x: ord(str(x)[0]) if str(x) else 0,
            "LEN": lambda x: len(str(x)),
            "LEFT$": lambda s, n: str(s)[:int(n)],
            "RIGHT$": lambda s, n: str(s)[-int(n):] if int(n) > 0 else "",
            "CEIL": lambda x: math.ceil(float(x)),
            "FIX": lambda x: int(float(x)) if float(x) >= 0 else -int(-float(x)),
            "EXP2": lambda x: 2 ** float(x),
            "EXP10": lambda x: 10 ** float(x),
            "LOG2": lambda x: math.log2(float(x)) if float(x) > 0 else 0,
            "LOG10": lambda x: math.log10(float(x)) if float(x) > 0 else 0,
            "CHR": lambda x: chr(int(x)),
            "UCASE": lambda x: str(x).upper(),
            "LCASE": lambda x: str(x).lower(),
            "BIN": lambda x: bin(int(x))[2:],
            "OCT": lambda x: oct(int(x))[2:],
            "HEX": lambda x: hex(int(x))[2:],
            "TIMER": lambda: round(time.time() - self._program_start_time, 3),
            "TYPE": lambda x: "STRING" if isinstance(x, str) else ("NUMBER" if isinstance(x, (int, float)) else "UNKNOWN"),
        }

        # Replace array element accesses (but not function calls)
        def _arr(m):
            name, idxs = m.group(1), m.group(2)
            if name in allowed:
                return m.group(0)
            if name in self.variables and isinstance(self.variables[name], dict):
                try:
                    cur = self.variables[name]
                    for idx in idxs.split(","):
                        cur = cur[int(self.evaluate_expression(idx.strip()))]
                    return str(cur)
                except Exception:
                    return "0"
            return "0"

        expr = re.sub(r"([A-Za-z_]\w*)\(([^)]+)\)", _arr, expr)

        # Replace bare variable names (longest first to prevent prefix collisions)
        for var_name, var_value in sorted(
            self.variables.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if isinstance(var_value, dict):
                continue
            val_repr = str(var_value) if isinstance(var_value, (int, float)) else f'"{var_value}"'
            try:
                if "$" in var_name:
                    expr = re.sub(rf"\b{re.escape(var_name)}(?=\s|$|[^A-Za-z0-9_$])", val_repr, expr)
                else:
                    expr = re.sub(rf"\b{re.escape(var_name)}\b", val_repr, expr)
            except re.error:
                expr = expr.replace(var_name, val_repr)

        safe_dict = {"__builtins__": {}}
        safe_dict.update(allowed)

        # Handle RND variants
        rnd_val = str(random.random())
        expr = expr.replace("RND(1)", rnd_val)
        expr = expr.replace("RND()", rnd_val)
        expr = re.sub(r'\bRND\b(?!\s*\()', rnd_val, expr)

        # Handle TIMER, DATE$, TIME$ pseudo-variables
        import datetime as _dt
        expr = re.sub(r'\bTIMER\b(?!\s*\()', str(round(time.time() - self._program_start_time, 3)), expr)
        expr = re.sub(r'\bDATE\$', f'"{_dt.date.today().isoformat()}"', expr)
        expr = re.sub(r'\bTIME\$', f'"{_dt.datetime.now().strftime("%H:%M:%S")}"', expr)

        # BASIC operator aliases
        expr = re.sub(r"\bMOD\b", "%", expr, flags=re.IGNORECASE)
        expr = re.sub(r"<>", "!=", expr)

        # Inline $ functions: STR$(), CHR$(), LEFT$(), RIGHT$()
        def _str_fn(m):
            try:
                return f'"{self.evaluate_expression(m.group(1))}"'
            except Exception:
                return f'"{m.group(1)}"'

        def _chr_fn(m):
            try:
                return f'"{chr(int(self.evaluate_expression(m.group(1))))}"'
            except Exception:
                return '""'

        def _lr_fn(m, right=False):
            args = m.group(1).split(",")
            if len(args) == 2:
                try:
                    s = str(self.evaluate_expression(args[0].strip()))
                    n = int(self.evaluate_expression(args[1].strip()))
                    return f'"{s[-n:] if n > 0 else ""}"' if right else f'"{s[:n]}"'
                except Exception:
                    pass
            return '""'

        expr = re.sub(r"STR\$\(([^)]+)\)", _str_fn, expr)
        expr = re.sub(r"CHR\$\(([^)]+)\)", _chr_fn, expr)
        expr = re.sub(r"LEFT\$\(([^)]+)\)", lambda m: _lr_fn(m, False), expr)
        expr = re.sub(r"RIGHT\$\(([^)]+)\)", lambda m: _lr_fn(m, True), expr)

        try:
            return eval(expr, safe_dict)  # noqa: S307
        except ZeroDivisionError:
            self.log_error("Division by zero in expression", None)
            return "ERROR: Division by zero"
        except TypeError as te:
            if "can only concatenate str" in str(te):
                try:
                    parts = [p.strip() for p in re.split(r"(?<!\\)\+", expr)]
                    if len(parts) > 1:
                        resolved = []
                        for p in parts:
                            try:
                                resolved.append(str(eval(p, safe_dict)))  # noqa: S307
                            except Exception:
                                resolved.append(p.strip("\"'"))
                        return "".join(resolved)
                except Exception:
                    pass
            self.log_error(f"Type error in expression: {te}", None)
            return 0
        except NameError as ne:
            self.log_error(f"Undefined variable or function: {ne}", None)
            return 0
        except SyntaxError as se:
            self.log_error(f"Syntax error in expression: {se}", None)
            return 0
        except Exception:
            stripped = expr.strip()
            if stripped.startswith('"') and stripped.endswith('"'):
                return stripped[1:-1]
            if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", stripped):
                return float(stripped) if "." in stripped else int(stripped)
            if re.fullmatch(r"[A-Za-z_]\w*", stripped):
                return stripped
            return stripped

    def interpolate_text(self, text: str) -> str:
        """Interpolate *VAR* and *expr* tokens inside a string."""
        for var_name, var_value in self.variables.items():
            text = text.replace(f"*{var_name}*", str(var_value))
        try:
            for tok in re.findall(r"\*(.+?)\*", text):
                if tok in self.variables:
                    continue
                ts = tok.strip()
                if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", ts):
                    text = text.replace(f"*{tok}*", ts)
                    continue
                if re.search(r"[\(\)\+\-\*/%<>=]", tok):
                    try:
                        text = text.replace(f"*{tok}*", str(self.evaluate_expression(tok)))
                    except Exception:
                        pass
        except Exception:
            pass
        return text

    # ==================================================================
    #  User Input
    # ==================================================================

    def get_input(self, prompt=""):
        """Shorthand for get_user_input."""
        return self.get_user_input(prompt)

    def get_user_input(self, prompt=""):
        """Prompt the user for input via buffer, GUI, or terminal."""
        # 1. Check pre-filled buffer (from tests or queued input)
        if self.input_buffer:
            value = self.input_buffer.pop(0)
            self.log_output(f">> {value}")
            return value

        # 2. GUI mode — wait for the IDE input bar
        if self.output_widget and self.ide_turtle_canvas:
            if prompt:
                self.log_output(prompt)
            self.log_output("⌨️  Waiting for input (type below and press Submit)...")

            # Use a threading.Event so the interpreter thread blocks
            # while the main GUI thread remains fully responsive.
            event = threading.Event()
            self._input_result = ""
            self._input_event = event    # _submit_input sets this
            self._input_wait_var = event  # truthy sentinel for legacy checks

            # Setting this flag causes the GUI drain loop (_drain_output_queue)
            # to call _start_key_capture(), which:
            #   1. Turns the input entry yellow so the user sees where to type
            #   2. Calls focus_force() to grab keyboard focus (works on Wayland)
            #   3. Binds <KeyPress> on the root window so ALL keystrokes reach
            #      the entry, regardless of which widget Tk thinks has focus
            self._waiting_for_input = True

            # Block THIS (interpreter) thread until the GUI calls _submit_input().
            # The GUI drain loop watches _waiting_for_input and enables root-level
            # key capture so the user can type regardless of OS focus state.
            event.wait()

            # Done waiting — GUI drain loop clears key capture automatically.
            self._waiting_for_input = False

            value = self._input_result
            self._input_event = None
            self._input_wait_var = None
            self.log_output(f">> {value}")
            return value

        # 3. Fallback: GUI with no canvas (shouldn't happen) → dialog
        if self.output_widget:
            result = simpledialog.askstring("Input", prompt or "Enter value")
            if result is not None:
                self.log_output(f">> {result}")
                return result
            return ""

        # 4. Terminal mode
        return input(prompt)

    # ==================================================================
    #  Line & Program Execution
    # ==================================================================

    def execute_line(self, line):
        """Execute a single program line via the TempleCode executor."""
        line_num = None
        try:
            line_num, command = self.parse_line(line)
            if not command:
                return "continue"
            stripped = command.lstrip()
            if stripped.startswith(";") or stripped.startswith("#"):
                return "continue"
            self.debug_output(f"Executing: {command}")
            return self.templecode_executor.execute_command(command)
        except Exception as e:
            # If inside a TRY block, jump to CATCH instead of crashing
            if self.try_stack:
                frame = self.try_stack[-1]
                catch_line = frame.get("catch_line")
                if catch_line is not None:
                    self.last_error = str(e)
                    self.variables["ERROR$"] = str(e)
                    # Extract variable from CATCH line
                    _, catch_cmd = self.program_lines[catch_line]
                    cm = re.match(r'CATCH\s+(\w+)', catch_cmd.strip(), re.IGNORECASE)
                    if cm:
                        self.variables[cm.group(1).upper()] = str(e)
                    # Jump to the line AFTER "CATCH" so the body executes
                    self.current_line = catch_line + 1
                    return "jump"
            self.log_error(f"Execution error in line {line_num or self.current_line}: {e}", line_num)
            return "error"

    def load_program(self, program_text):
        """Load and parse a program, collecting labels."""
        self.labels = {}
        self.program_lines = []
        self.current_line = 0
        self.stack = []
        self.for_stack = []
        self.do_stack = []
        self.while_stack = []
        self.select_stack = []
        self.match_flag = False
        self._last_match_set = False
        self.running = False
        self.error_history = []
        # NOTE: logo_procedures is NOT reset here — the preprocessor
        # in run_program() populates it before load_program() is called.

        for i, raw_line in enumerate(program_text.strip().split("\n")):
            ln, cmd = self.parse_line(raw_line)
            self.program_lines.append((ln, cmd))

            # Collect label definitions
            if cmd.startswith("L:"):
                self.labels[cmd[2:].strip()] = i
            elif cmd.startswith("*"):
                label = cmd[1:].strip()
                if label:
                    self.labels[label] = i
            elif re.match(r'^[A-Za-z_]\w*:$', cmd):
                # Exclude single-letter PILOT commands (A: T: E: etc.)
                if len(cmd) > 2:
                    self.labels[cmd[:-1].strip()] = i

            # Pre-collect DATA statements
            dm = re.match(r'^DATA\s+(.*)', cmd, re.IGNORECASE)
            if dm:
                for val in dm.group(1).split(","):
                    val = val.strip().strip('"')
                    try:
                        val = float(val)
                        if val == int(val):
                            val = int(val)
                    except ValueError:
                        pass
                    self._data_values.append(val)

        return True

    def run_program(self, program_text, language=None):  # noqa: C901
        """Execute a TempleCode program from source text."""
        self.current_language = "templecode"
        self.current_language_mode = "templecode"

        # Reset procedures before preprocessor collects new ones
        self.logo_procedures = {}
        program_text = self._preprocess_logo_program(program_text)

        if not self.load_program(program_text):
            self.log_output("Error loading program")
            return False

        self.running = True
        self.current_line = 0
        self._program_start_time = time.time()
        max_iterations = 100_000
        iterations = 0

        # Reset profiler if attached
        if self.profiler and self.profiler.enabled:
            self.profiler.reset()

        try:
            while (self.current_line < len(self.program_lines)
                   and self.running
                   and iterations < max_iterations):
                iterations += 1

                if self.debug_mode and self.current_line in self.breakpoints:
                    self.log_output(f"🔍 DEBUG: Breakpoint hit at line {self.current_line + 1}")
                    # Show watch expressions at breakpoint
                    if self.watch_manager and self.watch_manager.expressions:
                        self.log_output("👁  Watches:")
                        self.log_output(self.watch_manager.format_report(self))
                    break

                _ln, command = self.program_lines[self.current_line]
                if not command.strip():
                    self.current_line += 1
                    continue

                if self.debug_mode:
                    self.debug_output(
                        f"Executing line {self.current_line + 1}: {command[:50]}"
                    )

                # Profiler: begin line
                if self.profiler and self.profiler.enabled:
                    self.profiler.begin_line(self.current_line + 1, command.strip())

                try:
                    result = self.execute_line(command)
                except Exception as e:
                    # Profiler: end line even on error
                    if self.profiler and self.profiler.enabled:
                        self.profiler.end_line(self.current_line + 1)
                    self.log_error(
                        f"Unexpected error at line {self.current_line + 1}: {e}",
                        self.current_line + 1,
                    )
                    if not self.debug_mode:
                        break
                    self.current_line += 1
                    continue

                # Profiler: end line
                if self.profiler and self.profiler.enabled:
                    self.profiler.end_line(self.current_line + 1)

                if result == "end":
                    break
                if result == "return":
                    break  # SUB/FUNCTION return
                if result == "jump":
                    continue
                if isinstance(result, str) and result.startswith("jump:"):
                    try:
                        target = int(result.split(":")[1])
                        if 0 <= target < len(self.program_lines):
                            self.current_line = target
                            continue
                        self.log_error(f"Invalid jump target: {target}", self.current_line + 1)
                        break
                    except (ValueError, IndexError) as e:
                        self.log_error(f"Jump command error: {e}", self.current_line + 1)
                        break
                elif result == "error":
                    if not self.debug_mode:
                        self.log_output("🛑 Program terminated due to error")
                        break
                    self.log_output("⚠️  Continuing after error (debug mode)")

                self.current_line += 1

                # Feature 12: optional per-line delay for slow execution
                if self.exec_delay_ms > 0:
                    time.sleep(self.exec_delay_ms / 1000.0)
                    if self.ide_turtle_canvas:
                        self._canvas_safe(self.ide_turtle_canvas, "update_idletasks")

            if iterations >= max_iterations:
                self.log_error(
                    "Maximum iterations reached (possible infinite loop)",
                    self.current_line + 1,
                )

        except Exception as e:
            self.log_error(
                f"Critical runtime error at line {self.current_line + 1}: {e}",
                self.current_line + 1,
            )
        finally:
            self.running = False
            # Show profiler report if active
            if self.profiler and self.profiler.enabled and self.profiler.get_stats():
                self.log_output("\n" + self.profiler.format_report())
            if self.error_history:
                self.log_output(f"📊 Execution completed with {len(self.error_history)} error(s)")
            else:
                self.log_output("✅ Program execution completed successfully")

        return True

    # ==================================================================
    #  Debugger Helpers
    # ==================================================================

    def step(self):
        """Single-step: execute one line and pause."""
        if self.current_line >= len(self.program_lines):
            self.log_output("Program finished – nothing to step.")
            return False
        _, command = self.program_lines[self.current_line]
        if command.strip():
            self.log_output(f"STEP [{self.current_line + 1}]: {command}")
            result = self.execute_line(command)
            if result == "end":
                self.running = False
                return False
            if result == "jump":
                return True
        self.current_line += 1
        return True

    def get_current_time(self):
        """Return the current wall-clock time."""
        return time.time()

    def stop_program(self):
        """Stop the currently running program."""
        self.running = False

    def set_debug_mode(self, enabled):
        """Enable or disable debug mode."""
        self.debug_mode = enabled

    def toggle_breakpoint(self, line_number):
        """Toggle a breakpoint on the given line number."""
        self.breakpoints.symmetric_difference_update({line_number})

    # ==================================================================
    #  Logo Pre-processor (TO/END, multi-line REPEAT)
    # ==================================================================

    def _preprocess_logo_program(self, program_text):
        """Collect TO/END procedure definitions and flatten multi-line REPEAT blocks."""
        lines = program_text.split("\n")
        processed = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.upper().startswith("TO "):
                parts = line[3:].strip().split()
                if not parts:
                    i += 1
                    continue
                proc_name = parts[0].lower()
                proc_params = [p.lstrip(":").upper() for p in parts[1:] if p.startswith(":")]
                body = []
                i += 1
                while i < len(lines):
                    bl = lines[i].strip()
                    if bl.upper() == "END":
                        break
                    if bl and not bl.startswith(";"):
                        if "[" in bl and "]" not in bl:
                            block = [bl]
                            depth = bl.count("[") - bl.count("]")
                            i += 1
                            while i < len(lines) and depth > 0:
                                nl = lines[i].strip()
                                if nl and not nl.startswith(";"):
                                    block.append(nl)
                                    depth += nl.count("[") - nl.count("]")
                                i += 1
                            body.append("\n".join(block))
                            continue
                        body.append(bl)
                    i += 1
                self.logo_procedures[proc_name] = (proc_params, body)
                self.log_output(f"📝 Defined procedure {proc_name}{proc_params}")
                i += 1
                continue

            elif line.upper().startswith("REPEAT ") and "[" in line and "]" not in line:
                block = line
                depth = line.count("[") - line.count("]")
                i += 1
                while i < len(lines) and depth > 0:
                    nl = lines[i].strip()
                    if nl and not nl.startswith(";"):
                        block += " " + nl
                        depth += nl.count("[") - nl.count("]")
                    i += 1
                processed.append(block)
            else:
                processed.append(line)
                i += 1

        return "\n".join(processed)


# ---------------------------------------------------------------------------
#  Demo program for standalone testing
# ---------------------------------------------------------------------------

def create_demo_program():
    """Return a demo TempleCode program for standalone testing."""
    return """L:START
T:Welcome to TempleCode Interpreter Demo!
A:NAME
T:Hello *NAME*! Let's do some math.
U:X=10
U:Y=20
T:X = *X*, Y = *Y*
U:SUM=*X*+*Y*
T:Sum of X and Y is *SUM*
T:
T:Let's count to 5:
U:COUNT=1
L:LOOP
Y:*COUNT* > 5
J:END_LOOP
T:Count: *COUNT*
U:COUNT=*COUNT*+1
J:LOOP
L:END_LOOP
T:
T:Program completed. Thanks for using TempleCode!
END"""


if __name__ == "__main__":
    interpreter = TempleCodeInterpreter()
    print("Running TempleCode interpreter demo...")
    interpreter.run_program(create_demo_program())
