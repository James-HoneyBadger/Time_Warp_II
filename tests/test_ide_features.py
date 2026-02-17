#!/usr/bin/env python3
"""
Tests for IDE features: watch expressions, profiler, code formatter,
snippet manager, undo/redo history, and import graph visualization.
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Ensure project root is on sys.path
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.features.ide_features import (
    WatchManager,
    Profiler,
    SnippetManager,
    UndoHistoryManager,
    format_code,
    parse_imports,
    build_import_graph,
    format_import_graph,
)
from tests.helpers import run_program, FakeOutputWidget
from core.interpreter import TempleCodeInterpreter


# =====================================================================
#  Watch Expressions
# =====================================================================

class TestWatchManager:
    """Tests for the WatchManager class."""

    def test_add_expression(self):
        wm = WatchManager()
        wm.add("X")
        assert "X" in wm.expressions

    def test_add_no_duplicates(self):
        wm = WatchManager()
        wm.add("X")
        wm.add("X")
        assert len(wm.expressions) == 1

    def test_remove_expression(self):
        wm = WatchManager()
        wm.add("X")
        wm.remove("X")
        assert "X" not in wm.expressions

    def test_clear(self):
        wm = WatchManager()
        wm.add("X")
        wm.add("Y")
        wm.clear()
        assert len(wm.expressions) == 0

    def test_evaluate_all_with_variables(self):
        interp = TempleCodeInterpreter()
        interp.variables["X"] = 42
        interp.variables["NAME"] = "hello"

        wm = WatchManager()
        wm.add("X")
        wm.add("NAME")
        results = wm.evaluate_all(interp)
        assert len(results) == 2
        assert results[0] == ("X", "42")
        assert results[1] == ("NAME", "'hello'")

    def test_evaluate_missing_variable(self):
        interp = TempleCodeInterpreter()
        wm = WatchManager()
        wm.add("MISSING")
        results = wm.evaluate_all(interp)
        assert len(results) == 1
        # Should try evaluate_expression and either return a value or error
        assert results[0][0] == "MISSING"

    def test_format_report_empty(self):
        interp = TempleCodeInterpreter()
        wm = WatchManager()
        report = wm.format_report(interp)
        assert "no watches" in report

    def test_format_report_with_data(self):
        interp = TempleCodeInterpreter()
        interp.variables["X"] = 10
        wm = WatchManager()
        wm.add("X")
        report = wm.format_report(interp)
        assert "X = 10" in report

    def test_watch_in_interpreter_breakpoint(self):
        """Verify watch manager is attached and reports at breakpoint."""
        out = FakeOutputWidget()
        interp = TempleCodeInterpreter(out)
        wm = WatchManager()
        wm.add("X")
        interp.watch_manager = wm
        interp.set_debug_mode(True)
        interp.toggle_breakpoint(1)  # breakpoint on line 2 (0-indexed)

        interp.run_program("LET X = 42\nPRINT X")
        output = out.raw
        assert "Watches" in output or "X" in output


# =====================================================================
#  Profiler
# =====================================================================

class TestProfiler:
    """Tests for the Profiler class."""

    def test_disabled_by_default(self):
        p = Profiler()
        assert not p.enabled

    def test_begin_end_line(self):
        p = Profiler()
        p.enabled = True
        p.begin_line(1, "PRINT 42")
        time.sleep(0.001)
        p.end_line(1)
        stats = p.get_stats()
        assert 1 in stats
        assert stats[1]["count"] == 1
        assert stats[1]["total_time"] > 0

    def test_multiple_hits(self):
        p = Profiler()
        p.enabled = True
        for _ in range(5):
            p.begin_line(1, "LET X = X + 1")
            p.end_line(1)
        stats = p.get_stats()
        assert stats[1]["count"] == 5

    def test_reset(self):
        p = Profiler()
        p.enabled = True
        p.begin_line(1, "test")
        p.end_line(1)
        p.reset()
        assert p.get_stats() == {}

    def test_format_report_empty(self):
        p = Profiler()
        p.enabled = True
        report = p.format_report()
        assert "No profiling data" in report

    def test_format_report_with_data(self):
        p = Profiler()
        p.enabled = True
        p.begin_line(1, "PRINT 42")
        p.end_line(1)
        p.begin_line(2, "LET X = 1")
        p.end_line(2)
        report = p.format_report()
        assert "PROFILER REPORT" in report
        assert "PRINT 42" in report
        assert "LET X = 1" in report

    def test_profiler_integrated_with_interpreter(self):
        """Run a program with profiler enabled and verify stats collected."""
        out = FakeOutputWidget()
        interp = TempleCodeInterpreter(out)
        profiler = Profiler()
        profiler.enabled = True
        interp.profiler = profiler

        interp.run_program("LET X = 1\nLET Y = 2\nPRINT X + Y")
        stats = profiler.get_stats()
        assert len(stats) >= 2  # at least 2 lines profiled
        # Report should appear in output
        assert "PROFILER REPORT" in out.raw

    def test_no_profiling_when_disabled(self):
        p = Profiler()
        p.begin_line(1, "PRINT 42")
        p.end_line(1)
        assert p.get_stats() == {}


# =====================================================================
#  Code Formatter
# =====================================================================

class TestCodeFormatter:
    """Tests for the format_code function."""

    def test_basic_indentation(self):
        code = "FOR I = 1 TO 10\nPRINT I\nNEXT I"
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[0] == "FOR I = 1 TO 10"
        assert lines[1] == "  PRINT I"
        assert lines[2] == "NEXT I"

    def test_nested_indentation(self):
        code = "FOR I = 1 TO 5\nIF I > 2 THEN\nPRINT I\nENDIF\nNEXT I"
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[0] == "FOR I = 1 TO 5"
        assert lines[1] == "  IF I > 2 THEN"
        assert lines[2] == "    PRINT I"
        assert lines[3] == "  ENDIF"
        assert lines[4] == "NEXT I"

    def test_while_indentation(self):
        code = "WHILE X < 10\nLET X = X + 1\nWEND"
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[0] == "WHILE X < 10"
        assert lines[1] == "  LET X = X + 1"
        assert lines[2] == "WEND"

    def test_if_else(self):
        code = 'IF X > 0 THEN\nPRINT "yes"\nELSE\nPRINT "no"\nENDIF'
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[0] == 'IF X > 0 THEN'
        assert lines[1] == '  PRINT "yes"'
        assert lines[2] == 'ELSE'
        assert lines[3] == '  PRINT "no"'
        assert lines[4] == 'ENDIF'

    def test_single_line_if_no_indent(self):
        code = 'IF X > 0 THEN PRINT "yes"\nPRINT "always"'
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[0] == 'IF X > 0 THEN PRINT "yes"'
        assert lines[1] == 'PRINT "always"'

    def test_preserves_blank_lines(self):
        code = "PRINT 1\n\nPRINT 2"
        formatted = format_code(code)
        assert "\n\n" in formatted

    def test_custom_indent_width(self):
        code = "FOR I = 1 TO 10\nPRINT I\nNEXT I"
        formatted = format_code(code, indent_width=4)
        lines = formatted.split("\n")
        assert lines[1] == "    PRINT I"

    def test_sub_function_indentation(self):
        code = "SUB MySub(a)\nPRINT a\nEND SUB"
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[0] == "SUB MySub(a)"
        assert lines[1] == "  PRINT a"
        assert lines[2] == "END SUB"

    def test_try_catch(self):
        code = "TRY\nPRINT 1/0\nCATCH err\nPRINT err\nEND TRY"
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[0] == "TRY"
        assert lines[1] == "  PRINT 1/0"
        assert lines[2] == "CATCH err"
        assert lines[3] == "  PRINT err"
        assert lines[4] == "END TRY"

    def test_line_numbers_preserved(self):
        code = "10 FOR I = 1 TO 5\n20 PRINT I\n30 NEXT I"
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert "10 FOR" in lines[0]
        assert "20 PRINT" in lines[1]
        assert lines[1].startswith("  ")
        assert "30 NEXT" in lines[2]

    def test_strips_trailing_whitespace(self):
        code = "PRINT 1   \nPRINT 2  "
        formatted = format_code(code)
        for line in formatted.split("\n"):
            assert line == line.rstrip()

    def test_elseif(self):
        code = 'IF X = 1 THEN\nPRINT "one"\nELSEIF X = 2 THEN\nPRINT "two"\nENDIF'
        formatted = format_code(code)
        lines = formatted.split("\n")
        assert lines[2] == 'ELSEIF X = 2 THEN'
        assert lines[3] == '  PRINT "two"'


# =====================================================================
#  Snippet Manager
# =====================================================================

class TestSnippetManager:
    """Tests for the SnippetManager class."""

    def test_builtin_snippets_exist(self):
        sm = SnippetManager()
        all_snips = sm.all_snippets()
        assert "for_loop" in all_snips
        assert "while_loop" in all_snips
        assert "if_block" in all_snips

    def test_get_builtin(self):
        sm = SnippetManager()
        snip = sm.get("for_loop")
        assert snip is not None
        assert "FOR" in snip["body"]

    def test_add_user_snippet(self):
        sm = SnippetManager()
        sm.add("my_test", "Test Snippet", "mytest", "PRINT 42", "A test snippet")
        snip = sm.get("my_test")
        assert snip is not None
        assert snip["body"] == "PRINT 42"
        # Clean up
        sm.remove("my_test")

    def test_remove_user_snippet(self):
        sm = SnippetManager()
        sm.add("temp_snip", "Temp", "tmp", "PRINT 1")
        assert sm.remove("temp_snip")
        assert sm.get("temp_snip") is None or sm.get("temp_snip") == sm.BUILTIN_SNIPPETS.get("temp_snip")

    def test_cannot_remove_builtin(self):
        sm = SnippetManager()
        result = sm.remove("for_loop")
        assert not result  # built-in snippets not in _user_snippets

    def test_find_by_prefix(self):
        sm = SnippetManager()
        results = sm.find_by_prefix("for")
        assert any(k == "for_loop" for k, _ in results)

    def test_list_keys(self):
        sm = SnippetManager()
        keys = sm.list_keys()
        assert isinstance(keys, list)
        assert len(keys) >= len(sm.BUILTIN_SNIPPETS)

    def test_user_overrides_builtin(self):
        sm = SnippetManager()
        sm.add("for_loop", "My FOR", "for", "MY CUSTOM FOR", "override")
        snip = sm.get("for_loop")
        assert snip["body"] == "MY CUSTOM FOR"
        # Clean up
        sm.remove("for_loop")


# =====================================================================
#  Undo/Redo History
# =====================================================================

class TestUndoHistory:
    """Tests for the UndoHistoryManager class."""

    def test_snapshot(self):
        uh = UndoHistoryManager()
        uh.snapshot("hello", "initial")
        assert len(uh.get_history_list()) == 1

    def test_no_duplicate_snapshots(self):
        uh = UndoHistoryManager()
        uh.snapshot("hello", "edit")
        uh.snapshot("hello", "edit")
        assert len(uh.get_history_list()) == 1

    def test_undo(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        uh.snapshot("v2", "edit2")
        result = uh.undo()
        assert result == "v1"

    def test_redo(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        uh.snapshot("v2", "edit2")
        uh.undo()
        result = uh.redo()
        assert result == "v2"

    def test_undo_at_beginning_returns_none(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        assert uh.undo() is None

    def test_redo_at_end_returns_none(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        assert uh.redo() is None

    def test_can_undo_redo(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        uh.snapshot("v2", "edit2")
        assert uh.can_undo()
        assert not uh.can_redo()
        uh.undo()
        assert uh.can_redo()

    def test_jump_to(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        uh.snapshot("v2", "edit2")
        uh.snapshot("v3", "edit3")
        result = uh.jump_to(0)
        assert result == "v1"

    def test_jump_to_invalid(self):
        uh = UndoHistoryManager()
        assert uh.jump_to(99) is None

    def test_clear(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        uh.clear()
        assert len(uh.get_history_list()) == 0
        assert not uh.can_undo()

    def test_max_history(self):
        uh = UndoHistoryManager()
        uh.MAX_HISTORY = 5
        for i in range(10):
            uh.snapshot(f"v{i}", f"edit{i}")
        assert len(uh.get_history_list()) == 5

    def test_truncate_forward_on_new_edit(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        uh.snapshot("v2", "edit2")
        uh.snapshot("v3", "edit3")
        uh.undo()  # back to v2
        uh.snapshot("v4", "edit4")  # should truncate v3
        history = uh.get_history_list()
        assert len(history) == 3  # v1, v2, v4

    def test_history_list_has_current_marker(self):
        uh = UndoHistoryManager()
        uh.snapshot("v1", "edit1")
        uh.snapshot("v2", "edit2")
        history = uh.get_history_list()
        current_entries = [e for e in history if e["current"]]
        assert len(current_entries) == 1
        assert current_entries[0]["index"] == 1


# =====================================================================
#  Import Graph
# =====================================================================

class TestImportGraph:
    """Tests for import parsing and graph building."""

    def test_parse_imports_quoted(self):
        source = 'IMPORT "utils.tc"\nPRINT 1\nIMPORT "math_lib.tc"'
        result = parse_imports(source)
        assert result == ["utils.tc", "math_lib.tc"]

    def test_parse_imports_unquoted(self):
        source = "IMPORT utils\nPRINT 1"
        result = parse_imports(source)
        assert result == ["utils"]

    def test_parse_imports_empty(self):
        source = "PRINT 1\nLET X = 2"
        result = parse_imports(source)
        assert result == []

    def test_parse_imports_case_insensitive(self):
        source = 'import "lower.tc"\nImport "mixed.tc"'
        result = parse_imports(source)
        assert "lower.tc" in result
        assert "mixed.tc" in result

    def test_build_import_graph_single_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            main = Path(tmpdir) / "main.tc"
            main.write_text('IMPORT "helper.tc"\nPRINT 1', encoding="utf-8")
            helper = Path(tmpdir) / "helper.tc"
            helper.write_text("PRINT 2", encoding="utf-8")

            graph = build_import_graph(str(main))
            assert "main.tc" in graph
            assert "helper.tc" in graph["main.tc"]
            assert graph["helper.tc"] == []

    def test_build_import_graph_circular(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            a = Path(tmpdir) / "a.tc"
            b = Path(tmpdir) / "b.tc"
            a.write_text('IMPORT "b.tc"', encoding="utf-8")
            b.write_text('IMPORT "a.tc"', encoding="utf-8")

            graph = build_import_graph(str(a))
            assert "a.tc" in graph
            assert "b.tc" in graph
            # No infinite loop

    def test_build_import_graph_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            main = Path(tmpdir) / "main.tc"
            main.write_text('IMPORT "missing.tc"', encoding="utf-8")

            graph = build_import_graph(str(main))
            assert "missing.tc" in graph
            assert graph["missing.tc"] == []

    def test_format_import_graph_empty(self):
        result = format_import_graph({})
        assert "No imports found" in result

    def test_format_import_graph_tree(self):
        graph = {"main.tc": ["helper.tc", "utils.tc"], "helper.tc": [], "utils.tc": []}
        result = format_import_graph(graph)
        assert "main.tc" in result
        assert "helper.tc" in result
        assert "utils.tc" in result
        assert "Files:" in result

    def test_format_import_graph_circular_annotation(self):
        graph = {"a.tc": ["b.tc"], "b.tc": ["a.tc"]}
        result = format_import_graph(graph)
        assert "circular" in result


# =====================================================================
#  CLI format sub-command
# =====================================================================

class TestCLIFormat:
    """Tests for the CLI format sub-command."""

    def test_format_stdout(self):
        from core.cli import main as cli_main  # noqa: C0415
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tc",
                                         delete=False, encoding="utf-8") as f:
            f.write("FOR I = 1 TO 5\nPRINT I\nNEXT I\n")
            f.flush()
            path = f.name
        try:
            import io
            from unittest.mock import patch

            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                cli_main(["format", path])
            output = mock_stdout.getvalue()
            assert "  PRINT I" in output
        finally:
            os.unlink(path)

    def test_format_check_pass(self):
        from core.cli import main as cli_main  # noqa: C0415
        # Already formatted
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tc",
                                         delete=False, encoding="utf-8") as f:
            f.write("FOR I = 1 TO 5\n  PRINT I\nNEXT I\n")
            f.flush()
            path = f.name
        try:
            # Should not raise SystemExit
            cli_main(["format", path, "--check"])
        except SystemExit as e:
            pytest.fail(f"Format check failed unexpectedly: {e}")
        finally:
            os.unlink(path)

    def test_format_inplace(self):
        from core.cli import main as cli_main  # noqa: C0415
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tc",
                                         delete=False, encoding="utf-8") as f:
            f.write("FOR I = 1 TO 5\nPRINT I\nNEXT I\n")
            f.flush()
            path = f.name
        try:
            cli_main(["format", path, "--inplace"])
            content = Path(path).read_text(encoding="utf-8")
            assert "  PRINT I" in content
        finally:
            os.unlink(path)


# =====================================================================
#  CLI run --profile flag
# =====================================================================

class TestCLIProfile:
    """Test that --profile attaches profiler to interpreter."""

    def test_profile_flag(self):
        from core.cli import main as cli_main  # noqa: C0415
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tc",
                                         delete=False, encoding="utf-8") as f:
            f.write('PRINT "hello"\n')
            f.flush()
            path = f.name
        try:
            import io
            from unittest.mock import patch

            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                cli_main(["run", path, "--profile"])
            output = mock_stdout.getvalue()
            assert "PROFILER REPORT" in output
        finally:
            os.unlink(path)
