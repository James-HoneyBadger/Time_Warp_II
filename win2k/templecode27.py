# -*- coding: utf-8 -*-
"""
TempleCode Interpreter Engine -- Python 2.7 / Windows 2000 Back-port
=====================================================================
Part of the *Time Warp II -- Retro Edition* experimental side-project.

This module implements the core TempleCode language executor
(BASIC + PILOT + Logo) in pure Python 2.7 so it can run on
systems as old as Windows 2000 with Python 2.7.8 installed.

Copyright (c) 2025-2026 Honey Badger Universe
"""
from __future__ import print_function, division

import math
import os
import random
import re
import time

try:
    import json
except ImportError:
    json = None  # ancient Pythons

# ======================================================================
#  Utility helpers
# ======================================================================

def _safe_num(value):
    """Try to convert *value* to int or float; return original on failure."""
    try:
        f = float(value)
        if f == int(f):
            return int(f)
        return f
    except (ValueError, TypeError):
        return value


def _is_number(v):
    return isinstance(v, (int, float))


def _is_string(v):
    return isinstance(v, str)

# ======================================================================
#  TempleCode Engine
# ======================================================================

class TempleCodeEngine(object):
    """
    Self-contained TempleCode interpreter for Python 2.7.

    Communication with the outside world uses three callbacks:

    * ``output_cb(text)``   -- print text to the user
    * ``input_cb(prompt)``  -- ask the user for a line of input (blocking)
    * ``canvas_cb(action, **kw)``  -- draw on the turtle canvas (optional)
    """

    # ------------------------------------------------------------------
    #  Construction
    # ------------------------------------------------------------------

    def __init__(self, output_cb=None, input_cb=None, canvas_cb=None):
        # Callbacks
        self.output_cb  = output_cb  or self._default_output
        self.input_cb   = input_cb   or self._default_input
        self.canvas_cb  = canvas_cb  or (lambda *a, **kw: None)

        self._reset()

    # ------------------------------------------------------------------
    #  Full state reset
    # ------------------------------------------------------------------

    def _reset(self):
        # Program storage
        self.program_lines = []   # [(line_num_or_None, command_str), ...]
        self.labels        = {}   # label_name -> index into program_lines

        # Execution
        self.current_line = 0
        self.running      = False

        # Variables
        self.variables = {}
        self.constants = set()
        self.arrays    = {}       # name -> {int_index: value, ...}

        # Stacks
        self.gosub_stack   = []
        self.for_stack     = []
        self.while_stack   = []
        self.do_stack      = []
        self.select_stack  = []
        self.call_stack    = []     # SUB/FUNCTION return info

        # PILOT state
        self.match_flag       = False
        self._last_match_set  = False

        # DATA / READ
        self._data_values  = []
        self._data_pos     = 0

        # Turtle state
        self.turtle_x       = 0.0
        self.turtle_y       = 0.0
        self.turtle_heading = 0.0  # 0 = North, degrees clockwise
        self.turtle_pen     = True
        self.turtle_color   = "white"
        self.turtle_width   = 2
        self.turtle_visible = True

        # Logo procedures: name -> (param_names_list, body_lines_list)
        self.logo_procs = {}

        # SUB / FUNCTION defs: name -> {params, start, end}
        self.sub_defs  = {}
        self.func_defs = {}
        self.return_value = None

        # Lists & Dicts
        self.lists = {}
        self.dicts = {}

        # Error handling
        self.try_stack  = []
        self.last_error = ""

        # Timing
        self._start_time = time.time()

        # Iteration cap (prevent infinite loops)
        self.max_iterations = 100000

    # ------------------------------------------------------------------
    #  Default I/O callbacks
    # ------------------------------------------------------------------

    @staticmethod
    def _default_output(text):
        print(text)

    @staticmethod
    def _default_input(prompt):
        try:
            return raw_input(prompt)
        except NameError:
            return input(prompt)  # Python 3 fallback

    # ------------------------------------------------------------------
    #  Expression evaluator
    # ------------------------------------------------------------------

    def evaluate(self, expr):
        """Evaluate a BASIC expression and return its value."""
        if not isinstance(expr, str):
            return expr
        expr = expr.strip()
        if not expr:
            return 0

        # Bare string literal
        if expr.startswith('"') and expr.endswith('"') and expr.count('"') == 2:
            return expr[1:-1]

        # ---- build a Python expression string ----
        s = self._transform_expr(expr)

        ns = dict(self._builtins())
        # Inject variables ($ -> _S in key name for Python compat)
        for k, v in self.variables.items():
            ns[self._py_name(k)] = v
        # Inject arrays
        for k, v in self.arrays.items():
            ns[self._py_name(k)] = v
        # Inject lists
        for k, v in self.lists.items():
            ns[self._py_name(k)] = v
        # Inject dicts
        for k, v in self.dicts.items():
            ns["_d_" + self._py_name(k)] = v

        try:
            return eval(s, {"__builtins__": {}}, ns)
        except ZeroDivisionError:
            self.output_cb("ERROR: Division by zero")
            return 0
        except Exception:
            # Fallback: maybe a lone variable
            up = expr.strip().upper()
            if up in self.variables:
                return self.variables[up]
            # Or a number after all
            try:
                return _safe_num(expr.strip())
            except Exception:
                return expr.strip()

    def _transform_expr(self, s):
        """Rewrite BASIC expression syntax -> Python-evaluable string."""
        # Interpolate *VAR*
        for vn, vv in self.variables.items():
            val_repr = str(vv) if _is_number(vv) else '"%s"' % str(vv).replace('"', '\\"')
            s = s.replace("*%s*" % vn, val_repr)

        # --- String functions ($ suffix) ---
        sf = [
            ("REPLACE$", "_replace_s"), ("REPEAT$", "_repeat_s"),
            ("FORMAT$", "_format_s"),
            ("UCASE$", "_ucase"), ("LCASE$", "_lcase"), ("TRIM$", "_trim"),
            ("LEFT$", "_left"), ("RIGHT$", "_right"), ("MID$", "_mid"),
            ("CHR$", "_chr"), ("STR$", "_str"), ("INSTR$", "_instr"),
        ]
        for old, new in sf:
            s = re.sub(re.escape(old) + r"\s*\(", new + "(", s, flags=re.IGNORECASE)

        # --- Regular functions ---
        ff = [
            ("TOSTR", "_tostr"), ("TONUM", "_tonum"),
            ("ISNUMBER", "_isnumber"), ("ISSTRING", "_isstring"),
            ("CONTAINS", "_contains"), ("HASKEY", "_haskey"),
            ("LENGTH", "_length"), ("LEN", "len"),
            ("SQR", "_sqrt"), ("SQRT", "_sqrt"),
            ("ABS", "abs"), ("INT", "int"), ("ROUND", "_round"),
            ("SIN", "_sin"), ("COS", "_cos"), ("TAN", "_tan"),
            ("ATN", "_atan"), ("ATAN", "_atan"),
            ("LOG", "_log"), ("EXP", "_exp"),
            ("SGN", "_sgn"), ("CEIL", "_ceil"), ("FLOOR", "_floor"),
            ("CLAMP", "_clamp"), ("LERP", "_lerp"), ("LOG2", "_log2"),
            ("ASC", "_asc"), ("VAL", "_tonum"),
            ("HEX", "_hex"), ("BIN", "_bin"), ("OCT", "_oct"),
        ]
        for old, new in ff:
            s = re.sub(r"\b" + old + r"\s*\(", new + "(", s, flags=re.IGNORECASE)

        # Standalone RND (no parens)
        s = re.sub(r"\bRND\b(?!\s*\()", str(random.random()), s, flags=re.IGNORECASE)
        # RND(n) form
        s = re.sub(r"\bRND\s*\(", "_rnd(", s, flags=re.IGNORECASE)

        # Pseudo-variables
        import datetime as _dt
        s = re.sub(r"\bTIMER\b(?!\s*\()",
                   str(round(time.time() - self._start_time, 3)), s, flags=re.IGNORECASE)
        s = re.sub(r"\bDATE\$",
                   '"%s"' % _dt.date.today().isoformat(), s, flags=re.IGNORECASE)
        s = re.sub(r"\bTIME\$",
                   '"%s"' % _dt.datetime.now().strftime("%H:%M:%S"), s, flags=re.IGNORECASE)

        # Constants
        s = re.sub(r"\bPI\b", str(math.pi), s, flags=re.IGNORECASE)
        s = re.sub(r"\bTAU\b", str(math.pi * 2), s, flags=re.IGNORECASE)
        # E is tricky -- only replace standalone E not part of a word
        s = re.sub(r"(?<![A-Za-z_])E(?![A-Za-z_0-9])", str(math.e), s)

        # Operators
        s = s.replace("<>", "!=")
        s = re.sub(r"\bMOD\b", "%", s, flags=re.IGNORECASE)
        s = re.sub(r"\bAND\b", " and ", s, flags=re.IGNORECASE)
        s = re.sub(r"\bOR\b", " or ", s, flags=re.IGNORECASE)
        s = re.sub(r"(?<!\w)NOT\b", " not ", s, flags=re.IGNORECASE)

        # Array element access: A(i) -> A[int(i)] for known arrays
        def _arr_repl(m):
            name = m.group(1).upper()
            pyname = self._py_name(name)
            if name in self.arrays:
                return pyname + "[int("
            if name in self.lists:
                return pyname + "[int("
            return m.group(0)

        s = re.sub(r"\b([A-Za-z_]\w*)\s*\(", _arr_repl, s)
        # Matching close-parens for arrays that got turned into brackets
        # would require a full parser; rely on eval handling it

        # Variable name substitution (longest first)
        for vn in sorted(self.variables.keys(), key=lambda x: -len(x)):
            if isinstance(self.variables[vn], dict):
                continue
            vr = str(self.variables[vn]) if _is_number(self.variables[vn]) \
                else '"%s"' % str(self.variables[vn]).replace('"', '\\"')
            if "$" in vn:
                s = re.sub(re.escape(vn) + r"(?=\s|$|[^A-Za-z0-9_$])", vr, s)
            else:
                s = re.sub(r"\b" + re.escape(vn) + r"\b", vr, s)

        return s

    @staticmethod
    def _py_name(name):
        """Make a BASIC variable name safe for Python eval namespace."""
        return name.replace("$", "_S").replace(".", "_DOT_")

    def _builtins(self):
        """Return dict of Python-callable builtins for eval."""
        return {
            # Math
            "_sqrt": math.sqrt, "abs": abs, "int": int, "float": float,
            "_round": lambda x, n=0: round(float(x), int(n)),
            "_sin": math.sin, "_cos": math.cos, "_tan": math.tan,
            "_atan": math.atan, "_log": math.log, "_exp": math.exp,
            "_sgn": lambda x: (1 if x > 0 else (-1 if x < 0 else 0)),
            "_ceil": lambda x: int(math.ceil(float(x))),
            "_floor": lambda x: int(math.floor(float(x))),
            "_clamp": lambda x, lo, hi: max(float(lo), min(float(hi), float(x))),
            "_lerp": lambda a, b, t: float(a) + (float(b) - float(a)) * float(t),
            "_log2": lambda x: math.log(float(x)) / math.log(2) if float(x) > 0 else 0,
            "_rnd": lambda *a: random.random() if not a else random.random() * float(a[0]),
            "max": max, "min": min, "round": round, "len": len, "str": str,
            # String
            "_left":  lambda s, n: str(s)[:int(n)],
            "_right": lambda s, n: str(s)[-int(n):] if int(n) > 0 else "",
            "_mid":   lambda s, st, ln: str(s)[int(st)-1:int(st)-1+int(ln)],
            "_ucase": lambda s: str(s).upper(),
            "_lcase": lambda s: str(s).lower(),
            "_trim":  lambda s: str(s).strip(),
            "_chr":   lambda x: chr(int(x)),
            "_str":   lambda x: str(x),
            "_asc":   lambda x: ord(str(x)[0]) if str(x) else 0,
            "_instr": lambda s, sub: str(s).find(str(sub)) + 1,
            "_replace_s": lambda s, old, new: str(s).replace(str(old), str(new)),
            "_repeat_s":  lambda s, n: str(s) * int(n),
            "_format_s":  lambda x, fmt="": format(x, fmt) if fmt else str(x),
            "_contains": lambda s, sub: str(sub) in str(s),
            "_tostr":  str,
            "_tonum":  lambda x: _safe_num(x),
            "_isnumber": lambda x: isinstance(x, (int, float)),
            "_isstring": lambda x: isinstance(x, str),
            "_length":   lambda x: len(x),
            "_haskey":   lambda d, k: k in d if isinstance(d, dict) else False,
            "_hex": lambda x: hex(int(x))[2:],
            "_bin": lambda x: bin(int(x))[2:],
            "_oct": lambda x: oct(int(x)).replace("0o", "").lstrip("0") or "0",
            # Boolean
            "True": True, "False": False,
        }

    def _eval_condition(self, cond):
        """Evaluate a BASIC boolean condition (handles = as ==)."""
        s = self._transform_expr(cond)
        # Replace single = with == (not <=, >=, !=, ==)
        s = re.sub(r"(?<!=)(?<![<>!])=(?!=)", "==", s)
        ns = dict(self._builtins())
        for k, v in self.variables.items():
            ns[self._py_name(k)] = v
        for k, v in self.lists.items():
            ns[self._py_name(k)] = v
        try:
            return bool(eval(s, {"__builtins__": {}}, ns))
        except Exception:
            return False

    # ------------------------------------------------------------------
    #  Program loading
    # ------------------------------------------------------------------

    def load_program(self, text):
        """Parse source text into program_lines; collect labels & DATA."""
        self._reset()
        self._preprocess_logo_defs(text)

        for raw in text.strip().split("\n"):
            line = raw.strip()
            m = re.match(r"^(\d+)\s+(.*)", line)
            if m:
                ln, cmd = int(m.group(1)), m.group(2).strip()
            else:
                ln, cmd = None, line
            self.program_lines.append((ln, cmd))

        # Collect labels and DATA in a second pass
        for i, (ln, cmd) in enumerate(self.program_lines):
            if not cmd:
                continue
            # PILOT / custom labels
            if cmd.startswith("*"):
                label = cmd[1:].strip()
                if label:
                    self.labels[label] = i
            elif re.match(r"^[A-Za-z_]\w*:$", cmd):
                if not (len(cmd) == 2 and cmd[0].isalpha()):
                    self.labels[cmd[:-1].strip()] = i
            # DATA
            dm = re.match(r"^DATA\s+(.*)", cmd, re.IGNORECASE)
            if dm:
                for val in self._split_data(dm.group(1)):
                    self._data_values.append(_safe_num(val))
            # SUB / FUNCTION definitions (record start lines)
            sm = re.match(r"^SUB\s+(\w+)\s*\(([^)]*)\)", cmd, re.IGNORECASE)
            if sm:
                name = sm.group(1).upper()
                params = [p.strip().upper() for p in sm.group(2).split(",") if p.strip()]
                self.sub_defs[name] = {"params": params, "start": i, "end": None}
            fm = re.match(r"^FUNCTION\s+(\w+)\s*\(([^)]*)\)", cmd, re.IGNORECASE)
            if fm:
                name = fm.group(1).upper()
                params = [p.strip().upper() for p in fm.group(2).split(",") if p.strip()]
                self.func_defs[name] = {"params": params, "start": i, "end": None}
            if cmd.upper().strip() == "END SUB":
                for sd in self.sub_defs.values():
                    if sd["end"] is None:
                        sd["end"] = i
                        break
            if cmd.upper().strip() == "END FUNCTION":
                for fd in self.func_defs.values():
                    if fd["end"] is None:
                        fd["end"] = i
                        break

    @staticmethod
    def _split_data(text):
        """Split a DATA line honouring quoted strings."""
        parts = []
        current = ""
        in_q = False
        for ch in text:
            if ch == '"':
                in_q = not in_q
            elif ch == "," and not in_q:
                parts.append(current.strip().strip('"'))
                current = ""
                continue
            else:
                current += ch
        if current.strip():
            parts.append(current.strip().strip('"'))
        return parts

    def _preprocess_logo_defs(self, text):
        """Collect TO ... END Logo procedure definitions."""
        lines = text.strip().split("\n")
        i = 0
        while i < len(lines):
            m = re.match(r"^\s*TO\s+(\w+)(.*)", lines[i], re.IGNORECASE)
            if m:
                name = m.group(1).lower()
                rest = m.group(2).strip()
                params = re.findall(r":(\w+)", rest)
                body = []
                i += 1
                while i < len(lines) and lines[i].strip().upper() != "END":
                    body.append(lines[i].strip())
                    i += 1
                self.logo_procs[name] = (params, body)
            i += 1

    # ------------------------------------------------------------------
    #  Program execution
    # ------------------------------------------------------------------

    def run(self, text):
        """Load and execute a TempleCode program."""
        self.load_program(text)
        self.running = True
        self.current_line = 0
        self._start_time = time.time()
        iterations = 0

        while (self.current_line < len(self.program_lines)
               and self.running
               and iterations < self.max_iterations):
            iterations += 1
            _ln, cmd = self.program_lines[self.current_line]
            if not cmd or not cmd.strip():
                self.current_line += 1
                continue

            try:
                result = self._execute(cmd)
            except Exception as exc:
                if self.try_stack:
                    fr = self.try_stack[-1]
                    cl = fr.get("catch_line")
                    if cl is not None:
                        self.last_error = str(exc)
                        self.variables["ERROR_S"] = str(exc)
                        _, cc = self.program_lines[cl]
                        cm = re.match(r"CATCH\s+(\w+)", cc.strip(), re.IGNORECASE)
                        if cm:
                            self.variables[cm.group(1).upper()] = str(exc)
                        self.current_line = cl
                        continue
                self.output_cb("ERROR at line %d: %s" % (self.current_line + 1, exc))
                break

            if result == "end":
                break
            elif result == "return":
                break
            elif result == "jump":
                continue
            elif isinstance(result, str) and result.startswith("jump:"):
                try:
                    target = int(result.split(":")[1])
                    self.current_line = target
                    continue
                except (ValueError, IndexError):
                    break
            elif result == "break":
                # find the end of the current loop
                self.current_line += 1
                continue
            elif result == "error":
                break

            self.current_line += 1

        if iterations >= self.max_iterations:
            self.output_cb("ERROR: Maximum iterations reached (possible infinite loop)")
        self.running = False

    # ------------------------------------------------------------------
    #  Top-level command dispatch
    # ------------------------------------------------------------------

    def _execute(self, command):
        command = command.strip()
        if not command:
            return "continue"

        # Comments
        if command.upper().startswith("REM") or command.startswith("'"):
            return "continue"
        if command.startswith("*") or command.startswith(";"):
            return "continue"

        # PILOT single-letter colon commands
        if len(command) > 1 and command[1] == ":" and command[0].isalpha():
            return self._dispatch_pilot(command)

        # Label definition (skip)
        if re.match(r"^[A-Za-z_]\w*:$", command):
            return "continue"

        upper = command.upper()
        first = command.split()[0].upper() if command.split() else ""

        # Logo procedure definition – skip the entire TO … END block
        if first == "TO":
            depth = 1
            self.current_line += 1
            while self.current_line < len(self.program_lines):
                _, nxt = self.program_lines[self.current_line]
                nu = nxt.strip().upper() if nxt else ""
                if nu.startswith("TO "):
                    depth += 1
                elif nu == "END":
                    depth -= 1
                    if depth == 0:
                        return "continue"  # main loop will ++
                self.current_line += 1
            return "continue"

        # Logo turtle commands
        logo_kw = {
            "FORWARD", "FD", "BACK", "BK", "BACKWARD",
            "LEFT", "LT", "RIGHT", "RT",
            "PENUP", "PU", "PENDOWN", "PD",
            "HOME", "CLEARSCREEN", "CS",
            "SHOWTURTLE", "ST", "HIDETURTLE", "HT",
            "SETXY", "SETPOS", "SETX", "SETY",
            "SETCOLOR", "SETCOLOUR", "SETPENCOLOR",
            "SETPENSIZE", "SETWIDTH",
            "SETHEADING", "SETH",
            "CIRCLE", "ARC", "DOT",
            "SQUARE", "TRIANGLE", "POLYGON", "STAR",
            "RECT", "RECTANGLE",
            "REPEAT",
            "LABEL",
        }
        if first in logo_kw:
            return self._dispatch_logo(command, first)

        # User-defined Logo procedure call
        if first.lower() in self.logo_procs:
            return self._call_logo_proc(first.lower(), command.split()[1:])

        # BASIC / Modern
        return self._dispatch_basic(command, first, upper)

    # ==================================================================
    #  PILOT sub-system
    # ==================================================================

    def _dispatch_pilot(self, command):
        letter = command[0].upper()
        cond = None
        arg = command[2:].strip() if len(command) > 2 else ""

        # Conditional prefix: TY: TN:
        if len(command) > 2 and command[1] in "YyNn" and command[2] == ":":
            cond = command[1].upper()
            letter = command[0].upper()
            arg = command[3:].strip() if len(command) > 3 else ""
        elif len(command) > 1 and command[1] == ":":
            letter = command[0].upper()
            arg = command[2:].strip() if len(command) > 2 else ""

        # Check conditional
        if cond == "Y" and not self.match_flag:
            return "continue"
        if cond == "N" and self.match_flag:
            return "continue"

        if letter == "T":
            return self._pilot_type(arg)
        elif letter == "A":
            return self._pilot_accept(arg)
        elif letter == "M":
            return self._pilot_match(arg)
        elif letter == "Y":
            if self.match_flag:
                return self._execute(arg) if arg else "continue"
            return "continue"
        elif letter == "N":
            if not self.match_flag:
                return self._execute(arg) if arg else "continue"
            return "continue"
        elif letter == "J":
            return self._pilot_jump(arg)
        elif letter == "C":
            return self._pilot_compute(arg)
        elif letter == "P":
            return self._pilot_pause(arg)
        elif letter == "E":
            self.running = False
            return "end"
        elif letter == "R":
            return self._pilot_remark()
        elif letter == "L":
            return self._pilot_label(arg)
        else:
            return "continue"

    def _pilot_type(self, text):
        """T: -- type text, resolving $VAR references."""
        resolved = self._resolve_pilot_vars(text)
        self.output_cb(resolved)
        return "continue"

    def _pilot_accept(self, arg):
        """A: -- accept user input."""
        prompt = ""
        if arg:
            prompt = self._resolve_pilot_vars(arg)
        value = self.input_cb(prompt if prompt else "")
        # Auto-convert numeric
        converted = _safe_num(value)
        self.variables["ANSWER"] = converted
        self.variables["INPUT"] = converted
        return "continue"

    def _pilot_match(self, pattern):
        """M: -- match pattern against ANSWER."""
        answer_str = str(self.variables.get("ANSWER", ""))
        patterns = [p.strip() for p in pattern.split(",")]
        self.match_flag = False
        for pat in patterns:
            if pat.upper() in answer_str.upper():
                self.match_flag = True
                break
        self._last_match_set = True
        return "continue"

    def _pilot_jump(self, label):
        """J: -- jump to *label."""
        label = label.strip()
        if label in self.labels:
            self.current_line = self.labels[label]
            return "jump"
        self.output_cb("ERROR: Label not found: %s" % label)
        return "continue"

    def _pilot_compute(self, stmt):
        """C: -- compute (execute a BASIC-style statement)."""
        return self._dispatch_basic(stmt.strip(), stmt.split()[0].upper() if stmt.split() else "", stmt.upper())

    def _pilot_pause(self, arg):
        """P: -- pause for N milliseconds."""
        try:
            ms = int(self.evaluate(arg)) if arg else 1000
            time.sleep(ms / 1000.0)
        except Exception:
            time.sleep(1.0)
        return "continue"

    def _pilot_remark(self):
        return "continue"

    def _pilot_label(self, arg):
        """L: -- declare label (already collected at load time)."""
        return "continue"

    def _resolve_pilot_vars(self, text):
        """Replace $VAR, {VAR}, and {expr} placeholders in PILOT text."""
        # {N} positional placeholders -- not applicable here, keep simple
        # $VAR
        def _dv(m):
            name = m.group(1).upper()
            return str(self.variables.get(name, ""))
        text = re.sub(r"\$([A-Za-z_]\w*)", _dv, text)
        # {VAR} or {expr}
        def _brace(m):
            inner = m.group(1).strip()
            up = inner.upper()
            if up in self.variables:
                return str(self.variables[up])
            try:
                return str(self.evaluate(inner))
            except Exception:
                return inner
        text = re.sub(r"\{([^}]+)\}", _brace, text)
        return text

    # ==================================================================
    #  Logo sub-system
    # ==================================================================

    def _dispatch_logo(self, command, first):
        args = command.split()[1:]
        argstr = " ".join(args)

        if first in ("FORWARD", "FD"):
            return self._logo_forward(argstr)
        elif first in ("BACK", "BK", "BACKWARD"):
            return self._logo_back(argstr)
        elif first in ("LEFT", "LT"):
            return self._logo_left(argstr)
        elif first in ("RIGHT", "RT"):
            return self._logo_right(argstr)
        elif first in ("PENUP", "PU"):
            self.turtle_pen = False
            return "continue"
        elif first in ("PENDOWN", "PD"):
            self.turtle_pen = True
            return "continue"
        elif first == "HOME":
            return self._logo_home()
        elif first in ("CLEARSCREEN", "CS"):
            self.canvas_cb("clear")
            self.turtle_x, self.turtle_y, self.turtle_heading = 0, 0, 0
            return "continue"
        elif first in ("HIDETURTLE", "HT"):
            self.turtle_visible = False
            self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                           heading=self.turtle_heading, visible=False)
            return "continue"
        elif first in ("SHOWTURTLE", "ST"):
            self.turtle_visible = True
            self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                           heading=self.turtle_heading, visible=True)
            return "continue"
        elif first in ("SETCOLOR", "SETCOLOUR", "SETPENCOLOR"):
            return self._logo_setcolor(argstr)
        elif first in ("SETPENSIZE", "SETWIDTH"):
            return self._logo_setpensize(argstr)
        elif first in ("SETXY", "SETPOS"):
            return self._logo_setxy(argstr)
        elif first in ("SETX",):
            return self._logo_setxy("%s %s" % (argstr, self.turtle_y))
        elif first in ("SETY",):
            return self._logo_setxy("%s %s" % (self.turtle_x, argstr))
        elif first in ("SETHEADING", "SETH"):
            return self._logo_setheading(argstr)
        elif first == "CIRCLE":
            return self._logo_circle(argstr)
        elif first == "ARC":
            return self._logo_arc(argstr)
        elif first == "DOT":
            return self._logo_dot(argstr)
        elif first == "SQUARE":
            return self._logo_shape(argstr, 4)
        elif first == "TRIANGLE":
            return self._logo_shape(argstr, 3)
        elif first == "POLYGON":
            return self._logo_polygon(argstr)
        elif first == "STAR":
            return self._logo_star(argstr)
        elif first in ("RECT", "RECTANGLE"):
            return self._logo_rect(argstr)
        elif first == "LABEL":
            return self._logo_label(argstr)
        elif first == "REPEAT":
            return self._logo_repeat(command)
        return "continue"

    # -- movement --

    def _logo_forward(self, argstr):
        dist = float(self.evaluate(argstr))
        rad = math.radians(90 - self.turtle_heading)
        ox, oy = self.turtle_x, self.turtle_y
        self.turtle_x += dist * math.cos(rad)
        self.turtle_y += dist * math.sin(rad)
        if self.turtle_pen:
            self.canvas_cb("line", x1=ox, y1=oy, x2=self.turtle_x, y2=self.turtle_y,
                           color=self.turtle_color, width=self.turtle_width)
        self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                       heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    def _logo_back(self, argstr):
        dist = float(self.evaluate(argstr))
        return self._logo_forward(str(-dist))

    def _logo_left(self, argstr):
        angle = float(self.evaluate(argstr))
        self.turtle_heading = (self.turtle_heading - angle) % 360
        self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                       heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    def _logo_right(self, argstr):
        angle = float(self.evaluate(argstr))
        self.turtle_heading = (self.turtle_heading + angle) % 360
        self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                       heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    def _logo_home(self):
        if self.turtle_pen:
            self.canvas_cb("line", x1=self.turtle_x, y1=self.turtle_y,
                           x2=0, y2=0, color=self.turtle_color, width=self.turtle_width)
        self.turtle_x = self.turtle_y = 0.0
        self.turtle_heading = 0.0
        self.canvas_cb("turtle", x=0, y=0, heading=0, visible=self.turtle_visible)
        return "continue"

    def _logo_setcolor(self, argstr):
        color = argstr.strip().strip('"').lower()
        if not color:
            return "continue"
        try:
            idx = int(color)
            palette = ["black", "red", "blue", "green", "purple", "orange", "teal", "magenta",
                       "white", "yellow", "cyan", "pink", "brown", "gray", "lime", "navy"]
            color = palette[idx % len(palette)]
        except (ValueError, IndexError):
            pass
        self.turtle_color = color
        return "continue"

    def _logo_setpensize(self, argstr):
        try:
            self.turtle_width = max(1, int(float(self.evaluate(argstr))))
        except Exception:
            pass
        return "continue"

    def _logo_setxy(self, argstr):
        parts = argstr.replace(",", " ").split()
        if len(parts) >= 2:
            x = float(self.evaluate(parts[0]))
            y = float(self.evaluate(parts[1]))
            if self.turtle_pen:
                self.canvas_cb("line", x1=self.turtle_x, y1=self.turtle_y,
                               x2=x, y2=y, color=self.turtle_color, width=self.turtle_width)
            self.turtle_x, self.turtle_y = x, y
            self.canvas_cb("turtle", x=x, y=y,
                           heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    def _logo_setheading(self, argstr):
        self.turtle_heading = float(self.evaluate(argstr)) % 360
        self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                       heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    # -- drawing primitives --

    def _logo_circle(self, argstr):
        try:
            r = float(self.evaluate(argstr))
        except Exception:
            return "continue"
        self.canvas_cb("circle", x=self.turtle_x, y=self.turtle_y,
                       radius=r, color=self.turtle_color, width=self.turtle_width)
        return "continue"

    def _logo_arc(self, argstr):
        parts = argstr.split()
        if len(parts) >= 2:
            angle = float(self.evaluate(parts[0]))
            radius = float(self.evaluate(parts[1]))
            self.canvas_cb("arc", x=self.turtle_x, y=self.turtle_y,
                           radius=radius, angle=angle,
                           heading=self.turtle_heading,
                           color=self.turtle_color, width=self.turtle_width)
        return "continue"

    def _logo_dot(self, argstr):
        sz = int(float(self.evaluate(argstr))) if argstr.strip() else 4
        self.canvas_cb("dot", x=self.turtle_x, y=self.turtle_y,
                       size=sz, color=self.turtle_color)
        return "continue"

    def _logo_shape(self, argstr, sides):
        """Draw a regular polygon at the turtle position."""
        sz = float(self.evaluate(argstr)) if argstr.strip() else 50
        saved = (self.turtle_x, self.turtle_y, self.turtle_heading)
        angle = 360.0 / sides
        for _ in range(sides):
            self._logo_forward(str(sz))
            self._logo_right(str(angle))
        self.turtle_x, self.turtle_y, self.turtle_heading = saved
        self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                       heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    def _logo_polygon(self, argstr):
        parts = argstr.split()
        sides = int(float(self.evaluate(parts[0]))) if parts else 6
        sz = float(self.evaluate(parts[1])) if len(parts) > 1 else 50
        self._logo_shape(str(sz), sides)
        return "continue"

    def _logo_star(self, argstr):
        parts = argstr.split()
        if len(parts) >= 2:
            n_points = int(float(self.evaluate(parts[0])))
            sz = float(self.evaluate(parts[1]))
        else:
            n_points = 5
            sz = float(self.evaluate(argstr)) if argstr.strip() else 50
        if n_points < 2:
            n_points = 5
        angle = 180 - (180.0 / n_points)
        saved = (self.turtle_x, self.turtle_y, self.turtle_heading)
        for _ in range(n_points):
            self._logo_forward(str(sz))
            self._logo_right(str(angle))
        self.turtle_x, self.turtle_y, self.turtle_heading = saved
        self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                       heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    def _logo_rect(self, argstr):
        parts = argstr.split()
        w = float(self.evaluate(parts[0])) if parts else 50
        h = float(self.evaluate(parts[1])) if len(parts) > 1 else w
        self.canvas_cb("rect", x=self.turtle_x, y=self.turtle_y,
                       width=w, height=h,
                       color=self.turtle_color, pen_width=self.turtle_width)
        return "continue"

    def _logo_label(self, argstr):
        # LABEL "text" [size]
        m = re.match(r'"([^"]*)"(?:\s+(\d+))?', argstr)
        if m:
            text = m.group(1)
            sz = int(m.group(2)) if m.group(2) else 12
        else:
            text = str(self.evaluate(argstr))
            sz = 12
        self.canvas_cb("text", x=self.turtle_x, y=self.turtle_y,
                       text=text, color=self.turtle_color, size=sz)
        return "continue"

    # -- REPEAT [...] --

    def _logo_repeat(self, command):
        """REPEAT n [cmd1 cmd2 ...]  (nested brackets okay)."""
        m = re.match(r"REPEAT\s+(.+?)\s*\[(.+)\]\s*$", command, re.IGNORECASE)
        if not m:
            return "continue"
        count = int(float(self.evaluate(m.group(1).strip())))
        body = m.group(2).strip()
        # Split body on spaces, but respect nested brackets
        cmds = self._split_repeat_body(body)
        for _ in range(count):
            for c in cmds:
                c = c.strip()
                if not c:
                    continue
                r = self._execute(c)
                if r in ("end", "break"):
                    return r
        return "continue"

    def _split_repeat_body(self, body):
        """Split REPEAT body into commands, respecting nested brackets."""
        cmds = []
        depth = 0
        current = ""
        i = 0
        while i < len(body):
            ch = body[i]
            if ch == "[":
                depth += 1
                current += ch
            elif ch == "]":
                depth -= 1
                current += ch
            elif ch == " " and depth == 0:
                # Check if we're at a command boundary
                # A command boundary is when the next word is a known command or
                # we've accumulated a complete command
                rest = body[i+1:].strip()
                first_next = rest.split()[0].upper() if rest.split() else ""
                # Only split if the current buffer looks like a complete command
                if current.strip():
                    # Check if current starts with a known command
                    first_cur = current.strip().split()[0].upper() if current.strip() else ""
                    known = {"FORWARD", "FD", "BACK", "BK", "LEFT", "LT", "RIGHT", "RT",
                             "PENUP", "PU", "PENDOWN", "PD", "SETCOLOR", "SETCOLOUR",
                             "SETPENSIZE", "HOME", "CIRCLE", "ARC", "DOT", "LABEL",
                             "SQUARE", "TRIANGLE", "POLYGON", "STAR", "RECT",
                             "REPEAT", "HIDETURTLE", "HT", "SHOWTURTLE", "ST",
                             "SETXY", "SETHEADING", "SETH", "SETPENCOLOR"}
                    if first_next in known:
                        cmds.append(current.strip())
                        current = ""
                        i += 1
                        continue
                current += ch
            else:
                current += ch
            i += 1
        if current.strip():
            cmds.append(current.strip())
        return cmds

    def _call_logo_proc(self, name, args):
        """Call a user-defined TO ... END procedure."""
        if name not in self.logo_procs:
            return "continue"
        params, body = self.logo_procs[name]
        # Evaluate args
        arg_vals = []
        for a in args:
            arg_vals.append(self.evaluate(a))
        # Build param map
        param_map = {}
        for i, p in enumerate(params):
            if i < len(arg_vals):
                param_map[":" + p.lower()] = arg_vals[i]
        # Execute body lines with parameter substitution
        for line in body:
            expanded = line
            for pname, pval in param_map.items():
                expanded = re.sub(re.escape(pname) + r"\b",
                                  str(pval) if _is_number(pval) else '"%s"' % pval,
                                  expanded, flags=re.IGNORECASE)
            r = self._execute(expanded)
            if r in ("end", "break"):
                return r
        return "continue"

    # ==================================================================
    #  BASIC sub-system
    # ==================================================================

    def _dispatch_basic(self, command, first, upper):
        cmd = first.upper() if first else ""

        if cmd in ("PRINT", "?"):
            return self._basic_print(command)
        elif cmd == "LET":
            return self._basic_let(command)
        elif cmd == "INPUT":
            return self._basic_input(command)
        elif cmd == "IF":
            return self._basic_if(command)
        elif cmd == "ELSE":
            return self._basic_else()
        elif cmd == "ELSEIF":
            return self._basic_elseif(command)
        elif cmd in ("ENDIF",):
            return "continue"
        elif cmd == "FOR":
            return self._basic_for(command)
        elif cmd == "NEXT":
            return self._basic_next(command)
        elif cmd == "WHILE":
            return self._basic_while(command)
        elif cmd == "WEND":
            return self._basic_wend()
        elif cmd == "DO":
            return self._basic_do(command)
        elif cmd == "LOOP":
            return self._basic_loop(command)
        elif cmd == "GOTO":
            return self._basic_goto(command)
        elif cmd == "GOSUB":
            return self._basic_gosub(command)
        elif cmd == "RETURN":
            return self._basic_return(command)
        elif cmd == "DIM":
            return self._basic_dim(command)
        elif cmd == "DATA":
            return "continue"
        elif cmd == "READ":
            return self._basic_read(command)
        elif cmd == "RESTORE":
            self._data_pos = 0
            return "continue"
        elif cmd == "RANDOMIZE":
            rest = command[len("RANDOMIZE"):].strip().upper()
            if not rest or rest == "TIMER":
                random.seed()
            else:
                try:
                    random.seed(int(float(self.evaluate(rest))))
                except Exception:
                    random.seed()
            return "continue"
        elif cmd in ("DELAY", "SLEEP"):
            return self._basic_delay(command)
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
        elif cmd == "CLS":
            self.canvas_cb("cls")
            return "continue"
        elif cmd == "BEEP":
            return "continue"
        elif cmd == "STOP" or (cmd == "END" and upper.strip() == "END"):
            self.running = False
            return "end"
        elif cmd == "END":
            eu = upper.strip()
            if eu == "END SELECT":
                if self.select_stack:
                    self.select_stack.pop()
                return "continue"
            elif eu in ("END IF", "ENDIF"):
                return "continue"
            elif eu == "END SUB":
                return "return"
            elif eu == "END FUNCTION":
                return "return"
            elif eu == "END TRY":
                if self.try_stack:
                    self.try_stack.pop()
                return "continue"
            self.running = False
            return "end"
        elif cmd == "BREAK":
            return "break"
        elif cmd == "EXIT":
            return self._basic_exit(command)
        elif cmd == "ON":
            return self._basic_on(command)

        # Modern extensions
        elif cmd == "SUB":
            return self._skip_block("END SUB")
        elif cmd == "FUNCTION":
            return self._skip_block("END FUNCTION")
        elif cmd == "CALL":
            return self._modern_call(command)
        elif cmd == "CONST":
            return self._modern_const(command)
        elif cmd == "FOREACH":
            return self._modern_foreach(command)
        elif cmd == "PRINTF":
            return self._modern_printf(command)
        elif cmd == "LIST":
            return self._modern_list(command)
        elif cmd == "PUSH":
            return self._modern_push(command)
        elif cmd == "POP":
            return self._modern_pop(command)
        elif cmd == "SORT":
            return self._modern_sort(command)
        elif cmd == "REVERSE":
            return self._modern_reverse(command)
        elif cmd == "DICT":
            return self._modern_dict(command)
        elif cmd == "SET":
            return self._modern_set(command)
        elif cmd == "GET":
            return self._modern_get(command)
        elif cmd == "DELETE":
            return self._modern_delete(command)
        elif cmd == "TRY":
            return self._modern_try()
        elif cmd == "CATCH":
            return self._modern_catch()
        elif cmd == "THROW":
            return self._modern_throw(command)
        elif cmd == "ASSERT":
            return self._modern_assert(command)
        elif cmd == "TYPEOF":
            return self._modern_typeof(command)
        elif cmd == "ENUM":
            return self._modern_enum(command)
        elif cmd == "STRUCT":
            return "continue"  # simplified: no struct support
        elif cmd == "LAMBDA":
            return self._modern_lambda(command)
        elif cmd == "MAP":
            return self._modern_map(command)
        elif cmd == "FILTER":
            return self._modern_filter(command)
        elif cmd == "REDUCE":
            return self._modern_reduce(command)
        elif cmd == "JSON":
            return self._modern_json(command)
        elif cmd == "REGEX":
            return self._modern_regex(command)
        elif cmd == "SPLIT":
            return self._modern_split(command)
        elif cmd == "JOIN":
            return self._modern_join(command)

        # Direct assignment: X = 5
        elif "=" in command and not command.upper().startswith("IF"):
            return self._basic_let("LET " + command)
        else:
            # Try evaluating as assignment with dotted names (dict.key = val)
            self.output_cb("Unknown command: %s" % command)
            return "continue"

    # ------------------------------------------------------------------
    #  BASIC commands
    # ------------------------------------------------------------------

    def _basic_print(self, command):
        text = re.sub(r"^(PRINT|\?)\s*", "", command, flags=re.IGNORECASE).strip()
        if not text:
            self.output_cb("")
            return "continue"

        # Split on ; keeping track of suppress-newline
        suppress = text.endswith(";")
        if suppress:
            text = text[:-1].strip()

        # Handle TAB and SPC
        parts = re.split(r"(?:;|,)", text)
        result = ""
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                if i > 0:
                    result += "  "
                continue
            val = self.evaluate(part)
            result += str(val)

        self.output_cb(result)
        return "continue"

    def _basic_let(self, command):
        text = re.sub(r"^LET\s+", "", command, flags=re.IGNORECASE).strip()
        m = re.match(r"(\w+(?:\$)?)\s*\(([^)]+)\)\s*=\s*(.*)", text)
        if m:
            # Array assignment: A(i) = val
            name = m.group(1).upper()
            idx = int(float(self.evaluate(m.group(2).strip())))
            val = self.evaluate(m.group(3).strip())
            if name in self.arrays:
                self.arrays[name][idx] = val
            elif name in self.lists:
                lst = self.lists[name]
                while len(lst) <= idx:
                    lst.append(0)
                lst[idx] = val
            self.variables[name] = self.arrays.get(name, self.lists.get(name))
            return "continue"

        # Dotted assignment: DICT.KEY = val
        m = re.match(r"(\w+)\.(\w+)\s*=\s*(.*)", text)
        if m:
            dname = m.group(1).upper()
            key = m.group(2)
            val = self.evaluate(m.group(3).strip())
            if dname in self.dicts:
                self.dicts[dname][key] = val
            return "continue"

        m = re.match(r"(\w+(?:\$)?)\s*=\s*(.*)", text)
        if not m:
            return "continue"
        var_name = m.group(1).strip().upper()
        if var_name in self.constants:
            self.output_cb("ERROR: Cannot reassign constant %s" % var_name)
            return "continue"
        val = self.evaluate(m.group(2).strip())
        self.variables[var_name] = val
        return "continue"

    def _basic_input(self, command):
        text = re.sub(r"^INPUT\s+", "", command, flags=re.IGNORECASE).strip()
        prompt = "? "
        var_name = text

        # INPUT "prompt"; VAR  or  INPUT "prompt", VAR
        m = re.match(r'"([^"]*)"[;,]\s*(\w+\$?)', text)
        if m:
            prompt = m.group(1) + " "
            var_name = m.group(2)
        else:
            # INPUT "prompt" VAR (no separator)
            m = re.match(r'"([^"]*)"\s+(\w+\$?)', text)
            if m:
                prompt = m.group(1) + " "
                var_name = m.group(2)

        var_name = var_name.strip().upper()
        value = self.input_cb(prompt)
        value = _safe_num(value)
        self.variables[var_name] = value
        return "continue"

    def _basic_if(self, command):
        m = re.match(r"IF\s+(.+?)\s+THEN\s*(.*)", command, re.IGNORECASE)
        if not m:
            return "continue"
        cond = m.group(1)
        then_rest = m.group(2).strip()

        # Multi-line block IF
        if not then_rest:
            if self._eval_condition(cond):
                return "continue"
            else:
                depth = 1
                self.current_line += 1
                while self.current_line < len(self.program_lines):
                    _, lt = self.program_lines[self.current_line]
                    lu = lt.strip().upper() if lt else ""
                    if lu.startswith("IF ") and ("THEN" in lu):
                        depth += 1
                    elif lu == "ELSE" and depth == 1:
                        return "continue"
                    elif lu.startswith("ELSEIF ") and depth == 1:
                        ei = re.match(r"ELSEIF\s+(.+?)\s+THEN", lt.strip(), re.IGNORECASE)
                        if ei and self._eval_condition(ei.group(1)):
                            return "continue"
                    elif lu in ("END IF", "ENDIF"):
                        depth -= 1
                        if depth == 0:
                            return "continue"
                    self.current_line += 1
                return "continue"

        # Single-line IF ... THEN ... [ELSE ...]
        parts = re.split(r"\bELSE\b", then_rest, flags=re.IGNORECASE)
        then_part = parts[0].strip()
        else_part = parts[1].strip() if len(parts) > 1 else None

        if self._eval_condition(cond):
            if re.match(r"^\d+$", then_part):
                return self._basic_goto("GOTO %s" % then_part)
            return self._execute(then_part)
        elif else_part:
            if re.match(r"^\d+$", else_part):
                return self._basic_goto("GOTO %s" % else_part)
            return self._execute(else_part)
        return "continue"

    def _basic_else(self):
        depth = 1
        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            lu = lt.strip().upper() if lt else ""
            if lu.startswith("IF ") and ("THEN" in lu):
                depth += 1
            elif lu in ("END IF", "ENDIF"):
                depth -= 1
                if depth == 0:
                    return "continue"
            self.current_line += 1
        return "continue"

    def _basic_elseif(self, command):
        # Reached ELSEIF after a true IF block executed -> skip to END IF
        return self._basic_else()

    def _basic_for(self, command):
        m = re.match(r"FOR\s+(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$",
                     command, re.IGNORECASE)
        if not m:
            self.output_cb("FOR syntax error: %s" % command)
            return "continue"
        var = m.group(1).upper()
        start = float(self.evaluate(m.group(2)))
        end = float(self.evaluate(m.group(3)))
        step = float(self.evaluate(m.group(4))) if m.group(4) else 1
        if step == 0:
            self.output_cb("FOR error: STEP cannot be 0")
            return "continue"
        val = int(start) if start == int(start) else start
        self.variables[var] = val
        self.for_stack.append({
            "var": var, "end": end, "step": step,
            "line": self.current_line
        })
        # If start already past end, skip to NEXT
        if (step > 0 and val > end) or (step < 0 and val < end):
            return self._skip_to_next(var)
        return "continue"

    def _basic_next(self, command):
        rest = re.sub(r"^NEXT\s*", "", command, flags=re.IGNORECASE).strip()
        if not self.for_stack:
            return "continue"
        frame = self.for_stack[-1]
        var = frame["var"]
        step = frame["step"]
        end = frame["end"]
        self.variables[var] = self.variables[var] + step
        # Adjust to int when possible
        v = self.variables[var]
        if isinstance(v, float) and v == int(v):
            self.variables[var] = int(v)
        v = self.variables[var]

        if (step > 0 and v > end) or (step < 0 and v < end):
            self.for_stack.pop()
            return "continue"
        # Jump to the line AFTER the FOR statement (first body line),
        # not to the FOR itself — re-executing FOR would reset the
        # counter and push duplicate stack frames.
        self.current_line = frame["line"] + 1
        return "jump"

    def _skip_to_next(self, var):
        depth = 1
        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            lu = lt.strip().upper() if lt else ""
            if lu.startswith("FOR "):
                depth += 1
            elif lu.startswith("NEXT"):
                depth -= 1
                if depth == 0:
                    if self.for_stack and self.for_stack[-1]["var"] == var:
                        self.for_stack.pop()
                    return "continue"
            self.current_line += 1
        return "continue"

    def _basic_while(self, command):
        cond_text = re.sub(r"^WHILE\s+", "", command, flags=re.IGNORECASE).strip()
        if self._eval_condition(cond_text):
            self.while_stack.append({
                "line": self.current_line, "cond": cond_text
            })
            return "continue"
        else:
            depth = 1
            self.current_line += 1
            while self.current_line < len(self.program_lines):
                _, lt = self.program_lines[self.current_line]
                lu = lt.strip().upper() if lt else ""
                if lu.startswith("WHILE "):
                    depth += 1
                elif lu == "WEND":
                    depth -= 1
                    if depth == 0:
                        return "continue"
                self.current_line += 1
            return "continue"

    def _basic_wend(self):
        if not self.while_stack:
            return "continue"
        frame = self.while_stack[-1]
        if self._eval_condition(frame["cond"]):
            self.current_line = frame["line"]
            return "jump"
        self.while_stack.pop()
        return "continue"

    def _basic_do(self, command):
        rest = re.sub(r"^DO\s*", "", command, flags=re.IGNORECASE).strip().upper()
        self.do_stack.append({"line": self.current_line, "cond": rest})
        if rest.startswith("WHILE "):
            cond = rest[6:].strip()
            if not self._eval_condition(cond):
                return self._skip_to_loop()
        return "continue"

    def _basic_loop(self, command):
        rest = re.sub(r"^LOOP\s*", "", command, flags=re.IGNORECASE).strip().upper()
        if not self.do_stack:
            return "continue"
        frame = self.do_stack[-1]
        if rest.startswith("WHILE "):
            cond = rest[6:].strip()
            if self._eval_condition(cond):
                self.current_line = frame["line"]
                return "jump"
        elif rest.startswith("UNTIL "):
            cond = rest[6:].strip()
            if not self._eval_condition(cond):
                self.current_line = frame["line"]
                return "jump"
        else:
            # Plain LOOP -- just loops back
            fc = frame.get("cond", "")
            if fc.startswith("WHILE "):
                cond = fc[6:].strip()
                if self._eval_condition(cond):
                    self.current_line = frame["line"]
                    return "jump"
            elif fc.startswith("UNTIL "):
                cond = fc[6:].strip()
                if not self._eval_condition(cond):
                    self.current_line = frame["line"]
                    return "jump"
            else:
                self.current_line = frame["line"]
                return "jump"
        self.do_stack.pop()
        return "continue"

    def _skip_to_loop(self):
        depth = 1
        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            lu = lt.strip().upper() if lt else ""
            if lu.startswith("DO"):
                depth += 1
            elif lu.startswith("LOOP"):
                depth -= 1
                if depth == 0:
                    if self.do_stack:
                        self.do_stack.pop()
                    return "continue"
            self.current_line += 1
        return "continue"

    def _basic_goto(self, command):
        target = re.sub(r"^GOTO\s+", "", command, flags=re.IGNORECASE).strip()
        # Line number
        try:
            target_num = int(target)
            for i, (ln, _) in enumerate(self.program_lines):
                if ln == target_num:
                    self.current_line = i
                    return "jump"
        except ValueError:
            pass
        # Label
        if target in self.labels:
            self.current_line = self.labels[target]
            return "jump"
        self.output_cb("ERROR: GOTO target not found: %s" % target)
        return "continue"

    def _basic_gosub(self, command):
        target = re.sub(r"^GOSUB\s+", "", command, flags=re.IGNORECASE).strip()
        self.gosub_stack.append(self.current_line)
        return self._basic_goto("GOTO %s" % target)

    def _basic_return(self, command):
        # Check for FUNCTION return value
        rest = re.sub(r"^RETURN\s*", "", command, flags=re.IGNORECASE).strip()
        if rest:
            self.return_value = self.evaluate(rest)
        if self.call_stack:
            frame = self.call_stack.pop()
            self.current_line = frame["return_line"]
            # Restore variables except return value
            for k, v in frame.get("saved_vars", {}).items():
                self.variables[k] = v
            return "jump"
        if self.gosub_stack:
            self.current_line = self.gosub_stack.pop()
            return "continue"  # will be incremented
        return "continue"

    def _basic_dim(self, command):
        m = re.match(r"DIM\s+(\w+)\s*\((\d+)\)", command, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            size = int(m.group(2)) + 1
            self.arrays[name] = dict((i, 0) for i in range(size))
            self.variables[name] = self.arrays[name]
        return "continue"

    def _basic_read(self, command):
        vars_str = re.sub(r"^READ\s+", "", command, flags=re.IGNORECASE).strip()
        for vname in vars_str.split(","):
            vname = vname.strip().upper()
            if self._data_pos < len(self._data_values):
                self.variables[vname] = self._data_values[self._data_pos]
                self._data_pos += 1
            else:
                self.output_cb("ERROR: Out of DATA")
                break
        return "continue"

    def _basic_delay(self, command):
        rest = re.sub(r"^(DELAY|SLEEP)\s*", "", command, flags=re.IGNORECASE).strip()
        try:
            ms = int(float(self.evaluate(rest))) if rest else 1000
            time.sleep(ms / 1000.0)
        except Exception:
            time.sleep(1.0)
        return "continue"

    def _basic_select(self, command):
        m = re.match(r"SELECT\s+CASE\s+(.*)", command, re.IGNORECASE)
        if not m:
            return "continue"
        val = self.evaluate(m.group(1).strip())
        self.select_stack.append({"value": val, "matched": False})
        return "continue"

    def _basic_case(self, command):
        if not self.select_stack:
            return "continue"
        frame = self.select_stack[-1]
        if frame["matched"]:
            return self._skip_to_end_select()

        cu = command.upper().strip()
        if cu.startswith("CASE ELSE"):
            frame["matched"] = True
            return "continue"

        case_text = re.sub(r"^CASE\s+", "", command, flags=re.IGNORECASE).strip()
        case_val = self.evaluate(case_text)
        if str(case_val) == str(frame["value"]) or case_val == frame["value"]:
            frame["matched"] = True
            return "continue"
        # Skip to next CASE
        return self._skip_to_next_case()

    def _skip_to_next_case(self):
        depth = 0
        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            lu = lt.strip().upper() if lt else ""
            if lu.startswith("SELECT CASE"):
                depth += 1
            elif lu == "END SELECT":
                if depth == 0:
                    if self.select_stack:
                        self.select_stack.pop()
                    return "continue"
                depth -= 1
            elif lu.startswith("CASE") and depth == 0:
                return self._basic_case(lt.strip())
            self.current_line += 1
        return "continue"

    def _skip_to_end_select(self):
        depth = 0
        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            lu = lt.strip().upper() if lt else ""
            if lu.startswith("SELECT CASE"):
                depth += 1
            elif lu == "END SELECT":
                if depth == 0:
                    if self.select_stack:
                        self.select_stack.pop()
                    return "continue"
                depth -= 1
            self.current_line += 1
        return "continue"

    def _basic_swap(self, command):
        m = re.match(r"SWAP\s+(\w+)\s*,\s*(\w+)", command, re.IGNORECASE)
        if m:
            a, b = m.group(1).upper(), m.group(2).upper()
            va = self.variables.get(a, 0)
            vb = self.variables.get(b, 0)
            self.variables[a] = vb
            self.variables[b] = va
        return "continue"

    def _basic_incr_decr(self, command, delta):
        m = re.match(r"(?:INCR|DECR)\s+(\w+)(?:\s*,?\s*(.+))?", command, re.IGNORECASE)
        if m:
            var = m.group(1).upper()
            amt = delta
            if m.group(2):
                amt = delta * abs(float(self.evaluate(m.group(2).strip())))
            cur = self.variables.get(var, 0)
            new = cur + amt
            if isinstance(new, float) and new == int(new):
                new = int(new)
            self.variables[var] = new
        return "continue"

    def _basic_exit(self, command):
        rest = command.upper().replace("EXIT", "").strip()
        if rest in ("FOR",):
            if self.for_stack:
                frame = self.for_stack.pop()
                return self._skip_to_next(frame["var"])
        elif rest in ("WHILE",):
            if self.while_stack:
                self.while_stack.pop()
                # skip to WEND
                depth = 1
                self.current_line += 1
                while self.current_line < len(self.program_lines):
                    _, lt = self.program_lines[self.current_line]
                    lu = lt.strip().upper() if lt else ""
                    if lu.startswith("WHILE "):
                        depth += 1
                    elif lu == "WEND":
                        depth -= 1
                        if depth == 0:
                            return "continue"
                    self.current_line += 1
        elif rest in ("DO",):
            if self.do_stack:
                self.do_stack.pop()
                return self._skip_to_loop()
        return "continue"

    def _basic_on(self, command):
        m = re.match(r"ON\s+(.+?)\s+GOTO\s+(.+)", command, re.IGNORECASE)
        if m:
            idx = int(float(self.evaluate(m.group(1))))
            targets = [t.strip() for t in m.group(2).split(",")]
            if 1 <= idx <= len(targets):
                return self._basic_goto("GOTO %s" % targets[idx - 1])
        return "continue"

    def _skip_block(self, end_marker):
        """Skip from SUB/FUNCTION definition to its END."""
        eu = end_marker.upper()
        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            if lt and lt.strip().upper() == eu:
                return "continue"
            self.current_line += 1
        return "continue"

    # ------------------------------------------------------------------
    #  Modern extensions
    # ------------------------------------------------------------------

    def _modern_call(self, command):
        rest = re.sub(r"^CALL\s+", "", command, flags=re.IGNORECASE).strip()
        m = re.match(r"(\w+)\s*\(([^)]*)\)", rest)
        if not m:
            m = re.match(r"(\w+)(.*)", rest)
        if not m:
            return "continue"
        name = m.group(1).upper()
        args_str = m.group(2).strip().strip("()") if m.group(2) else ""
        args = [a.strip() for a in args_str.split(",") if a.strip()] if args_str else []
        arg_vals = [self.evaluate(a) for a in args]

        # Check SUB definitions
        if name in self.sub_defs:
            defn = self.sub_defs[name]
            saved = dict(self.variables)
            for i, p in enumerate(defn["params"]):
                if i < len(arg_vals):
                    self.variables[p] = arg_vals[i]
            self.call_stack.append({
                "return_line": self.current_line,
                "saved_vars": saved
            })
            self.current_line = defn["start"]
            return "jump"

        # Check FUNCTION definitions
        if name in self.func_defs:
            return self._call_function(name, arg_vals)

        self.output_cb("ERROR: Undefined SUB/FUNCTION: %s" % name)
        return "continue"

    def _call_function(self, name, arg_vals):
        """Execute a FUNCTION and return its value."""
        defn = self.func_defs[name]
        saved = dict(self.variables)
        for i, p in enumerate(defn["params"]):
            if i < len(arg_vals):
                self.variables[p] = arg_vals[i]
        self.return_value = None
        # Execute body lines
        line = defn["start"] + 1
        while line < defn.get("end", len(self.program_lines)):
            _, cmd = self.program_lines[line]
            if cmd:
                r = self._execute(cmd.strip())
                if r == "return":
                    break
            line += 1
        # Restore variables
        rv = self.return_value
        self.variables = saved
        if rv is not None:
            self.return_value = rv
        return "continue"

    def _modern_const(self, command):
        m = re.match(r"CONST\s+(\w+)\s*=\s*(.*)", command, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            val = self.evaluate(m.group(2).strip())
            self.variables[name] = val
            self.constants.add(name)
        return "continue"

    def _modern_foreach(self, command):
        m = re.match(r"FOREACH\s+(\w+)\s+IN\s+(\w+)", command, re.IGNORECASE)
        if not m:
            return "continue"
        iter_var = m.group(1).upper()
        list_name = m.group(2).upper()
        items = self.lists.get(list_name, [])
        if not isinstance(items, list):
            items = self.variables.get(list_name, [])
            if not isinstance(items, list):
                return "continue"

        # Collect body until NEXT
        body_start = self.current_line + 1
        body_end = body_start
        depth = 1
        idx = body_start
        while idx < len(self.program_lines):
            _, lt = self.program_lines[idx]
            lu = lt.strip().upper() if lt else ""
            if lu.startswith("FOREACH "):
                depth += 1
            elif lu.startswith("NEXT"):
                depth -= 1
                if depth == 0:
                    body_end = idx
                    break
            idx += 1

        # Execute body for each item
        for item in items:
            self.variables[iter_var] = item
            line = body_start
            while line < body_end:
                _, cmd = self.program_lines[line]
                if cmd and cmd.strip():
                    r = self._execute(cmd.strip())
                    if r in ("end", "break"):
                        self.current_line = body_end
                        return "continue" if r == "break" else r
                    if r == "jump":
                        continue
                line += 1

        self.current_line = body_end
        return "continue"

    def _modern_printf(self, command):
        rest = re.sub(r"^PRINTF\s+", "", command, flags=re.IGNORECASE).strip()
        # PRINTF "format", arg1, arg2 ...
        m = re.match(r'"([^"]*)"(?:\s*,\s*(.*))?', rest)
        if m:
            fmt = m.group(1)
            args_raw = m.group(2) or ""
            if args_raw:
                args = [self.evaluate(a.strip()) for a in args_raw.split(",")]
            else:
                args = []
            # Replace {N} positional and {VAR} named
            result = fmt
            for i, a in enumerate(args):
                result = result.replace("{%d}" % i, str(a))
            # {VARNAME} references
            def _vr(mv):
                n = mv.group(1).upper()
                return str(self.variables.get(n, mv.group(0)))
            result = re.sub(r"\{([A-Za-z_]\w*)\}", _vr, result)
            self.output_cb(result)
        else:
            # Fallback: just resolve and print
            self.output_cb(self._resolve_pilot_vars(rest.strip('"')))
        return "continue"

    def _modern_list(self, command):
        m = re.match(r"LIST\s+(\w+)(?:\s*=\s*(.*))?", command, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            init = m.group(2)
            if init:
                items = [self.evaluate(x.strip()) for x in init.split(",")]
                self.lists[name] = items
            else:
                self.lists[name] = []
            self.variables[name] = self.lists[name]
        return "continue"

    def _modern_push(self, command):
        m = re.match(r"PUSH\s+(\w+)\s*,\s*(.*)", command, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            val = self.evaluate(m.group(2).strip())
            if name in self.lists:
                self.lists[name].append(val)
        return "continue"

    def _modern_pop(self, command):
        m = re.match(r"POP\s+(\w+)(?:\s+INTO\s+(\w+))?", command, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            target = m.group(2)
            if name in self.lists and self.lists[name]:
                val = self.lists[name].pop()
                if target:
                    self.variables[target.upper()] = val
        return "continue"

    def _modern_sort(self, command):
        name = re.sub(r"^SORT\s+", "", command, flags=re.IGNORECASE).strip().upper()
        if name in self.lists:
            try:
                self.lists[name].sort()
            except TypeError:
                self.lists[name].sort(key=str)
        return "continue"

    def _modern_reverse(self, command):
        name = re.sub(r"^REVERSE\s+", "", command, flags=re.IGNORECASE).strip().upper()
        if name in self.lists:
            self.lists[name].reverse()
        return "continue"

    def _modern_dict(self, command):
        m = re.match(r"DICT\s+(\w+)", command, re.IGNORECASE)
        if m:
            self.dicts[m.group(1).upper()] = {}
        return "continue"

    def _modern_set(self, command):
        # SET DICT, KEY, VALUE  or  SET DICT.KEY = VALUE
        rest = re.sub(r"^SET\s+", "", command, flags=re.IGNORECASE).strip()
        m = re.match(r"(\w+)\.(\w+)\s*=\s*(.*)", rest)
        if m:
            dname = m.group(1).upper()
            key = m.group(2)
            val = self.evaluate(m.group(3).strip())
            if dname in self.dicts:
                self.dicts[dname][key] = val
            return "continue"
        m = re.match(r"(\w+)\s*,\s*\"?([^,\"]+)\"?\s*,\s*(.*)", rest)
        if m:
            dname = m.group(1).upper()
            key = m.group(2).strip()
            val = self.evaluate(m.group(3).strip())
            if dname in self.dicts:
                self.dicts[dname][key] = val
        return "continue"

    def _modern_get(self, command):
        rest = re.sub(r"^GET\s+", "", command, flags=re.IGNORECASE).strip()
        # GET DICT.KEY INTO VAR
        m = re.match(r"(\w+)\.(\w+)\s+INTO\s+(\w+)", rest, re.IGNORECASE)
        if m:
            dname = m.group(1).upper()
            key = m.group(2)
            var = m.group(3).upper()
            if dname in self.dicts:
                self.variables[var] = self.dicts[dname].get(key, "")
            return "continue"
        # GET DICT, KEY, VAR
        m = re.match(r'(\w+)\s*,\s*"?([^,"]+)"?\s*,\s*(\w+)', rest)
        if m:
            dname = m.group(1).upper()
            key = m.group(2).strip()
            var = m.group(3).upper()
            if dname in self.dicts:
                self.variables[var] = self.dicts[dname].get(key, "")
        return "continue"

    def _modern_delete(self, command):
        rest = re.sub(r"^DELETE\s+", "", command, flags=re.IGNORECASE).strip()
        m = re.match(r"(\w+)\s*,\s*\"?([^\"]+)\"?", rest)
        if m:
            dname = m.group(1).upper()
            key = m.group(2).strip()
            if dname in self.dicts and key in self.dicts[dname]:
                del self.dicts[dname][key]
        return "continue"

    def _modern_try(self):
        # Scan for CATCH line
        catch_line = None
        end_line = None
        depth = 0
        for i in range(self.current_line + 1, len(self.program_lines)):
            _, lt = self.program_lines[i]
            lu = lt.strip().upper() if lt else ""
            if lu == "TRY":
                depth += 1
            elif lu.startswith("CATCH") and depth == 0:
                catch_line = i
            elif lu == "END TRY":
                if depth == 0:
                    end_line = i
                    break
                depth -= 1
        self.try_stack.append({
            "catch_line": catch_line, "end_line": end_line
        })
        return "continue"

    def _modern_catch(self):
        # Skip CATCH block (reached when TRY body completed without error)
        if self.try_stack:
            frame = self.try_stack[-1]
            end_line = frame.get("end_line")
            if end_line is not None:
                self.current_line = end_line
                return "continue"
        return "continue"

    def _modern_throw(self, command):
        rest = re.sub(r"^THROW\s+", "", command, flags=re.IGNORECASE).strip()
        msg = str(self.evaluate(rest))
        raise RuntimeError(msg)

    def _modern_assert(self, command):
        rest = re.sub(r"^ASSERT\s+", "", command, flags=re.IGNORECASE).strip()
        m = re.match(r"(.+?)\s*,\s*\"([^\"]+)\"", rest)
        if m:
            cond = m.group(1)
            msg = m.group(2)
        else:
            cond = rest
            msg = "Assertion failed"
        if not self._eval_condition(cond):
            raise RuntimeError(msg)
        return "continue"

    def _modern_typeof(self, command):
        m = re.match(r"TYPEOF\s+(\w+)\s+INTO\s+(\w+)", command, re.IGNORECASE)
        if m:
            val = self.variables.get(m.group(1).upper(), "")
            if isinstance(val, int):
                t = "INTEGER"
            elif isinstance(val, float):
                t = "FLOAT"
            elif isinstance(val, str):
                t = "STRING"
            elif isinstance(val, list):
                t = "LIST"
            elif isinstance(val, dict):
                t = "DICT"
            else:
                t = "UNKNOWN"
            self.variables[m.group(2).upper()] = t
        return "continue"

    def _modern_enum(self, command):
        m = re.match(r"ENUM\s+(\w+)\s*=\s*(.*)", command, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            values = [v.strip().upper() for v in m.group(2).split(",")]
            for i, v in enumerate(values):
                self.variables[v] = i
                self.constants.add(v)
        return "continue"

    def _modern_lambda(self, command):
        m = re.match(r"LAMBDA\s+(\w+)\s*\(([^)]*)\)\s*=\s*(.*)", command, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            params = [p.strip().upper() for p in m.group(2).split(",") if p.strip()]
            body = m.group(3).strip()
            self.func_defs[name] = {
                "params": params,
                "lambda_body": body,
                "start": -1, "end": -1
            }
        return "continue"

    def _eval_lambda(self, name, args):
        """Evaluate a lambda function."""
        defn = self.func_defs.get(name)
        if not defn or "lambda_body" not in defn:
            return 0
        saved = dict(self.variables)
        for i, p in enumerate(defn["params"]):
            if i < len(args):
                self.variables[p] = args[i]
        result = self.evaluate(defn["lambda_body"])
        self.variables = saved
        return result

    def _modern_map(self, command):
        m = re.match(r"MAP\s+(\w+)\s+ON\s+(\w+)\s+INTO\s+(\w+)", command, re.IGNORECASE)
        if m:
            func_name = m.group(1).upper()
            src = m.group(2).upper()
            dest = m.group(3).upper()
            items = self.lists.get(src, [])
            result = [self._eval_lambda(func_name, [x]) for x in items]
            self.lists[dest] = result
            self.variables[dest] = result
        return "continue"

    def _modern_filter(self, command):
        m = re.match(r"FILTER\s+(\w+)\s+ON\s+(\w+)\s+INTO\s+(\w+)", command, re.IGNORECASE)
        if m:
            func_name = m.group(1).upper()
            src = m.group(2).upper()
            dest = m.group(3).upper()
            items = self.lists.get(src, [])
            result = [x for x in items if self._eval_lambda(func_name, [x])]
            self.lists[dest] = result
            self.variables[dest] = result
        return "continue"

    def _modern_reduce(self, command):
        m = re.match(r"REDUCE\s+(\w+)\s+ON\s+(\w+)\s+INTO\s+(\w+)\s+FROM\s+(.*)",
                     command, re.IGNORECASE)
        if m:
            func_name = m.group(1).upper()
            src = m.group(2).upper()
            dest = m.group(3).upper()
            init = self.evaluate(m.group(4).strip())
            items = self.lists.get(src, [])
            acc = init
            for x in items:
                acc = self._eval_lambda(func_name, [acc, x])
            self.variables[dest] = acc
        return "continue"

    def _modern_json(self, command):
        rest = re.sub(r"^JSON\s+", "", command, flags=re.IGNORECASE).strip()
        if not json:
            self.output_cb("ERROR: JSON not available")
            return "continue"
        mu = rest.upper()
        if mu.startswith("STRINGIFY"):
            m = re.match(r"STRINGIFY\s+(\w+)\s+INTO\s+(\w+)", rest, re.IGNORECASE)
            if m:
                dname = m.group(1).upper()
                var = m.group(2).upper()
                d = self.dicts.get(dname, {})
                self.variables[var] = json.dumps(d)
        elif mu.startswith("PARSE"):
            m = re.match(r"PARSE\s+(\w+)\s+INTO\s+(\w+)", rest, re.IGNORECASE)
            if m:
                src_var = m.group(1).upper()
                dest = m.group(2).upper()
                src_val = str(self.variables.get(src_var, "{}"))
                try:
                    parsed = json.loads(src_val)
                    if isinstance(parsed, dict):
                        self.dicts[dest] = parsed
                except Exception:
                    pass
        return "continue"

    def _modern_regex(self, command):
        rest = re.sub(r"^REGEX\s+", "", command, flags=re.IGNORECASE).strip()
        m = re.match(r"MATCH\s+(.+?)\s+IN\s+(.+?)\s+INTO\s+(\w+)", rest, re.IGNORECASE)
        if m:
            pattern = str(self.evaluate(m.group(1).strip()))
            text = str(self.evaluate(m.group(2).strip()))
            var = m.group(3).upper()
            hit = re.search(pattern, text, re.IGNORECASE)
            self.variables[var] = hit.group(0) if hit else ""
        return "continue"

    def _modern_split(self, command):
        m = re.match(r"SPLIT\s+(\w+)\s*,\s*\"([^\"]*)\"\s+INTO\s+(\w+)", command, re.IGNORECASE)
        if m:
            src = str(self.variables.get(m.group(1).upper(), ""))
            sep = m.group(2)
            dest = m.group(3).upper()
            self.lists[dest] = src.split(sep)
            self.variables[dest] = self.lists[dest]
        return "continue"

    def _modern_join(self, command):
        m = re.match(r"JOIN\s+(\w+)\s*,\s*\"([^\"]*)\"\s+INTO\s+(\w+)", command, re.IGNORECASE)
        if m:
            src = self.lists.get(m.group(1).upper(), [])
            sep = m.group(2)
            dest = m.group(3).upper()
            self.variables[dest] = sep.join(str(x) for x in src)
        return "continue"

    # ==================================================================
    #  Convenience: get_current_time for error history
    # ==================================================================

    @staticmethod
    def get_current_time():
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
