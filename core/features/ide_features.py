#!/usr/bin/env python3
"""
IDE feature modules for Time Warp II.

Provides:
- Watch expressions (debug mode variable inspector)
- Program profiler (per-line timing & hit counts)
- Code formatter / auto-indenter
- Snippet manager (user-defined code templates)
- Undo/redo history viewer
- Import graph visualization

Copyright © 2025-2026 Honey Badger Universe. All rights reserved.
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
#  Snippet storage path
# ---------------------------------------------------------------------------

SNIPPETS_FILE = Path.home() / ".templecode_snippets.json"


# ===================================================================
#  1. Watch Expressions
# ===================================================================

class WatchManager:
    """Manage a set of watched variable names and evaluate them."""

    def __init__(self) -> None:
        self.expressions: List[str] = []

    def add(self, expr: str) -> None:
        """Add a watch expression (variable name or simple expression)."""
        expr = expr.strip()
        if expr and expr not in self.expressions:
            self.expressions.append(expr)

    def remove(self, expr: str) -> None:
        """Remove a watch expression."""
        expr = expr.strip()
        if expr in self.expressions:
            self.expressions.remove(expr)

    def clear(self) -> None:
        """Remove all watch expressions."""
        self.expressions.clear()

    def evaluate_all(self, interpreter) -> list[tuple[str, str]]:
        """Evaluate all watch expressions against the interpreter state.

        Returns a list of (expression, value_string) tuples.
        """
        results: list[tuple[str, str]] = []
        for expr in self.expressions:
            try:
                # First try as a plain variable lookup
                upper = expr.upper()
                if upper in interpreter.variables:
                    results.append((expr, repr(interpreter.variables[upper])))
                elif hasattr(interpreter, 'evaluate_expression'):
                    val = interpreter.evaluate_expression(expr)
                    results.append((expr, repr(val)))
                else:
                    results.append((expr, "<unavailable>"))
            except Exception as exc:
                results.append((expr, f"<error: {exc}>"))
        return results

    def format_report(self, interpreter) -> str:
        """Return a formatted watch report string."""
        pairs = self.evaluate_all(interpreter)
        if not pairs:
            return "  (no watches)"
        lines = []
        for expr, val in pairs:
            lines.append(f"  {expr} = {val}")
        return "\n".join(lines)


# ===================================================================
#  2. Program Profiler
# ===================================================================

class Profiler:
    """Collect per-line execution counts and timing."""

    def __init__(self) -> None:
        self.enabled: bool = False
        self._line_stats: Dict[int, dict] = {}
        # Each entry: { "count": int, "total_time": float, "source": str }
        self._current_line: int = -1
        self._current_start: float = 0.0

    def reset(self) -> None:
        """Clear all profiling data."""
        self._line_stats.clear()
        self._current_line = -1
        self._current_start = 0.0

    def begin_line(self, line_num: int, source: str) -> None:
        """Mark the start of executing a line."""
        if not self.enabled:
            return
        self._current_line = line_num
        self._current_start = time.perf_counter()
        if line_num not in self._line_stats:
            self._line_stats[line_num] = {
                "count": 0,
                "total_time": 0.0,
                "source": source[:80],
            }

    def end_line(self, line_num: int) -> None:
        """Mark the end of executing a line."""
        if not self.enabled or line_num not in self._line_stats:
            return
        elapsed = time.perf_counter() - self._current_start
        self._line_stats[line_num]["count"] += 1
        self._line_stats[line_num]["total_time"] += elapsed

    def get_stats(self) -> dict[int, dict]:
        """Return a copy of the per-line statistics."""
        return dict(self._line_stats)

    def format_report(self, top_n: int = 20) -> str:
        """Return a formatted profiler report.

        Lines are sorted by total time descending.
        """
        if not self._line_stats:
            return "No profiling data collected."

        lines_by_time = sorted(
            self._line_stats.items(),
            key=lambda item: item[1]["total_time"],
            reverse=True,
        )

        total_time = sum(s["total_time"] for _, s in lines_by_time)
        total_calls = sum(s["count"] for _, s in lines_by_time)

        report = ["═══ PROFILER REPORT ═══"]
        report.append(f"Total time: {total_time:.4f}s  |  Total line executions: {total_calls}")
        report.append("")
        report.append(f"{'Line':>5}  {'Hits':>6}  {'Total(ms)':>10}  {'Avg(ms)':>9}  {'%':>5}  Source")
        report.append("─" * 78)

        for line_num, stats in lines_by_time[:top_n]:
            count = stats["count"]
            total_ms = stats["total_time"] * 1000
            avg_ms = total_ms / count if count else 0
            pct = (stats["total_time"] / total_time * 100) if total_time else 0
            src = stats["source"]
            report.append(
                f"{line_num:>5}  {count:>6}  {total_ms:>10.2f}  {avg_ms:>9.3f}  {pct:>5.1f}  {src}"
            )

        report.append("─" * 78)
        return "\n".join(report)


# ===================================================================
#  3. Code Formatter / Auto-indenter
# ===================================================================

# Block openers (increase indent after this line)
_INDENT_OPENERS = {
    "FOR", "WHILE", "IF", "ELSEIF", "ELSE", "DO", "REPEAT",
    "SELECT", "SUB", "FUNCTION", "TRY", "CATCH",
}

# Block closers (decrease indent for this line)
_INDENT_CLOSERS = {
    "NEXT", "WEND", "ENDIF", "END IF", "LOOP", "END SELECT",
    "END SUB", "END FUNCTION", "END TRY", "ELSE", "ELSEIF",
    "CATCH",
}


def format_code(source: str, indent_width: int = 2) -> str:
    """Auto-indent TempleCode source code.

    - Strips trailing whitespace from every line.
    - Normalises indentation based on block structure.
    - Preserves blank lines.
    """
    lines = source.split("\n")
    result: list[str] = []
    indent_level = 0
    indent_str = " " * indent_width

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            result.append("")
            continue

        # Parse optional line number
        line_num_prefix = ""
        body = stripped
        m = re.match(r'^(\d+)\s+(.*)', stripped)
        if m:
            line_num_prefix = m.group(1) + " "
            body = m.group(2).strip()

        upper_body = body.upper()

        # Determine the first keyword token
        first_word = upper_body.split()[0] if upper_body.split() else ""
        # Check for two-word closers
        two_word = " ".join(upper_body.split()[:2]) if len(upper_body.split()) >= 2 else ""

        # Decrease indent BEFORE writing this line if it's a closer
        is_closer = (first_word in _INDENT_CLOSERS or two_word in _INDENT_CLOSERS)
        # ELSE/ELSEIF/CATCH are both closers and openers
        is_both = first_word in ("ELSE", "ELSEIF", "CATCH")

        if is_closer and not is_both:
            indent_level = max(0, indent_level - 1)
        elif is_both:
            indent_level = max(0, indent_level - 1)

        result.append(f"{indent_str * indent_level}{line_num_prefix}{body}")

        # Increase indent AFTER writing this line if it's an opener
        is_opener = False
        if first_word in _INDENT_OPENERS:
            is_opener = True
        # Multi-line IF: "IF ... THEN" with nothing after THEN
        if first_word == "IF" and "THEN" in upper_body:
            after_then = upper_body.split("THEN", 1)[1].strip()
            if after_then:
                is_opener = False  # single-line IF

        if is_opener or is_both:
            indent_level += 1

    return "\n".join(result)


# ===================================================================
#  4. Snippet Manager
# ===================================================================

class SnippetManager:
    """Manage user-defined code snippets (templates)."""

    # Built-in snippets that ship with the IDE
    BUILTIN_SNIPPETS: dict[str, dict] = {
        "for_loop": {
            "label": "FOR Loop",
            "prefix": "for",
            "body": "FOR I = 1 TO 10\n  PRINT I\nNEXT I",
            "description": "Basic FOR/NEXT loop",
        },
        "while_loop": {
            "label": "WHILE Loop",
            "prefix": "while",
            "body": "LET X = 0\nWHILE X < 10\n  LET X = X + 1\nWEND",
            "description": "WHILE/WEND loop",
        },
        "if_block": {
            "label": "IF Block",
            "prefix": "if",
            "body": 'IF X > 0 THEN\n  PRINT "positive"\nELSE\n  PRINT "non-positive"\nENDIF',
            "description": "Multi-line IF/ELSE/ENDIF",
        },
        "sub_def": {
            "label": "SUB Definition",
            "prefix": "sub",
            "body": "SUB MySub(param)\n  PRINT param\nEND SUB",
            "description": "Subroutine definition",
        },
        "function_def": {
            "label": "FUNCTION Definition",
            "prefix": "func",
            "body": "FUNCTION Add(a, b)\n  RETURN a + b\nEND FUNCTION",
            "description": "Function definition",
        },
        "turtle_square": {
            "label": "Turtle Square",
            "prefix": "tsquare",
            "body": "REPEAT 4 [FORWARD 100 RIGHT 90]",
            "description": "Draw a square with turtle",
        },
        "turtle_circle": {
            "label": "Turtle Circle",
            "prefix": "tcircle",
            "body": "SETCOLOR \"red\"\nCIRCLE 50",
            "description": "Draw a circle with turtle",
        },
        "try_catch": {
            "label": "TRY/CATCH",
            "prefix": "try",
            "body": "TRY\n  REM risky code here\nCATCH err\n  PRINT err\nEND TRY",
            "description": "Error handling block",
        },
        "select_case": {
            "label": "SELECT CASE",
            "prefix": "select",
            "body": "SELECT CASE X\n  CASE 1\n    PRINT \"one\"\n  CASE 2\n    PRINT \"two\"\n  CASE ELSE\n    PRINT \"other\"\nEND SELECT",
            "description": "Multi-branch SELECT CASE",
        },
        "input_prompt": {
            "label": "Input Prompt",
            "prefix": "input",
            "body": 'INPUT "Enter your name: "; NAME$\nPRINT "Hello, "; NAME$',
            "description": "Input prompt with greeting",
        },
    }

    def __init__(self) -> None:
        self._user_snippets: Dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        """Load user snippets from disk."""
        try:
            if SNIPPETS_FILE.exists():
                with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
                    self._user_snippets = json.load(f)
        except Exception:
            self._user_snippets = {}

    def _save(self) -> None:
        """Persist user snippets to disk."""
        try:
            with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._user_snippets, f, indent=2)
        except Exception:
            pass

    def all_snippets(self) -> dict[str, dict]:
        """Return merged dict of builtin + user snippets (user overrides)."""
        merged = dict(self.BUILTIN_SNIPPETS)
        merged.update(self._user_snippets)
        return merged

    def get(self, key: str) -> Optional[dict]:
        """Look up a snippet by key."""
        if key in self._user_snippets:
            return self._user_snippets[key]
        return self.BUILTIN_SNIPPETS.get(key)

    def find_by_prefix(self, prefix: str) -> list[tuple[str, dict]]:
        """Find snippets whose prefix starts with the given text."""
        prefix_lower = prefix.lower()
        results = []
        for key, snip in self.all_snippets().items():
            if snip.get("prefix", "").lower().startswith(prefix_lower):
                results.append((key, snip))
        return results

    def add(self, key: str, label: str, prefix: str, body: str,
            description: str = "") -> None:
        """Add or update a user snippet."""
        self._user_snippets[key] = {
            "label": label,
            "prefix": prefix,
            "body": body,
            "description": description,
        }
        self._save()

    def remove(self, key: str) -> bool:
        """Remove a user snippet. Returns True if removed."""
        if key in self._user_snippets:
            del self._user_snippets[key]
            self._save()
            return True
        return False

    def list_keys(self) -> list[str]:
        """Return sorted list of all snippet keys."""
        return sorted(self.all_snippets().keys())


# ===================================================================
#  5. Undo/Redo History Viewer
# ===================================================================

class UndoHistoryManager:
    """Track explicit undo/redo history snapshots.

    Tkinter's Text widget has built-in undo/redo, but this manager
    provides a visible history list the user can browse.
    """

    MAX_HISTORY = 50

    def __init__(self) -> None:
        self._history: List[dict] = []
        # index points to the *current* position in history
        # -1 means "at latest"
        self._index: int = -1

    def snapshot(self, content: str, description: str = "edit") -> None:
        """Record a snapshot of the editor content."""
        # If we're not at the end, truncate forward history
        if self._index != -1 and self._index < len(self._history) - 1:
            self._history = self._history[:self._index + 1]

        # Don't duplicate identical consecutive snapshots
        if self._history and self._history[-1]["content"] == content:
            return

        self._history.append({
            "content": content,
            "description": description,
            "timestamp": time.time(),
        })

        # Trim oldest entries
        if len(self._history) > self.MAX_HISTORY:
            self._history = self._history[-self.MAX_HISTORY:]

        self._index = len(self._history) - 1

    def undo(self) -> Optional[str]:
        """Move back in history, returning the previous content or None."""
        if self._index > 0:
            self._index -= 1
            return self._history[self._index]["content"]
        return None

    def redo(self) -> Optional[str]:
        """Move forward in history, returning the next content or None."""
        if self._index < len(self._history) - 1:
            self._index += 1
            return self._history[self._index]["content"]
        return None

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self._index > 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self._index < len(self._history) - 1

    def get_history_list(self) -> list[dict]:
        """Return the history list with metadata."""
        result = []
        for i, entry in enumerate(self._history):
            result.append({
                "index": i,
                "description": entry["description"],
                "timestamp": entry["timestamp"],
                "current": i == self._index,
                "length": len(entry["content"]),
            })
        return result

    def jump_to(self, index: int) -> Optional[str]:
        """Jump to a specific history entry, returning its content."""
        if 0 <= index < len(self._history):
            self._index = index
            return self._history[index]["content"]
        return None

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._index = -1


# ===================================================================
#  6. Import Graph Visualization
# ===================================================================

def parse_imports(source: str) -> list[str]:
    """Extract IMPORT statements from TempleCode source.

    Supports:
        IMPORT "filename.tc"
        IMPORT filename
    """
    imports = []
    for line in source.split("\n"):
        stripped = line.strip()
        m = re.match(r'^IMPORT\s+"([^"]+)"', stripped, re.IGNORECASE)
        if m:
            imports.append(m.group(1))
            continue
        m = re.match(r'^IMPORT\s+(\S+)', stripped, re.IGNORECASE)
        if m:
            imports.append(m.group(1))
    return imports


def build_import_graph(entry_file: str,
                       base_dir: Optional[str] = None) -> Dict[str, List[str]]:
    """Build a dependency graph starting from an entry file.

    Returns a dict mapping filename -> list of imported filenames.
    """
    if base_dir is None:
        base_dir = str(Path(entry_file).parent)

    graph: dict[str, list[str]] = {}
    visited: set[str] = set()
    queue = [str(Path(entry_file).name)]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        filepath = Path(base_dir) / current
        if not filepath.is_file():
            graph[current] = []
            continue

        try:
            source = filepath.read_text(encoding="utf-8")
        except Exception:
            graph[current] = []
            continue

        deps = parse_imports(source)
        graph[current] = deps

        for dep in deps:
            if dep not in visited:
                queue.append(dep)

    return graph


def format_import_graph(graph: dict[str, list[str]]) -> str:
    """Format an import graph as a readable tree string."""
    if not graph:
        return "No imports found."

    lines = ["═══ IMPORT DEPENDENCY GRAPH ═══", ""]

    # Find root nodes (files not imported by anyone)
    all_imported = set()
    for deps in graph.values():
        all_imported.update(deps)
    roots = [f for f in graph if f not in all_imported]
    if not roots:
        roots = list(graph.keys())[:1]

    visited: set[str] = set()

    def _tree(name: str, prefix: str = "", is_last: bool = True) -> None:
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{name}")
        visited.add(name)

        deps = graph.get(name, [])
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, dep in enumerate(deps):
            if dep in visited:
                is_last_child = i == len(deps) - 1
                conn = "└── " if is_last_child else "├── "
                lines.append(f"{child_prefix}{conn}{dep} (circular)")
            else:
                _tree(dep, child_prefix, i == len(deps) - 1)

    for i, root in enumerate(roots):
        if i > 0:
            lines.append("")
        _tree(root, "", i == len(roots) - 1)

    lines.append("")
    lines.append(f"Files: {len(graph)}  |  Edges: {sum(len(d) for d in graph.values())}")
    return "\n".join(lines)
