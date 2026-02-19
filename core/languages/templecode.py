#!/usr/bin/env python3
"""
TempleCode Language Executor
=============================

TempleCode is a unified educational programming language that blends the best of
BASIC, PILOT, and Logo into a single cohesive language, as if designed in the
early 1990s for teaching programming fundamentals.

Language Heritage:
  From BASIC (1964): Line numbers, PRINT, LET, IF/THEN/ELSE, FOR/NEXT, GOTO,
                     GOSUB/RETURN, DIM, INPUT, REM, END, math & string functions
  From PILOT (1968): T: (type text), A: (accept input), M: (match), Y:/N:
                     (conditional on match), J: (jump to label), C: (call sub)
  From Logo  (1967): FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN, REPEAT,
                     SETCOLOR, CIRCLE, HOME, CLEARSCREEN, TO/END procedures

Design Philosophy:
  TempleCode programs can freely mix all three styles. A program can use
  line-numbered BASIC statements, PILOT colon-commands, and Logo turtle
  graphics interchangeably. The interpreter auto-detects which sub-system
  handles each line, giving learners a smooth multi-paradigm experience.

File Extension: .tc
"""

import re
import math
import random
import time


class TempleCodeExecutor:
    """
    Unified executor for the TempleCode language.

    Combines BASIC structured programming, PILOT interactive text commands,
    and Logo turtle graphics into one language.
    """

    def __init__(self, interpreter):
        self.interpreter = interpreter

        # PILOT state
        self.arrays = {}
        self.return_stack = []
        self.system_vars = {
            "answer": "",
            "matched": "",
            "left": "",
            "right": "",
            "status": 0,
        }

        # Logo state – procedures defined with TO ... END
        self.logo_procedures = {}

    # ------------------------------------------------------------------
    #  Top-level dispatch
    # ------------------------------------------------------------------

    def execute_command(self, command):
        """Execute a single TempleCode command, routing to the correct sub-system."""
        command = command.strip()
        if not command:
            return "continue"

        # ------ Comments ------
        if command.startswith("REM") or command.startswith("'") or command.startswith("*"):
            return "continue"
        if command.startswith(";"):
            return "continue"

        # ------ PILOT colon-commands (single letter + colon) ------
        # Must be checked before label definitions so A: E: T: etc. work
        if len(command) > 1 and command[1] == ":" and command[0].isalpha():
            return self._dispatch_pilot(command)

        # ------ Colon-suffixed label definitions (e.g. MyLabel:) – skip at runtime ------
        if re.match(r'^[A-Za-z_]\w*:$', command):
            return "continue"

        # ------ Logo procedure definition (TO ... END) ------
        upper = command.upper()
        first_word = command.split()[0].upper() if command.split() else ""

        if first_word == "TO":
            return self._handle_logo_define(command)

        # ------ Logo turtle / drawing commands ------
        logo_keywords = {
            "FORWARD", "FD", "BACK", "BK", "BACKWARD",
            "LEFT", "LT", "RIGHT", "RT",
            "PENUP", "PU", "PENDOWN", "PD",
            "HOME", "CLEARSCREEN", "CS", "CLEAN",
            "SHOWTURTLE", "ST", "HIDETURTLE", "HT",
            "SETXY", "SETPOS", "SETX", "SETY",
            "SETCOLOR", "SETCOLOUR", "SETPENCOLOR", "SETPC",
            "SETPENSIZE", "SETWIDTH",
            "SETFILLCOLOR", "SETFC",
            "SETBACKGROUND", "SETBG",
            "SETSCREENCOLOR", "SETSCREENCOLOUR",
            "SETHEADING", "SETH",
            "CIRCLE", "ARC", "DOT",
            "SQUARE", "TRIANGLE", "POLYGON", "STAR",
            "RECT", "RECTANGLE", "FILL", "FILLED",
            "TOWARDS",
            "REPEAT",
            "MAKE",
            "HEADING", "POS", "POSITION", "XCOR", "YCOR",
            "TRACE", "NOTRACE",
            "LABEL", "STAMP",
            "PENCOLOR?", "PENSIZE?",
            "WRAP", "WINDOW", "FENCE",
        }

        if first_word in logo_keywords:
            return self._dispatch_logo(command, first_word)

        # ------ Check if it's a user-defined Logo procedure call ------
        if first_word.lower() in self.logo_procedures:
            return self._call_logo_procedure(first_word.lower(),
                                             self._logo_proc_args(command, first_word))
        # Also check interpreter-level logo_procedures (set during TO..END collection)
        if hasattr(self.interpreter, 'logo_procedures') and first_word.lower() in self.interpreter.logo_procedures:
            return self._call_logo_procedure(first_word.lower(),
                                             self._logo_proc_args(command, first_word))

        # ------ BASIC statements ------
        return self._dispatch_basic(command, first_word, upper)

    # ==================================================================
    #  PILOT sub-system
    # ==================================================================

    def _dispatch_pilot(self, command):
        """Route PILOT colon-commands."""
        prefix = command[0].upper()
        arg = command[2:].strip() if len(command) > 2 else ""

        handlers = {
            "T": self._pilot_type,
            "A": self._pilot_accept,
            "Y": self._pilot_yes,
            "N": self._pilot_no,
            "M": self._pilot_match,
            "J": self._pilot_jump,
            "C": self._pilot_call,
            "E": self._pilot_end,
            "R": self._pilot_remark,
            "U": self._pilot_use,
            "L": self._pilot_label,
            "G": self._pilot_graphics,
            "S": self._pilot_string,
            "D": self._pilot_dim,
            "P": self._pilot_pause,
            "X": self._pilot_execute,
        }

        handler = handlers.get(prefix)
        if handler:
            return handler(arg)
        else:
            self.interpreter.log_output(f"Unknown PILOT command: {prefix}:")
            return "continue"

    def _pilot_type(self, arg):
        """T: – Type / print text with variable interpolation."""
        text = self._interpolate_vars(arg)
        self.interpreter.log_output(text)
        return "continue"

    def _pilot_accept(self, arg):
        """A: – Accept user input, store in variable or $INPUT."""
        prompt = self._interpolate_vars(arg) if arg else ""
        value = self.interpreter.get_input(prompt)

        # Try numeric conversion (matches BASIC INPUT behaviour)
        try:
            value = float(value)
            if value == int(value):
                value = int(value)
        except (ValueError, TypeError):
            pass

        self.system_vars["answer"] = value
        self.interpreter.variables["INPUT"] = value
        self.interpreter.variables["ANSWER"] = value

        # If arg names a variable (A:NAME), store there too
        if arg and not any(c in arg for c in " $*!?"):
            self.interpreter.variables[arg.upper()] = value
        return "continue"

    def _pilot_yes(self, arg):
        """Y: – Execute only if last match succeeded."""
        if self.interpreter.match_flag:
            return self.execute_command(arg)
        return "continue"

    def _pilot_no(self, arg):
        """N: – Execute only if last match failed."""
        if not self.interpreter.match_flag:
            return self.execute_command(arg)
        return "continue"

    def _pilot_match(self, arg):
        """M: – Match answer against pattern(s), set match flag."""
        answer = self.system_vars.get("answer", "").lower()
        patterns = [p.strip().lower() for p in arg.split(",")]
        matched = any(p in answer for p in patterns if p)
        self.interpreter.match_flag = matched
        self.interpreter._last_match_set = True  # pylint: disable=protected-access
        if matched:
            self.system_vars["matched"] = arg
            self.system_vars["status"] = 1
        else:
            self.system_vars["status"] = 0
        return "continue"

    def _pilot_jump(self, arg):
        """J: – Jump to label."""
        label = arg.strip().lstrip("*")
        if label in self.interpreter.labels:
            self.interpreter.current_line = self.interpreter.labels[label]
            return "jump"
        else:
            self.interpreter.log_output(f"Label not found: {label}")
        return "continue"

    def _pilot_call(self, arg):
        """C: – Compute (assign variable).  C:X=5+3  or call subroutine C:*label"""
        arg = arg.strip()
        # If starts with * it's a subroutine call
        if arg.startswith("*"):
            label = arg.lstrip("*")
            if label in self.interpreter.labels:
                self.return_stack.append(self.interpreter.current_line)
                self.interpreter.current_line = self.interpreter.labels[label]
                return "jump"
            else:
                self.interpreter.log_output(f"Subroutine not found: {label}")
            return "continue"
        # Otherwise it's a Compute: C:X=5+3
        if "=" in arg:
            name, _, expr = arg.partition("=")
            name = name.strip().upper()
            value = self.interpreter.evaluate_expression(expr.strip())
            self.interpreter.variables[name] = value
        return "continue"

    def _pilot_end(self, _arg):
        """E: – End subroutine or program."""
        if self.return_stack:
            self.interpreter.current_line = self.return_stack.pop()
            return "continue"
        self.interpreter.running = False
        return "end"

    def _pilot_remark(self, _arg):
        """R: – Remark / comment."""
        return "continue"

    def _pilot_use(self, arg):
        """U: – Use / set variable.  U:X=5"""
        if "=" in arg:
            name, _, expr = arg.partition("=")
            name = name.strip().upper()
            value = self.interpreter.evaluate_expression(expr.strip())
            self.interpreter.variables[name] = value
        return "continue"

    def _pilot_label(self, arg):
        """L: – Label definition (handled at load time, noop at runtime)."""
        return "continue"

    def _pilot_graphics(self, arg):
        """G: – Inline turtle graphics shorthand.
        G:FORWARD 100   or   G:FD 100  etc."""
        return self._dispatch_logo(arg.strip(), arg.strip().split()[0].upper() if arg.strip() else "")

    def _pilot_string(self, arg):
        """S: – String operations.  S:UPPER X  /  S:LEN X  etc."""
        parts = arg.split()
        if len(parts) < 2:
            return "continue"
        op = parts[0].upper()
        var_name = parts[1].upper()
        val = str(self.interpreter.variables.get(var_name, ""))

        if op == "UPPER":
            self.interpreter.variables[var_name] = val.upper()
        elif op == "LOWER":
            self.interpreter.variables[var_name] = val.lower()
        elif op == "LEN":
            self.interpreter.variables[var_name + "_LEN"] = len(val)
        elif op == "REVERSE":
            self.interpreter.variables[var_name] = val[::-1]
        elif op == "TRIM":
            self.interpreter.variables[var_name] = val.strip()
        return "continue"

    def _pilot_dim(self, arg):
        """D: – Dimension an array.  D:ARR(10)"""
        m = re.match(r'(\w+)\((\d+)\)', arg)
        if m:
            name, size = m.group(1).upper(), int(m.group(2))
            self.arrays[name] = [0] * size
        return "continue"

    def _pilot_pause(self, arg):
        """P: – Pause for N milliseconds."""
        try:
            ms = int(self.interpreter.evaluate_expression(arg))
            time.sleep(ms / 1000.0)
        except Exception:
            time.sleep(1)
        return "continue"

    def _pilot_execute(self, arg):
        """X: – Execute a BASIC or Logo command inline."""
        return self.execute_command(arg)

    # ------------------------------------------------------------------
    #  Variable interpolation (PILOT-style $VAR and *VAR*)
    # ------------------------------------------------------------------

    def _interpolate_vars(self, text):
        """Replace $VAR and *VAR* references with variable values."""
        def replace_dollar(m):
            name = m.group(1).upper()
            return str(self.interpreter.variables.get(name, self.system_vars.get(name.lower(), "")))

        text = re.sub(r'\$(\w+)', replace_dollar, text)

        def replace_star(m):
            name = m.group(1).upper()
            return str(self.interpreter.variables.get(name, ""))

        text = re.sub(r'\*(\w+)\*', replace_star, text)
        return text

    # ==================================================================
    #  Logo sub-system
    # ==================================================================

    def _dispatch_logo(self, command, first_word):  # noqa: C901
        """Route Logo turtle-graphics commands."""
        parts = command.split()
        cmd = first_word.upper()

        # Movement
        if cmd in ("FORWARD", "FD"):
            return self._logo_forward(parts)
        elif cmd in ("BACK", "BK", "BACKWARD"):
            return self._logo_back(parts)
        elif cmd in ("LEFT", "LT"):
            return self._logo_left(parts)
        elif cmd in ("RIGHT", "RT"):
            return self._logo_right(parts)

        # Pen control
        elif cmd in ("PENUP", "PU"):
            return self._logo_penup()
        elif cmd in ("PENDOWN", "PD"):
            return self._logo_pendown()

        # Screen / position
        elif cmd == "HOME":
            return self._logo_home()
        elif cmd in ("CLEARSCREEN", "CS", "CLEAN"):
            return self._logo_clearscreen()
        elif cmd in ("SETXY", "SETPOS"):
            return self._logo_setxy(parts)
        elif cmd == "SETX":
            return self._logo_setx(parts)
        elif cmd == "SETY":
            return self._logo_sety(parts)
        elif cmd in ("SETHEADING", "SETH"):
            return self._logo_setheading(parts)
        elif cmd == "TOWARDS":
            return self._logo_towards(parts)

        # Visibility
        elif cmd in ("SHOWTURTLE", "ST"):
            return self._logo_showturtle()
        elif cmd in ("HIDETURTLE", "HT"):
            return self._logo_hideturtle()

        # Color / pen
        elif cmd in ("SETCOLOR", "SETCOLOUR", "SETPENCOLOR", "SETPC"):
            return self._logo_setcolor(parts)
        elif cmd in ("SETPENSIZE", "SETWIDTH"):
            return self._logo_setpensize(parts)
        elif cmd in ("SETFILLCOLOR", "SETFC"):
            return self._logo_setfillcolor(parts)
        elif cmd in ("SETBACKGROUND", "SETBG", "SETSCREENCOLOR", "SETSCREENCOLOUR"):
            return self._logo_setbackground(parts)

        # Drawing shapes
        elif cmd == "CIRCLE":
            return self._logo_circle(parts)
        elif cmd == "ARC":
            return self._logo_arc(parts)
        elif cmd == "DOT":
            return self._logo_dot(parts)
        elif cmd in ("RECT", "RECTANGLE"):
            return self._logo_rect(parts)
        elif cmd == "SQUARE":
            return self._logo_square(parts)
        elif cmd == "TRIANGLE":
            return self._logo_triangle(parts)
        elif cmd == "POLYGON":
            return self._logo_polygon(parts)
        elif cmd == "STAR":
            return self._logo_star(parts)
        elif cmd in ("FILL", "FILLED"):
            return self._logo_fill()

        # Control structures
        elif cmd == "REPEAT":
            return self._logo_repeat(command)

        # Variables
        elif cmd == "MAKE":
            return self._logo_make(parts)

        # Query
        elif cmd in ("HEADING",):
            return self._logo_query_heading()
        elif cmd in ("POS", "POSITION"):
            return self._logo_query_position()
        elif cmd in ("XCOR",):
            tg = self.interpreter.turtle_graphics
            if tg:
                self.interpreter.log_output(str(tg["x"]))
            return "continue"
        elif cmd in ("YCOR",):
            tg = self.interpreter.turtle_graphics
            if tg:
                self.interpreter.log_output(str(tg["y"]))
            return "continue"

        # Tracing
        elif cmd == "TRACE":
            self.interpreter.turtle_trace = True
            return "continue"
        elif cmd == "NOTRACE":
            self.interpreter.turtle_trace = False
            return "continue"

        # Text / stamp
        elif cmd in ("LABEL", "STAMP"):
            return self._logo_label(parts)

        # Pen queries
        elif cmd == "PENCOLOR?":
            tg = self.interpreter.turtle_graphics
            if tg:
                self.interpreter.log_output(f"Pen color: {tg['pen_color']}")
            return "continue"
        elif cmd == "PENSIZE?":
            tg = self.interpreter.turtle_graphics
            if tg:
                self.interpreter.log_output(f"Pen size: {tg['pen_size']}")
            return "continue"

        # Screen boundary modes
        elif cmd == "WRAP":
            self._ensure_turtle()
            tg = self.interpreter.turtle_graphics
            if tg:
                tg["boundary_mode"] = "wrap"
            return "continue"
        elif cmd == "WINDOW":
            self._ensure_turtle()
            tg = self.interpreter.turtle_graphics
            if tg:
                tg["boundary_mode"] = "window"
            return "continue"
        elif cmd == "FENCE":
            self._ensure_turtle()
            tg = self.interpreter.turtle_graphics
            if tg:
                tg["boundary_mode"] = "fence"
            return "continue"

        else:
            self.interpreter.log_output(f"Unknown Logo command: {cmd}")
            return "continue"

    # --- Logo movement helpers ---

    def _eval_logo_arg(self, parts, index=1):
        """Evaluate a Logo argument (number or expression)."""
        if index >= len(parts):
            return 0
        arg = parts[index]
        # Handle :VAR references
        if arg.startswith(":"):
            var_name = arg[1:].upper()
            return float(self.interpreter.variables.get(var_name, 0))
        try:
            return float(self.interpreter.evaluate_expression(arg))
        except Exception:
            return 0

    def _ensure_turtle(self):
        """Make sure turtle graphics are initialised."""
        self.interpreter.init_turtle_graphics()

    def _logo_forward(self, parts):
        self._ensure_turtle()
        dist = self._eval_logo_arg(parts)
        self.interpreter.move_turtle(dist)
        return "continue"

    def _logo_back(self, parts):
        self._ensure_turtle()
        dist = self._eval_logo_arg(parts)
        self.interpreter.move_turtle(-dist)
        return "continue"

    def _logo_left(self, parts):
        self._ensure_turtle()
        angle = self._eval_logo_arg(parts)
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["heading"] = (tg["heading"] - angle) % 360
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_right(self, parts):
        self._ensure_turtle()
        angle = self._eval_logo_arg(parts)
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["heading"] = (tg["heading"] + angle) % 360
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_penup(self):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["pen_down"] = False
        return "continue"

    def _logo_pendown(self):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["pen_down"] = True
        return "continue"

    def _logo_home(self):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["x"] = 0.0
            tg["y"] = 0.0
            tg["heading"] = 0.0
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_clearscreen(self):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg and tg.get("canvas"):
            tg["canvas"].delete("all")
            tg["x"] = 0.0
            tg["y"] = 0.0
            tg["heading"] = 0.0
            tg["lines"] = []
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_setxy(self, parts):
        self._ensure_turtle()
        # Support comma-separated expressions: SETXY expr1, expr2
        raw_args = " ".join(parts[1:]).strip()
        if "," in raw_args:
            halves = self._smart_split(raw_args, ",")
            try:
                x = float(self._eval_basic_expression(halves[0].strip()))
            except Exception:
                x = 0
            try:
                y = float(self._eval_basic_expression(halves[1].strip())) if len(halves) > 1 else 0
            except Exception:
                y = 0
        else:
            x = self._eval_logo_arg(parts, 1)
            y = self._eval_logo_arg(parts, 2)
        tg = self.interpreter.turtle_graphics
        if tg:
            if tg["pen_down"] and tg.get("canvas"):
                cx, cy = tg["center_x"], tg["center_y"]
                old_sx = cx + tg["x"]
                old_sy = cy - tg["y"]
                new_sx = cx + x
                new_sy = cy - y
                line_id = tg["canvas"].create_line(
                    old_sx, old_sy, new_sx, new_sy,
                    fill=tg["pen_color"], width=tg["pen_size"]
                )
                tg["lines"].append(line_id)
            tg["x"] = float(x)
            tg["y"] = float(y)
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_setx(self, parts):
        self._ensure_turtle()
        x = self._eval_logo_arg(parts, 1)
        tg = self.interpreter.turtle_graphics
        if tg:
            if tg["pen_down"] and tg.get("canvas"):
                cx, cy = tg["center_x"], tg["center_y"]
                old_sx = cx + tg["x"]
                old_sy = cy - tg["y"]
                new_sx = cx + x
                line_id = tg["canvas"].create_line(
                    old_sx, old_sy, new_sx, old_sy,
                    fill=tg["pen_color"], width=tg["pen_size"]
                )
                tg["lines"].append(line_id)
            tg["x"] = float(x)
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_sety(self, parts):
        self._ensure_turtle()
        y = self._eval_logo_arg(parts, 1)
        tg = self.interpreter.turtle_graphics
        if tg:
            if tg["pen_down"] and tg.get("canvas"):
                cx, cy = tg["center_x"], tg["center_y"]
                old_sx = cx + tg["x"]
                old_sy = cy - tg["y"]
                new_sy = cy - y
                line_id = tg["canvas"].create_line(
                    old_sx, old_sy, old_sx, new_sy,
                    fill=tg["pen_color"], width=tg["pen_size"]
                )
                tg["lines"].append(line_id)
            tg["y"] = float(y)
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_setheading(self, parts):
        self._ensure_turtle()
        h = self._eval_logo_arg(parts, 1)
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["heading"] = float(h) % 360
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_towards(self, parts):
        self._ensure_turtle()
        tx = self._eval_logo_arg(parts, 1)
        ty = self._eval_logo_arg(parts, 2)
        tg = self.interpreter.turtle_graphics
        if tg:
            dx = tx - tg["x"]
            dy = ty - tg["y"]
            angle = math.degrees(math.atan2(dx, dy)) % 360
            tg["heading"] = angle
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_showturtle(self):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["visible"] = True
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_hideturtle(self):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg:
            tg["visible"] = False
            self.interpreter.update_turtle_display()
        return "continue"

    def _logo_setcolor(self, parts):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg and len(parts) > 1:
            raw = " ".join(parts[1:]).strip()
            # Resolve :VAR (Logo-style) and bare variable names
            if raw.startswith(":"):
                raw = str(self.interpreter.variables.get(raw[1:].upper(), raw))
            elif " " not in raw:
                resolved = self.interpreter.variables.get(raw.upper())
                if resolved is not None:
                    raw = str(resolved)
            color = raw.lower()
            color_map = {
                "0": "black", "1": "blue", "2": "green", "3": "cyan",
                "4": "red", "5": "magenta", "6": "yellow", "7": "white",
                "8": "brown", "9": "tan", "10": "forest", "11": "aqua",
                "12": "salmon", "13": "violet", "14": "orange", "15": "gray",
            }
            tg["pen_color"] = color_map.get(color, color)
        return "continue"

    def _logo_setpensize(self, parts):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg and len(parts) > 1:
            try:
                tg["pen_size"] = max(1, int(float(self._eval_logo_arg(parts))))
            except Exception:
                pass
        return "continue"

    def _logo_setfillcolor(self, parts):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg and len(parts) > 1:
            raw = " ".join(parts[1:]).strip()
            # Resolve :VAR (Logo-style) and bare variable names
            if raw.startswith(":"):
                raw = str(self.interpreter.variables.get(raw[1:].upper(), raw))
            elif " " not in raw:
                resolved = self.interpreter.variables.get(raw.upper())
                if resolved is not None:
                    raw = str(resolved)
            tg["fill_color"] = raw.lower()
        return "continue"

    def _logo_setbackground(self, parts):
        self._ensure_turtle()
        tg = self.interpreter.turtle_graphics
        if tg and tg.get("canvas") and len(parts) > 1:
            color = " ".join(parts[1:]).strip().lower()
            try:
                tg["canvas"].config(bg=color)
            except Exception:
                pass
        return "continue"

    def _logo_circle(self, parts):
        self._ensure_turtle()
        radius = self._eval_logo_arg(parts)
        tg = self.interpreter.turtle_graphics
        if tg and tg.get("canvas"):
            cx = tg["center_x"] + tg["x"]
            cy = tg["center_y"] - tg["y"]
            r = abs(radius)
            tg["canvas"].create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=tg["pen_color"], width=tg["pen_size"]
            )
        return "continue"

    def _logo_arc(self, parts):
        self._ensure_turtle()
        angle = self._eval_logo_arg(parts, 1)
        radius = self._eval_logo_arg(parts, 2) if len(parts) > 2 else 50
        tg = self.interpreter.turtle_graphics
        if tg and tg.get("canvas"):
            cx = tg["center_x"] + tg["x"]
            cy = tg["center_y"] - tg["y"]
            r = abs(radius)
            start = tg["heading"]
            tg["canvas"].create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=90 - start, extent=-angle,
                outline=tg["pen_color"], width=tg["pen_size"], style="arc"
            )
        return "continue"

    def _logo_dot(self, parts):
        self._ensure_turtle()
        size = self._eval_logo_arg(parts) if len(parts) > 1 else 3
        tg = self.interpreter.turtle_graphics
        if tg and tg.get("canvas"):
            cx = tg["center_x"] + tg["x"]
            cy = tg["center_y"] - tg["y"]
            r = max(1, size / 2)
            tg["canvas"].create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=tg["pen_color"], outline=tg["pen_color"]
            )
        return "continue"

    def _logo_rect(self, parts):
        self._ensure_turtle()
        w = self._eval_logo_arg(parts, 1)
        h = self._eval_logo_arg(parts, 2) if len(parts) > 2 else w
        tg = self.interpreter.turtle_graphics
        if tg and tg.get("canvas"):
            cx = tg["center_x"] + tg["x"]
            cy = tg["center_y"] - tg["y"]
            tg["canvas"].create_rectangle(
                cx, cy, cx + w, cy + h,
                outline=tg["pen_color"], width=tg["pen_size"]
            )
        return "continue"

    def _logo_square(self, parts):
        """Draw a square of given side length using turtle movement."""
        self._ensure_turtle()
        side = self._eval_logo_arg(parts) if len(parts) > 1 else 50
        for _ in range(4):
            self.interpreter.move_turtle(side)
            tg = self.interpreter.turtle_graphics
            if tg:
                tg["heading"] = (tg["heading"] + 90) % 360
        return "continue"

    def _logo_triangle(self, parts):
        """Draw an equilateral triangle of given side length."""
        self._ensure_turtle()
        side = self._eval_logo_arg(parts) if len(parts) > 1 else 50
        for _ in range(3):
            self.interpreter.move_turtle(side)
            tg = self.interpreter.turtle_graphics
            if tg:
                tg["heading"] = (tg["heading"] + 120) % 360
        return "continue"

    def _logo_polygon(self, parts):
        """Draw a regular polygon.  POLYGON sides length"""
        self._ensure_turtle()
        sides = int(self._eval_logo_arg(parts, 1)) if len(parts) > 1 else 6
        length = self._eval_logo_arg(parts, 2) if len(parts) > 2 else 50
        angle = 360.0 / max(sides, 3)
        for _ in range(max(sides, 3)):
            self.interpreter.move_turtle(length)
            tg = self.interpreter.turtle_graphics
            if tg:
                tg["heading"] = (tg["heading"] + angle) % 360
        return "continue"

    def _logo_star(self, parts):
        """Draw a star.  STAR points length"""
        self._ensure_turtle()
        points = int(self._eval_logo_arg(parts, 1)) if len(parts) > 1 else 5
        length = self._eval_logo_arg(parts, 2) if len(parts) > 2 else 50
        angle = 360.0 / max(points, 3) * 2  # skip-one vertex pattern
        for _ in range(max(points, 3)):
            self.interpreter.move_turtle(length)
            tg = self.interpreter.turtle_graphics
            if tg:
                tg["heading"] = (tg["heading"] + angle) % 360
        return "continue"

    def _logo_fill(self):
        """Fill placeholder – real flood fill requires bitmap canvas."""
        self.interpreter.log_output("FILL: (visual fill not supported in vector canvas)")
        return "continue"

    # --- REPEAT ---

    def _logo_repeat(self, command):
        """REPEAT n [ commands ]"""
        m = re.match(r'REPEAT\s+(\S+)\s*\[(.+)\]', command, re.IGNORECASE | re.DOTALL)
        if not m:
            self.interpreter.log_output("REPEAT syntax: REPEAT n [ commands ]")
            return "continue"
        count_expr = m.group(1)
        block = m.group(2).strip()

        # Evaluate count
        try:
            if count_expr.startswith(":"):
                count = int(float(self.interpreter.variables.get(count_expr[1:].upper(), 0)))
            else:
                count = int(float(self.interpreter.evaluate_expression(count_expr)))
        except Exception:
            count = 0

        # Split block into commands
        cmds = self._split_block_commands(block)

        for i in range(count):
            self.interpreter.variables["REPCOUNT"] = i + 1
            for c in cmds:
                c = c.strip()
                if c:
                    result = self.execute_command(c)
                    if result in ("end", "stop"):
                        return result
        return "continue"

    def _split_block_commands(self, block):
        """Split a bracketed block into individual commands, respecting nested brackets."""
        commands = []
        depth = 0
        current = []
        for char in block:
            if char == '[':
                depth += 1
                current.append(char)
            elif char == ']':
                depth -= 1
                current.append(char)
            elif char == '\n' and depth == 0:
                commands.append(''.join(current))
                current = []
            else:
                current.append(char)
        if current:
            commands.append(''.join(current))

        # Further split on spaces between commands at top level
        result = []
        for cmd_line in commands:
            result.extend(self._split_top_level_line(cmd_line.strip()))
        return result

    def _split_top_level_line(self, line):
        """Split a single line into separate commands, respecting brackets."""
        if not line:
            return []

        # If line contains REPEAT with brackets, keep as one unit
        # Otherwise split by recognizing command keywords
        commands = []
        tokens = []
        depth = 0
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '[':
                depth += 1
                tokens.append(ch)
            elif ch == ']':
                depth -= 1
                tokens.append(ch)
                # After closing bracket at depth 0, make a command break
                if depth == 0:
                    commands.append(''.join(tokens).strip())
                    tokens = []
            elif ch == ' ' and depth == 0:
                # Check if next word is a command keyword
                rest = line[i + 1:].lstrip()
                first_next = rest.split()[0].upper() if rest.split() else ""
                all_keywords = {
                    "FORWARD", "FD", "BACK", "BK", "BACKWARD",
                    "LEFT", "LT", "RIGHT", "RT",
                    "PENUP", "PU", "PENDOWN", "PD",
                    "HOME", "CLEARSCREEN", "CS",
                    "SHOWTURTLE", "ST", "HIDETURTLE", "HT",
                    "SETXY", "SETCOLOR", "SETCOLOUR", "SETPENCOLOR", "SETPC",
                    "SETPENSIZE", "SETWIDTH", "SETHEADING", "SETH",
                    "SETFILLCOLOR", "SETFC", "SETBACKGROUND", "SETBG",
                    "CIRCLE", "ARC", "DOT", "RECT", "RECTANGLE",
                    "SQUARE", "TRIANGLE", "FILL", "FILLED",
                    "REPEAT", "MAKE", "TOWARDS",
                    "PRINT", "LET", "IF", "FOR", "GOTO", "GOSUB", "REM", "END",
                }
                if first_next in all_keywords and tokens:
                    commands.append(''.join(tokens).strip())
                    tokens = []
                else:
                    tokens.append(ch)
            else:
                tokens.append(ch)
            i += 1

        if tokens:
            commands.append(''.join(tokens).strip())
        return [c for c in commands if c]

    # --- MAKE ---

    def _logo_make(self, parts):
        """MAKE "varname value"""
        if len(parts) < 3:
            return "continue"
        name = parts[1].strip('"').upper()
        value_str = " ".join(parts[2:])
        try:
            value = self.interpreter.evaluate_expression(value_str)
        except Exception:
            value = value_str
        self.interpreter.variables[name] = value
        return "continue"

    # --- Logo procedure definition ---

    def _handle_logo_define(self, command):
        """TO procname :param1 :param2 ...  collects lines until END."""
        parts = command.split()
        if len(parts) < 2:
            self.interpreter.log_output("TO requires a procedure name")
            return "continue"

        proc_name = parts[1].lower()
        params = [p.lstrip(":").upper() for p in parts[2:] if p.startswith(":")]

        # Collect body lines until END
        body_lines = []
        self.interpreter.current_line += 1
        found_end = False
        while self.interpreter.current_line < len(self.interpreter.program_lines):
            _, line_text = self.interpreter.program_lines[self.interpreter.current_line]
            if line_text.strip().upper() == "END":
                found_end = True
                break
            body_lines.append(line_text)
            self.interpreter.current_line += 1

        if not found_end:
            self.interpreter.log_error(f"TO {proc_name}: missing END", self.interpreter.current_line + 1)

        self.logo_procedures[proc_name] = (params, body_lines)
        # Also store on interpreter for cross-reference
        self.interpreter.logo_procedures[proc_name] = (params, body_lines)
        return "continue"

    def _logo_proc_args(self, command, first_word):
        """Extract args for a Logo procedure call.
        Uses comma-split when commas are present (for multi-expression args),
        otherwise falls back to whitespace-split (classic Logo style)."""
        rest = command[len(first_word):].strip()
        if not rest:
            return []
        if "," in rest:
            return [a.strip() for a in self._smart_split(rest, ",") if a.strip()]
        return rest.split()

    def _call_logo_procedure(self, proc_name, args):
        """Call a user-defined Logo procedure."""
        procs = self.logo_procedures
        if proc_name not in procs:
            procs = getattr(self.interpreter, 'logo_procedures', {})
        if proc_name not in procs:
            self.interpreter.log_output(f"Unknown procedure: {proc_name}")
            return "continue"

        params, body = procs[proc_name]

        # Save current variables
        saved = {}
        for i, param in enumerate(params):
            saved[param] = self.interpreter.variables.get(param)
            if i < len(args):
                arg_val = args[i]
                if isinstance(arg_val, str) and arg_val.startswith(":"):
                    arg_val = self.interpreter.variables.get(arg_val[1:].upper(), 0)
                try:
                    arg_val = self.interpreter.evaluate_expression(str(arg_val))
                except Exception:
                    pass
                self.interpreter.variables[param] = arg_val

        # Execute body
        for line in body:
            result = self.execute_command(line.strip())
            if result in ("end", "stop"):
                break

        # Restore variables
        for param in params:
            if saved.get(param) is not None:
                self.interpreter.variables[param] = saved[param]
            elif param in self.interpreter.variables:
                del self.interpreter.variables[param]

        return "continue"

    # --- Logo queries ---

    def _logo_query_heading(self):
        tg = self.interpreter.turtle_graphics
        if tg:
            self.interpreter.log_output(f"Heading: {tg['heading']}")
        return "continue"

    def _logo_query_position(self):
        tg = self.interpreter.turtle_graphics
        if tg:
            self.interpreter.log_output(f"Position: [{tg['x']}, {tg['y']}]")
        return "continue"

    # ==================================================================
    #  BASIC sub-system
    # ==================================================================

    def _dispatch_basic(self, command, first_word, upper_cmd):  # noqa: C901
        """Route BASIC-style statements."""
        cmd = first_word.upper()

        # Handle line-number prefixed commands
        # (The interpreter parse_line already strips line numbers, but in case)

        if cmd == "PRINT" or cmd == "?":
            return self._basic_print(command)
        elif cmd == "LET":
            return self._basic_let(command)
        elif cmd == "INPUT":
            return self._basic_input(command)
        elif cmd == "IF":
            return self._basic_if(command)
        elif cmd == "ELSE":
            return self._basic_else()
        elif cmd == "FOR":
            return self._basic_for(command)
        elif cmd == "NEXT":
            return self._basic_next(command)
        elif cmd == "GOTO":
            return self._basic_goto(command)
        elif cmd == "GOSUB":
            return self._basic_gosub(command)
        elif cmd == "RETURN":
            return self._modern_return(command)
        elif cmd == "DIM":
            return self._basic_dim(command)
        elif cmd == "REM" or cmd == "'":
            return "continue"
        elif cmd == "END":
            # Check for block-closing END variants
            upper_cmd = command.upper().strip()
            if upper_cmd == "END SELECT":
                if self.interpreter.select_stack:
                    self.interpreter.select_stack.pop()
                return "continue"
            elif upper_cmd == "END IF":
                return "continue"  # Block IF closing — no-op
            elif upper_cmd == "END SUB":
                return "return"  # End of subroutine
            elif upper_cmd == "END FUNCTION":
                return "return"  # End of function
            elif upper_cmd == "END TRY":
                if self.interpreter.try_stack:
                    self.interpreter.try_stack.pop()
                return "continue"
            else:
                self.interpreter.running = False
                return "end"
        elif cmd == "STOP":
            self.interpreter.running = False
            return "end"
        elif cmd == "BREAK":
            return "break"
        elif cmd == "CLS":
            if hasattr(self.interpreter, 'output_widget') and self.interpreter.output_widget:
                try:
                    self.interpreter.output_widget.delete("1.0", "end")
                except Exception:
                    self.interpreter.log_output("\n" * 25)
            else:
                self.interpreter.log_output("\n" * 25)
            return "continue"
        elif cmd == "DATA":
            return "continue"  # DATA lines are pre-parsed
        elif cmd == "READ":
            return self._basic_read(command)
        elif cmd == "RANDOMIZE":
            # Support RANDOMIZE, RANDOMIZE TIMER, or RANDOMIZE <seed>
            rest = command[len("RANDOMIZE"):].strip().upper()
            if not rest or rest == "TIMER":
                random.seed()
            else:
                try:
                    random.seed(int(float(self._eval_basic_expression(rest))))
                except Exception:
                    random.seed()
            return "continue"
        elif cmd == "RESTORE":
            return self._basic_restore()
        elif cmd == "DELAY" or cmd == "SLEEP":
            return self._basic_delay(command)
        elif cmd == "DO":
            return self._basic_do(command)
        elif cmd == "LOOP":
            return self._basic_loop(command)
        elif cmd == "WHILE":
            return self._basic_while(command)
        elif cmd == "WEND":
            return self._basic_wend()
        elif cmd == "EXIT":
            return self._basic_exit(command)
        elif cmd == "SELECT":
            return self._basic_select(command)
        elif cmd == "CASE":
            return self._basic_case(command)
        elif cmd == "SWAP":
            return self._basic_swap(command)
        elif cmd == "INCR":
            return self._basic_incr_decr(command, 1)
        elif cmd == "DECR":
            return self._basic_incr_decr(command, -1)
        elif cmd == "COLOR" or cmd == "COLOUR":
            # Turtle color change, for BASIC-style usage
            return self._logo_setcolor(command.split())
        elif cmd == "ENDIF":
            return "continue"  # Block IF closing — alias for END IF
        elif cmd == "ELSEIF":
            return self._basic_elseif(command)
        elif cmd == "ON":
            return self._basic_on(command)
        elif cmd == "BEEP":
            return self._basic_beep()
        elif cmd == "TAB":
            return self._basic_tab(command)
        elif cmd == "SPC":
            return self._basic_spc(command)

        # --- Modern language extensions ---
        elif cmd == "SUB":
            return self._modern_sub_define(command)
        elif cmd == "FUNCTION":
            return self._modern_function_define(command)
        elif cmd == "CALL":
            return self._modern_call(command)
        elif cmd == "RETURN":
            return self._modern_return(command)

        # List operations
        elif cmd == "LIST":
            return self._modern_list(command)
        elif cmd == "SPLIT":
            return self._modern_split_stmt(command)
        elif cmd == "JOIN":
            return self._modern_join_stmt(command)
        elif cmd == "PUSH":
            return self._modern_push(command)
        elif cmd == "POP":
            return self._modern_pop(command)
        elif cmd == "SHIFT":
            return self._modern_shift(command)
        elif cmd == "UNSHIFT":
            return self._modern_unshift(command)
        elif cmd == "SORT":
            return self._modern_sort(command)
        elif cmd == "REVERSE":
            return self._modern_reverse(command)
        elif cmd == "SPLICE":
            return self._modern_splice(command)

        # Dictionary operations
        elif cmd == "DICT":
            return self._modern_dict(command)
        elif cmd == "SET":
            return self._modern_set(command)
        elif cmd == "GET":
            return self._modern_get(command)
        elif cmd == "DELETE":
            return self._modern_delete(command)

        # File I/O
        elif cmd == "OPEN":
            return self._modern_open(command)
        elif cmd == "CLOSE":
            return self._modern_close(command)
        elif cmd == "READLINE":
            return self._modern_readline(command)
        elif cmd == "WRITELINE":
            return self._modern_writeline(command)
        elif cmd == "READFILE":
            return self._modern_readfile(command)
        elif cmd == "WRITEFILE":
            return self._modern_writefile(command)
        elif cmd == "APPENDFILE":
            return self._modern_appendfile(command)

        # Error handling
        elif cmd == "TRY":
            return self._modern_try(command)
        elif cmd == "CATCH":
            return self._modern_catch(command)
        elif cmd == "THROW":
            return self._modern_throw(command)

        # Modern control flow
        elif cmd == "FOREACH":
            return self._modern_foreach(command)

        # Constants & type operations
        elif cmd == "CONST":
            return self._modern_const(command)
        elif cmd == "TYPEOF":
            return self._modern_typeof(command)
        elif cmd == "ASSERT":
            return self._modern_assert(command)

        # Module system
        elif cmd == "IMPORT":
            return self._modern_import(command)

        # Formatted output
        elif cmd == "PRINTF":
            return self._modern_printf(command)

        # JSON operations
        elif cmd == "JSON":
            return self._modern_json(command)

        # Regex operations
        elif cmd == "REGEX":
            return self._modern_regex(command)

        # ENUM
        elif cmd == "ENUM":
            return self._modern_enum(command)

        # STRUCT
        elif cmd == "STRUCT":
            return self._modern_struct(command)
        elif cmd == "NEW":
            return self._modern_new(command)

        # LAMBDA
        elif cmd == "LAMBDA":
            return self._modern_lambda(command)

        # Functional list operations
        elif cmd == "MAP":
            return self._modern_map(command)
        elif cmd == "FILTER":
            return self._modern_filter(command)
        elif cmd == "REDUCE":
            return self._modern_reduce(command)

        # Turtle graphics commands accessible from BASIC style
        elif cmd in ("FORWARD", "FD", "BACK", "BK", "BACKWARD",
                     "LEFT", "LT", "RIGHT", "RT",
                     "PENUP", "PU", "PENDOWN", "PD"):
            return self._dispatch_logo(command, cmd)

        # Direct variable assignment: X = 5
        elif "=" in command and not command.startswith("IF"):
            return self._basic_let("LET " + command)

        # Math/string function calls as statements
        elif cmd in ("SIN", "COS", "TAN", "SQRT", "ABS", "INT", "RND",
                     "LOG", "EXP", "CEIL", "FIX"):
            return self._basic_math_func(command)
        elif cmd in ("LEN", "MID", "LEFT", "RIGHT", "INSTR", "STR",
                     "VAL", "CHR", "ASC", "UCASE", "LCASE"):
            return self._basic_string_func(command)

        else:
            self.interpreter.log_output(f"Unknown command: {command}")
            return "continue"

    # --- BASIC PRINT ---

    def _basic_print(self, command):
        """PRINT expression[; expression]..."""
        # Strip PRINT or ?
        text = re.sub(r'^(PRINT|\?)\s*', '', command, flags=re.IGNORECASE).strip()

        if not text:
            self.interpreter.log_output("")
            return "continue"

        # Split on ; for concatenation (no newline) and , for tab
        output_parts = []
        trailing_semi = text.endswith(";")
        if trailing_semi:
            text = text[:-1]

        # Tokenize respecting quoted strings to avoid splitting inside them
        segments = self._tokenize_print(text)
        for seg in segments:
            seg = seg.strip()
            if seg == ";" or seg == ",":
                if seg == ",":
                    output_parts.append("\t")
                continue
            if not seg:
                continue
            output_parts.append(str(self._eval_basic_expression(seg)))

        result = "".join(output_parts)
        if trailing_semi:
            self.interpreter.log_output(result, end="")
        else:
            self.interpreter.log_output(result)
        return "continue"

    @staticmethod
    def _tokenize_print(text):
        """Split PRINT arguments on ; and , delimiters, respecting quoted strings
        and parenthesis depth so that f(a, b) is never split at the inner comma."""
        tokens = []
        current = []
        in_string = False
        depth = 0
        for ch in text:
            if ch == '"' and depth == 0:
                in_string = not in_string
                current.append(ch)
            elif ch in '([' and not in_string:
                depth += 1
                current.append(ch)
            elif ch in ')]' and not in_string:
                depth -= 1
                current.append(ch)
            elif (ch == ';' or ch == ',') and not in_string and depth == 0:
                tokens.append(''.join(current))
                tokens.append(ch)
                current = []
            else:
                current.append(ch)
        if current:
            tokens.append(''.join(current))
        return tokens

    # --- BASIC LET ---

    def _basic_let(self, command):
        """LET var = expression   or   var = expression"""
        text = re.sub(r'^LET\s+', '', command, flags=re.IGNORECASE).strip()
        m = re.match(r'(\w+\$?(?:\([^)]*\))?)\s*=\s*(.*)', text, re.DOTALL)
        if not m:
            return "continue"

        var_part = m.group(1)
        expr = m.group(2).strip()

        # Array element:  ARR(index)
        arr_match = re.match(r'(\w+)\((.+)\)', var_part)
        if arr_match:
            arr_name = arr_match.group(1).upper()
            idx_expr = arr_match.group(2)
            idx = int(float(self.interpreter.evaluate_expression(idx_expr)))
            if arr_name in self.arrays:
                if 0 <= idx < len(self.arrays[arr_name]):
                    self.arrays[arr_name][idx] = self._eval_basic_expression(expr)
            else:
                self.interpreter.variables[f"{arr_name}({idx})"] = self._eval_basic_expression(expr)
            return "continue"

        var_name = var_part.upper()

        # Protect constants
        if var_name in self.interpreter.constants:
            self.interpreter.log_output(f"Cannot reassign constant: {var_name}")
            return "continue"

        # Support list element assignment: LIST[index]
        list_m = re.match(r'(\w+)\[(.+)\]', text.split("=")[0].strip())
        if list_m:
            lname = list_m.group(1).upper()
            idx = int(float(self._eval_basic_expression(list_m.group(2))))
            if lname in self.interpreter.lists:
                while len(self.interpreter.lists[lname]) <= idx:
                    self.interpreter.lists[lname].append(0)
                self.interpreter.lists[lname][idx] = self._eval_basic_expression(expr)
                return "continue"

        # Support dict field assignment: DICT.key
        dot_m = re.match(r'(\w+)\.(\w+)', text.split("=")[0].strip())
        if dot_m:
            dname = dot_m.group(1).upper()
            key = dot_m.group(2)
            if dname in self.interpreter.dicts:
                self.interpreter.dicts[dname][key] = self._eval_basic_expression(expr)
                return "continue"

        value = self._eval_basic_expression(expr)
        self.interpreter.variables[var_name] = value
        # Mirror Python lists (e.g. from SPLIT()) into interpreter.lists so
        # list-indexing syntax (X[n]) and LENGTH(X) work without a separate
        # LIST declaration.
        if isinstance(value, list):
            self.interpreter.lists[var_name] = value
        return "continue"

    # --- BASIC INPUT ---

    def _basic_input(self, command):
        """INPUT ["prompt"[;,]] var"""
        text = re.sub(r'^INPUT\s+', '', command, flags=re.IGNORECASE).strip()

        prompt = "? "
        var_name = text

        # INPUT "prompt"; VAR   or   INPUT "prompt", VAR
        m = re.match(r'"([^"]*)"[;,]\s*(\w+\$?)', text)
        if m:
            prompt = m.group(1) + " "
            var_name = m.group(2)
        else:
            # INPUT "prompt" VAR   (no separator — common user shorthand)
            m = re.match(r'"([^"]*)"\s+(\w+\$?)', text)
            if m:
                prompt = m.group(1) + " "
                var_name = m.group(2)
            # else: INPUT VAR (no prompt) — var_name is already set to text

        var_name = var_name.strip().upper()
        value = self.interpreter.get_input(prompt)

        # Try numeric conversion
        try:
            value = float(value)
            if value == int(value):
                value = int(value)
        except (ValueError, TypeError):
            pass

        self.interpreter.variables[var_name] = value
        return "continue"

    # --- BASIC IF ---

    def _basic_if(self, command):
        """IF condition THEN statement [ELSE statement]
        Supports both single-line and multi-line IF blocks:
          IF cond THEN stmt [ELSE stmt]          -- single-line
          IF cond THEN                           -- multi-line (no stmt after THEN)
              ...body...
          [ELSE]
              ...body...
          END IF
        """
        m = re.match(r'IF\s+(.+?)\s+THEN\s*(.*)', command, re.IGNORECASE)
        if not m:
            return "continue"

        condition = m.group(1)
        then_rest = m.group(2).strip()

        # --- Multi-line block IF (nothing after THEN) ---
        if not then_rest:
            cond_result = self._eval_basic_condition(condition)
            if cond_result:
                # Execute lines until ELSE/ELSEIF or END IF
                return "continue"  # just let main loop proceed into the block
            else:
                # Skip to ELSE, ELSEIF, or END IF
                depth = 1
                self.interpreter.current_line += 1
                while self.interpreter.current_line < len(self.interpreter.program_lines):
                    _, lt = self.interpreter.program_lines[self.interpreter.current_line]
                    lu = lt.strip().upper()
                    if lu.startswith("IF ") and (lu.endswith("THEN") or " THEN " in lu):
                        depth += 1
                    elif lu == "ELSE" and depth == 1:
                        # Found our ELSE — execute from here
                        return "continue"
                    elif lu.startswith("ELSEIF ") and depth == 1:
                        # Found ELSEIF — evaluate its condition
                        ei_match = re.match(r'ELSEIF\s+(.+?)\s+THEN', lt.strip(), re.IGNORECASE)
                        if ei_match and self._eval_basic_condition(ei_match.group(1)):
                            return "continue"  # condition true, execute this block
                        # else keep scanning
                    elif lu in ("END IF", "ENDIF"):
                        depth -= 1
                        if depth == 0:
                            return "continue"
                    self.interpreter.current_line += 1
                return "continue"

        # --- Single-line IF ---
        then_else = then_rest

        # Split THEN...ELSE
        else_match = re.split(r'\bELSE\b', then_else, flags=re.IGNORECASE)
        then_part = else_match[0].strip()
        else_part = else_match[1].strip() if len(else_match) > 1 else None

        # Evaluate condition
        cond_result = self._eval_basic_condition(condition)

        if cond_result:
            # THEN part could be line number (GOTO) or statement
            if re.match(r'^\d+$', then_part):
                return self._basic_goto(f"GOTO {then_part}")
            return self.execute_command(then_part)
        elif else_part:
            if re.match(r'^\d+$', else_part):
                return self._basic_goto(f"GOTO {else_part}")
            return self.execute_command(else_part)

        return "continue"

    def _basic_else(self):
        """ELSE — only reached when IF-true block was executed (need to skip to END IF)."""
        depth = 1
        self.interpreter.current_line += 1
        while self.interpreter.current_line < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[self.interpreter.current_line]
            lu = lt.strip().upper()
            if lu.startswith("IF ") and (lu.endswith("THEN") or " THEN " in lu):
                depth += 1
            elif lu in ("END IF", "ENDIF"):
                depth -= 1
                if depth == 0:
                    return "continue"
            self.interpreter.current_line += 1
        return "continue"

    # --- BASIC FOR/NEXT ---

    def _basic_for(self, command):
        """FOR var = start TO end [STEP step]"""
        m = re.match(r'FOR\s+(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$',
                     command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output(f"FOR syntax error: {command}")
            return "continue"

        var_name = m.group(1).upper()
        start = float(self.interpreter.evaluate_expression(m.group(2)))
        end = float(self.interpreter.evaluate_expression(m.group(3)))
        step = float(self.interpreter.evaluate_expression(m.group(4))) if m.group(4) else 1

        if step == 0:
            self.interpreter.log_output("FOR error: STEP cannot be 0")
            return "continue"

        self.interpreter.variables[var_name] = start if start == int(start) else start
        if start == int(start):
            self.interpreter.variables[var_name] = int(start)

        self.interpreter.for_stack.append({
            "var": var_name,
            "end": end,
            "step": step,
            "line": self.interpreter.current_line,
        })
        return "continue"

    def _basic_next(self, command):
        """NEXT [var]"""
        if not self.interpreter.for_stack:
            self.interpreter.log_output("NEXT without FOR")
            return "continue"

        loop = self.interpreter.for_stack[-1]
        var_name = loop["var"]

        # Check optional variable name
        parts = command.split()
        if len(parts) > 1:
            specified_var = parts[1].upper()
            if specified_var != var_name:
                self.interpreter.log_output(f"NEXT {specified_var} doesn't match FOR {var_name}")
                return "continue"

        current_val = float(self.interpreter.variables.get(var_name, 0))
        current_val += loop["step"]
        self.interpreter.variables[var_name] = int(current_val) if current_val == int(current_val) else current_val

        # Check loop condition
        if loop["step"] > 0 and current_val > loop["end"]:
            self.interpreter.for_stack.pop()
            return "continue"
        elif loop["step"] < 0 and current_val < loop["end"]:
            self.interpreter.for_stack.pop()
            return "continue"
        else:
            self.interpreter.current_line = loop["line"] + 1
            return "jump"

    # --- BASIC GOTO/GOSUB ---

    def _basic_goto(self, command):
        """GOTO line_number or label"""
        parts = command.split()
        if len(parts) < 2:
            return "continue"
        target = parts[1].strip()

        # Try label first
        if target in self.interpreter.labels:
            self.interpreter.current_line = self.interpreter.labels[target]
            return "jump"

        # Try line number
        try:
            target_line = int(target)
            for i, (line_num, _) in enumerate(self.interpreter.program_lines):
                if line_num == target_line:
                    self.interpreter.current_line = i
                    return "jump"
            self.interpreter.log_output(f"Line {target_line} not found")
        except ValueError:
            self.interpreter.log_output(f"Invalid GOTO target: {target}")
        return "continue"

    def _basic_gosub(self, command):
        """GOSUB line_number"""
        parts = command.split()
        if len(parts) < 2:
            return "continue"
        target = parts[1].strip()

        self.interpreter.stack.append(self.interpreter.current_line)

        if target in self.interpreter.labels:
            self.interpreter.current_line = self.interpreter.labels[target]
            return "jump"

        try:
            target_line = int(target)
            for i, (line_num, _) in enumerate(self.interpreter.program_lines):
                if line_num == target_line:
                    self.interpreter.current_line = i
                    return "jump"
            self.interpreter.log_output(f"Line {target_line} not found")
        except ValueError:
            self.interpreter.log_output(f"Invalid GOSUB target: {target}")
        return "continue"

    def _basic_return(self):
        """RETURN from GOSUB."""
        if self.interpreter.stack:
            self.interpreter.current_line = self.interpreter.stack.pop()
            return "continue"
        self.interpreter.log_output("RETURN without GOSUB")
        return "continue"

    # --- BASIC DIM ---

    def _basic_dim(self, command):
        """DIM arrayname(size)"""
        text = re.sub(r'^DIM\s+', '', command, flags=re.IGNORECASE).strip()
        for decl in text.split(","):
            decl = decl.strip()
            m = re.match(r'(\w+)\((\d+)\)', decl)
            if m:
                name = m.group(1).upper()
                size = int(m.group(2))
                self.arrays[name] = [0] * (size + 1)
        return "continue"

    # --- BASIC READ (from DATA statements) ---

    def _basic_read(self, command):
        """READ var1[, var2, ...]

        Uses DATA values pre-collected by interpreter.load_program().
        """
        text = re.sub(r'^READ\s+', '', command, flags=re.IGNORECASE).strip()
        var_names = [v.strip().upper() for v in text.split(",")]

        # Use interpreter's pre-collected data values
        data_values = self.interpreter._data_values  # pylint: disable=protected-access
        data_pos = self.interpreter._data_pos  # pylint: disable=protected-access

        for var in var_names:
            if data_pos < len(data_values):
                self.interpreter.variables[var] = data_values[data_pos]
                data_pos += 1
            else:
                self.interpreter.log_output("Out of DATA")
                break
        self.interpreter._data_pos = data_pos  # pylint: disable=protected-access
        return "continue"

    # --- BASIC RESTORE ---

    def _basic_restore(self):
        """RESTORE – reset DATA pointer to beginning."""
        self.interpreter._data_pos = 0  # pylint: disable=protected-access
        return "continue"

    # --- BASIC DELAY ---

    def _basic_delay(self, command):
        """DELAY milliseconds  or  SLEEP seconds"""
        parts = command.split()
        if len(parts) > 1:
            try:
                val = float(self.interpreter.evaluate_expression(parts[1]))
                if parts[0].upper() == "SLEEP":
                    time.sleep(val)
                else:
                    time.sleep(val / 1000.0)
            except Exception:
                time.sleep(1)
        return "continue"

    # --- BASIC DO/LOOP ---

    def _basic_do(self, command):
        """DO [WHILE condition | UNTIL condition]"""
        rest = command[2:].strip() if len(command) > 2 else ""
        self.interpreter.do_stack.append({
            "line": self.interpreter.current_line,
            "condition": rest,
        })

        # Evaluate pre-condition if present
        upper_rest = rest.upper().strip()
        if upper_rest.startswith("WHILE"):
            cond = rest[5:].strip()
            if not self._eval_basic_condition(cond):
                # Skip to LOOP
                self.interpreter.do_stack.pop()
                depth = 1
                self.interpreter.current_line += 1
                while self.interpreter.current_line < len(self.interpreter.program_lines):
                    _, lt = self.interpreter.program_lines[self.interpreter.current_line]
                    lu = lt.strip().upper()
                    if lu.startswith("DO"):
                        depth += 1
                    elif lu.startswith("LOOP"):
                        depth -= 1
                        if depth == 0:
                            break
                    self.interpreter.current_line += 1
                return "continue"
        elif upper_rest.startswith("UNTIL"):
            cond = rest[5:].strip()
            if self._eval_basic_condition(cond):
                # Already true – skip to LOOP
                self.interpreter.do_stack.pop()
                depth = 1
                self.interpreter.current_line += 1
                while self.interpreter.current_line < len(self.interpreter.program_lines):
                    _, lt = self.interpreter.program_lines[self.interpreter.current_line]
                    lu = lt.strip().upper()
                    if lu.startswith("DO"):
                        depth += 1
                    elif lu.startswith("LOOP"):
                        depth -= 1
                        if depth == 0:
                            break
                    self.interpreter.current_line += 1
                return "continue"
        return "continue"

    def _basic_loop(self, command):
        """LOOP [WHILE condition | UNTIL condition]"""
        if not self.interpreter.do_stack:
            self.interpreter.log_output("LOOP without DO")
            return "continue"

        loop = self.interpreter.do_stack[-1]
        text = re.sub(r'^LOOP\s*', '', command, flags=re.IGNORECASE).strip()

        should_continue = True
        if text.upper().startswith("WHILE"):
            cond = text[5:].strip()
            should_continue = self._eval_basic_condition(cond)
        elif text.upper().startswith("UNTIL"):
            cond = text[5:].strip()
            should_continue = not self._eval_basic_condition(cond)

        if should_continue:
            self.interpreter.current_line = loop["line"]
            return "jump"
        else:
            self.interpreter.do_stack.pop()
            return "continue"

    # --- BASIC WHILE/WEND ---

    def _basic_while(self, command):
        """WHILE condition"""
        cond = re.sub(r'^WHILE\s+', '', command, flags=re.IGNORECASE).strip()
        if self._eval_basic_condition(cond):
            self.interpreter.while_stack.append({
                "line": self.interpreter.current_line,
                "condition": cond,
            })
            return "continue"
        else:
            # Condition false – skip to matching WEND
            depth = 1
            self.interpreter.current_line += 1
            while self.interpreter.current_line < len(self.interpreter.program_lines):
                _, lt = self.interpreter.program_lines[self.interpreter.current_line]
                if lt.strip().upper().startswith("WHILE"):
                    depth += 1
                elif lt.strip().upper() == "WEND":
                    depth -= 1
                    if depth == 0:
                        # current_line is now at WEND; the main loop will +1
                        return "continue"
                self.interpreter.current_line += 1
            return "continue"

    def _basic_wend(self):
        """WEND – loop back to WHILE."""
        if not self.interpreter.while_stack:
            self.interpreter.log_output("WEND without WHILE")
            return "continue"

        loop = self.interpreter.while_stack[-1]
        if self._eval_basic_condition(loop["condition"]):
            self.interpreter.current_line = loop["line"]
            return "jump"
        else:
            self.interpreter.while_stack.pop()
            return "continue"

    # --- BASIC EXIT ---

    def _basic_exit(self, command):
        """EXIT FOR/DO/WHILE – handles nested loops with depth tracking."""
        parts = command.split()
        what = parts[1].upper() if len(parts) > 1 else "FOR"

        if what == "FOR" and self.interpreter.for_stack:
            self.interpreter.for_stack.pop()
            # Skip to matching NEXT (handle nested FOR/NEXT)
            depth = 1
            self.interpreter.current_line += 1
            while self.interpreter.current_line < len(self.interpreter.program_lines):
                _, lt = self.interpreter.program_lines[self.interpreter.current_line]
                lu = lt.strip().upper()
                if lu.startswith("FOR "):
                    depth += 1
                elif lu.startswith("NEXT"):
                    depth -= 1
                    if depth == 0:
                        break
                self.interpreter.current_line += 1
        elif what == "DO" and self.interpreter.do_stack:
            self.interpreter.do_stack.pop()
            depth = 1
            self.interpreter.current_line += 1
            while self.interpreter.current_line < len(self.interpreter.program_lines):
                _, lt = self.interpreter.program_lines[self.interpreter.current_line]
                lu = lt.strip().upper()
                if lu.startswith("DO"):
                    depth += 1
                elif lu.startswith("LOOP"):
                    depth -= 1
                    if depth == 0:
                        break
                self.interpreter.current_line += 1
        elif what == "WHILE" and self.interpreter.while_stack:
            self.interpreter.while_stack.pop()
            depth = 1
            self.interpreter.current_line += 1
            while self.interpreter.current_line < len(self.interpreter.program_lines):
                _, lt = self.interpreter.program_lines[self.interpreter.current_line]
                lu = lt.strip().upper()
                if lu.startswith("WHILE ") or lu == "WHILE":
                    depth += 1
                elif lu == "WEND":
                    depth -= 1
                    if depth == 0:
                        break
                self.interpreter.current_line += 1
        return "continue"

    # --- BASIC SELECT/CASE ---

    def _basic_select(self, command):
        """SELECT CASE expression"""
        m = re.match(r'SELECT\s+CASE\s+(.*)', command, re.IGNORECASE)
        if m:
            expr_val = self._eval_basic_expression(m.group(1).strip())
            self.interpreter.select_stack.append({
                "value": expr_val,
                "matched": False,
            })
        return "continue"

    def _basic_case(self, command):
        """CASE value / CASE ELSE"""
        if not self.interpreter.select_stack:
            return "continue"

        sel = self.interpreter.select_stack[-1]
        text = re.sub(r'^CASE\s+', '', command, flags=re.IGNORECASE).strip()

        if text.upper() == "ELSE":
            if not sel["matched"]:
                sel["matched"] = True
                return "continue"
            # Skip to END SELECT
            return self._skip_to_end_select()

        # Check if this CASE matches
        case_val = self._eval_basic_expression(text)
        if case_val == sel["value"] and not sel["matched"]:
            sel["matched"] = True
            return "continue"
        else:
            # Skip to next CASE or END SELECT
            return self._skip_to_next_case()

    def _skip_to_end_select(self):
        depth = 1
        self.interpreter.current_line += 1
        while self.interpreter.current_line < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[self.interpreter.current_line]
            upper_lt = lt.strip().upper()
            if upper_lt.startswith("SELECT"):
                depth += 1
            elif upper_lt == "END SELECT":
                depth -= 1
                if depth == 0:
                    self.interpreter.select_stack.pop()
                    break
            self.interpreter.current_line += 1
        return "continue"

    def _skip_to_next_case(self):
        self.interpreter.current_line += 1
        while self.interpreter.current_line < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[self.interpreter.current_line]
            upper_lt = lt.strip().upper()
            if upper_lt.startswith("CASE") or upper_lt == "END SELECT":
                self.interpreter.current_line -= 1  # Will be incremented by main loop
                break
            self.interpreter.current_line += 1
        return "continue"

    # --- BASIC SWAP ---

    def _basic_swap(self, command):
        """SWAP var1, var2"""
        text = re.sub(r'^SWAP\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip().upper() for p in text.split(",")]
        if len(parts) == 2:
            v1 = self.interpreter.variables.get(parts[0], 0)
            v2 = self.interpreter.variables.get(parts[1], 0)
            self.interpreter.variables[parts[0]] = v2
            self.interpreter.variables[parts[1]] = v1
        return "continue"

    # --- BASIC INCR / DECR ---

    def _basic_incr_decr(self, command, direction):
        """INCR var [, amount]  or  DECR var [, amount]"""
        text = re.sub(r'^(INCR|DECR)\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in text.split(",")]
        var_name = parts[0].upper()
        amount = 1
        if len(parts) > 1:
            try:
                amount = float(self.interpreter.evaluate_expression(parts[1]))
            except Exception:
                amount = 1
        current = float(self.interpreter.variables.get(var_name, 0))
        new_val = current + (amount * direction)
        self.interpreter.variables[var_name] = int(new_val) if new_val == int(new_val) else new_val
        return "continue"

    # --- BASIC math/string functions (as statements) ---

    def _basic_math_func(self, command):
        """Handle math function calls as print statements."""
        self.interpreter.log_output(str(self._eval_basic_expression(command)))
        return "continue"

    def _basic_string_func(self, command):
        """Handle string function calls as print statements."""
        self.interpreter.log_output(str(self._eval_basic_expression(command)))
        return "continue"

    # ==================================================================
    #  New BASIC commands (ELSEIF, ON, BEEP, TAB, SPC)
    # ==================================================================

    def _basic_elseif(self, command):
        """ELSEIF condition THEN statement — mid-block branch.

        Reached when a preceding IF/ELSEIF block was executed, so we
        need to skip ahead to END IF (same logic as ELSE).
        """
        # If we reach here normally, the prior IF/ELSEIF was true –
        # skip to END IF.
        depth = 1
        self.interpreter.current_line += 1
        while self.interpreter.current_line < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[self.interpreter.current_line]
            lu = lt.strip().upper()
            if lu.startswith("IF ") and (lu.endswith("THEN") or " THEN " in lu):
                depth += 1
            elif lu in ("END IF", "ENDIF"):
                depth -= 1
                if depth == 0:
                    return "continue"
            self.interpreter.current_line += 1
        return "continue"

    def _basic_on(self, command):
        """ON expr GOTO label1,label2,...  or  ON expr GOSUB label1,label2,..."""
        m = re.match(r'ON\s+(.+?)\s+(GOTO|GOSUB)\s+(.*)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("ON syntax: ON expr GOTO/GOSUB target1, target2, ...")
            return "continue"
        expr_val = int(float(self._eval_basic_expression(m.group(1).strip())))
        mode = m.group(2).upper()
        targets = [t.strip() for t in m.group(3).split(",")]
        if expr_val < 1 or expr_val > len(targets):
            return "continue"  # out of range – fall through
        target = targets[expr_val - 1]
        if mode == "GOSUB":
            return self._basic_gosub(f"GOSUB {target}")
        else:
            return self._basic_goto(f"GOTO {target}")

    def _basic_beep(self):
        """BEEP — emit a system bell."""
        try:
            print("\a", end="", flush=True)
        except Exception:
            pass
        return "continue"

    def _basic_tab(self, command):
        """TAB n — print spaces to move to column n."""
        parts = command.split()
        n = int(float(self._eval_basic_expression(parts[1]))) if len(parts) > 1 else 8
        self.interpreter.log_output(" " * n, end="")
        return "continue"

    def _basic_spc(self, command):
        """SPC n — print n spaces."""
        parts = command.split()
        n = int(float(self._eval_basic_expression(parts[1]))) if len(parts) > 1 else 1
        self.interpreter.log_output(" " * n, end="")
        return "continue"

    # ==================================================================
    #  Logo LABEL command
    # ==================================================================

    def _logo_label(self, parts):
        """LABEL \"text\" [size]  or  LABEL expr [size] — draw text at turtle position."""
        self._ensure_turtle()
        raw = " ".join(parts[1:]).strip()
        size = 12
        # Check for trailing number as font size
        tokens = raw.rsplit(None, 1)
        if len(tokens) == 2:
            try:
                size = int(tokens[1])
                raw = tokens[0]
            except ValueError:
                pass
        # Quoted string literal → use as-is
        if raw.startswith('"') and raw.endswith('"'):
            text = raw[1:-1]
        elif raw.startswith("'") and raw.endswith("'"):
            text = raw[1:-1]
        else:
            # Evaluate as expression (variable name, function call, etc.)
            try:
                text = str(self._eval_basic_expression(raw))
            except Exception:
                text = raw
        self.interpreter.turtle_text(text, size)
        return "continue"

    # ==================================================================
    #  Expression evaluation helpers
    # ==================================================================

    def _eval_basic_expression(self, expr):  # noqa: C901
        """Evaluate a BASIC expression (string or numeric)."""
        expr = expr.strip()
        if not expr:
            return ""

        # String literal — must be a single properly closed string like "hello".
        # Reject compound expressions that start AND end with " but contain
        # concatenation in between, e.g. "[" + TOSTR(S) + "]".
        if expr.startswith('"') and len(expr) >= 2:
            close_pos = expr.index('"', 1)   # position of the matching close quote
            if close_pos == len(expr) - 1:
                return expr[1:-1]
            # else: opening quote closes before the end — it's a concat expression

        # String concatenation with +
        if '"' in expr and '+' in expr:
            parts = self._split_string_concat(expr)
            if len(parts) > 1:  # only concat when the expression actually splits
                return "".join(str(self._eval_basic_expression(p.strip())) for p in parts)

        # Variable reference (including A$ string vars)
        if re.match(r'^[A-Za-z_]\w*\$?$', expr):
            var_name = expr.upper()
            # Pseudo-variables take priority over regular variables
            if var_name == "TIMER":
                return round(time.time() - self.interpreter._program_start_time, 3)  # pylint: disable=protected-access
            if var_name == "DATE$":
                import datetime as _dt
                return _dt.date.today().isoformat()
            if var_name == "TIME$":
                import datetime as _dt
                return _dt.datetime.now().strftime("%H:%M:%S")
            # Check user-assigned variables first; fall back to math constants.
            # Use `in` check (not truthiness) so that variables set to 0 or ""
            # are returned correctly rather than falling through to a constant.
            if var_name in self.interpreter.variables:
                return self.interpreter.variables[var_name]
            # Mathematical constants (only when not shadowed by a user variable)
            if var_name == "PI":
                return math.pi
            if var_name == "E":
                return math.e
            if var_name == "TAU":
                return math.tau
            if var_name == "INF":
                return float("inf")
            return 0

        # BASIC built-in functions
        upper_expr = expr.upper()

        # TIMER pseudo-variable
        if upper_expr == "TIMER":
            return round(time.time() - self.interpreter._program_start_time, 3)  # pylint: disable=protected-access

        # DATE$ and TIME$ pseudo-variables
        if upper_expr == "DATE$":
            import datetime as _dt
            return _dt.date.today().isoformat()
        if upper_expr == "TIME$":
            import datetime as _dt
            return _dt.datetime.now().strftime("%H:%M:%S")

        # TYPE() function
        type_match = re.match(r'^TYPE\((.+)\)$', upper_expr)
        if type_match:
            val = self._eval_basic_expression(type_match.group(1))
            if isinstance(val, str):
                return "STRING"
            elif isinstance(val, (int, float)):
                return "NUMBER"
            elif isinstance(val, (list, dict)):
                return "ARRAY"
            return "UNKNOWN"

        # RND function
        rnd_match = re.match(r'^RND(?:\(([^)]*)\))?$', upper_expr)
        if rnd_match:
            arg = rnd_match.group(1)
            if arg:
                n = int(float(self.interpreter.evaluate_expression(arg)))
                return random.randint(1, max(1, n))
            return random.random()

        # INT function — standard BASIC INT() is the floor function
        int_match = re.match(r'^INT\((.+)\)$', upper_expr)
        if int_match:
            return math.floor(float(self._eval_basic_expression(int_match.group(1))))

        # ABS function — return int when result is a whole number
        abs_match = re.match(r'^ABS\((.+)\)$', upper_expr)
        if abs_match:
            v = abs(float(self._eval_basic_expression(abs_match.group(1))))
            return int(v) if v == int(v) else v

        # SQRT function
        sqrt_match = re.match(r'^SQRT?\((.+)\)$', upper_expr)
        if sqrt_match:
            return math.sqrt(float(self._eval_basic_expression(sqrt_match.group(1))))

        # Trig functions
        for fn, func in [("SIN", math.sin), ("COS", math.cos), ("TAN", math.tan), ("ATN", math.atan), ("ATAN", math.atan)]:
            fn_match = re.match(rf'^{fn}\((.+)\)$', upper_expr)
            if fn_match:
                return func(float(self._eval_basic_expression(fn_match.group(1))))

        # LOG, EXP
        log_match = re.match(r'^LOG\((.+)\)$', upper_expr)
        if log_match:
            return math.log(float(self._eval_basic_expression(log_match.group(1))))
        exp_match = re.match(r'^EXP\((.+)\)$', upper_expr)
        if exp_match:
            return math.exp(float(self._eval_basic_expression(exp_match.group(1))))

        # CEIL function
        ceil_match = re.match(r'^CEIL\((.+)\)$', upper_expr)
        if ceil_match:
            return math.ceil(float(self._eval_basic_expression(ceil_match.group(1))))

        # FIX function (truncate toward zero)
        fix_match = re.match(r'^FIX\((.+)\)$', upper_expr)
        if fix_match:
            val = float(self._eval_basic_expression(fix_match.group(1)))
            return int(val) if val >= 0 else -int(-val)

        # String functions
        len_match = re.match(r'^LEN\((.+)\)$', upper_expr)
        if len_match:
            return len(str(self._eval_basic_expression(len_match.group(1))))

        # String functions — use re.IGNORECASE on the original expr so that
        # string literals inside arguments are NOT uppercased.
        mid_match = re.match(r'^MID\$?\((.+),\s*(.+),\s*(.+)\)$', expr, re.IGNORECASE)
        if mid_match:
            s = str(self._eval_basic_expression(mid_match.group(1)))
            start = int(float(self._eval_basic_expression(mid_match.group(2)))) - 1
            length = int(float(self._eval_basic_expression(mid_match.group(3))))
            return s[start:start + length]

        left_match = re.match(r'^LEFT\$?\((.+),\s*(.+)\)$', expr, re.IGNORECASE)
        if left_match:
            s = str(self._eval_basic_expression(left_match.group(1)))
            n = int(float(self._eval_basic_expression(left_match.group(2))))
            return s[:n]

        right_match = re.match(r'^RIGHT\$?\((.+),\s*(.+)\)$', expr, re.IGNORECASE)
        if right_match:
            s = str(self._eval_basic_expression(right_match.group(1)))
            n = int(float(self._eval_basic_expression(right_match.group(2))))
            return s[-n:] if n > 0 else ""

        chr_match = re.match(r'^CHR\$?\((.+)\)$', expr, re.IGNORECASE)
        if chr_match:
            return chr(int(float(self._eval_basic_expression(chr_match.group(1)))))

        asc_match = re.match(r'^ASC\((.+)\)$', expr, re.IGNORECASE)
        if asc_match:
            s = str(self._eval_basic_expression(asc_match.group(1)))
            return ord(s[0]) if s else 0

        str_match = re.match(r'^STR\$?\((.+)\)$', expr, re.IGNORECASE)
        if str_match:
            return str(self._eval_basic_expression(str_match.group(1)))

        val_match = re.match(r'^VAL\((.+)\)$', expr, re.IGNORECASE)
        if val_match:
            v = self._eval_basic_expression(val_match.group(1))
            try:
                f = float(v)
                return int(f) if f == int(f) else f
            except (ValueError, TypeError):
                return 0

        ucase_match = re.match(r'^UCASE\$?\((.+)\)$', expr, re.IGNORECASE)
        if ucase_match:
            return str(self._eval_basic_expression(ucase_match.group(1))).upper()

        lcase_match = re.match(r'^LCASE\$?\((.+)\)$', expr, re.IGNORECASE)
        if lcase_match:
            return str(self._eval_basic_expression(lcase_match.group(1))).lower()

        instr_match = re.match(r'^INSTR\((.+),\s*(.+)\)$', expr, re.IGNORECASE)
        if instr_match:
            haystack = str(self._eval_basic_expression(instr_match.group(1)))
            needle = str(self._eval_basic_expression(instr_match.group(2)))
            pos = haystack.find(needle)
            return pos + 1 if pos >= 0 else 0

        # Try extended expression evaluator for modern features (TOSTR, TONUM,
        # ROUND, FORMAT$, HASKEY, LENGTH, etc.) BEFORE the generic arr_match
        # fallback so those built-ins are never mistaken for array accesses.
        ext_result = self._eval_basic_expression_extended(expr)
        if ext_result is not expr:  # extended evaluator handled it
            return ext_result

        # Array access / user-defined function call: name(args) or name()
        arr_match = re.match(r'^(\w+)\((.*)\)$', expr)
        if arr_match:
            arr_name = arr_match.group(1).upper()
            # Check if this is a user-defined function call
            if arr_name in self.interpreter.function_definitions:
                defn = self.interpreter.function_definitions[arr_name]
                # Use _smart_split to correctly handle nested calls like f(g(x, y), z)
                raw_args = arr_match.group(2).strip()
                args = [a.strip() for a in self._smart_split(raw_args, ",")] if raw_args else []
                if defn.get("is_lambda"):
                    return self._apply_func(arr_name, [self._eval_basic_expression(a) for a in args])
                else:
                    self._execute_sub_or_function(arr_name, defn, args)
                    return self.interpreter.return_value if self.interpreter.return_value is not None else 0
            # Fall back to DIM array access: ARRAY(index)
            try:
                idx = int(float(self.interpreter.evaluate_expression(arr_match.group(2))))
                if arr_name in self.arrays:
                    if 0 <= idx < len(self.arrays[arr_name]):
                        return self.arrays[arr_name][idx]
                # Check interpreter variables (e.g. DIM stored as "NAME(idx)")
                return self.interpreter.variables.get(f"{arr_name}({idx})", 0)
            except (TypeError, ValueError):
                pass

        # Pre-substitute user-defined function calls in compound expressions
        # (e.g. "N * FACT(N - 1)") before handing off to evaluate_expression.
        _subst = expr
        for _fn_name in self.interpreter.function_definitions:
            if _fn_name.upper() + "(" in _subst.upper():
                _subst = re.sub(
                    rf'\b{re.escape(_fn_name)}\s*\(([^()]*)\)',
                    lambda m, fn=_fn_name: str(self._eval_basic_expression(
                        f"{fn}({m.group(1)})"
                    )),
                    _subst,
                    flags=re.IGNORECASE,
                )
        # If the expression contains a bare = (BASIC equality test) or <>,
        # those would cause Python SyntaxError inside eval(); route them through
        # _eval_basic_condition which handles BASIC comparisons natively.
        _has_bare_eq = bool(re.search(r'(?<![=<>!])=(?!=)', _subst))
        _has_neq = '<>' in _subst
        if _has_bare_eq or _has_neq:
            try:
                return 1 if self._eval_basic_condition(_subst) else 0
            except Exception:
                pass
        # Fall through to interpreter's evaluate_expression
        try:
            return self.interpreter.evaluate_expression(_subst)
        except Exception:
            pass
        # Last resort: try interpreting the expression as a boolean condition
        # (handles cases like "N MOD 2 = 0" used in a RETURN or LET context)
        try:
            return 1 if self._eval_basic_condition(expr) else 0
        except Exception:
            return expr

    def _split_string_concat(self, expr):
        """Split a string concatenation expression respecting quotes."""
        parts = []
        current = []
        in_string = False
        for ch in expr:
            if ch == '"':
                in_string = not in_string
                current.append(ch)
            elif ch == '+' and not in_string:
                parts.append(''.join(current))
                current = []
            else:
                current.append(ch)
        if current:
            parts.append(''.join(current))
        return parts

    def _eval_basic_condition(self, condition):
        """Evaluate a BASIC condition to True/False."""
        condition = condition.strip()

        # Handle AND / OR
        if ' AND ' in condition.upper():
            parts = re.split(r'\bAND\b', condition, flags=re.IGNORECASE)
            return all(self._eval_basic_condition(p) for p in parts)
        if ' OR ' in condition.upper():
            parts = re.split(r'\bOR\b', condition, flags=re.IGNORECASE)
            return any(self._eval_basic_condition(p) for p in parts)
        if condition.upper().startswith("NOT "):
            return not self._eval_basic_condition(condition[4:])

        # Comparison operators
        for op, func in [
            ("<>", lambda a, b: a != b),
            ("<=", lambda a, b: a <= b),
            (">=", lambda a, b: a >= b),
            ("!=", lambda a, b: a != b),
            ("==", lambda a, b: a == b),
            ("<", lambda a, b: a < b),
            (">", lambda a, b: a > b),
            ("=", lambda a, b: a == b),
        ]:
            if op in condition:
                left, right = condition.split(op, 1)
                left_val = self._eval_basic_expression(left.strip())
                right_val = self._eval_basic_expression(right.strip())
                try:
                    return func(float(left_val), float(right_val))
                except (ValueError, TypeError):
                    return func(str(left_val), str(right_val))

        # Truthy evaluation
        val = self._eval_basic_expression(condition)
        return bool(val)

    # ==================================================================
    #  MODERN LANGUAGE EXTENSIONS
    # ==================================================================
    #
    #  These features transform TempleCode from a purely educational
    #  language into a practical, modern programming language while
    #  retaining its accessible BASIC-family syntax.
    #

    # ------------------------------------------------------------------
    #  SUB / FUNCTION — Structured procedures with parameters & locals
    # ------------------------------------------------------------------

    def _modern_sub_define(self, command):
        """SUB name(param1, param2, ...)
        Collects lines until END SUB. Subs don't return values."""
        m = re.match(r'SUB\s+(\w+)\s*\(([^)]*)\)', command, re.IGNORECASE)
        if not m:
            # SUB with no params: SUB name
            m2 = re.match(r'SUB\s+(\w+)', command, re.IGNORECASE)
            if m2:
                name = m2.group(1).upper()
                params = []
            else:
                self.interpreter.log_output("SUB syntax: SUB name(params)")
                return "continue"
        else:
            name = m.group(1).upper()
            params = [p.strip().upper() for p in m.group(2).split(",") if p.strip()]

        # Collect body lines until END SUB
        body_start = self.interpreter.current_line + 1
        depth = 1
        self.interpreter.current_line += 1
        while self.interpreter.current_line < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[self.interpreter.current_line]
            lu = lt.strip().upper()
            if lu.startswith("SUB ") or lu.startswith("FUNCTION "):
                depth += 1
            elif lu == "END SUB" or lu == "END FUNCTION":
                depth -= 1
                if depth == 0:
                    break
            self.interpreter.current_line += 1

        body_end = self.interpreter.current_line
        self.interpreter.sub_definitions[name] = {
            "params": params,
            "body_start": body_start,
            "body_end": body_end,
        }
        return "continue"

    def _modern_function_define(self, command):
        """FUNCTION name(param1, param2, ...)
        Collects lines until END FUNCTION. Use RETURN expr to return a value."""
        m = re.match(r'FUNCTION\s+(\w+)\s*\(([^)]*)\)', command, re.IGNORECASE)
        if not m:
            m2 = re.match(r'FUNCTION\s+(\w+)', command, re.IGNORECASE)
            if m2:
                name = m2.group(1).upper()
                params = []
            else:
                self.interpreter.log_output("FUNCTION syntax: FUNCTION name(params)")
                return "continue"
        else:
            name = m.group(1).upper()
            params = [p.strip().upper() for p in m.group(2).split(",") if p.strip()]

        body_start = self.interpreter.current_line + 1
        depth = 1
        self.interpreter.current_line += 1
        while self.interpreter.current_line < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[self.interpreter.current_line]
            lu = lt.strip().upper()
            if lu.startswith("SUB ") or lu.startswith("FUNCTION "):
                depth += 1
            elif lu == "END SUB" or lu == "END FUNCTION":
                depth -= 1
                if depth == 0:
                    break
            self.interpreter.current_line += 1

        body_end = self.interpreter.current_line
        self.interpreter.function_definitions[name] = {
            "params": params,
            "body_start": body_start,
            "body_end": body_end,
        }
        return "continue"

    def _modern_call(self, command):
        """CALL sub_name(arg1, arg2, ...)
        or CALL sub_name arg1, arg2"""
        text = re.sub(r'^CALL\s+', '', command, flags=re.IGNORECASE).strip()

        # Parse name and arguments
        m = re.match(r'(\w+)\s*\(([^)]*)\)', text)
        if m:
            name = m.group(1).upper()
            arg_str = m.group(2)
        else:
            parts = text.split(None, 1)
            name = parts[0].upper()
            arg_str = parts[1] if len(parts) > 1 else ""

        args = [a.strip() for a in arg_str.split(",") if a.strip()] if arg_str else []

        # Look up in sub_definitions or function_definitions
        defn = self.interpreter.sub_definitions.get(name) or self.interpreter.function_definitions.get(name)
        if not defn:
            self.interpreter.log_output(f"Undefined SUB/FUNCTION: {name}")
            return "continue"

        return self._execute_sub_or_function(name, defn, args)

    def _execute_sub_or_function(self, name, defn, args):
        """Execute a SUB or FUNCTION by running its body lines."""
        params = defn["params"]
        body_start = defn["body_start"]
        body_end = defn["body_end"]

        # Save caller state
        saved_vars = {}
        saved_lists = {}
        for i, param in enumerate(params):
            saved_vars[param] = self.interpreter.variables.get(param)
            saved_lists[param] = self.interpreter.lists.get(param)
            if i < len(args):
                val = self._eval_basic_expression(args[i])
                self.interpreter.variables[param] = val
                # If the arg is a list name, also bind the list under the param name
                arg_upper = str(args[i]).strip().upper()
                if arg_upper in self.interpreter.lists:
                    self.interpreter.lists[param] = self.interpreter.lists[arg_upper]

        # Save execution position
        self.interpreter.call_stack.append({
            "return_line": self.interpreter.current_line,
            "saved_vars": saved_vars,
            "saved_lists": saved_lists,
            "params": params,
        })

        # Execute body lines
        self.interpreter.return_value = None
        self.interpreter.current_line = body_start

        while self.interpreter.current_line < body_end:
            _, cmd = self.interpreter.program_lines[self.interpreter.current_line]
            cmd = cmd.strip()
            if not cmd:
                self.interpreter.current_line += 1
                continue

            result = self.execute_command(cmd)
            if result == "return" or result == "end":
                break
            if result == "jump":
                continue
            self.interpreter.current_line += 1

        # Restore caller state
        frame = self.interpreter.call_stack.pop()
        for param in frame["params"]:
            if frame["saved_vars"].get(param) is not None:
                self.interpreter.variables[param] = frame["saved_vars"][param]
            elif param in self.interpreter.variables:
                del self.interpreter.variables[param]
            # Restore list binding
            if frame.get("saved_lists", {}).get(param) is not None:
                self.interpreter.lists[param] = frame["saved_lists"][param]
            elif param in self.interpreter.lists:
                del self.interpreter.lists[param]

        self.interpreter.current_line = frame["return_line"]
        return "continue"

    def _modern_return(self, command):
        """RETURN [expression]
        In a FUNCTION, returns a value. In a SUB, just exits.
        Falls back to BASIC RETURN (GOSUB) if not in a SUB/FUNCTION."""
        text = re.sub(r'^RETURN\s*', '', command, flags=re.IGNORECASE).strip()

        # If we're inside a SUB/FUNCTION call
        if self.interpreter.call_stack:
            if text:
                self.interpreter.return_value = self._eval_basic_expression(text)
                self.interpreter.variables["RESULT"] = self.interpreter.return_value
            return "return"

        # Fall back to BASIC GOSUB RETURN
        return self._basic_return()

    # ------------------------------------------------------------------
    #  LIST — Dynamic arrays / lists
    # ------------------------------------------------------------------

    def _modern_list(self, command):
        """LIST name = val1, val2, val3   or   LIST name
        Creates a list (dynamic array)."""
        text = re.sub(r'^LIST\s+', '', command, flags=re.IGNORECASE).strip()

        if "=" in text:
            name, _, vals_str = text.partition("=")
            name = name.strip().upper()
            vals = []
            for v in self._smart_split(vals_str.strip(), ","):
                v = v.strip()
                vals.append(self._eval_basic_expression(v))
            self.interpreter.lists[name] = vals
        else:
            name = text.strip().upper()
            self.interpreter.lists[name] = []
        return "continue"

    def _modern_split_stmt(self, command):
        """SPLIT expr, delimiter INTO list_name
        Statement form of the SPLIT expression function."""
        text = re.sub(r'^SPLIT\s+', '', command, flags=re.IGNORECASE).strip()
        m = re.match(r'(.+?),\s*(".*?"|\'.*?\'|\S+)\s+INTO\s+(\w+)', text, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("SPLIT syntax: SPLIT expr, delimiter INTO list_name")
            return "continue"
        src = str(self._eval_basic_expression(m.group(1).strip()))
        delim = str(self._eval_basic_expression(m.group(2).strip()))
        list_name = m.group(3).upper()
        result = src.split(delim)
        self.interpreter.lists[list_name] = result
        self.interpreter.variables[list_name] = result
        self.interpreter.variables[list_name + "_LENGTH"] = len(result)
        return "continue"

    def _modern_join_stmt(self, command):
        """JOIN list_name, delimiter INTO result_var
        Statement form of the JOIN expression function."""
        text = re.sub(r'^JOIN\s+', '', command, flags=re.IGNORECASE).strip()
        m = re.match(r'(\w+),\s*(".*?"|\'.*?\'|\S+)\s+INTO\s+(\w+)', text, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("JOIN syntax: JOIN list_name, delimiter INTO result_var")
            return "continue"
        list_name = m.group(1).upper()
        delim = str(self._eval_basic_expression(m.group(2).strip()))
        result_var = m.group(3).upper()
        lst = self.interpreter.lists.get(list_name, [])
        self.interpreter.variables[result_var] = delim.join(str(x) for x in lst)
        return "continue"

    def _modern_push(self, command):
        """PUSH list_name, value [, value ...]"""
        text = re.sub(r'^PUSH\s+', '', command, flags=re.IGNORECASE).strip()
        parts = self._smart_split(text, ",")
        if len(parts) < 2:
            self.interpreter.log_output("PUSH syntax: PUSH list, value")
            return "continue"
        name = parts[0].strip().upper()
        if name not in self.interpreter.lists:
            self.interpreter.lists[name] = []
        for v in parts[1:]:
            self.interpreter.lists[name].append(self._eval_basic_expression(v.strip()))
        self.interpreter.variables[name + "_LENGTH"] = len(self.interpreter.lists[name])
        return "continue"

    def _modern_pop(self, command):
        """POP list_name [, var_name]  — remove last element, optionally store it."""
        text = re.sub(r'^POP\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in text.split(",")]
        name = parts[0].upper()
        if name not in self.interpreter.lists or not self.interpreter.lists[name]:
            self.interpreter.log_output(f"POP: list '{name}' is empty or undefined")
            return "continue"
        val = self.interpreter.lists[name].pop()
        if len(parts) > 1:
            self.interpreter.variables[parts[1].upper()] = val
        self.interpreter.variables[name + "_LENGTH"] = len(self.interpreter.lists[name])
        return "continue"

    def _modern_shift(self, command):
        """SHIFT list_name [, var_name]  — remove first element."""
        text = re.sub(r'^SHIFT\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in text.split(",")]
        name = parts[0].upper()
        if name not in self.interpreter.lists or not self.interpreter.lists[name]:
            self.interpreter.log_output(f"SHIFT: list '{name}' is empty or undefined")
            return "continue"
        val = self.interpreter.lists[name].pop(0)
        if len(parts) > 1:
            self.interpreter.variables[parts[1].upper()] = val
        self.interpreter.variables[name + "_LENGTH"] = len(self.interpreter.lists[name])
        return "continue"

    def _modern_unshift(self, command):
        """UNSHIFT list_name, value  — prepend to list."""
        text = re.sub(r'^UNSHIFT\s+', '', command, flags=re.IGNORECASE).strip()
        parts = self._smart_split(text, ",")
        if len(parts) < 2:
            self.interpreter.log_output("UNSHIFT syntax: UNSHIFT list, value")
            return "continue"
        name = parts[0].strip().upper()
        if name not in self.interpreter.lists:
            self.interpreter.lists[name] = []
        for v in reversed(parts[1:]):
            self.interpreter.lists[name].insert(0, self._eval_basic_expression(v.strip()))
        self.interpreter.variables[name + "_LENGTH"] = len(self.interpreter.lists[name])
        return "continue"

    def _modern_sort(self, command):
        """SORT list_name [DESC]"""
        text = re.sub(r'^SORT\s+', '', command, flags=re.IGNORECASE).strip()
        desc = False
        if text.upper().endswith(" DESC"):
            desc = True
            text = text[:-5].strip()
        name = text.upper()
        if name in self.interpreter.lists:
            try:
                self.interpreter.lists[name].sort(
                    key=lambda x: (0, float(x)) if isinstance(x, (int, float)) else (1, str(x)),
                    reverse=desc
                )
            except Exception:
                self.interpreter.lists[name].sort(key=str, reverse=desc)
        return "continue"

    def _modern_reverse(self, command):
        """REVERSE list_name"""
        text = re.sub(r'^REVERSE\s+', '', command, flags=re.IGNORECASE).strip()
        name = text.upper()
        if name in self.interpreter.lists:
            self.interpreter.lists[name].reverse()
        return "continue"

    def _modern_splice(self, command):
        """SPLICE list_name, start, count [, val1, val2, ...]"""
        text = re.sub(r'^SPLICE\s+', '', command, flags=re.IGNORECASE).strip()
        parts = self._smart_split(text, ",")
        if len(parts) < 3:
            self.interpreter.log_output("SPLICE syntax: SPLICE list, start, count [, insertvals...]")
            return "continue"
        name = parts[0].strip().upper()
        start = int(float(self._eval_basic_expression(parts[1].strip())))
        count = int(float(self._eval_basic_expression(parts[2].strip())))
        inserts = [self._eval_basic_expression(p.strip()) for p in parts[3:]]
        if name in self.interpreter.lists:
            del self.interpreter.lists[name][start:start + count]
            for i, v in enumerate(inserts):
                self.interpreter.lists[name].insert(start + i, v)
            self.interpreter.variables[name + "_LENGTH"] = len(self.interpreter.lists[name])
        return "continue"

    # ------------------------------------------------------------------
    #  DICT — Dictionaries / hashmaps
    # ------------------------------------------------------------------

    def _modern_dict(self, command):
        """DICT name   or   DICT name = key1:val1, key2:val2"""
        text = re.sub(r'^DICT\s+', '', command, flags=re.IGNORECASE).strip()
        if "=" in text:
            name, _, vals_str = text.partition("=")
            name = name.strip().upper()
            d = {}
            for kv in self._smart_split(vals_str.strip(), ","):
                if ":" in kv:
                    k, _, v = kv.partition(":")
                    d[self._eval_basic_expression(k.strip())] = self._eval_basic_expression(v.strip())
            self.interpreter.dicts[name] = d
        else:
            name = text.strip().upper()
            self.interpreter.dicts[name] = {}
        return "continue"

    def _modern_set(self, command):
        """SET dict_name, key, value   or   SET dict_name.key = value"""
        text = re.sub(r'^SET\s+', '', command, flags=re.IGNORECASE).strip()

        # SET dict.key = value
        dot_m = re.match(r'(\w+)\.(\w+)\s*=\s*(.*)', text)
        if dot_m:
            name = dot_m.group(1).upper()
            key = dot_m.group(2)
            val = self._eval_basic_expression(dot_m.group(3).strip())
            if name not in self.interpreter.dicts:
                self.interpreter.dicts[name] = {}
            self.interpreter.dicts[name][key] = val
            return "continue"

        # SET dict, key, value
        parts = self._smart_split(text, ",")
        if len(parts) >= 3:
            name = parts[0].strip().upper()
            key = self._eval_basic_expression(parts[1].strip())
            val = self._eval_basic_expression(parts[2].strip())
            if name not in self.interpreter.dicts:
                self.interpreter.dicts[name] = {}
            self.interpreter.dicts[name][key] = val
        return "continue"

    def _modern_get(self, command):
        """GET dict_name, key, result_var   or   GET dict.key INTO var"""
        text = re.sub(r'^GET\s+', '', command, flags=re.IGNORECASE).strip()

        # GET dict.key INTO var
        dot_m = re.match(r'(\w+)\.(\w+)\s+INTO\s+(\w+)', text, re.IGNORECASE)
        if dot_m:
            name = dot_m.group(1).upper()
            key = dot_m.group(2)
            var = dot_m.group(3).upper()
            if name in self.interpreter.dicts:
                self.interpreter.variables[var] = self.interpreter.dicts[name].get(key, "")
            return "continue"

        # GET dict, key, var
        parts = self._smart_split(text, ",")
        if len(parts) >= 3:
            name = parts[0].strip().upper()
            key = self._eval_basic_expression(parts[1].strip())
            var = parts[2].strip().upper()
            if name in self.interpreter.dicts:
                self.interpreter.variables[var] = self.interpreter.dicts[name].get(key, "")
            else:
                self.interpreter.variables[var] = ""
        return "continue"

    def _modern_delete(self, command):
        """DELETE dict_name, key   or   DELETE dict.key"""
        text = re.sub(r'^DELETE\s+', '', command, flags=re.IGNORECASE).strip()
        dot_m = re.match(r'(\w+)\.(\w+)', text)
        if dot_m:
            name = dot_m.group(1).upper()
            key = dot_m.group(2)
            if name in self.interpreter.dicts:
                self.interpreter.dicts[name].pop(key, None)
            return "continue"

        parts = self._smart_split(text, ",")
        if len(parts) >= 2:
            name = parts[0].strip().upper()
            key = self._eval_basic_expression(parts[1].strip())
            if name in self.interpreter.dicts:
                self.interpreter.dicts[name].pop(key, None)
        return "continue"

    # ------------------------------------------------------------------
    #  FILE I/O
    # ------------------------------------------------------------------

    def _modern_open(self, command):
        """OPEN "filename" FOR INPUT|OUTPUT|APPEND AS #n"""
        m = re.match(
            r'OPEN\s+"([^"]+)"\s+FOR\s+(INPUT|OUTPUT|APPEND)\s+AS\s+#?(\d+)',
            command, re.IGNORECASE
        )
        if not m:
            self.interpreter.log_output('OPEN syntax: OPEN "file" FOR INPUT|OUTPUT|APPEND AS #n')
            return "continue"
        filename = m.group(1)
        mode_str = m.group(2).upper()
        handle = int(m.group(3))
        mode_map = {"INPUT": "r", "OUTPUT": "w", "APPEND": "a"}
        try:
            self.interpreter.file_handles[handle] = open(filename, mode_map[mode_str], encoding="utf-8")
        except Exception as e:
            self.interpreter.log_output(f"File error: {e}")
        return "continue"

    def _modern_close(self, command):
        """CLOSE #n   or   CLOSE ALL"""
        text = re.sub(r'^CLOSE\s+', '', command, flags=re.IGNORECASE).strip()
        if text.upper() == "ALL":
            for fh in self.interpreter.file_handles.values():
                try:
                    fh.close()
                except Exception:
                    pass
            self.interpreter.file_handles.clear()
        else:
            handle = int(text.lstrip("#"))
            if handle in self.interpreter.file_handles:
                try:
                    self.interpreter.file_handles[handle].close()
                except Exception:
                    pass
                del self.interpreter.file_handles[handle]
        return "continue"

    def _modern_readline(self, command):
        """READLINE #n, var_name   — read one line from file"""
        text = re.sub(r'^READLINE\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in text.split(",")]
        if len(parts) < 2:
            self.interpreter.log_output("READLINE syntax: READLINE #n, variable")
            return "continue"
        handle = int(parts[0].lstrip("#"))
        var = parts[1].upper()
        fh = self.interpreter.file_handles.get(handle)
        if fh:
            line = fh.readline()
            if line:
                self.interpreter.variables[var] = line.rstrip("\n\r")
                self.interpreter.variables["EOF"] = 0
            else:
                self.interpreter.variables[var] = ""
                self.interpreter.variables["EOF"] = 1
        return "continue"

    def _modern_writeline(self, command):
        """WRITELINE #n, expression"""
        text = re.sub(r'^WRITELINE\s+', '', command, flags=re.IGNORECASE).strip()
        parts = self._smart_split(text, ",")
        if len(parts) < 2:
            self.interpreter.log_output("WRITELINE syntax: WRITELINE #n, expression")
            return "continue"
        handle = int(parts[0].strip().lstrip("#"))
        val = self._eval_basic_expression(",".join(parts[1:]).strip())
        fh = self.interpreter.file_handles.get(handle)
        if fh:
            fh.write(str(val) + "\n")
        return "continue"

    def _modern_readfile(self, command):
        """READFILE "filename", var_name -- read entire file into variable"""
        m = re.match(r'READFILE\s+"([^"]+)"\s*,\s*(\w+)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output('READFILE syntax: READFILE "file", variable')
            return "continue"
        filename = m.group(1)
        var = m.group(2).upper()
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.interpreter.variables[var] = f.read()
        except Exception as e:
            self.interpreter.log_error(f"File error: {e}")
            self.interpreter.variables[var] = ""
        return "continue"

    def _modern_writefile(self, command):
        """WRITEFILE "filename", expression"""
        m = re.match(r'WRITEFILE\s+"([^"]+)"\s*,\s*(.*)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output('WRITEFILE syntax: WRITEFILE "file", expression')
            return "continue"
        filename = m.group(1)
        val = self._eval_basic_expression(m.group(2).strip())
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(val))
        except Exception as e:
            self.interpreter.log_output(f"File error: {e}")
        return "continue"

    def _modern_appendfile(self, command):
        """APPENDFILE "filename", expression"""
        m = re.match(r'APPENDFILE\s+"([^"]+)"\s*,\s*(.*)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output('APPENDFILE syntax: APPENDFILE "file", expression')
            return "continue"
        filename = m.group(1)
        val = self._eval_basic_expression(m.group(2).strip())
        try:
            with open(filename, "a", encoding="utf-8") as f:
                f.write(str(val) + "\n")
        except Exception as e:
            self.interpreter.log_output(f"File error: {e}")
        return "continue"

    # ------------------------------------------------------------------
    #  TRY / CATCH / THROW — Error handling
    # ------------------------------------------------------------------

    def _modern_try(self, _command):
        """TRY — begin error-protected block. Errors jump to CATCH."""
        self.interpreter.try_stack.append({
            "try_line": self.interpreter.current_line,
            "catch_line": None,
            "end_line": None,
        })
        # Scan ahead for CATCH and END TRY
        scan = self.interpreter.current_line + 1
        depth = 1
        while scan < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[scan]
            lu = lt.strip().upper()
            if lu == "TRY":
                depth += 1
            elif lu.startswith("CATCH") and depth == 1:
                self.interpreter.try_stack[-1]["catch_line"] = scan
            elif lu == "END TRY":
                depth -= 1
                if depth == 0:
                    self.interpreter.try_stack[-1]["end_line"] = scan
                    break
            scan += 1
        return "continue"

    def _modern_catch(self, command):
        """CATCH [var]  — error handler block. Only reached by jump from error."""
        # If execution flows here normally (no error), skip to END TRY
        if self.interpreter.try_stack:
            end_line = self.interpreter.try_stack[-1].get("end_line")
            if end_line:
                self.interpreter.current_line = end_line
                self.interpreter.try_stack.pop()
                return "jump"
        return "continue"

    def _modern_throw(self, command):
        """THROW expression  — raise a runtime error."""
        text = re.sub(r'^THROW\s+', '', command, flags=re.IGNORECASE).strip()
        error_msg = str(self._eval_basic_expression(text))
        self.interpreter.last_error = error_msg

        # If inside TRY, jump to CATCH
        if self.interpreter.try_stack:
            frame = self.interpreter.try_stack[-1]
            catch_line = frame.get("catch_line")
            if catch_line:
                # Extract variable name from CATCH line
                _, catch_cmd = self.interpreter.program_lines[catch_line]
                cm = re.match(r'CATCH\s+(\w+)', catch_cmd.strip(), re.IGNORECASE)
                if cm:
                    self.interpreter.variables[cm.group(1).upper()] = error_msg
                self.interpreter.variables["ERROR$"] = error_msg
                # Jump to the line AFTER "CATCH" so the body executes
                self.interpreter.current_line = catch_line + 1
                return "jump"
            else:
                self.interpreter.try_stack.pop()

        self.interpreter.log_output(f"Unhandled error: {error_msg}")
        return "error"

    # ------------------------------------------------------------------
    #  FOR EACH — Iterate over lists and dictionaries
    # ------------------------------------------------------------------

    def _modern_foreach(self, command):
        """FOREACH var IN list_name
           ...body...
        NEXT var

        Also supports: FOREACH key, value IN dict_name"""
        m = re.match(r'FOREACH\s+([\w$]+)(?:\s*,\s*([\w$]+))?\s+IN\s+([\w$]+)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("FOREACH syntax: FOREACH var IN collection")
            return "continue"

        var1 = m.group(1).upper()
        var2 = m.group(2).upper() if m.group(2) else None
        collection_name = m.group(3).upper()

        # Collect body lines until matching NEXT
        body_start = self.interpreter.current_line + 1
        depth = 1
        scan = body_start
        while scan < len(self.interpreter.program_lines):
            _, lt = self.interpreter.program_lines[scan]
            lu = lt.strip().upper()
            if lu.startswith("FOR ") or lu.startswith("FOREACH "):
                depth += 1
            elif lu.startswith("NEXT"):
                depth -= 1
                if depth == 0:
                    break
            scan += 1
        body_end = scan

        # Track (line_index, command) so nested FOREACH/FOR can scan
        # program_lines from the correct position.
        body_lines = []
        for idx in range(body_start, body_end):
            _, cmd = self.interpreter.program_lines[idx]
            body_lines.append((idx, cmd))

        # Determine collection type
        items = []
        if collection_name in self.interpreter.lists:
            lst = self.interpreter.lists[collection_name]
            if var2:
                items = [(i, v) for i, v in enumerate(lst)]
            else:
                items = [(v, None) for v in lst]
        elif collection_name in self.interpreter.dicts:
            d = self.interpreter.dicts[collection_name]
            if var2:
                items = [(k, v) for k, v in d.items()]
            else:
                items = [(k, None) for k in d.keys()]
        else:
            self.interpreter.log_output(f"FOREACH: collection '{collection_name}' not found")
            self.interpreter.current_line = body_end
            return "continue"

        # Execute body for each item
        for item in items:
            self.interpreter.variables[var1] = item[0]
            if var2 and item[1] is not None:
                self.interpreter.variables[var2] = item[1]
            _broke = False
            i = 0
            while i < len(body_lines):
                line_idx, line = body_lines[i]
                line = line.strip()
                if line:
                    # Set current_line so nested FOREACH/FOR can locate their
                    # body in program_lines by scanning from this position.
                    self.interpreter.current_line = line_idx
                    result = self.execute_command(line)
                    if result in ("end", "stop", "return"):
                        self.interpreter.current_line = body_end
                        return result
                    if result == "break":
                        _broke = True
                        break
                # If current_line advanced (e.g. nested FOREACH consumed lines),
                # skip outer body_lines that were already handled.
                new_pos = self.interpreter.current_line
                while i + 1 < len(body_lines) and body_lines[i + 1][0] <= new_pos:
                    i += 1
                i += 1
            if _broke:
                break

        self.interpreter.current_line = body_end
        return "continue"

    # ------------------------------------------------------------------
    #  CONST — Constant (immutable) variables
    # ------------------------------------------------------------------

    def _modern_const(self, command):
        """CONST name = value"""
        text = re.sub(r'^CONST\s+', '', command, flags=re.IGNORECASE).strip()
        m = re.match(r'(\w+)\s*=\s*(.*)', text)
        if m:
            name = m.group(1).upper()
            if name in self.interpreter.constants:
                self.interpreter.log_output(f"Cannot reassign constant: {name}")
                return "continue"
            val = self._eval_basic_expression(m.group(2).strip())
            self.interpreter.variables[name] = val
            self.interpreter.constants.add(name)
        return "continue"

    # ------------------------------------------------------------------
    #  TYPEOF — Type introspection
    # ------------------------------------------------------------------

    def _modern_typeof(self, command):
        """TYPEOF expr [INTO var]"""
        text = re.sub(r'^TYPEOF\s+', '', command, flags=re.IGNORECASE).strip()
        into_m = re.match(r'(.+?)\s+INTO\s+(\w+)', text, re.IGNORECASE)
        if into_m:
            expr = into_m.group(1).strip()
            var = into_m.group(2).upper()
        else:
            expr = text
            var = None

        val = self._eval_basic_expression(expr)
        if val is None:
            type_name = "NULL"
        elif isinstance(val, bool):
            type_name = "BOOLEAN"
        elif isinstance(val, int):
            type_name = "INTEGER"
        elif isinstance(val, float):
            type_name = "FLOAT"
        elif isinstance(val, str):
            type_name = "STRING"
        elif isinstance(val, list):
            type_name = "LIST"
        elif isinstance(val, dict):
            type_name = "DICT"
        else:
            type_name = "UNKNOWN"

        if var:
            self.interpreter.variables[var] = type_name
        else:
            self.interpreter.log_output(type_name)
        return "continue"

    # ------------------------------------------------------------------
    #  ASSERT — Testing / validation
    # ------------------------------------------------------------------

    def _modern_assert(self, command):
        """ASSERT condition [, "message"]"""
        text = re.sub(r'^ASSERT\s+', '', command, flags=re.IGNORECASE).strip()
        # Split on last comma to find optional message
        msg = "Assertion failed"
        parts = self._smart_split(text, ",")
        if len(parts) >= 2 and parts[-1].strip().startswith('"'):
            msg = parts[-1].strip().strip('"')
            text = ",".join(parts[:-1])

        result = self._eval_basic_condition(text)
        if not result:
            self.interpreter.log_output(f"❌ ASSERT FAILED: {msg}")
            if self.interpreter.try_stack:
                self.interpreter.last_error = msg
                return self._modern_throw(f'THROW "{msg}"')
            return "error"
        return "continue"

    # ------------------------------------------------------------------
    #  IMPORT — Module system
    # ------------------------------------------------------------------

    def _modern_import(self, command):
        """IMPORT "filename.tc"  — include and execute another TempleCode file."""
        m = re.match(r'IMPORT\s+"([^"]+)"', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output('IMPORT syntax: IMPORT "filename.tc"')
            return "continue"
        filename = m.group(1)
        if filename in self.interpreter.imported_modules:
            return "continue"  # already imported
        self.interpreter.imported_modules.add(filename)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                module_code = f.read()
            # Pre-process for TO/END procedures
            module_code = self.interpreter._preprocess_logo_program(module_code)  # pylint: disable=protected-access
            for raw_line in module_code.strip().split("\n"):
                _, cmd = self.interpreter.parse_line(raw_line)
                if cmd.strip():
                    self.execute_command(cmd.strip())
        except FileNotFoundError:
            self.interpreter.log_output(f"Module not found: {filename}")
        except Exception as e:
            self.interpreter.log_output(f"Import error: {e}")
        return "continue"

    # ------------------------------------------------------------------
    #  PRINTF — Formatted output
    # ------------------------------------------------------------------

    def _modern_printf(self, command):
        """PRINTF "format string {0} {1}", arg1, arg2
        Supports {n} positional, {var} variable interpolation,
        and %-style: %d, %s, %f, %.Nf"""
        text = re.sub(r'^PRINTF\s+', '', command, flags=re.IGNORECASE).strip()
        parts = self._smart_split(text, ",")
        if not parts:
            return "continue"

        fmt_str = self._eval_basic_expression(parts[0].strip())
        if not isinstance(fmt_str, str):
            fmt_str = str(fmt_str)

        args = [self._eval_basic_expression(p.strip()) for p in parts[1:]]

        # Replace {0}, {1}, ... with positional args
        for i, arg in enumerate(args):
            fmt_str = fmt_str.replace(f"{{{i}}}", str(arg))

        # Replace {VAR_NAME} with variable values
        def repl_var(m):
            vn = m.group(1).upper()
            return str(self.interpreter.variables.get(vn, m.group(0)))
        fmt_str = re.sub(r'\{([A-Za-z_]\w*)\}', repl_var, fmt_str)

        # %-style format specifiers
        try:
            if "%" in fmt_str and args:
                fmt_str = fmt_str % tuple(args[:fmt_str.count("%")])
        except Exception:
            pass

        # Escape sequences
        fmt_str = fmt_str.replace("\\n", "\n").replace("\\t", "\t")

        self.interpreter.log_output(fmt_str)
        return "continue"

    # ------------------------------------------------------------------
    #  JSON — Parse and stringify
    # ------------------------------------------------------------------

    def _modern_json(self, command):
        """JSON PARSE "string" INTO var
        JSON STRINGIFY dict/list INTO var
        JSON GET var.key INTO result_var"""
        text = re.sub(r'^JSON\s+', '', command, flags=re.IGNORECASE).strip()
        upper_text = text.upper()

        if upper_text.startswith("PARSE"):
            m = re.match(r'PARSE\s+(.+?)\s+INTO\s+(\w+)', text, re.IGNORECASE)
            if m:
                import json
                expr = self._eval_basic_expression(m.group(1).strip())
                var = m.group(2).upper()
                try:
                    parsed = json.loads(str(expr))
                    if isinstance(parsed, dict):
                        self.interpreter.dicts[var] = parsed
                    elif isinstance(parsed, list):
                        self.interpreter.lists[var] = parsed
                    else:
                        self.interpreter.variables[var] = parsed
                except json.JSONDecodeError as e:
                    self.interpreter.log_output(f"JSON parse error: {e}")
            return "continue"

        elif upper_text.startswith("STRINGIFY"):
            m = re.match(r'STRINGIFY\s+(\w+)\s+INTO\s+(\w+)', text, re.IGNORECASE)
            if m:
                import json
                name = m.group(1).upper()
                var = m.group(2).upper()
                if name in self.interpreter.dicts:
                    self.interpreter.variables[var] = json.dumps(self.interpreter.dicts[name])
                elif name in self.interpreter.lists:
                    self.interpreter.variables[var] = json.dumps(self.interpreter.lists[name])
                else:
                    self.interpreter.variables[var] = json.dumps(
                        self.interpreter.variables.get(name, "")
                    )
            return "continue"

        elif upper_text.startswith("GET"):
            m = re.match(r'GET\s+(\w+)\.(\w+)\s+INTO\s+(\w+)', text, re.IGNORECASE)
            if m:
                dict_name = m.group(1).upper()
                key = m.group(2)
                var = m.group(3).upper()
                if dict_name in self.interpreter.dicts:
                    self.interpreter.variables[var] = self.interpreter.dicts[dict_name].get(key, "")
            return "continue"

        self.interpreter.log_output("JSON syntax: JSON PARSE|STRINGIFY|GET ...")
        return "continue"

    # ------------------------------------------------------------------
    #  REGEX — Regular expression operations
    # ------------------------------------------------------------------

    def _modern_regex(self, command):
        """REGEX MATCH "pattern" IN expr INTO var
        REGEX REPLACE "pattern" WITH "replacement" IN expr INTO var
        REGEX FIND "pattern" IN expr INTO list_name
        REGEX SPLIT "pattern" IN expr INTO list_name"""
        text = re.sub(r'^REGEX\s+', '', command, flags=re.IGNORECASE).strip()
        upper_text = text.upper()

        if upper_text.startswith("MATCH"):
            m = re.match(r'MATCH\s+"([^"]+)"\s+IN\s+(.+?)\s+INTO\s+(\w+)', text, re.IGNORECASE)
            if m:
                pattern = m.group(1)
                expr = str(self._eval_basic_expression(m.group(2).strip()))
                var = m.group(3).upper()
                match = re.search(pattern, expr)
                if match:
                    self.interpreter.variables[var] = match.group(0)
                    self.interpreter.variables[var + "_POS"] = match.start()
                    self.interpreter.match_flag = True
                else:
                    self.interpreter.variables[var] = ""
                    self.interpreter.variables[var + "_POS"] = -1
                    self.interpreter.match_flag = False
            return "continue"

        elif upper_text.startswith("REPLACE"):
            m = re.match(
                r'REPLACE\s+"([^"]+)"\s+WITH\s+"([^"]*)"\s+IN\s+(.+?)\s+INTO\s+(\w+)',
                text, re.IGNORECASE
            )
            if m:
                pattern = m.group(1)
                replacement = m.group(2)
                expr = str(self._eval_basic_expression(m.group(3).strip()))
                var = m.group(4).upper()
                self.interpreter.variables[var] = re.sub(pattern, replacement, expr)
            return "continue"

        elif upper_text.startswith("FIND"):
            m = re.match(r'FIND\s+"([^"]+)"\s+IN\s+(.+?)\s+INTO\s+(\w+)', text, re.IGNORECASE)
            if m:
                pattern = m.group(1)
                expr = str(self._eval_basic_expression(m.group(2).strip()))
                list_name = m.group(3).upper()
                matches = re.findall(pattern, expr)
                self.interpreter.lists[list_name] = matches
                self.interpreter.variables[list_name + "_LENGTH"] = len(matches)
            return "continue"

        elif upper_text.startswith("SPLIT"):
            m = re.match(r'SPLIT\s+"([^"]+)"\s+IN\s+(.+?)\s+INTO\s+(\w+)', text, re.IGNORECASE)
            if m:
                pattern = m.group(1)
                expr = str(self._eval_basic_expression(m.group(2).strip()))
                list_name = m.group(3).upper()
                self.interpreter.lists[list_name] = re.split(pattern, expr)
                self.interpreter.variables[list_name + "_LENGTH"] = len(self.interpreter.lists[list_name])
            return "continue"

        self.interpreter.log_output("REGEX syntax: REGEX MATCH|REPLACE|FIND|SPLIT ...")
        return "continue"

    # ------------------------------------------------------------------
    #  ENUM — Enumeration type
    # ------------------------------------------------------------------

    def _modern_enum(self, command):
        """ENUM name = VAL1, VAL2, VAL3
        Creates constants NAME.VAL1=0, NAME.VAL2=1, etc."""
        text = re.sub(r'^ENUM\s+', '', command, flags=re.IGNORECASE).strip()
        m = re.match(r'(\w+)\s*=\s*(.*)', text)
        if not m:
            self.interpreter.log_output("ENUM syntax: ENUM name = VAL1, VAL2, VAL3")
            return "continue"
        name = m.group(1).upper()
        values = [v.strip().upper() for v in m.group(2).split(",") if v.strip()]
        for i, val in enumerate(values):
            key = f"{name}_{val}"
            self.interpreter.variables[key] = i
            self.interpreter.constants.add(key)
        self.interpreter.variables[name + "_COUNT"] = len(values)
        return "continue"

    # ------------------------------------------------------------------
    #  STRUCT — Simple record type
    # ------------------------------------------------------------------

    def _modern_struct(self, command):
        """STRUCT name = field1, field2, field3
        Defines a template for structured data (stored as dict)."""
        text = re.sub(r'^STRUCT\s+', '', command, flags=re.IGNORECASE).strip()
        m = re.match(r'(\w+)\s*=\s*(.*)', text)
        if not m:
            self.interpreter.log_output("STRUCT syntax: STRUCT name = field1, field2, ...")
            return "continue"
        name = m.group(1).upper()
        fields = [f.strip().upper() for f in m.group(2).split(",") if f.strip()]
        # Store struct definition as a dict template
        self.interpreter.variables["__STRUCT_" + name] = fields
        return "continue"

    def _modern_new(self, command):
        """NEW struct_name AS var_name  — create instance of struct."""
        m = re.match(r'NEW\s+(\w+)\s+AS\s+(\w+)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("NEW syntax: NEW struct_name AS var_name")
            return "continue"
        struct_name = m.group(1).upper()
        var_name = m.group(2).upper()
        fields = self.interpreter.variables.get("__STRUCT_" + struct_name)
        if not fields:
            self.interpreter.log_output(f"Undefined struct: {struct_name}")
            return "continue"
        instance = {f: 0 for f in fields}
        self.interpreter.dicts[var_name] = instance
        return "continue"

    # ------------------------------------------------------------------
    #  LAMBDA — Inline function expressions
    # ------------------------------------------------------------------

    def _modern_lambda(self, command):
        """LAMBDA name(params) = expression
        Creates a lightweight inline function."""
        m = re.match(r'LAMBDA\s+(\w+)\s*\(([^)]*)\)\s*=\s*(.*)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("LAMBDA syntax: LAMBDA name(params) = expression")
            return "continue"
        name = m.group(1).upper()
        params = [p.strip().upper() for p in m.group(2).split(",") if p.strip()]
        body_expr = m.group(3).strip()
        # Store as a function definition with a single RETURN line
        self.interpreter.function_definitions[name] = {
            "params": params,
            "body_expr": body_expr,  # inline expression
            "is_lambda": True,
        }
        return "continue"

    # ------------------------------------------------------------------
    #  MAP / FILTER / REDUCE — Functional list operations
    # ------------------------------------------------------------------

    def _modern_map(self, command):
        """MAP func_name ON list_name INTO result_list"""
        m = re.match(r'MAP\s+(\w+)\s+ON\s+(\w+)\s+INTO\s+(\w+)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("MAP syntax: MAP function ON list INTO result_list")
            return "continue"
        func_name = m.group(1).upper()
        list_name = m.group(2).upper()
        result_name = m.group(3).upper()

        src = self.interpreter.lists.get(list_name, [])
        result = []
        for item in src:
            val = self._apply_func(func_name, [item])
            result.append(val if val is not None else item)
        self.interpreter.lists[result_name] = result
        self.interpreter.variables[result_name + "_LENGTH"] = len(result)
        return "continue"

    def _modern_filter(self, command):
        """FILTER func_name ON list_name INTO result_list"""
        m = re.match(r'FILTER\s+(\w+)\s+ON\s+(\w+)\s+INTO\s+(\w+)', command, re.IGNORECASE)
        if not m:
            self.interpreter.log_output("FILTER syntax: FILTER function ON list INTO result_list")
            return "continue"
        func_name = m.group(1).upper()
        list_name = m.group(2).upper()
        result_name = m.group(3).upper()

        src = self.interpreter.lists.get(list_name, [])
        result = []
        for item in src:
            val = self._apply_func(func_name, [item])
            if val:
                result.append(item)
        self.interpreter.lists[result_name] = result
        self.interpreter.variables[result_name + "_LENGTH"] = len(result)
        return "continue"

    def _modern_reduce(self, command):
        """REDUCE func_name ON list_name INTO var [FROM initial]"""
        m = re.match(
            r'REDUCE\s+(\w+)\s+ON\s+(\w+)\s+INTO\s+(\w+)(?:\s+FROM\s+(.+))?',
            command, re.IGNORECASE
        )
        if not m:
            self.interpreter.log_output("REDUCE syntax: REDUCE function ON list INTO var [FROM initial]")
            return "continue"
        func_name = m.group(1).upper()
        list_name = m.group(2).upper()
        result_var = m.group(3).upper()
        initial = self._eval_basic_expression(m.group(4).strip()) if m.group(4) else None

        src = self.interpreter.lists.get(list_name, [])
        if not src:
            self.interpreter.variables[result_var] = initial if initial is not None else 0
            return "continue"

        if initial is not None:
            acc = initial
            start = 0
        else:
            acc = src[0]
            start = 1

        for i in range(start, len(src)):
            acc = self._apply_func(func_name, [acc, src[i]])
            if acc is None:
                acc = 0

        self.interpreter.variables[result_var] = acc
        return "continue"

    def _apply_func(self, func_name, args):
        """Apply a user-defined function or lambda to arguments."""
        defn = self.interpreter.function_definitions.get(func_name)
        if defn:
            if defn.get("is_lambda"):
                # Lambda: evaluate body expression with params bound
                saved = {}
                for i, param in enumerate(defn["params"]):
                    saved[param] = self.interpreter.variables.get(param)
                    if i < len(args):
                        self.interpreter.variables[param] = args[i]

                result = self._eval_basic_expression(defn["body_expr"])

                for param in defn["params"]:
                    if saved.get(param) is not None:
                        self.interpreter.variables[param] = saved[param]
                    elif param in self.interpreter.variables:
                        del self.interpreter.variables[param]
                return result
            else:
                # Full function
                str_args = [str(a) for a in args]
                self._execute_sub_or_function(func_name, defn, str_args)
                return self.interpreter.return_value

        # Built-in simple functions
        fn = func_name.upper()
        if fn == "ABS" and args:
            return abs(float(args[0]))
        if fn == "INT" and args:
            return int(float(args[0]))
        if fn == "SQRT" and args:
            return math.sqrt(float(args[0]))
        if fn == "UPPER" and args:
            return str(args[0]).upper()
        if fn == "LOWER" and args:
            return str(args[0]).lower()
        if fn == "STR" and args:
            return str(args[0])
        if fn == "LEN" and args:
            return len(str(args[0]))

        return None

    def _func_args_split(self, expr, func_name):
        """If *expr* is a complete call to *func_name*(...), return the argument
        list split with bracket-aware logic so nested calls like f(g(a, b), c)
        are handled correctly.  Returns None if the expression does not match."""
        fname_up = func_name.upper()
        expr_up = expr.upper()
        # Accept both NAME( and NAME$( forms by trying both
        for candidate in (fname_up + "(", fname_up.rstrip("$") + "$("):
            if expr_up.startswith(candidate):
                inner_start = len(candidate)
                break
        else:
            return None
        if not expr.endswith(")"):
            return None
        inner = expr[inner_start:-1]
        # Verify the slice is correct (outer paren depth stays >= 0)
        depth = 0
        in_str = False
        for ch in inner:
            if ch == '"':
                in_str = not in_str
            elif not in_str:
                if ch in "([":
                    depth += 1
                elif ch in ")]":
                    depth -= 1
                    if depth < 0:
                        return None  # extra closing paren → our slice was wrong
        if depth != 0:
            return None
        return [a.strip() for a in self._smart_split(inner, ",")]

    # ------------------------------------------------------------------
    #  Helper: smart split respecting quotes and brackets
    # ------------------------------------------------------------------

    def _smart_split(self, text, delimiter=","):
        """Split text on delimiter, respecting quoted strings and brackets."""
        parts = []
        current = []
        in_string = False
        depth = 0
        for ch in text:
            if ch == '"' and depth == 0:
                in_string = not in_string
                current.append(ch)
            elif ch in "([" and not in_string:
                depth += 1
                current.append(ch)
            elif ch in ")]" and not in_string:
                depth -= 1
                current.append(ch)
            elif ch == delimiter and not in_string and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(ch)
        if current:
            parts.append("".join(current))
        return parts

    # ------------------------------------------------------------------
    #  Extended expression evaluation for new features
    # ------------------------------------------------------------------

    def _eval_basic_expression_extended(self, expr):  # noqa: C901
        """Extended expression evaluation supporting new data types."""
        expr = expr.strip()

        # List literal: [1, 2, 3]
        if expr.startswith("[") and expr.endswith("]"):
            items = self._smart_split(expr[1:-1], ",")
            return [self._eval_basic_expression(i.strip()) for i in items if i.strip()]

        # List access: LISTNAME[index]
        m = re.match(r'(\w+)\[(.+)\]', expr)
        if m:
            name = m.group(1).upper()
            idx = int(float(self._eval_basic_expression(m.group(2))))
            if name in self.interpreter.lists:
                lst = self.interpreter.lists[name]
                if 0 <= idx < len(lst):
                    return lst[idx]
                return ""
            # Fallback: variable may hold a Python list (e.g. from SPLIT)
            lv = self.interpreter.variables.get(name)
            if isinstance(lv, list):
                if 0 <= idx < len(lv):
                    return lv[idx]
                return ""

        # Dict access: DICTNAME.key
        m = re.match(r'(\w+)\.(\w+)', expr)
        if m:
            name = m.group(1).upper()
            key = m.group(2)
            if name in self.interpreter.dicts:
                return self.interpreter.dicts[name].get(key, "")

        # LENGTH(list_or_string)
        m = re.match(r'LENGTH\((\w+)\)', expr, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            if name in self.interpreter.lists:
                return len(self.interpreter.lists[name])
            if name in self.interpreter.dicts:
                return len(self.interpreter.dicts[name])
            val = self.interpreter.variables.get(name, "")
            # Variable may hold a Python list (e.g. from SPLIT)
            if isinstance(val, list):
                return len(val)
            return len(str(val))

        # KEYS(dict) / VALUES(dict)
        m = re.match(r'KEYS\((\w+)\)', expr, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            if name in self.interpreter.dicts:
                return list(self.interpreter.dicts[name].keys())

        m = re.match(r'VALUES\((\w+)\)', expr, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            if name in self.interpreter.dicts:
                return list(self.interpreter.dicts[name].values())

        # HASKEY(dict, key)
        _args = self._func_args_split(expr, "HASKEY")
        if _args and len(_args) == 2:
            name = _args[0].upper()
            key = self._eval_basic_expression(_args[1])
            if name in self.interpreter.dicts:
                return 1 if key in self.interpreter.dicts[name] else 0
            return 0

        # INDEXOF(list, value)
        _args = self._func_args_split(expr, "INDEXOF")
        if _args and len(_args) == 2:
            name = _args[0].upper()
            val = self._eval_basic_expression(_args[1])
            if name in self.interpreter.lists:
                try:
                    return self.interpreter.lists[name].index(val)
                except ValueError:
                    return -1
            return -1

        # CONTAINS(list_or_string, value)
        _args = self._func_args_split(expr, "CONTAINS")
        if _args and len(_args) == 2:
            name = _args[0].upper()
            val = self._eval_basic_expression(_args[1])
            if name in self.interpreter.lists:
                return 1 if val in self.interpreter.lists[name] else 0
            sv = str(self.interpreter.variables.get(name, ""))
            return 1 if str(val) in sv else 0

        # SLICE(list, start, end)
        _args = self._func_args_split(expr, "SLICE")
        if _args and len(_args) == 3:
            name = _args[0].upper()
            start = int(float(self._eval_basic_expression(_args[1])))
            end = int(float(self._eval_basic_expression(_args[2])))
            if name in self.interpreter.lists:
                return self.interpreter.lists[name][start:end]
            sv = str(self.interpreter.variables.get(name, ""))
            return sv[start:end]

        # JOIN(list, delimiter)
        _args = self._func_args_split(expr, "JOIN")
        if _args and len(_args) == 2:
            name = _args[0].upper()
            delim = str(self._eval_basic_expression(_args[1]))
            if name in self.interpreter.lists:
                return delim.join(str(x) for x in self.interpreter.lists[name])

        # SPLIT(string, delimiter)
        _args = self._func_args_split(expr, "SPLIT")
        if _args and len(_args) == 2:
            s = str(self._eval_basic_expression(_args[0]))
            delim = str(self._eval_basic_expression(_args[1]))
            return s.split(delim)

        # REPLACE$(string, old, new)  — accept both REPLACE and REPLACE$
        _args = self._func_args_split(expr, "REPLACE$") or self._func_args_split(expr, "REPLACE")
        if _args and len(_args) == 3:
            s = str(self._eval_basic_expression(_args[0]))
            old = str(self._eval_basic_expression(_args[1]))
            new = str(self._eval_basic_expression(_args[2]))
            return s.replace(old, new)

        # TRIM$(string)
        m = re.match(r'TRIM\$?\((.+)\)', expr, re.IGNORECASE)
        if m:
            return str(self._eval_basic_expression(m.group(1).strip())).strip()

        # STARTSWITH(string, prefix)
        _args = self._func_args_split(expr, "STARTSWITH")
        if _args and len(_args) == 2:
            s = str(self._eval_basic_expression(_args[0]))
            prefix = str(self._eval_basic_expression(_args[1]))
            return 1 if s.startswith(prefix) else 0

        # ENDSWITH(string, suffix)
        _args = self._func_args_split(expr, "ENDSWITH")
        if _args and len(_args) == 2:
            s = str(self._eval_basic_expression(_args[0]))
            suffix = str(self._eval_basic_expression(_args[1]))
            return 1 if s.endswith(suffix) else 0

        # REPEAT$(string, count)  — accept both REPEAT$ and REPEAT
        _args = self._func_args_split(expr, "REPEAT$") or self._func_args_split(expr, "REPEAT")
        if _args and len(_args) == 2:
            s = str(self._eval_basic_expression(_args[0]))
            n = int(float(self._eval_basic_expression(_args[1])))
            return s * n

        # FORMAT$(value, format_spec)  — accept both FORMAT$ and FORMAT
        _args = self._func_args_split(expr, "FORMAT$") or self._func_args_split(expr, "FORMAT")
        if _args and len(_args) == 2:
            val = self._eval_basic_expression(_args[0])
            spec = str(self._eval_basic_expression(_args[1]))
            try:
                return format(val, spec)
            except Exception:
                return str(val)

        # ISNUMBER(value)
        m = re.match(r'ISNUMBER\((.+)\)', expr, re.IGNORECASE)
        if m:
            val = self._eval_basic_expression(m.group(1).strip())
            return 1 if isinstance(val, (int, float)) else 0

        # ISSTRING(value)
        m = re.match(r'ISSTRING\((.+)\)', expr, re.IGNORECASE)
        if m:
            val = self._eval_basic_expression(m.group(1).strip())
            return 1 if isinstance(val, str) else 0

        # TONUM(value)
        m = re.match(r'TONUM\((.+)\)', expr, re.IGNORECASE)
        if m:
            val = self._eval_basic_expression(m.group(1).strip())
            try:
                f = float(val)
                return int(f) if f == int(f) else f
            except (ValueError, TypeError):
                return 0

        # TOSTR(value)
        m = re.match(r'TOSTR\((.+)\)', expr, re.IGNORECASE)
        if m:
            return str(self._eval_basic_expression(m.group(1).strip()))

        # ROUND(value [, decimals])
        _args = self._func_args_split(expr, "ROUND")
        if _args and len(_args) in (1, 2):
            val = float(self._eval_basic_expression(_args[0]))
            decimals = int(float(self._eval_basic_expression(_args[1]))) if len(_args) == 2 else 0
            result = round(val, decimals)
            # Return int when rounding to 0 decimal places and result is whole
            if decimals == 0:
                return int(result)
            return result

        # FLOOR(value)
        m = re.match(r'FLOOR\((.+)\)', expr, re.IGNORECASE)
        if m:
            return math.floor(float(self._eval_basic_expression(m.group(1).strip())))

        # POWER(base, exp)
        _args = self._func_args_split(expr, "POWER")
        if _args and len(_args) == 2:
            base = float(self._eval_basic_expression(_args[0]))
            exp = float(self._eval_basic_expression(_args[1]))
            result = base ** exp
            return int(result) if result == int(result) else result

        # CLAMP(value, min, max)
        _args = self._func_args_split(expr, "CLAMP")
        if _args and len(_args) == 3:
            val = float(self._eval_basic_expression(_args[0]))
            lo = float(self._eval_basic_expression(_args[1]))
            hi = float(self._eval_basic_expression(_args[2]))
            return max(lo, min(hi, val))

        # LERP(a, b, t) — linear interpolation
        _args = self._func_args_split(expr, "LERP")
        if _args and len(_args) == 3:
            a = float(self._eval_basic_expression(_args[0]))
            b = float(self._eval_basic_expression(_args[1]))
            t = float(self._eval_basic_expression(_args[2]))
            return a + (b - a) * t

        # RANDOM(min, max)
        _args = self._func_args_split(expr, "RANDOM")
        if _args and len(_args) == 2:
            lo = int(float(self._eval_basic_expression(_args[0])))
            hi = int(float(self._eval_basic_expression(_args[1])))
            return random.randint(lo, hi)

        # PI, E constants
        if expr.upper() == "PI":
            return math.pi
        if expr.upper() == "E":
            return math.e
        if expr.upper() == "TAU":
            return math.tau
        if expr.upper() == "INF":
            return float("inf")

        # FILEEXISTS(filename)
        m = re.match(r'FILEEXISTS\((.+)\)', expr, re.IGNORECASE)
        if m:
            import os
            fn = str(self._eval_basic_expression(m.group(1).strip()))
            return 1 if os.path.exists(fn) else 0

        # RESULT (function return value)
        if expr.upper() == "RESULT":
            return self.interpreter.return_value if self.interpreter.return_value is not None else 0

        # ERROR$ (last error message)
        if expr.upper() == "ERROR$":
            return self.interpreter.last_error

        # Signal that no extended feature matched — return the expr object itself
        # so the caller can distinguish "not handled" from a legitimate result
        return expr
