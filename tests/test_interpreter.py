#!/usr/bin/env python3
"""
Core interpreter tests for Time Warp II.

Covers BASIC commands, PILOT commands, Logo turtle, expressions, and
control flow.  All tests run headless (no GUI required).
"""

import pytest
from tests.helpers import run_program


# =====================================================================
#  BASIC — PRINT, LET, expressions
# =====================================================================

class TestPrint:
    def test_print_string(self):
        assert run_program('PRINT "hello"').last_line == "hello"

    def test_print_number(self):
        assert run_program("PRINT 42").last_line == "42"

    def test_print_expression(self):
        assert run_program("PRINT 2 + 3").last_line == "5"

    def test_print_semicolon_concat(self):
        out = run_program('PRINT "A"; "B"')
        assert "AB" in out.raw


class TestLet:
    def test_let_integer(self):
        assert run_program("LET X = 5\nPRINT X").last_line == "5"

    def test_let_expression(self):
        assert run_program("LET X = 2 + 3\nPRINT X").last_line == "5"

    def test_let_multiply(self):
        assert run_program("LET X = 6 * 7\nPRINT X").last_line == "42"

    def test_let_divide(self):
        out = run_program("LET X = 20 / 4\nPRINT X").last_line
        assert float(out) == 5.0

    def test_let_modulo(self):
        assert run_program("LET X = 10 MOD 3\nPRINT X").last_line == "1"

    def test_let_negative(self):
        assert run_program("LET X = -5\nPRINT X").last_line == "-5"

    def test_let_nested_parens(self):
        assert run_program("LET X = (2 + 3) * 4\nPRINT X").last_line == "20"


# =====================================================================
#  BASIC — Control flow
# =====================================================================

class TestIfThen:
    def test_if_true(self):
        assert run_program('LET X = 10\nIF X > 5 THEN PRINT "yes"').last_line == "yes"

    def test_if_false(self):
        lines = run_program('LET X = 2\nIF X > 5 THEN PRINT "no"').program_lines
        assert not any("no" in l for l in lines)

    def test_if_equals(self):
        assert run_program('LET X = 5\nIF X = 5 THEN PRINT "eq"').last_line == "eq"


class TestForNext:
    def test_for_sum(self):
        code = "LET S = 0\nFOR I = 1 TO 5\nLET S = S + I\nNEXT I\nPRINT S"
        assert run_program(code).last_line == "15"

    def test_for_step(self):
        code = "LET S = 0\nFOR I = 0 TO 10 STEP 5\nLET S = S + I\nNEXT I\nPRINT S"
        assert run_program(code).last_line == "15"


class TestWhile:
    def test_while_loop(self):
        code = "LET X = 0\nWHILE X < 3\nLET X = X + 1\nWEND\nPRINT X"
        assert run_program(code).last_line == "3"


class TestDoLoop:
    def test_do_while(self):
        code = "LET X = 0\nDO WHILE X < 3\nLET X = X + 1\nLOOP\nPRINT X"
        assert run_program(code).last_line == "3"


class TestGoto:
    def test_goto_skips(self):
        code = '10 PRINT "A"\n20 GOTO 40\n30 PRINT "B"\n40 PRINT "C"'
        lines = run_program(code).program_lines
        assert "A" in lines[0]
        assert "C" in lines[1]
        assert not any("B" in l for l in lines)


class TestGosub:
    def test_gosub_return(self):
        code = '10 GOSUB 30\n20 END\n30 PRINT "sub"\n40 RETURN'
        assert run_program(code).last_line == "sub"


class TestDataRead:
    def test_data_read_sum(self):
        code = "DATA 10,20\nREAD A\nREAD B\nPRINT A + B"
        assert run_program(code).last_line == "30"


class TestRem:
    def test_rem_ignored(self):
        assert run_program("REM this is a comment\nPRINT 1").last_line == "1"


# =====================================================================
#  BASIC — Math functions
# =====================================================================

class TestMathFunctions:
    def test_abs(self):
        out = run_program("LET X = ABS(-7)\nPRINT X").last_line
        assert float(out) == 7.0

    def test_sqr(self):
        out = run_program("LET X = SQR(9)\nPRINT X").last_line
        assert float(out) == 3.0

    def test_int_func(self):
        out = run_program("LET X = INT(20 / 4)\nPRINT X").last_line
        assert out == "5"


# =====================================================================
#  PILOT
# =====================================================================

class TestPilot:
    def test_type(self):
        assert run_program("T: hello pilot").last_line == "hello pilot"


# =====================================================================
#  Logo Turtle
# =====================================================================

class TestLogo:
    def test_forward(self):
        out = run_program('FORWARD 50\nPRINT "done"')
        assert out.last_line == "done"

    def test_repeat(self):
        out = run_program('REPEAT 3 [PRINT "R"]')
        r_lines = [l for l in out.program_lines if l.strip() == "R"]
        assert len(r_lines) == 3


# =====================================================================
#  Config module
# =====================================================================

class TestConfig:
    def test_themes_loaded(self):
        from core.config import THEMES
        assert len(THEMES) >= 9
        assert "dark" in THEMES
        assert "light" in THEMES

    def test_font_sizes(self):
        from core.config import FONT_SIZES
        assert "medium" in FONT_SIZES
        assert "editor" in FONT_SIZES["medium"]

    def test_welcome_message(self):
        from core.config import WELCOME_MESSAGE
        assert len(WELCOME_MESSAGE) > 0
        assert "TempleCode" in WELCOME_MESSAGE
