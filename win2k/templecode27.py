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
import sys
import time

try:
    import json
except ImportError:
    json = None  # ancient Pythons

try:
    import shutil as _shutil
except ImportError:
    _shutil = None

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


def _levenshtein(a, b):
    """Compute Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1,
                            prev[j] + (0 if ca == cb else 1)))
        prev = curr
    return prev[-1]


ALL_KEYWORDS = [
    "PRINT", "LET", "INPUT", "IF", "THEN", "ELSE", "ELSEIF", "ENDIF",
    "FOR", "NEXT", "WHILE", "WEND", "DO", "LOOP", "GOTO", "GOSUB",
    "RETURN", "DIM", "DATA", "READ", "RESTORE", "RANDOMIZE",
    "DELAY", "SLEEP", "SELECT", "CASE", "SWAP", "INCR", "DECR",
    "INC", "DEC", "CLS", "BEEP", "STOP", "END", "BREAK", "EXIT",
    "ON", "SUB", "FUNCTION", "CALL", "CONST", "FOREACH", "PRINTF",
    "LIST", "PUSH", "POP", "SHIFT", "UNSHIFT", "SORT", "REVERSE", "SPLICE",
    "DICT", "SET", "GET", "DELETE",
    "TRY", "CATCH", "THROW", "ASSERT", "TYPEOF", "ENUM",
    "STRUCT", "NEW", "LAMBDA", "MAP", "FILTER", "REDUCE",
    "JSON", "REGEX", "SPLIT", "JOIN", "IMPORT",
    "OPEN", "CLOSE", "READLINE", "WRITELINE", "READFILE", "WRITEFILE", "APPENDFILE",
    "RANGE", "FILEEXISTS", "COPYFILE", "DELETEFILE",
    "UNSET", "EVAL", "PROGRAMINFO", "HELP", "INKEY",
    "WRITE", "WRITELN", "READLN", "PAUSE", "TAB", "SPC",
    "PLAYNOTE", "SOUND", "LOAD", "SAVE", "CHAIN",
    "ASSERTA", "ASSERTZ", "RETRACT", "QUERY", "FACTS",
    "FORWARD", "FD", "BACK", "BK", "LEFT", "LT", "RIGHT", "RT",
    "PENUP", "PU", "PENDOWN", "PD", "HOME", "CLEARSCREEN", "CS",
    "SHOWTURTLE", "ST", "HIDETURTLE", "HT",
    "SETXY", "SETCOLOR", "SETPENSIZE", "SETHEADING", "SETH",
    "CIRCLE", "CIRCLEFILL", "ARC", "DOT", "RECT", "RECTFILL",
    "SQUARE", "TRIANGLE", "POLYGON", "STAR", "FILL", "FILLED",
    "PSET", "PRESET", "POINT", "SCREEN", "REPEAT", "MAKE", "LABEL",
    "SETFILLCOLOR", "SETFC", "SETBACKGROUND", "SETBG", "TOWARDS",
    "COLOR", "COLOUR", "CLEAN", "WRAP", "WINDOW", "FENCE",
]


def _suggest_command(cmd):
    """Return the closest keyword if within edit distance 2, else None."""
    cmd_upper = cmd.upper()
    best, best_dist = None, 3
    for kw in ALL_KEYWORDS:
        d = _levenshtein(cmd_upper, kw)
        if d < best_dist:
            best, best_dist = kw, d
    return best


def _smart_split(text, delimiter=","):
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

    def __init__(self, output_cb=None, input_cb=None, canvas_cb=None, key_cb=None):
        # Callbacks
        self.output_cb  = output_cb  or self._default_output
        self.input_cb   = input_cb   or self._default_input
        self.canvas_cb  = canvas_cb  or (lambda *a, **kw: None)
        self.key_cb     = key_cb     or (lambda: "")

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

        # Prolog facts
        self.prolog_facts = []

        # File handles
        self.file_handles = {}

        # Imported modules
        self.imported_modules = set()

        # Key buffer for INKEY
        self.key_buffer = []

        # Fill color and boundary mode
        self.turtle_fill_color = "white"
        self.turtle_boundary = "wrap"

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

        # Extended expression checks first
        ext = self._eval_extended(expr)
        if ext is not expr:
            return ext

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

    def _eval_extended(self, expr):
        """Extended expression evaluation for new features.
        Returns the expr object itself (identity) if not handled."""
        upper = expr.upper().strip()

        # INKEY / INKEY$
        if upper in ("INKEY$", "INKEY"):
            if self.key_buffer:
                return self.key_buffer.pop(0)
            return self.key_cb()

        # TIMER pseudo-variable
        if upper == "TIMER":
            return round(time.time() - self._start_time, 3)

        # DATE$ and TIME$
        if upper in ("DATE$", "DATE"):
            import datetime as _dt
            return _dt.date.today().isoformat()
        if upper in ("TIME$", "TIME"):
            import datetime as _dt
            return _dt.datetime.now().strftime("%H:%M:%S")
        if upper == "NOW":
            return time.time()

        # Constants
        if upper == "PI":
            return math.pi
        if upper == "TAU":
            return math.pi * 2
        if upper == "INF":
            return float("inf")
        if upper == "RESULT":
            return self.return_value if self.return_value is not None else 0
        if upper == "ERROR$":
            return self.last_error
        if upper == "TRUE":
            return 1
        if upper == "FALSE":
            return 0

        # List literal: [1, 2, 3]
        if expr.startswith("[") and expr.endswith("]"):
            items = _smart_split(expr[1:-1], ",")
            return [self.evaluate(it.strip()) for it in items if it.strip()]

        # List access: NAME[index]
        m = re.match(r'(\w+)\[(.+)\]', expr)
        if m:
            name = m.group(1).upper()
            idx = int(float(self.evaluate(m.group(2))))
            if name in self.lists:
                lst = self.lists[name]
                if 0 <= idx < len(lst):
                    return lst[idx]
                return ""
            lv = self.variables.get(name)
            if isinstance(lv, list) and 0 <= idx < len(lv):
                return lv[idx]
            return ""

        # Dict access: NAME.key
        m = re.match(r'^(\w+)\.(\w+)$', expr)
        if m:
            name = m.group(1).upper()
            key = m.group(2)
            if name in self.dicts:
                d = self.dicts[name]
                if key in d:
                    return d[key]
                if key.upper() in d:
                    return d[key.upper()]
                return ""

        # LENGTH(x)
        m = re.match(r'^LENGTH\((\w+)\)$', expr, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            if name in self.lists:
                return len(self.lists[name])
            if name in self.dicts:
                return len(self.dicts[name])
            val = self.variables.get(name, "")
            if isinstance(val, list):
                return len(val)
            return len(str(val))

        # ROUND(value, n?)
        m = re.match(r'^ROUND\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            val = float(self.evaluate(args[0].strip()))
            n = int(self.evaluate(args[1].strip())) if len(args) > 1 else 0
            result = round(val, n)
            return int(result) if n == 0 else result

        # FLOOR(value)
        m = re.match(r'^FLOOR\((.+)\)$', expr, re.IGNORECASE)
        if m:
            return int(math.floor(float(self.evaluate(m.group(1).strip()))))

        # TRUNC(value)
        m = re.match(r'^TRUNC\((.+)\)$', expr, re.IGNORECASE)
        if m:
            val = float(self.evaluate(m.group(1).strip()))
            return int(val) if val >= 0 else -int(-val)

        # POWER(base, exp)
        m = re.match(r'^POWER\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                base = float(self.evaluate(args[0].strip()))
                exp = float(self.evaluate(args[1].strip()))
                r = base ** exp
                return int(r) if r == int(r) else r

        # RANDOM(min, max)
        m = re.match(r'^RANDOM\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                lo = int(float(self.evaluate(args[0].strip())))
                hi = int(float(self.evaluate(args[1].strip())))
                return random.randint(lo, hi)

        # RANDINT(n)
        m = re.match(r'^RANDINT\((.+)\)$', expr, re.IGNORECASE)
        if m:
            n = int(float(self.evaluate(m.group(1).strip())))
            return random.randrange(max(1, n))

        # KEYS(dict) / VALUES(dict)
        m = re.match(r'^KEYS\((\w+)\)$', expr, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            return list(self.dicts[name].keys()) if name in self.dicts else []
        m = re.match(r'^VALUES\((\w+)\)$', expr, re.IGNORECASE)
        if m:
            name = m.group(1).upper()
            return list(self.dicts[name].values()) if name in self.dicts else []

        # HASKEY(dict, key)
        m = re.match(r'^HASKEY\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                name = args[0].strip().upper()
                key = self.evaluate(args[1].strip())
                return 1 if (name in self.dicts and key in self.dicts[name]) else 0
            return 0

        # INDEXOF(list, value)
        m = re.match(r'^INDEXOF\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                name = args[0].strip().upper()
                val = self.evaluate(args[1].strip())
                if name in self.lists:
                    try:
                        return self.lists[name].index(val)
                    except ValueError:
                        return -1
            return -1

        # SLICE(list, start, end)
        m = re.match(r'^SLICE\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 3:
                name = args[0].strip().upper()
                start = int(float(self.evaluate(args[1].strip())))
                end = int(float(self.evaluate(args[2].strip())))
                if name in self.lists:
                    return self.lists[name][start:end]

        # CONTAINS(x, y)
        m = re.match(r'^CONTAINS\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                hay = self.evaluate(args[0].strip())
                needle = self.evaluate(args[1].strip())
                if isinstance(hay, (list, dict)):
                    return 1 if needle in hay else 0
                return 1 if str(needle) in str(hay) else 0

        # STARTSWITH / ENDSWITH
        m = re.match(r'^STARTSWITH\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                return 1 if str(self.evaluate(args[0].strip())).startswith(str(self.evaluate(args[1].strip()))) else 0
        m = re.match(r'^ENDSWITH\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                return 1 if str(self.evaluate(args[0].strip())).endswith(str(self.evaluate(args[1].strip()))) else 0

        # ISNUMBER / ISSTRING
        m = re.match(r'^ISNUMBER\((.+)\)$', expr, re.IGNORECASE)
        if m:
            return 1 if isinstance(self.evaluate(m.group(1).strip()), (int, float)) else 0
        m = re.match(r'^ISSTRING\((.+)\)$', expr, re.IGNORECASE)
        if m:
            return 1 if isinstance(self.evaluate(m.group(1).strip()), str) else 0

        # TONUM / TOSTR
        m = re.match(r'^TONUM\((.+)\)$', expr, re.IGNORECASE)
        if m:
            try:
                f = float(self.evaluate(m.group(1).strip()))
                return int(f) if f == int(f) else f
            except (ValueError, TypeError):
                return 0
        m = re.match(r'^TOSTR\((.+)\)$', expr, re.IGNORECASE)
        if m:
            return str(self.evaluate(m.group(1).strip()))

        # FILEEXISTS(filename) as expression
        m = re.match(r'^FILEEXISTS\((.+)\)$', expr, re.IGNORECASE)
        if m:
            return 1 if os.path.exists(str(self.evaluate(m.group(1).strip()))) else 0

        # TYPE(x)
        m = re.match(r'^TYPE\((.+)\)$', expr, re.IGNORECASE)
        if m:
            val = self.evaluate(m.group(1).strip())
            if isinstance(val, str):
                return "STRING"
            elif isinstance(val, (int, float)):
                return "NUMBER"
            elif isinstance(val, list):
                return "LIST"
            elif isinstance(val, dict):
                return "DICT"
            return "UNKNOWN"

        # SPLIT(string, delimiter)
        m = re.match(r'^SPLIT\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                return str(self.evaluate(args[0].strip())).split(str(self.evaluate(args[1].strip())))

        # JOIN(list, delimiter)
        m = re.match(r'^JOIN\((.+)\)$', expr, re.IGNORECASE)
        if m:
            args = _smart_split(m.group(1), ",")
            if len(args) == 2:
                name = args[0].strip().upper()
                d = str(self.evaluate(args[1].strip()))
                if name in self.lists:
                    return d.join(str(x) for x in self.lists[name])

        # FIX(x) - truncate toward zero
        m = re.match(r'^FIX\((.+)\)$', expr, re.IGNORECASE)
        if m:
            val = float(self.evaluate(m.group(1).strip()))
            return int(val) if val >= 0 else -int(-val)

        # User-defined function / lambda call
        m = re.match(r'^(\w+)\(([^)]*)\)$', expr)
        if m:
            fname = m.group(1).upper()
            if fname in self.func_defs:
                raw_args = m.group(2).strip()
                args = [a.strip() for a in _smart_split(raw_args, ",")] if raw_args else []
                arg_vals = [self.evaluate(a) for a in args]
                if "lambda_body" in self.func_defs[fname]:
                    return self._eval_lambda(fname, arg_vals)
                else:
                    return self._call_function(fname, arg_vals)

        # Not handled -- return identity
        return expr

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
                s = re.sub(re.escape(vn) + r"(?=\s|$|[^A-Za-z0-9_$])", vr, s, flags=re.IGNORECASE)
            else:
                s = re.sub(r"\b" + re.escape(vn) + r"\b", vr, s, flags=re.IGNORECASE)

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
            "HOME", "CLEARSCREEN", "CS", "CLEAN",
            "SHOWTURTLE", "ST", "HIDETURTLE", "HT",
            "SETXY", "SETPOS", "SETX", "SETY",
            "SETCOLOR", "SETCOLOUR", "SETPENCOLOR", "SETPC",
            "SETPENSIZE", "SETWIDTH",
            "SETFILLCOLOR", "SETFC",
            "SETBACKGROUND", "SETBG",
            "SETSCREENCOLOR", "SETSCREENCOLOUR",
            "SETHEADING", "SETH",
            "TOWARDS",
            "CIRCLE", "CIRCLEFILL", "ARC", "DOT",
            "SQUARE", "TRIANGLE", "POLYGON", "STAR",
            "RECT", "RECTANGLE", "RECTFILL",
            "FILL", "FILLED",
            "PSET", "PRESET", "POINT", "SCREEN",
            "REPEAT",
            "MAKE",
            "LABEL", "STAMP",
            "WRAP", "WINDOW", "FENCE",
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
        elif letter == "G":
            return self._pilot_graphics(arg)
        elif letter == "S":
            return self._pilot_string(arg)
        elif letter == "D":
            return self._pilot_dim(arg)
        elif letter == "X":
            return self._pilot_execute(arg)
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

    def _pilot_graphics(self, arg):
        """G: -- Inline turtle graphics shorthand.  G:FORWARD 100"""
        arg = arg.strip()
        if not arg:
            return "continue"
        first = arg.split()[0].upper() if arg.split() else ""
        return self._dispatch_logo(arg, first)

    def _pilot_string(self, arg):
        """S: -- String operations.  S:UPPER X  /  S:LEN X  etc."""
        parts = arg.split()
        if len(parts) < 2:
            return "continue"
        op = parts[0].upper()
        var_name = parts[1].upper()
        val = str(self.variables.get(var_name, ""))
        if op == "UPPER":
            self.variables[var_name] = val.upper()
        elif op == "LOWER":
            self.variables[var_name] = val.lower()
        elif op == "LEN":
            self.variables[var_name + "_LEN"] = len(val)
        elif op == "REVERSE":
            self.variables[var_name] = val[::-1]
        elif op == "TRIM":
            self.variables[var_name] = val.strip()
        return "continue"

    def _pilot_dim(self, arg):
        """D: -- Dimension an array.  D:ARR(10)"""
        m = re.match(r'(\w+)\((\d+)\)', arg)
        if m:
            name = m.group(1).upper()
            size = int(m.group(2))
            self.arrays[name] = dict((i, 0) for i in range(size))
        return "continue"

    def _pilot_execute(self, arg):
        """X: -- Execute a BASIC or Logo command inline."""
        return self._execute(arg)

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
        elif first in ("CLEARSCREEN", "CS", "CLEAN"):
            self.canvas_cb("clear")
            if first != "CLEAN":
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
        elif first in ("SETCOLOR", "SETCOLOUR", "SETPENCOLOR", "SETPC"):
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
        elif first in ("SETFILLCOLOR", "SETFC"):
            return self._logo_setfillcolor(argstr)
        elif first in ("SETBACKGROUND", "SETBG", "SETSCREENCOLOR", "SETSCREENCOLOUR"):
            return self._logo_setbackground(argstr)
        elif first == "TOWARDS":
            return self._logo_towards(argstr)
        elif first == "MAKE":
            return self._logo_make(argstr)
        elif first == "CIRCLEFILL":
            return self._logo_circlefill(argstr)
        elif first == "RECTFILL":
            return self._logo_rectfill(argstr)
        elif first in ("FILL", "FILLED"):
            return self._logo_fill()
        elif first == "PSET":
            return self._logo_pset(argstr)
        elif first == "PRESET":
            return self._logo_preset(argstr)
        elif first == "POINT":
            return self._logo_point(argstr)
        elif first == "SCREEN":
            return self._logo_screen(argstr)
        elif first == "STAMP":
            return self._logo_label(argstr)
        elif first == "WRAP":
            self.turtle_boundary = "wrap"
            return "continue"
        elif first == "WINDOW":
            self.turtle_boundary = "window"
            return "continue"
        elif first == "FENCE":
            self.turtle_boundary = "fence"
            return "continue"
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

    # -- new Logo commands --

    def _logo_setfillcolor(self, argstr):
        """SETFILLCOLOR color -- set fill color for filled shapes."""
        color = argstr.strip().strip('"').lower()
        if color.startswith(":"):
            color = str(self.variables.get(color[1:].upper(), color))
        if not color:
            return "continue"
        self.turtle_fill_color = color
        return "continue"

    def _logo_setbackground(self, argstr):
        """SETBACKGROUND color -- set canvas background color."""
        color = argstr.strip().strip('"').lower()
        if color:
            self.canvas_cb("background", color=color)
        return "continue"

    def _logo_towards(self, argstr):
        """TOWARDS x y -- set heading toward coordinates."""
        parts = argstr.replace(",", " ").split()
        if len(parts) >= 2:
            tx = float(self.evaluate(parts[0]))
            ty = float(self.evaluate(parts[1]))
            dx = tx - self.turtle_x
            dy = ty - self.turtle_y
            angle = math.degrees(math.atan2(dx, dy)) % 360
            self.turtle_heading = angle
            self.canvas_cb("turtle", x=self.turtle_x, y=self.turtle_y,
                           heading=self.turtle_heading, visible=self.turtle_visible)
        return "continue"

    def _logo_make(self, argstr):
        """MAKE \"varname value -- Logo variable assignment."""
        parts = argstr.split(None, 1)
        if len(parts) < 2:
            return "continue"
        name = parts[0].strip('"').upper()
        try:
            value = self.evaluate(parts[1])
        except Exception:
            value = parts[1]
        self.variables[name] = value
        return "continue"

    def _logo_circlefill(self, argstr):
        """CIRCLEFILL radius -- draw filled circle at turtle position."""
        radius = float(self.evaluate(argstr)) if argstr.strip() else 50
        self.canvas_cb("circlefill", x=self.turtle_x, y=self.turtle_y,
                       radius=abs(radius), color=self.turtle_color,
                       fill=self.turtle_fill_color, width=self.turtle_width)
        return "continue"

    def _logo_rectfill(self, argstr):
        """RECTFILL w h -- draw filled rectangle at turtle position."""
        parts = argstr.split()
        w = float(self.evaluate(parts[0])) if parts else 50
        h = float(self.evaluate(parts[1])) if len(parts) > 1 else w
        self.canvas_cb("rectfill", x=self.turtle_x, y=self.turtle_y,
                       w=w, h=h, color=self.turtle_color,
                       fill=self.turtle_fill_color, width=self.turtle_width)
        return "continue"

    def _logo_fill(self):
        """FILL -- flood fill at turtle position."""
        self.canvas_cb("fill", x=self.turtle_x, y=self.turtle_y,
                       color=self.turtle_fill_color)
        return "continue"

    def _logo_pset(self, argstr):
        """PSET x, y -- set pixel at coordinates to pen color."""
        parts = argstr.replace(",", " ").split()
        if len(parts) >= 2:
            x = float(self.evaluate(parts[0]))
            y = float(self.evaluate(parts[1]))
            self.canvas_cb("pixel", x=x, y=y, color=self.turtle_color)
        return "continue"

    def _logo_preset(self, argstr):
        """PRESET x, y -- reset pixel to background color."""
        parts = argstr.replace(",", " ").split()
        if len(parts) >= 2:
            x = float(self.evaluate(parts[0]))
            y = float(self.evaluate(parts[1]))
            self.canvas_cb("pixel", x=x, y=y, color="white")
        return "continue"

    def _logo_point(self, argstr):
        """POINT x, y -- query pixel (simplified: always 1)."""
        self.output_cb("1")
        return "continue"

    def _logo_screen(self, argstr):
        """SCREEN [w h | mode] -- resize canvas or set screen mode."""
        parts = argstr.split()
        if len(parts) >= 2:
            try:
                w = int(float(self.evaluate(parts[0])))
                h = int(float(self.evaluate(parts[1])))
                self.canvas_cb("resize", width=w, height=h)
            except Exception:
                pass
        elif len(parts) == 1:
            mode = parts[0].upper()
            presets = {
                "0": (320, 200), "1": (640, 480), "2": (800, 600),
                "SMALL": (320, 200), "MEDIUM": (640, 480), "LARGE": (800, 600),
            }
            if mode in presets:
                w, h = presets[mode]
                self.canvas_cb("resize", width=w, height=h)
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
                             "SETPENSIZE", "HOME", "CIRCLE", "CIRCLEFILL", "ARC", "DOT",
                             "LABEL", "SQUARE", "TRIANGLE", "POLYGON", "STAR", "RECT",
                             "RECTFILL", "FILL", "FILLED", "PSET", "PRESET", "SCREEN",
                             "REPEAT", "HIDETURTLE", "HT", "SHOWTURTLE", "ST",
                             "SETXY", "SETHEADING", "SETH", "SETPENCOLOR", "SETPC",
                             "SETFILLCOLOR", "SETFC", "SETBACKGROUND", "SETBG",
                             "TOWARDS", "MAKE", "STAMP", "CLEAN"}
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
        elif cmd == "INC":
            return self._basic_incr_decr(command, 1)
        elif cmd == "DEC":
            return self._basic_incr_decr(command, -1)
        elif cmd == "HELP":
            return self._basic_help()
        elif cmd == "INKEY":
            return self._basic_inkey()
        elif cmd == "PAUSE":
            return self._basic_pause(command)
        elif cmd == "WRITE":
            return self._basic_write(command)
        elif cmd == "WRITELN":
            return self._basic_writeln(command)
        elif cmd == "READLN":
            return self._basic_readln(command)
        elif cmd == "LOAD":
            return self._basic_load(command)
        elif cmd == "SAVE":
            return self._basic_save(command)
        elif cmd == "CHAIN":
            return self._basic_chain(command)
        elif cmd in ("PLAYNOTE", "SOUND"):
            return self._basic_playnote(command)
        elif cmd == "TAB":
            return self._basic_tab(command)
        elif cmd == "SPC":
            return self._basic_spc(command)
        elif cmd in ("COLOR", "COLOUR"):
            rest = command.split(None, 1)[1] if " " in command else ""
            return self._logo_setcolor(rest)
        elif cmd == "CLS":
            self.canvas_cb("cls")
            return "continue"
        elif cmd == "BEEP":
            try:
                sys.stdout.write('\a')
                sys.stdout.flush()
            except Exception:
                pass
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
            elif eu in ("END STRUCT", "END LAMBDA", "END METHOD"):
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
        elif cmd == "SHIFT":
            return self._modern_shift(command)
        elif cmd == "UNSHIFT":
            return self._modern_unshift(command)
        elif cmd == "SPLICE":
            return self._modern_splice(command)
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
            return self._modern_struct(command)
        elif cmd == "NEW":
            return self._modern_new(command)
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
        elif cmd == "IMPORT":
            return self._modern_import(command)
        elif cmd == "RANGE":
            return self._modern_range(command)
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
        elif cmd == "FILEEXISTS":
            return self._modern_fileexists(command)
        elif cmd == "COPYFILE":
            return self._modern_copyfile(command)
        elif cmd == "DELETEFILE":
            return self._modern_deletefile(command)
        elif cmd == "UNSET":
            return self._modern_unset(command)
        elif cmd == "EVAL":
            return self._modern_eval(command)
        elif cmd == "PROGRAMINFO":
            return self._modern_programinfo(command)
        elif cmd in ("ASSERTA", "ASSERTZ"):
            return self._prolog_assert(cmd, command)
        elif cmd == "RETRACT":
            return self._prolog_retract(command)
        elif cmd == "QUERY":
            return self._prolog_query(command)
        elif cmd == "FACTS":
            return self._prolog_facts()

        # Direct assignment: X = 5
        elif "=" in command and not command.upper().startswith("IF"):
            return self._basic_let("LET " + command)
        else:
            suggestion = _suggest_command(cmd)
            if suggestion:
                self.output_cb("Unknown command: %s  (Did you mean %s?)" % (command, suggestion))
            else:
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

        # Split on ; and , respecting parens/brackets/quotes
        parts = self._split_print_args(text)
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

    @staticmethod
    def _split_print_args(text):
        """Split PRINT arguments on ; and , respecting parens and quotes."""
        parts = []
        current = []
        depth = 0
        in_string = False
        for ch in text:
            if ch == '"':
                in_string = not in_string
                current.append(ch)
            elif not in_string:
                if ch in "([":
                    depth += 1
                    current.append(ch)
                elif ch in ")]":
                    depth -= 1
                    current.append(ch)
                elif ch in ",;" and depth == 0:
                    parts.append("".join(current))
                    current = []
                else:
                    current.append(ch)
            else:
                current.append(ch)
        if current:
            parts.append("".join(current))
        return parts

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
        m = re.match(r"(?:INCR?|DECR?)\s+(\w+)(?:\s*,?\s*(.+))?", command, re.IGNORECASE)
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
        m = re.match(r"ON\s+(.+?)\s+GOSUB\s+(.+)", command, re.IGNORECASE)
        if m:
            idx = int(float(self.evaluate(m.group(1))))
            targets = [t.strip() for t in m.group(2).split(",")]
            if 1 <= idx <= len(targets):
                return self._basic_gosub("GOSUB %s" % targets[idx - 1])
        return "continue"

    def _basic_help(self):
        """HELP -- print TempleCode quick reference."""
        lines = [
            "TempleCode HELP - available commands:",
            "PRINT, LET, INPUT, IF, ELSE, FOR, NEXT, GOTO, GOSUB, RETURN",
            "DIM, DATA, READ, RESTORE, END, STOP, SWAP, INCR, DECR",
            "SELECT, CASE, DO/LOOP, WHILE/WEND, RANDOMIZE",
            "LIST, SPLIT, JOIN, PUSH, POP, SHIFT, UNSHIFT, SORT, REVERSE, SPLICE",
            "DICT, SET, GET, DELETE, RANGE, EVAL, UNSET, PROGRAMINFO",
            "File I/O: OPEN, CLOSE, READLINE, WRITELINE, READFILE, WRITEFILE, APPENDFILE",
            "FILEEXISTS, COPYFILE, DELETEFILE",
            "Logo: FORWARD/FD, BACK/BK, LEFT/LT, RIGHT/RT, CIRCLE, RECT, PSET, SCREEN",
            "PILOT: T:, A:, M:, Y:, N:, J:, C:, G:, S:, D:, P:, X:",
            "Prolog: ASSERTA, ASSERTZ, RETRACT, QUERY, FACTS",
            "Turbo: WRITE, WRITELN, READLN, INC, DEC, LOAD, SAVE, CHAIN, PAUSE",
        ]
        for line in lines:
            self.output_cb(line)
        return "continue"

    def _basic_inkey(self):
        """INKEY -- return next buffered key or empty string."""
        if self.key_buffer:
            self.output_cb(self.key_buffer.pop(0))
        else:
            k = self.key_cb()
            self.output_cb(k if k else "")
        return "continue"

    def _basic_pause(self, command):
        """PAUSE n -- hold execution for n milliseconds."""
        text = re.sub(r'^PAUSE\s+', '', command, flags=re.IGNORECASE).strip()
        try:
            ms = int(float(self.evaluate(text))) if text else 1000
            time.sleep(ms / 1000.0)
        except Exception:
            time.sleep(1.0)
        return "continue"

    def _basic_write(self, command):
        """WRITE expr -- Turbo Pascal print (same line)."""
        text = re.sub(r'^WRITE\s*', '', command, flags=re.IGNORECASE).strip()
        if not text:
            return "continue"
        val = self.evaluate(text)
        self.output_cb(str(val))
        return "continue"

    def _basic_writeln(self, command):
        """WRITELN expr -- Turbo Pascal print with newline."""
        text = re.sub(r'^WRITELN\s*', '', command, flags=re.IGNORECASE).strip()
        if not text:
            self.output_cb("")
            return "continue"
        return self._basic_print("PRINT " + text)

    def _basic_readln(self, command):
        """READLN var -- Turbo Pascal input alias."""
        tail = re.sub(r'^READLN\s*', '', command, flags=re.IGNORECASE).strip()
        return self._basic_input("INPUT " + tail)

    def _basic_load(self, command):
        """LOAD \"file\", var -- Turbo BASIC alias for READFILE."""
        text = re.sub(r'^LOAD\s+', '', command, flags=re.IGNORECASE).strip()
        return self._modern_readfile('READFILE ' + text)

    def _basic_save(self, command):
        """SAVE \"file\", expression -- Turbo BASIC alias for WRITEFILE."""
        text = re.sub(r'^SAVE\s+', '', command, flags=re.IGNORECASE).strip()
        return self._modern_writefile('WRITEFILE ' + text)

    def _basic_chain(self, command):
        """CHAIN \"filename\", var -- load a file."""
        text = re.sub(r'^CHAIN\s+', '', command, flags=re.IGNORECASE).strip()
        parts = text.split(',', 1)
        if len(parts) == 2:
            return self._modern_readfile('READFILE %s, %s' % (parts[0].strip(), parts[1].strip()))
        self.output_cb('CHAIN syntax: CHAIN "file", var')
        return "continue"

    def _basic_playnote(self, command):
        """PLAYNOTE freq,duration  OR  SOUND freq,duration"""
        text = re.sub(r'^(PLAYNOTE|SOUND)\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in text.split(",")]
        if len(parts) < 2:
            self.output_cb('PLAYNOTE syntax: PLAYNOTE freq,duration')
            return "continue"
        try:
            freq = float(self.evaluate(parts[0]))
            dur = float(self.evaluate(parts[1]))
        except Exception:
            self.output_cb('PLAYNOTE: frequency and duration must be numbers')
            return "continue"
        try:
            import winsound
            winsound.Beep(int(freq), int(dur))
        except Exception:
            self.output_cb("[SOUND] %sHz for %sms" % (freq, dur))
        return "continue"

    def _basic_tab(self, command):
        """TAB n -- print spaces to column n."""
        parts = command.split()
        n = int(float(self.evaluate(parts[1]))) if len(parts) > 1 else 8
        self.output_cb(" " * n)
        return "continue"

    def _basic_spc(self, command):
        """SPC n -- print n spaces."""
        parts = command.split()
        n = int(float(self.evaluate(parts[1]))) if len(parts) > 1 else 1
        self.output_cb(" " * n)
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
        """LAMBDA name(params) = expression  (single-line)
        or multi-line: LAMBDA name(params) ... END LAMBDA"""
        # Single-line: LAMBDA name(params) = expression
        m = re.match(r"LAMBDA\s+(\w+)\s*\(([^)]*)\)\s*=\s*(.*)", command, re.IGNORECASE)
        if m and m.group(3).strip():
            name = m.group(1).upper()
            params = [p.strip().upper() for p in m.group(2).split(",") if p.strip()]
            body = m.group(3).strip()
            self.func_defs[name] = {
                "params": params,
                "lambda_body": body,
                "start": -1, "end": -1
            }
            return "continue"

        # Multi-line: LAMBDA name(params) ... END LAMBDA
        m2 = re.match(r'LAMBDA\s+(\w+)\s*\(([^)]*)\)\s*$', command, re.IGNORECASE)
        if not m2:
            return "continue"
        name = m2.group(1).upper()
        params = [p.strip().upper() for p in m2.group(2).split(",") if p.strip()]
        body_start = self.current_line + 1
        depth = 1
        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            lu = lt.strip().upper() if lt else ""
            if lu.startswith("LAMBDA ") and "=" not in lu:
                depth += 1
            elif lu == "END LAMBDA":
                depth -= 1
                if depth == 0:
                    break
            self.current_line += 1
        body_end = self.current_line
        self.func_defs[name] = {
            "params": params,
            "body_start": body_start,
            "body_end": body_end,
        }
        return "continue"

    def _eval_lambda(self, name, args):
        """Evaluate a lambda function (single-line or multi-line)."""
        defn = self.func_defs.get(name)
        if not defn:
            return 0
        saved = dict(self.variables)
        for i, p in enumerate(defn["params"]):
            if i < len(args):
                self.variables[p] = args[i]

        # Single-line lambda
        if "lambda_body" in defn:
            result = self.evaluate(defn["lambda_body"])
            self.variables = saved
            return result

        # Multi-line lambda
        self.return_value = None
        line = defn.get("body_start", defn.get("start", 0) + 1)
        end = defn.get("body_end", defn.get("end", len(self.program_lines)))
        while line < end:
            _, cmd = self.program_lines[line]
            if cmd and cmd.strip():
                r = self._execute(cmd.strip())
                if r == "return":
                    break
            line += 1
        rv = self.return_value
        self.variables = saved
        return rv if rv is not None else 0

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
        """REGEX MATCH|REPLACE|FIND|SPLIT ..."""
        rest = re.sub(r"^REGEX\s+", "", command, flags=re.IGNORECASE).strip()
        upper_rest = rest.upper()

        if upper_rest.startswith("MATCH"):
            m = re.match(r'MATCH\s+"([^"]+)"\s+IN\s+(.+?)\s+INTO\s+(\w+)', rest, re.IGNORECASE)
            if not m:
                m = re.match(r'MATCH\s+(.+?)\s+IN\s+(.+?)\s+INTO\s+(\w+)', rest, re.IGNORECASE)
            if m:
                pattern = str(self.evaluate(m.group(1).strip()))
                text = str(self.evaluate(m.group(2).strip()))
                var = m.group(3).upper()
                hit = re.search(pattern, text, re.IGNORECASE)
                if hit:
                    self.variables[var] = hit.group(0)
                    self.variables[var + "_POS"] = hit.start()
                    self.match_flag = True
                else:
                    self.variables[var] = ""
                    self.variables[var + "_POS"] = -1
                    self.match_flag = False
            return "continue"

        elif upper_rest.startswith("REPLACE"):
            m = re.match(
                r'REPLACE\s+"([^"]+)"\s+WITH\s+"([^"]*)"\s+IN\s+(.+?)\s+INTO\s+(\w+)',
                rest, re.IGNORECASE)
            if m:
                pattern = m.group(1)
                replacement = m.group(2)
                text = str(self.evaluate(m.group(3).strip()))
                var = m.group(4).upper()
                self.variables[var] = re.sub(pattern, replacement, text)
            return "continue"

        elif upper_rest.startswith("FIND"):
            m = re.match(r'FIND\s+"([^"]+)"\s+IN\s+(.+?)\s+INTO\s+(\w+)', rest, re.IGNORECASE)
            if m:
                pattern = m.group(1)
                text = str(self.evaluate(m.group(2).strip()))
                list_name = m.group(3).upper()
                self.lists[list_name] = re.findall(pattern, text)
            return "continue"

        elif upper_rest.startswith("SPLIT"):
            m = re.match(r'SPLIT\s+"([^"]+)"\s+IN\s+(.+?)\s+INTO\s+(\w+)', rest, re.IGNORECASE)
            if m:
                pattern = m.group(1)
                text = str(self.evaluate(m.group(2).strip()))
                list_name = m.group(3).upper()
                self.lists[list_name] = re.split(pattern, text)
            return "continue"

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

    # ------------------------------------------------------------------
    #  New modern extensions: SHIFT / UNSHIFT / SPLICE
    # ------------------------------------------------------------------

    def _modern_shift(self, command):
        """SHIFT list_name [, var_name] -- remove first element."""
        text = re.sub(r'^SHIFT\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in text.split(",")]
        name = parts[0].upper()
        if name not in self.lists or not self.lists[name]:
            return "continue"
        val = self.lists[name].pop(0)
        if len(parts) > 1:
            self.variables[parts[1].upper()] = val
        return "continue"

    def _modern_unshift(self, command):
        """UNSHIFT list_name, value -- prepend to list."""
        text = re.sub(r'^UNSHIFT\s+', '', command, flags=re.IGNORECASE).strip()
        parts = _smart_split(text, ",")
        if len(parts) < 2:
            return "continue"
        name = parts[0].strip().upper()
        if name not in self.lists:
            self.lists[name] = []
        for v in reversed(parts[1:]):
            self.lists[name].insert(0, self.evaluate(v.strip()))
        return "continue"

    def _modern_splice(self, command):
        """SPLICE list_name, start, count [, val1, val2, ...]"""
        text = re.sub(r'^SPLICE\s+', '', command, flags=re.IGNORECASE).strip()
        parts = _smart_split(text, ",")
        if len(parts) < 3:
            return "continue"
        name = parts[0].strip().upper()
        start = int(float(self.evaluate(parts[1].strip())))
        count = int(float(self.evaluate(parts[2].strip())))
        inserts = [self.evaluate(p.strip()) for p in parts[3:]]
        if name in self.lists:
            del self.lists[name][start:start + count]
            for i, v in enumerate(inserts):
                self.lists[name].insert(start + i, v)
        return "continue"

    # ------------------------------------------------------------------
    #  STRUCT (multi-line with FIELD/METHOD/END METHOD/END STRUCT)
    # ------------------------------------------------------------------

    def _modern_struct(self, command):
        """STRUCT name = field1, field2  or multi-line STRUCT."""
        text = re.sub(r'^STRUCT\s+', '', command, flags=re.IGNORECASE).strip()

        # Single-line: STRUCT name = field1, field2
        m = re.match(r'(\w+)\s*=\s*(.*)', text)
        if m:
            name = m.group(1).upper()
            fields = [f.strip().upper() for f in m.group(2).split(",") if f.strip()]
            self.variables["__STRUCT_" + name] = fields
            return "continue"

        # Multi-line: STRUCT name ... END STRUCT
        m2 = re.match(r'(\w+)\s*$', text)
        if not m2:
            return "continue"
        name = m2.group(1).upper()
        fields = []
        methods = {}

        self.current_line += 1
        while self.current_line < len(self.program_lines):
            _, lt = self.program_lines[self.current_line]
            lu = lt.strip().upper() if lt else ""
            if lu == "END STRUCT":
                break

            fm = re.match(r'FIELD\s+(.*)', lt.strip(), re.IGNORECASE)
            if fm:
                fields.extend(f.strip().upper() for f in fm.group(1).split(",") if f.strip())
                self.current_line += 1
                continue

            mm = re.match(r'METHOD\s+(\w+)\s*\(([^)]*)\)', lt.strip(), re.IGNORECASE)
            if mm:
                mname = mm.group(1).upper()
                mparams = [p.strip().upper() for p in mm.group(2).split(",") if p.strip()]
                body_start = self.current_line + 1
                depth = 1
                self.current_line += 1
                while self.current_line < len(self.program_lines):
                    _, mlt = self.program_lines[self.current_line]
                    mlu = mlt.strip().upper() if mlt else ""
                    if mlu.startswith("METHOD "):
                        depth += 1
                    elif mlu == "END METHOD":
                        depth -= 1
                        if depth == 0:
                            break
                    self.current_line += 1
                body_end = self.current_line
                methods[mname] = {"params": mparams, "body_start": body_start, "body_end": body_end}
                self.current_line += 1
                continue

            self.current_line += 1

        self.variables["__STRUCT_" + name] = fields
        if methods:
            self.variables["__STRUCT_METHODS_" + name] = methods
            for mname, mdef in methods.items():
                func_name = "%s_%s" % (name, mname)
                self.func_defs[func_name] = mdef
        return "continue"

    def _modern_new(self, command):
        """NEW struct_name AS var_name -- create instance of struct."""
        m = re.match(r'NEW\s+(\w+)\s+AS\s+(\w+)', command, re.IGNORECASE)
        if not m:
            return "continue"
        struct_name = m.group(1).upper()
        var_name = m.group(2).upper()
        fields = self.variables.get("__STRUCT_" + struct_name)
        if not fields:
            self.output_cb("Undefined struct: %s" % struct_name)
            return "continue"
        instance = {}
        for f in fields:
            instance[f] = 0
        instance["__TYPE__"] = struct_name
        self.dicts[var_name] = instance
        return "continue"

    # ------------------------------------------------------------------
    #  IMPORT
    # ------------------------------------------------------------------

    def _modern_import(self, command):
        """IMPORT \"filename.tc\" -- include and execute another file."""
        m = re.match(r'IMPORT\s+"([^"]+)"', command, re.IGNORECASE)
        if not m:
            return "continue"
        filename = m.group(1)
        if filename in self.imported_modules:
            return "continue"
        self.imported_modules.add(filename)
        try:
            f = open(filename, "r")
            module_code = f.read()
            f.close()
            for raw_line in module_code.strip().split("\n"):
                line_text = raw_line.strip()
                if line_text:
                    self._execute(line_text)
        except IOError:
            self.output_cb("Module not found: %s" % filename)
        except Exception as e:
            self.output_cb("Import error: %s" % e)
        return "continue"

    # ------------------------------------------------------------------
    #  RANGE
    # ------------------------------------------------------------------

    def _modern_range(self, command):
        """RANGE list_name, start, end [, step]"""
        text = re.sub(r'^RANGE\s+', '', command, flags=re.IGNORECASE).strip()
        parts = _smart_split(text, ",")
        if len(parts) < 3:
            return "continue"
        name = parts[0].strip().upper()
        start = int(float(self.evaluate(parts[1].strip())))
        end = int(float(self.evaluate(parts[2].strip())))
        step = int(float(self.evaluate(parts[3].strip()))) if len(parts) > 3 else (1 if end >= start else -1)
        if step == 0:
            return "continue"
        if step > 0:
            rng = list(range(start, end + 1, step))
        else:
            rng = list(range(start, end - 1, step))
        self.lists[name] = rng
        self.variables[name] = rng
        return "continue"

    # ------------------------------------------------------------------
    #  File I/O: OPEN / CLOSE / READLINE / WRITELINE / READFILE / WRITEFILE / APPENDFILE
    # ------------------------------------------------------------------

    def _modern_open(self, command):
        """OPEN \"filename\" FOR INPUT|OUTPUT|APPEND AS #n"""
        m = re.match(
            r'OPEN\s+"([^"]+)"\s+FOR\s+(INPUT|OUTPUT|APPEND)\s+AS\s+#?(\d+)',
            command, re.IGNORECASE
        )
        if not m:
            self.output_cb('OPEN syntax: OPEN "file" FOR INPUT|OUTPUT|APPEND AS #n')
            return "continue"
        filename = m.group(1)
        mode_str = m.group(2).upper()
        handle = int(m.group(3))
        mode_map = {"INPUT": "r", "OUTPUT": "w", "APPEND": "a"}
        try:
            self.file_handles[handle] = open(filename, mode_map[mode_str])
        except Exception as e:
            self.output_cb("File error: %s" % e)
        return "continue"

    def _modern_close(self, command):
        """CLOSE #n  or  CLOSE ALL"""
        text = re.sub(r'^CLOSE\s+', '', command, flags=re.IGNORECASE).strip()
        if text.upper() == "ALL":
            for fh in self.file_handles.values():
                try:
                    fh.close()
                except Exception:
                    pass
            self.file_handles.clear()
        else:
            try:
                handle = int(text.lstrip("#"))
            except ValueError:
                return "continue"
            if handle in self.file_handles:
                try:
                    self.file_handles[handle].close()
                except Exception:
                    pass
                del self.file_handles[handle]
        return "continue"

    def _modern_readline(self, command):
        """READLINE #n, var_name"""
        text = re.sub(r'^READLINE\s+', '', command, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in text.split(",")]
        if len(parts) < 2:
            return "continue"
        handle = int(parts[0].lstrip("#"))
        var = parts[1].upper()
        fh = self.file_handles.get(handle)
        if fh:
            line = fh.readline()
            if line:
                self.variables[var] = line.rstrip("\n\r")
                self.variables["EOF"] = 0
            else:
                self.variables[var] = ""
                self.variables["EOF"] = 1
        return "continue"

    def _modern_writeline(self, command):
        """WRITELINE #n, expression"""
        text = re.sub(r'^WRITELINE\s+', '', command, flags=re.IGNORECASE).strip()
        parts = _smart_split(text, ",")
        if len(parts) < 2:
            return "continue"
        handle = int(parts[0].strip().lstrip("#"))
        val = self.evaluate(",".join(parts[1:]).strip())
        fh = self.file_handles.get(handle)
        if fh:
            fh.write(str(val) + "\n")
        return "continue"

    def _modern_readfile(self, command):
        """READFILE \"filename\", var_name"""
        m = re.match(r'READFILE\s+"([^"]+)"\s*,\s*(\w+)', command, re.IGNORECASE)
        if not m:
            return "continue"
        filename = m.group(1)
        var = m.group(2).upper()
        try:
            f = open(filename, "r")
            self.variables[var] = f.read()
            f.close()
        except Exception as e:
            self.output_cb("File error: %s" % e)
            self.variables[var] = ""
        return "continue"

    def _modern_writefile(self, command):
        """WRITEFILE \"filename\", expression"""
        m = re.match(r'WRITEFILE\s+"([^"]+)"\s*,\s*(.*)', command, re.IGNORECASE)
        if not m:
            return "continue"
        filename = m.group(1)
        val = self.evaluate(m.group(2).strip())
        try:
            f = open(filename, "w")
            f.write(str(val))
            f.close()
        except Exception as e:
            self.output_cb("File error: %s" % e)
        return "continue"

    def _modern_appendfile(self, command):
        """APPENDFILE \"filename\", expression"""
        m = re.match(r'APPENDFILE\s+"([^"]+)"\s*,\s*(.*)', command, re.IGNORECASE)
        if not m:
            return "continue"
        filename = m.group(1)
        val = self.evaluate(m.group(2).strip())
        try:
            f = open(filename, "a")
            f.write(str(val) + "\n")
            f.close()
        except Exception as e:
            self.output_cb("File error: %s" % e)
        return "continue"

    # ------------------------------------------------------------------
    #  FILEEXISTS / COPYFILE / DELETEFILE
    # ------------------------------------------------------------------

    def _modern_fileexists(self, command):
        """FILEEXISTS \"filename\", var"""
        m = re.match(r'FILEEXISTS\s+"([^"]+)"\s*,\s*(\w+)', command, re.IGNORECASE)
        if not m:
            return "continue"
        self.variables[m.group(2).upper()] = 1 if os.path.exists(m.group(1)) else 0
        return "continue"

    def _modern_copyfile(self, command):
        """COPYFILE \"source\", \"dest\""""
        m = re.match(r'COPYFILE\s+"([^"]+)"\s*,\s*"([^"]+)"', command, re.IGNORECASE)
        if not m:
            return "continue"
        try:
            if _shutil:
                _shutil.copyfile(m.group(1), m.group(2))
            else:
                src = open(m.group(1), "rb")
                dst = open(m.group(2), "wb")
                dst.write(src.read())
                src.close()
                dst.close()
        except Exception as e:
            self.output_cb("File error: %s" % e)
        return "continue"

    def _modern_deletefile(self, command):
        """DELETEFILE \"filename\""""
        m = re.match(r'DELETEFILE\s+"([^"]+)"', command, re.IGNORECASE)
        if not m:
            return "continue"
        try:
            os.remove(m.group(1))
        except Exception as e:
            self.output_cb("File error: %s" % e)
        return "continue"

    # ------------------------------------------------------------------
    #  UNSET / EVAL / PROGRAMINFO
    # ------------------------------------------------------------------

    def _modern_unset(self, command):
        """UNSET var -- remove variable."""
        text = re.sub(r'^UNSET\s+', '', command, flags=re.IGNORECASE).strip().upper()
        self.variables.pop(text, None)
        self.lists.pop(text, None)
        self.dicts.pop(text, None)
        return "continue"

    def _modern_eval(self, command):
        """EVAL expr [AS var]"""
        text = re.sub(r'^EVAL\s+', '', command, flags=re.IGNORECASE).strip()
        as_m = re.match(r'(.+?)\s+AS\s+(\w+)$', text, re.IGNORECASE)
        if as_m:
            val = self.evaluate(as_m.group(1).strip())
            self.variables[as_m.group(2).upper()] = val
        else:
            self.output_cb(str(self.evaluate(text)))
        return "continue"

    def _modern_programinfo(self, command):
        """PROGRAMINFO [INTO var]"""
        m = re.match(r'PROGRAMINFO(?:\s+INTO\s+(\w+))?', command, re.IGNORECASE)
        info = "lines=%d vars=%d lists=%d dicts=%d" % (
            len(self.program_lines), len(self.variables),
            len(self.lists), len(self.dicts))
        var = m.group(1).upper() if m and m.group(1) else None
        if var:
            self.variables[var] = info
        else:
            self.output_cb(info)
        return "continue"

    # ------------------------------------------------------------------
    #  Prolog-style commands
    # ------------------------------------------------------------------

    def _prolog_assert(self, cmd, command):
        """ASSERTA/ASSERTZ fact -- add fact to knowledge base."""
        term = re.sub(r'^(ASSERTA|ASSERTZ)\s*', '', command, flags=re.IGNORECASE).strip()
        if not term:
            return "continue"
        if cmd == "ASSERTA":
            self.prolog_facts.insert(0, term)
        else:
            self.prolog_facts.append(term)
        return "continue"

    def _prolog_retract(self, command):
        """RETRACT fact -- remove fact from knowledge base."""
        term = re.sub(r'^RETRACT\s*', '', command, flags=re.IGNORECASE).strip()
        if term in self.prolog_facts:
            self.prolog_facts.remove(term)
            self.output_cb("TRUE")
        else:
            self.output_cb("FALSE")
        return "continue"

    def _prolog_query(self, command):
        """QUERY fact -- check if fact exists."""
        term = re.sub(r'^QUERY\s*', '', command, flags=re.IGNORECASE).strip()
        self.output_cb("TRUE" if term in self.prolog_facts else "FALSE")
        return "continue"

    def _prolog_facts(self):
        """FACTS -- list all facts."""
        if not self.prolog_facts:
            self.output_cb("(no facts)")
        else:
            for fact in self.prolog_facts:
                self.output_cb(fact)
        return "continue"

    # ==================================================================
    #  Convenience: get_current_time for error history
    # ==================================================================

    @staticmethod
    def get_current_time():
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
