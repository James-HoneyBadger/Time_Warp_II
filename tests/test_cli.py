#!/usr/bin/env python3
"""Tests for the TempleCode CLI (core.cli)."""

import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.cli import build_parser, main, _resolve_file, _CLIOutputWidget, __version__


# ---------------------------------------------------------------------------
#  Version / help
# ---------------------------------------------------------------------------

class TestCLIVersion:
    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit, match="0"):
            main(["--version"])
        out = capsys.readouterr().out
        assert __version__ in out

    def test_no_command_shows_help(self, capsys):
        with pytest.raises(SystemExit, match="0"):
            main([])
        out = capsys.readouterr().out
        assert "run" in out or "usage" in out.lower()


# ---------------------------------------------------------------------------
#  run sub-command
# ---------------------------------------------------------------------------

class TestCLIRun:
    def test_run_hello(self, capsys):
        main(["run", "examples/templecode/hello.tc"])
        out = capsys.readouterr().out
        assert "Welcome to TempleCode" in out

    def test_run_fizzbuzz(self, capsys):
        main(["run", "examples/templecode/fizzbuzz.tc"])
        out = capsys.readouterr().out
        assert "FizzBuzz" in out

    def test_run_with_time(self, capsys):
        main(["run", "examples/templecode/hello.tc", "--time"])
        out = capsys.readouterr().out
        assert "Elapsed" in out

    def test_run_with_debug(self, capsys):
        main(["run", "examples/templecode/hello.tc", "--debug"])
        out = capsys.readouterr().out
        assert "Executing line" in out

    def test_run_example_name_only(self, capsys):
        """File name without path should auto-resolve from examples/."""
        main(["run", "hello.tc"])
        out = capsys.readouterr().out
        assert "Welcome to TempleCode" in out

    def test_run_missing_file(self):
        with pytest.raises(SystemExit):
            main(["run", "nonexistent_program_xyz.tc"])


# ---------------------------------------------------------------------------
#  check sub-command
# ---------------------------------------------------------------------------

class TestCLICheck:
    def test_check_clean_file(self, capsys):
        main(["check", "examples/templecode/hello.tc"])
        out = capsys.readouterr().out
        assert "No issues found" in out

    def test_check_reports_unclosed_for(self, tmp_path, capsys):
        bad_file = tmp_path / "bad.tc"
        bad_file.write_text("FOR I = 1 TO 10\nPRINT I\n", encoding="utf-8")
        with pytest.raises(SystemExit, match="1"):
            main(["check", str(bad_file)])
        out = capsys.readouterr().out
        assert "unclosed FOR" in out

    def test_check_reports_unclosed_if(self, tmp_path, capsys):
        bad_file = tmp_path / "bad_if.tc"
        bad_file.write_text("IF X > 0 THEN\nPRINT X\n", encoding="utf-8")
        with pytest.raises(SystemExit, match="1"):
            main(["check", str(bad_file)])
        out = capsys.readouterr().out
        assert "unclosed IF" in out

    def test_check_reports_unclosed_while(self, tmp_path, capsys):
        bad_file = tmp_path / "bad_while.tc"
        bad_file.write_text("WHILE X < 10\nLET X = X + 1\n", encoding="utf-8")
        with pytest.raises(SystemExit, match="1"):
            main(["check", str(bad_file)])
        out = capsys.readouterr().out
        assert "unclosed WHILE" in out

    def test_check_balanced_for(self, tmp_path, capsys):
        good_file = tmp_path / "good.tc"
        good_file.write_text("FOR I = 1 TO 5\nPRINT I\nNEXT I\n", encoding="utf-8")
        main(["check", str(good_file)])
        out = capsys.readouterr().out
        assert "No issues found" in out


# ---------------------------------------------------------------------------
#  _CLIOutputWidget
# ---------------------------------------------------------------------------

class TestCLIOutputWidget:
    def test_insert_writes_to_stream(self, capsys):
        w = _CLIOutputWidget()
        w.insert("end", "hello world")
        out = capsys.readouterr().out
        assert "hello world" in out

    def test_see_and_delete_are_noops(self):
        w = _CLIOutputWidget()
        w.see("end")  # should not raise
        w.delete("1.0", "end")  # should not raise


# ---------------------------------------------------------------------------
#  _resolve_file
# ---------------------------------------------------------------------------

class TestResolveFile:
    def test_resolve_existing_path(self, tmp_path):
        f = tmp_path / "test.tc"
        f.write_text("PRINT 1", encoding="utf-8")
        assert _resolve_file(str(f)) == f.resolve()

    def test_resolve_example_by_name(self):
        # Should find hello.tc in examples/templecode/
        p = _resolve_file("hello.tc")
        assert p.name == "hello.tc"
        assert p.exists()

    def test_resolve_adds_extension(self):
        p = _resolve_file("hello")
        assert p.name == "hello.tc"
        assert p.exists()

    def test_resolve_missing_exits(self):
        with pytest.raises(SystemExit):
            _resolve_file("absolutely_nonexistent_file_xyz.tc")


# ---------------------------------------------------------------------------
#  build_parser
# ---------------------------------------------------------------------------

class TestBuildParser:
    def test_parser_subcommands(self):
        parser = build_parser()
        # Verify it parses known commands
        args = parser.parse_args(["run", "test.tc"])
        assert args.command == "run"
        assert args.file == "test.tc"

    def test_parser_repl(self):
        parser = build_parser()
        args = parser.parse_args(["repl"])
        assert args.command == "repl"

    def test_parser_check(self):
        parser = build_parser()
        args = parser.parse_args(["check", "test.tc"])
        assert args.command == "check"

    def test_parser_debug_flag(self):
        parser = build_parser()
        args = parser.parse_args(["run", "test.tc", "--debug"])
        assert args.debug is True

    def test_parser_time_flag(self):
        parser = build_parser()
        args = parser.parse_args(["run", "test.tc", "--time"])
        assert args.time is True
