#!/usr/bin/env python3
"""
Comprehensive tests for every TempleCode command and graphics function.

Covers BASIC statements, PILOT colon-commands, Logo turtle graphics,
expression evaluation, string functions, math functions, and control flow.
All tests run headless (no GUI required).
"""

import math
import pytest
from tests.helpers import run_program, run_with_interp


# =====================================================================
#  BASIC — PRINT variants
# =====================================================================

class TestPrintExtended:
    def test_print_empty(self):
        out = run_program("PRINT")
        # Empty print should produce a blank line
        assert "" in out.raw

    def test_print_question_mark(self):
        assert run_program('? "hello"').last_line == "hello"

    def test_print_tab_separator(self):
        out = run_program('PRINT "A", "B"')
        assert "A" in out.raw and "B" in out.raw

    def test_print_trailing_semicolon(self):
        out = run_program('PRINT "A";\nPRINT "B"')
        assert "AB" in out.raw

    def test_print_numeric_expression(self):
        assert run_program("PRINT 3 * 4 + 1").last_line == "13"

    def test_print_variable(self):
        assert run_program("LET X = 99\nPRINT X").last_line == "99"

    def test_print_string_concat(self):
        out = run_program('PRINT "hello"; " "; "world"')
        assert "hello world" in out.raw


# =====================================================================
#  BASIC — LET / direct assignment
# =====================================================================

class TestLetExtended:
    def test_direct_assignment(self):
        """X = 5 without LET keyword."""
        assert run_program("X = 5\nPRINT X").last_line == "5"

    def test_string_variable(self):
        out = run_program('LET X = "hello"\nPRINT X')
        assert out.last_line == "hello"

    def test_reassignment(self):
        code = "LET X = 1\nLET X = 2\nPRINT X"
        assert run_program(code).last_line == "2"

    def test_expression_with_variable(self):
        code = "LET A = 10\nLET B = A + 5\nPRINT B"
        assert run_program(code).last_line == "15"


# =====================================================================
#  BASIC — INPUT
# =====================================================================

class TestInput:
    def test_input_numeric(self):
        out = run_program("INPUT X\nPRINT X", input_buffer=["42"])
        assert out.last_line == "42"

    def test_input_with_prompt(self):
        out = run_program('INPUT "Enter: "; X\nPRINT X', input_buffer=["7"])
        assert out.last_line == "7"

    def test_input_string(self):
        out = run_program("INPUT S\nPRINT S", input_buffer=["hello"])
        assert out.last_line == "hello"

    def test_input_in_expression(self):
        code = "INPUT X\nLET Y = X + 10\nPRINT Y"
        out = run_program(code, input_buffer=["5"])
        assert out.last_line == "15"


# =====================================================================
#  BASIC — DIM / arrays
# =====================================================================

class TestDim:
    def test_dim_and_set(self):
        code = "DIM A(5)\nLET A(0) = 100\nPRINT A(0)"
        assert run_program(code).last_line == "100"

    def test_dim_multiple_elements(self):
        code = "DIM A(3)\nLET A(0) = 10\nLET A(1) = 20\nLET A(2) = 30\nPRINT A(1)"
        assert run_program(code).last_line == "20"

    def test_dim_element_access(self):
        code = "DIM A(3)\nLET A(2) = 99\nLET X = A(2)\nPRINT X"
        assert run_program(code).last_line == "99"


# =====================================================================
#  BASIC — IF / THEN / ELSE (extended)
# =====================================================================

class TestIfExtended:
    def test_if_else(self):
        code = 'LET X = 3\nIF X > 5 THEN PRINT "big" ELSE PRINT "small"'
        assert run_program(code).last_line == "small"

    def test_if_then_goto(self):
        code = '10 IF 1 = 1 THEN 30\n20 PRINT "skip"\n30 PRINT "hit"'
        out = run_program(code)
        assert "hit" in out.raw
        assert "skip" not in out.raw

    def test_if_not_equal(self):
        code = 'LET X = 5\nIF X <> 3 THEN PRINT "yes"'
        assert run_program(code).last_line == "yes"

    def test_if_less_equal(self):
        code = 'LET X = 5\nIF X <= 5 THEN PRINT "ok"'
        assert run_program(code).last_line == "ok"

    def test_if_greater_equal(self):
        code = 'LET X = 5\nIF X >= 5 THEN PRINT "ok"'
        assert run_program(code).last_line == "ok"

    def test_if_and_condition(self):
        code = 'LET X = 5\nLET Y = 10\nIF X = 5 AND Y = 10 THEN PRINT "both"'
        assert run_program(code).last_line == "both"

    def test_if_or_condition(self):
        code = 'LET X = 3\nIF X = 5 OR X = 3 THEN PRINT "either"'
        assert run_program(code).last_line == "either"

    def test_if_not_condition(self):
        code = 'LET X = 0\nIF NOT X THEN PRINT "falsy"'
        assert run_program(code).last_line == "falsy"

    def test_multiline_if_true(self):
        code = 'LET X = 10\nIF X > 5 THEN\nPRINT "inside"\nEND IF\nPRINT "after"'
        out = run_program(code)
        assert "inside" in out.raw
        assert "after" in out.raw

    def test_multiline_if_false_else(self):
        code = 'LET X = 2\nIF X > 5 THEN\nPRINT "yes"\nELSE\nPRINT "no"\nEND IF'
        out = run_program(code)
        assert "no" in out.raw
        assert "yes" not in out.raw


# =====================================================================
#  BASIC — FOR / NEXT (extended)
# =====================================================================

class TestForExtended:
    def test_for_negative_step(self):
        code = "LET S = 0\nFOR I = 5 TO 1 STEP -1\nLET S = S + I\nNEXT I\nPRINT S"
        assert run_program(code).last_line == "15"

    def test_nested_for(self):
        code = ("LET S = 0\n"
                "FOR I = 1 TO 2\n"
                "FOR J = 1 TO 3\n"
                "LET S = S + 1\n"
                "NEXT J\n"
                "NEXT I\n"
                "PRINT S")
        assert run_program(code).last_line == "6"

    def test_exit_for(self):
        code = ("LET S = 0\n"
                "FOR I = 1 TO 100\n"
                "LET S = S + I\n"
                "IF S > 10 THEN EXIT FOR\n"
                "NEXT I\n"
                "PRINT S")
        out = run_program(code)
        val = int(out.last_line)
        assert val > 10


# =====================================================================
#  BASIC — WHILE / WEND (extended)
# =====================================================================

class TestWhileExtended:
    def test_while_false_initially(self):
        code = 'LET X = 10\nWHILE X < 5\nLET X = X + 1\nWEND\nPRINT X'
        assert run_program(code).last_line == "10"

    def test_while_counts(self):
        code = "LET X = 0\nLET S = 0\nWHILE X < 5\nLET S = S + X\nLET X = X + 1\nWEND\nPRINT S"
        assert run_program(code).last_line == "10"  # 0+1+2+3+4


# =====================================================================
#  BASIC — DO / LOOP (extended)
# =====================================================================

class TestDoLoopExtended:
    def test_do_until(self):
        code = "LET X = 0\nDO UNTIL X >= 3\nLET X = X + 1\nLOOP\nPRINT X"
        assert run_program(code).last_line == "3"

    def test_loop_until(self):
        code = "LET X = 0\nDO\nLET X = X + 1\nLOOP UNTIL X >= 5\nPRINT X"
        assert run_program(code).last_line == "5"

    def test_loop_while(self):
        code = "LET X = 0\nDO\nLET X = X + 1\nLOOP WHILE X < 4\nPRINT X"
        assert run_program(code).last_line == "4"


# =====================================================================
#  BASIC — GOTO / GOSUB (extended)
# =====================================================================

class TestGotoGosubExtended:
    def test_goto_label(self):
        code = 'GOTO skip\nPRINT "no"\nskip:\nPRINT "yes"'
        out = run_program(code)
        assert "yes" in out.raw
        assert "no" not in out.raw

    def test_gosub_label(self):
        code = 'GOSUB mysub\nPRINT "after"\nEND\nmysub:\nPRINT "sub"\nRETURN'
        out = run_program(code)
        lines = out.program_lines
        assert "sub" in lines[0]
        assert "after" in lines[1]

    def test_nested_gosub(self):
        code = ('10 GOSUB 30\n'
                '20 END\n'
                '30 GOSUB 50\n'
                '40 RETURN\n'
                '50 PRINT "deep"\n'
                '60 RETURN')
        assert run_program(code).last_line == "deep"


# =====================================================================
#  BASIC — DATA / READ / RESTORE
# =====================================================================

class TestDataReadRestore:
    def test_data_string(self):
        code = 'DATA "hello"\nREAD A\nPRINT A'
        assert run_program(code).last_line == "hello"

    def test_restore(self):
        code = "DATA 1\nREAD A\nRESTORE\nREAD B\nPRINT B"
        assert run_program(code).last_line == "1"

    def test_multiple_data_lines(self):
        code = "DATA 10\nDATA 20\nREAD A\nREAD B\nPRINT A + B"
        assert run_program(code).last_line == "30"


# =====================================================================
#  BASIC — SELECT CASE
# =====================================================================

class TestSelectCase:
    def test_select_case_match(self):
        code = ('LET X = 2\n'
                'SELECT CASE X\n'
                'CASE 1\nPRINT "one"\n'
                'CASE 2\nPRINT "two"\n'
                'CASE 3\nPRINT "three"\n'
                'END SELECT')
        assert run_program(code).last_line == "two"

    def test_select_case_else(self):
        code = ('LET X = 99\n'
                'SELECT CASE X\n'
                'CASE 1\nPRINT "one"\n'
                'CASE ELSE\nPRINT "other"\n'
                'END SELECT')
        assert run_program(code).last_line == "other"


# =====================================================================
#  BASIC — SWAP, INCR, DECR
# =====================================================================

class TestSwapIncrDecr:
    def test_swap(self):
        code = "LET A = 1\nLET B = 2\nSWAP A, B\nPRINT A\nPRINT B"
        out = run_program(code)
        lines = out.program_lines
        assert lines[0] == "2"
        assert lines[1] == "1"

    def test_incr(self):
        code = "LET X = 5\nINCR X\nPRINT X"
        assert run_program(code).last_line == "6"

    def test_incr_amount(self):
        code = "LET X = 5\nINCR X, 10\nPRINT X"
        assert run_program(code).last_line == "15"

    def test_decr(self):
        code = "LET X = 10\nDECR X\nPRINT X"
        assert run_program(code).last_line == "9"

    def test_decr_amount(self):
        code = "LET X = 10\nDECR X, 3\nPRINT X"
        assert run_program(code).last_line == "7"


# =====================================================================
#  BASIC — STOP / END / CLS
# =====================================================================

class TestStopEndCls:
    def test_stop(self):
        code = 'PRINT "before"\nSTOP\nPRINT "after"'
        out = run_program(code)
        assert "before" in out.raw
        assert "after" not in out.raw

    def test_end(self):
        code = 'PRINT "before"\nEND\nPRINT "after"'
        out = run_program(code)
        assert "before" in out.raw
        assert "after" not in out.raw

    def test_cls(self):
        # CLS outputs 25 newlines
        out = run_program("CLS")
        assert "\n" in out.raw


# =====================================================================
#  BASIC — RANDOMIZE
# =====================================================================

class TestRandomize:
    def test_randomize_with_seed(self):
        code = "RANDOMIZE 42\nPRINT RND(100)"
        # With a fixed seed, result should be deterministic
        r1 = run_program(code).last_line
        r2 = run_program(code).last_line
        assert r1 == r2


# =====================================================================
#  BASIC — Math functions (extended)
# =====================================================================

class TestMathExtended:
    def test_sin(self):
        out = run_program("PRINT SIN(0)").last_line
        assert float(out) == pytest.approx(0.0)

    def test_cos(self):
        out = run_program("PRINT COS(0)").last_line
        assert float(out) == pytest.approx(1.0)

    def test_tan(self):
        out = run_program("PRINT TAN(0)").last_line
        assert float(out) == pytest.approx(0.0)

    def test_log(self):
        out = run_program("PRINT LOG(1)").last_line
        assert float(out) == pytest.approx(0.0)

    def test_exp(self):
        out = run_program("PRINT EXP(0)").last_line
        assert float(out) == pytest.approx(1.0)

    def test_ceil(self):
        out = run_program("LET X = CEIL(3.2)\nPRINT X").last_line
        assert float(out) == pytest.approx(4.0)

    def test_fix(self):
        out = run_program("LET X = FIX(3.7)\nPRINT X").last_line
        assert out == "3"

    def test_rnd_range(self):
        code = "RANDOMIZE 1\nPRINT RND(10)"
        val = int(run_program(code).last_line)
        assert 1 <= val <= 10

    def test_rnd_no_arg(self):
        code = "RANDOMIZE 1\nLET X = RND\nPRINT X"
        # RND without args returns 0..1 float, but it's used in expression
        # It may be treated differently; just check it doesn't crash
        out = run_program(code)
        # Should produce some output
        assert out.last_line != ""

    def test_sqrt(self):
        assert float(run_program("PRINT SQR(16)").last_line) == 4.0

    def test_abs_positive(self):
        assert float(run_program("PRINT ABS(5)").last_line) == 5.0

    def test_int_truncates(self):
        assert run_program("PRINT INT(7.9)").last_line == "7"


# =====================================================================
#  BASIC — String functions
# =====================================================================

class TestStringFunctions:
    def test_len(self):
        out = run_program('LET X = LEN("hello")\nPRINT X').last_line
        assert int(out) == 5

    def test_mid(self):
        out = run_program('LET S = "hello"\nLET X = MID(S, 2, 3)\nPRINT X').last_line
        assert out.lower() == "ell"

    def test_left(self):
        out = run_program('LET S = "hello"\nLET X = LEFT(S, 3)\nPRINT X').last_line
        assert out.lower() == "hel"

    def test_right(self):
        out = run_program('LET S = "hello"\nLET X = RIGHT(S, 3)\nPRINT X').last_line
        assert out.lower() == "llo"

    def test_chr(self):
        out = run_program("LET X = CHR(65)\nPRINT X").last_line
        assert out == "A"

    def test_asc(self):
        out = run_program('LET X = ASC("A")\nPRINT X').last_line
        assert int(out) == 65

    def test_str(self):
        out = run_program("LET X = STR(42)\nPRINT X").last_line
        assert "42" in out

    def test_val(self):
        out = run_program('LET X = VAL("3.14")\nPRINT X').last_line
        assert float(out) == pytest.approx(3.14)

    def test_ucase(self):
        out = run_program('LET X = UCASE("hello")\nPRINT X').last_line
        assert out == "HELLO"

    def test_lcase(self):
        out = run_program('LET X = LCASE("HELLO")\nPRINT X').last_line
        assert out == "hello"

    def test_instr_found(self):
        out = run_program('LET X = INSTR("hello", "ll")\nPRINT X').last_line
        assert int(out) == 3  # 1-based

    def test_instr_not_found(self):
        out = run_program('LET X = INSTR("hello", "xyz")\nPRINT X').last_line
        assert int(out) == 0


# =====================================================================
#  PILOT — T: (type)
# =====================================================================

class TestPilotType:
    def test_type_text(self):
        assert run_program("T: hello pilot").last_line == "hello pilot"

    def test_type_with_variable_interpolation(self):
        code = "LET NAME = 42\nT: value is $NAME"
        out = run_program(code)
        assert "value is 42" in out.raw

    def test_type_star_interpolation(self):
        code = 'LET X = "world"\nT: hello *X*'
        out = run_program(code)
        assert "hello world" in out.raw


# =====================================================================
#  PILOT — A: (accept) / INPUT
# =====================================================================

class TestPilotAccept:
    def test_accept_stores_answer(self):
        code = "A: name\nPRINT ANSWER"
        out, interp = run_with_interp(code, input_buffer=["James"])
        assert interp.variables.get("ANSWER") == "James"

    def test_accept_stores_input_var(self):
        code = "A:\nT: got $INPUT"
        out, interp = run_with_interp(code, input_buffer=["hello"])
        assert interp.variables.get("INPUT") == "hello"
        assert "got hello" in out.raw

    def test_accept_named_variable(self):
        code = "A:NAME\nT: hello $NAME"
        out = run_program(code, input_buffer=["Alice"])
        assert "hello Alice" in out.raw


# =====================================================================
#  PILOT — M: (match), Y: / N: (conditional)
# =====================================================================

class TestPilotMatch:
    def test_match_success(self):
        code = "A:\nM: yes,sure\nY: T: matched!"
        out, interp = run_with_interp(code, input_buffer=["yes"])
        assert interp.match_flag is True
        assert "matched!" in out.raw

    def test_match_failure(self):
        code = "A:\nM: yes\nN:T: no match"
        out, interp = run_with_interp(code, input_buffer=["no"])
        assert interp.match_flag is False
        assert "no match" in out.raw

    def test_match_partial(self):
        """M: does substring matching."""
        code = "A:\nM: cat\nY: T: found"
        out = run_program(code, input_buffer=["category"])
        assert "found" in out.raw

    def test_match_case_insensitive(self):
        code = "A:\nM: hello\nY: T: matched"
        out = run_program(code, input_buffer=["HELLO"])
        assert "matched" in out.raw


# =====================================================================
#  PILOT — J: (jump), C: (compute/call), E: (end)
# =====================================================================

class TestPilotJumpCallEnd:
    def test_jump_to_label(self):
        code = 'J: skip\nT: no\n*skip\nT: yes'
        out = run_program(code)
        assert "yes" in out.raw
        assert "no" not in out.raw

    def test_compute(self):
        code = "C:X=5+3\nPRINT X"
        assert run_program(code).last_line == "8"

    def test_call_subroutine(self):
        code = 'C:*mysub\nT: after\nE:\n*mysub\nT: in sub\nE:'
        out = run_program(code)
        assert "in sub" in out.raw

    def test_end(self):
        code = 'T: before\nE:\nT: after'
        out = run_program(code)
        assert "before" in out.raw
        assert "after" not in out.raw


# =====================================================================
#  PILOT — R: (remark), U: (use), L: (label), D: (dim)
# =====================================================================

class TestPilotMisc:
    def test_remark(self):
        code = "R: this is a comment\nPRINT 1"
        assert run_program(code).last_line == "1"

    def test_use_variable(self):
        code = "U:X=42\nPRINT X"
        assert run_program(code).last_line == "42"

    def test_label_noop(self):
        """L: at runtime is a no-op."""
        code = "L: myspot\nPRINT 1"
        assert run_program(code).last_line == "1"

    def test_dim_array(self):
        code = "D:ARR(5)\nPRINT 1"
        out, interp = run_with_interp(code)
        assert "ARR" in interp.templecode_executor.arrays
        assert len(interp.templecode_executor.arrays["ARR"]) == 5


# =====================================================================
#  PILOT — S: (string ops)
# =====================================================================

class TestPilotString:
    def test_upper(self):
        code = 'LET X = "hello"\nS: UPPER X\nPRINT X'
        assert run_program(code).last_line == "HELLO"

    def test_lower(self):
        code = 'LET X = "HELLO"\nS: LOWER X\nPRINT X'
        assert run_program(code).last_line == "hello"

    def test_reverse(self):
        code = 'LET X = "abc"\nS: REVERSE X\nPRINT X'
        assert run_program(code).last_line == "cba"

    def test_trim(self):
        code = 'LET X = "  hi  "\nS: TRIM X\nPRINT X'
        assert run_program(code).last_line == "hi"

    def test_len_op(self):
        code = 'LET X = "hello"\nS: LEN X\nPRINT X_LEN'
        assert run_program(code).last_line == "5"


# =====================================================================
#  PILOT — X: (execute), G: (graphics)
# =====================================================================

class TestPilotExecuteGraphics:
    def test_execute_basic_command(self):
        code = 'X: PRINT "executed"'
        assert run_program(code).last_line == "executed"

    def test_graphics_command(self):
        """G: dispatches to Logo system."""
        code = 'G: FORWARD 50\nPRINT "done"'
        out, interp = run_with_interp(code)
        assert out.last_line == "done"
        assert interp.turtle_graphics is not None


# =====================================================================
#  Logo — Movement (FORWARD, BACK, LEFT, RIGHT)
# =====================================================================

class TestLogoMovement:
    def test_forward(self):
        _, interp = run_with_interp("FORWARD 100")
        tg = interp.turtle_graphics
        # Default heading is 0 (north), so y increases
        assert tg["y"] == pytest.approx(100.0, abs=0.01)

    def test_fd_alias(self):
        _, interp = run_with_interp("FD 50")
        assert interp.turtle_graphics["y"] == pytest.approx(50.0, abs=0.01)

    def test_back(self):
        _, interp = run_with_interp("BACK 30")
        assert interp.turtle_graphics["y"] == pytest.approx(-30.0, abs=0.01)

    def test_bk_alias(self):
        _, interp = run_with_interp("BK 20")
        assert interp.turtle_graphics["y"] == pytest.approx(-20.0, abs=0.01)

    def test_backward_alias(self):
        _, interp = run_with_interp("BACKWARD 10")
        assert interp.turtle_graphics["y"] == pytest.approx(-10.0, abs=0.01)

    def test_left(self):
        _, interp = run_with_interp("LEFT 90")
        assert interp.turtle_graphics["heading"] == pytest.approx(270.0)

    def test_lt_alias(self):
        _, interp = run_with_interp("LT 45")
        assert interp.turtle_graphics["heading"] == pytest.approx(315.0)

    def test_right(self):
        _, interp = run_with_interp("RIGHT 90")
        assert interp.turtle_graphics["heading"] == pytest.approx(90.0)

    def test_rt_alias(self):
        _, interp = run_with_interp("RT 45")
        assert interp.turtle_graphics["heading"] == pytest.approx(45.0)

    def test_forward_and_turn(self):
        """Forward 100, turn right 90, forward 50 → should be at (50, 100)."""
        _, interp = run_with_interp("FORWARD 100\nRIGHT 90\nFORWARD 50")
        tg = interp.turtle_graphics
        assert tg["x"] == pytest.approx(50.0, abs=0.01)
        assert tg["y"] == pytest.approx(100.0, abs=0.01)


# =====================================================================
#  Logo — Pen control
# =====================================================================

class TestLogoPen:
    def test_penup(self):
        _, interp = run_with_interp("PENUP")
        assert interp.turtle_graphics["pen_down"] is False

    def test_pu_alias(self):
        _, interp = run_with_interp("PU")
        assert interp.turtle_graphics["pen_down"] is False

    def test_pendown(self):
        _, interp = run_with_interp("PENUP\nPENDOWN")
        assert interp.turtle_graphics["pen_down"] is True

    def test_pd_alias(self):
        _, interp = run_with_interp("PU\nPD")
        assert interp.turtle_graphics["pen_down"] is True

    def test_penup_no_draw(self):
        """When pen is up, no lines should be drawn on canvas."""
        _, interp = run_with_interp("PENUP\nFORWARD 100")
        canvas = interp.turtle_graphics["canvas"]
        # No lines should have been drawn (only headless canvas records)
        line_items = [c for c in canvas.created if c["type"] == "line"]
        assert len(line_items) == 0

    def test_pendown_draws(self):
        """When pen is down (default), lines ARE drawn."""
        _, interp = run_with_interp("FORWARD 100")
        canvas = interp.turtle_graphics["canvas"]
        line_items = [c for c in canvas.created if c["type"] == "line"]
        assert len(line_items) >= 1


# =====================================================================
#  Logo — Position / heading
# =====================================================================

class TestLogoPosition:
    def test_home(self):
        _, interp = run_with_interp("FORWARD 100\nRIGHT 45\nHOME")
        tg = interp.turtle_graphics
        assert tg["x"] == pytest.approx(0.0)
        assert tg["y"] == pytest.approx(0.0)
        assert tg["heading"] == pytest.approx(0.0)

    def test_setxy(self):
        _, interp = run_with_interp("SETXY 100 50")
        tg = interp.turtle_graphics
        assert tg["x"] == pytest.approx(100.0)
        assert tg["y"] == pytest.approx(50.0)

    def test_setpos_alias(self):
        _, interp = run_with_interp("SETPOS 30 40")
        tg = interp.turtle_graphics
        assert tg["x"] == pytest.approx(30.0)
        assert tg["y"] == pytest.approx(40.0)

    def test_setx(self):
        _, interp = run_with_interp("SETX 75")
        assert interp.turtle_graphics["x"] == pytest.approx(75.0)

    def test_sety(self):
        _, interp = run_with_interp("SETY 60")
        assert interp.turtle_graphics["y"] == pytest.approx(60.0)

    def test_setheading(self):
        _, interp = run_with_interp("SETHEADING 180")
        assert interp.turtle_graphics["heading"] == pytest.approx(180.0)

    def test_seth_alias(self):
        _, interp = run_with_interp("SETH 270")
        assert interp.turtle_graphics["heading"] == pytest.approx(270.0)

    def test_towards(self):
        _, interp = run_with_interp("TOWARDS 100 0")
        # heading should point towards (100, 0) from origin → 90 degrees (east)
        assert interp.turtle_graphics["heading"] == pytest.approx(90.0, abs=0.1)


# =====================================================================
#  Logo — Visibility
# =====================================================================

class TestLogoVisibility:
    def test_hideturtle(self):
        _, interp = run_with_interp("HIDETURTLE")
        assert interp.turtle_graphics["visible"] is False

    def test_ht_alias(self):
        _, interp = run_with_interp("HT")
        assert interp.turtle_graphics["visible"] is False

    def test_showturtle(self):
        _, interp = run_with_interp("HIDETURTLE\nSHOWTURTLE")
        assert interp.turtle_graphics["visible"] is True

    def test_st_alias(self):
        _, interp = run_with_interp("HT\nST")
        assert interp.turtle_graphics["visible"] is True


# =====================================================================
#  Logo — Color / pen size
# =====================================================================

class TestLogoColor:
    def test_setcolor_by_name(self):
        _, interp = run_with_interp("SETCOLOR red")
        assert interp.turtle_graphics["pen_color"] == "red"

    def test_setcolour_alias(self):
        _, interp = run_with_interp("SETCOLOUR blue")
        assert interp.turtle_graphics["pen_color"] == "blue"

    def test_setpencolor_alias(self):
        _, interp = run_with_interp("SETPENCOLOR green")
        assert interp.turtle_graphics["pen_color"] == "green"

    def test_setpc_alias(self):
        _, interp = run_with_interp("SETPC yellow")
        assert interp.turtle_graphics["pen_color"] == "yellow"

    def test_setcolor_by_number(self):
        _, interp = run_with_interp("SETCOLOR 4")
        assert interp.turtle_graphics["pen_color"] == "red"

    def test_setpensize(self):
        _, interp = run_with_interp("SETPENSIZE 5")
        assert interp.turtle_graphics["pen_size"] == 5

    def test_setwidth_alias(self):
        _, interp = run_with_interp("SETWIDTH 3")
        assert interp.turtle_graphics["pen_size"] == 3

    def test_setfillcolor(self):
        _, interp = run_with_interp("SETFILLCOLOR purple")
        assert interp.turtle_graphics["fill_color"] == "purple"

    def test_setfc_alias(self):
        _, interp = run_with_interp("SETFC orange")
        assert interp.turtle_graphics["fill_color"] == "orange"


# =====================================================================
#  Logo — Drawing shapes
# =====================================================================

class TestLogoShapes:
    def test_circle(self):
        _, interp = run_with_interp("CIRCLE 50")
        canvas = interp.turtle_graphics["canvas"]
        ovals = [c for c in canvas.created if c["type"] == "oval"]
        assert len(ovals) >= 1

    def test_arc(self):
        _, interp = run_with_interp("ARC 90 50")
        canvas = interp.turtle_graphics["canvas"]
        arcs = [c for c in canvas.created if c["type"] == "arc"]
        assert len(arcs) >= 1

    def test_dot(self):
        _, interp = run_with_interp("DOT 5")
        canvas = interp.turtle_graphics["canvas"]
        ovals = [c for c in canvas.created if c["type"] == "oval"]
        assert len(ovals) >= 1

    def test_rect(self):
        _, interp = run_with_interp("RECT 60 40")
        canvas = interp.turtle_graphics["canvas"]
        rects = [c for c in canvas.created if c["type"] == "rectangle"]
        assert len(rects) >= 1

    def test_rectangle_alias(self):
        _, interp = run_with_interp("RECTANGLE 80 60")
        canvas = interp.turtle_graphics["canvas"]
        rects = [c for c in canvas.created if c["type"] == "rectangle"]
        assert len(rects) >= 1

    def test_square(self):
        """SQUARE draws using forward+turn, creating 4 line segments."""
        _, interp = run_with_interp("SQUARE 50")
        canvas = interp.turtle_graphics["canvas"]
        lines = [c for c in canvas.created if c["type"] == "line"]
        assert len(lines) == 4

    def test_triangle(self):
        """TRIANGLE draws using forward+turn, creating 3 line segments."""
        _, interp = run_with_interp("TRIANGLE 50")
        canvas = interp.turtle_graphics["canvas"]
        lines = [c for c in canvas.created if c["type"] == "line"]
        assert len(lines) == 3

    def test_polygon(self):
        """POLYGON 6 30 should draw a hexagon (6 lines)."""
        _, interp = run_with_interp("POLYGON 6 30")
        canvas = interp.turtle_graphics["canvas"]
        lines = [c for c in canvas.created if c["type"] == "line"]
        assert len(lines) == 6

    def test_star(self):
        """STAR 5 50 should draw a 5-pointed star (5 line segments)."""
        _, interp = run_with_interp("STAR 5 50")
        canvas = interp.turtle_graphics["canvas"]
        lines = [c for c in canvas.created if c["type"] == "line"]
        assert len(lines) == 5

    def test_fill_placeholder(self):
        """FILL outputs a message (not supported in vector canvas)."""
        out = run_program("FILL")
        assert "fill" in out.raw.lower() or "FILL" in out.raw


# =====================================================================
#  Logo — REPEAT
# =====================================================================

class TestLogoRepeat:
    def test_repeat_print(self):
        out = run_program('REPEAT 4 [PRINT "X"]')
        x_lines = [l for l in out.program_lines if l.strip() == "X"]
        assert len(x_lines) == 4

    def test_repeat_drawing(self):
        """REPEAT 4 [FD 50 RT 90] draws a square."""
        _, interp = run_with_interp("REPEAT 4 [FD 50 RT 90]")
        canvas = interp.turtle_graphics["canvas"]
        lines = [c for c in canvas.created if c["type"] == "line"]
        assert len(lines) == 4

    def test_repeat_nested(self):
        out = run_program('REPEAT 2 [REPEAT 3 [PRINT "N"]]')
        n_lines = [l for l in out.program_lines if l.strip() == "N"]
        assert len(n_lines) == 6

    def test_repcount_variable(self):
        """REPCOUNT is set inside REPEAT."""
        out = run_program("LET S = 0\nREPEAT 5 [LET S = S + REPCOUNT]\nPRINT S")
        assert out.last_line == "15"  # 1+2+3+4+5


# =====================================================================
#  Logo — MAKE (variable assignment)
# =====================================================================

class TestLogoMake:
    def test_make(self):
        code = 'MAKE "X 42\nPRINT X'
        assert run_program(code).last_line == "42"

    def test_make_expression(self):
        code = 'MAKE "Y 3 + 4\nPRINT Y'
        assert run_program(code).last_line == "7"


# =====================================================================
#  Logo — Queries (HEADING, POS, XCOR, YCOR)
# =====================================================================

class TestLogoQueries:
    def test_heading_query(self):
        out = run_program("RIGHT 90\nHEADING")
        assert "90" in out.raw

    def test_position_query(self):
        out = run_program("FORWARD 100\nPOS")
        assert "100" in out.raw

    def test_xcor(self):
        out = run_program("SETX 42\nXCOR")
        assert "42" in out.raw

    def test_ycor(self):
        out = run_program("SETY 77\nYCOR")
        assert "77" in out.raw


# =====================================================================
#  Logo — TRACE / NOTRACE
# =====================================================================

class TestLogoTrace:
    def test_trace_on(self):
        _, interp = run_with_interp("TRACE")
        assert interp.turtle_trace is True

    def test_notrace(self):
        _, interp = run_with_interp("TRACE\nNOTRACE")
        assert interp.turtle_trace is False


# =====================================================================
#  Logo — CLEARSCREEN / CS
# =====================================================================

class TestLogoClearscreen:
    def test_clearscreen_resets(self):
        _, interp = run_with_interp("FORWARD 100\nRIGHT 45\nCLEARSCREEN")
        tg = interp.turtle_graphics
        assert tg["x"] == pytest.approx(0.0)
        assert tg["y"] == pytest.approx(0.0)
        assert tg["heading"] == pytest.approx(0.0)

    def test_cs_alias(self):
        _, interp = run_with_interp("FD 50\nCS")
        tg = interp.turtle_graphics
        assert tg["x"] == pytest.approx(0.0)


# =====================================================================
#  Logo — TO / END procedure definition & calling
# =====================================================================

class TestLogoProcedures:
    def test_define_and_call(self):
        code = "TO square\nFD 50\nRT 90\nFD 50\nRT 90\nFD 50\nRT 90\nFD 50\nRT 90\nEND\nsquare"
        _, interp = run_with_interp(code)
        canvas = interp.turtle_graphics["canvas"]
        lines = [c for c in canvas.created if c["type"] == "line"]
        assert len(lines) == 4

    def test_procedure_with_params(self):
        code = "TO myforward :dist\nFD :dist\nEND\nmyforward 80"
        _, interp = run_with_interp(code)
        assert interp.turtle_graphics["y"] == pytest.approx(80.0, abs=0.01)


# =====================================================================
#  Logo — COLOR from BASIC context
# =====================================================================

class TestColorFromBasic:
    def test_color_command(self):
        """COLOR 4 should set turtle pen color to red (CGA palette)."""
        _, interp = run_with_interp("COLOR 4")
        assert interp.turtle_graphics["pen_color"] == "red"

    def test_colour_alias(self):
        _, interp = run_with_interp("COLOUR 2")
        assert interp.turtle_graphics["pen_color"] == "green"


# =====================================================================
#  Comments and labels
# =====================================================================

class TestComments:
    def test_rem(self):
        assert run_program("REM comment\nPRINT 1").last_line == "1"

    def test_apostrophe(self):
        assert run_program("' comment\nPRINT 1").last_line == "1"

    def test_star_comment(self):
        """Lines starting with * are labels, but * alone or *comment is a comment."""
        code = "*comment\nPRINT 1"
        # *comment is treated as a label definition — should not crash
        out = run_program(code)
        assert out.last_line == "1"

    def test_semicolon_comment(self):
        assert run_program("; comment\nPRINT 1").last_line == "1"

    def test_hash_comment(self):
        assert run_program("# comment\nPRINT 1").last_line == "1"

    def test_label_definition(self):
        code = "skip:\nPRINT 1"
        assert run_program(code).last_line == "1"


# =====================================================================
#  Mixed-paradigm programs
# =====================================================================

class TestMixedParadigm:
    def test_basic_and_pilot(self):
        code = 'LET X = 5\nT: the value is $X'
        out = run_program(code)
        assert "the value is 5" in out.raw

    def test_basic_and_logo(self):
        code = 'LET SIZE = 100\nFORWARD SIZE\nPRINT "done"'
        out, interp = run_with_interp(code)
        assert out.last_line == "done"
        assert interp.turtle_graphics["y"] == pytest.approx(100.0, abs=0.01)

    def test_pilot_and_logo(self):
        code = 'G: FORWARD 50\nT: moved'
        out, interp = run_with_interp(code)
        assert "moved" in out.raw
        assert interp.turtle_graphics is not None

    def test_all_three(self):
        code = ('LET N = 4\n'
                'REPEAT N [FD 30 RT 90]\n'
                'T: drew a square\n'
                'PRINT "done"')
        out = run_program(code)
        assert "drew a square" in out.raw
        assert "done" in out.raw


# =====================================================================
#  Edge cases
# =====================================================================

class TestEdgeCases:
    def test_empty_program(self):
        out = run_program("")
        # Should not crash
        assert "✅" in out.raw

    def test_blank_lines(self):
        out = run_program("\n\n\nPRINT 1\n\n")
        assert out.last_line == "1"

    def test_max_iterations(self):
        """Programs with infinite loops should stop at max_iterations."""
        code = "label:\nGOTO label"
        out = run_program(code)
        assert "iterations" in out.raw.lower() or "error" in out.raw.lower()

    def test_unknown_command(self):
        out = run_program("XYZZY")
        assert "unknown" in out.raw.lower() or "Unknown" in out.raw


# =====================================================================
#  v2.0 — ELSEIF / ENDIF
# =====================================================================

class TestElseifEndif:
    def test_elseif_second_branch(self):
        code = (
            "LET X = 2\n"
            "IF X = 1 THEN\n"
            "PRINT \"one\"\n"
            "ELSEIF X = 2 THEN\n"
            "PRINT \"two\"\n"
            "ELSE\n"
            "PRINT \"other\"\n"
            "ENDIF\n"
        )
        out = run_program(code)
        assert "two" in out.raw
        assert "one" not in out.raw
        assert "other" not in out.raw

    def test_elseif_falls_to_else(self):
        code = (
            "LET X = 99\n"
            "IF X = 1 THEN\n"
            "PRINT \"one\"\n"
            "ELSEIF X = 2 THEN\n"
            "PRINT \"two\"\n"
            "ELSE\n"
            "PRINT \"other\"\n"
            "ENDIF\n"
        )
        out = run_program(code)
        assert "other" in out.raw
        assert "one" not in out.raw
        assert "two" not in out.raw

    def test_elseif_first_branch(self):
        code = (
            "LET X = 1\n"
            "IF X = 1 THEN\n"
            "PRINT \"one\"\n"
            "ELSEIF X = 2 THEN\n"
            "PRINT \"two\"\n"
            "ENDIF\n"
        )
        out = run_program(code)
        assert "one" in out.raw
        assert "two" not in out.raw

    def test_endif_alias_for_end_if(self):
        code = (
            "IF 1 = 1 THEN\n"
            "PRINT \"ok\"\n"
            "ENDIF\n"
        )
        assert "ok" in run_program(code).raw

    def test_multiple_elseif(self):
        code = (
            "LET X = 3\n"
            "IF X = 1 THEN\n"
            "PRINT \"one\"\n"
            "ELSEIF X = 2 THEN\n"
            "PRINT \"two\"\n"
            "ELSEIF X = 3 THEN\n"
            "PRINT \"three\"\n"
            "ELSE\n"
            "PRINT \"other\"\n"
            "ENDIF\n"
        )
        out = run_program(code)
        assert "three" in out.raw
        assert "one" not in out.raw
        assert "two" not in out.raw
        assert "other" not in out.raw


# =====================================================================
#  v2.0 — ON GOTO / ON GOSUB
# =====================================================================

class TestOnGotoGosub:
    def test_on_goto_first(self):
        code = (
            "LET X = 1\n"
            "ON X GOTO first, second, third\n"
            "PRINT \"fell through\"\n"
            "GOTO done\n"
            "*first\n"
            "PRINT \"first\"\n"
            "GOTO done\n"
            "*second\n"
            "PRINT \"second\"\n"
            "GOTO done\n"
            "*third\n"
            "PRINT \"third\"\n"
            "*done\n"
        )
        out = run_program(code)
        assert "first" in out.raw
        assert "second" not in out.raw

    def test_on_goto_third(self):
        code = (
            "LET X = 3\n"
            "ON X GOTO first, second, third\n"
            "PRINT \"fell through\"\n"
            "GOTO done\n"
            "*first\n"
            "PRINT \"first\"\n"
            "GOTO done\n"
            "*second\n"
            "PRINT \"second\"\n"
            "GOTO done\n"
            "*third\n"
            "PRINT \"third\"\n"
            "*done\n"
        )
        out = run_program(code)
        assert "third" in out.raw
        assert "first" not in out.raw

    def test_on_goto_out_of_range(self):
        code = (
            "LET X = 5\n"
            "ON X GOTO alpha, beta\n"
            "PRINT \"fell through\"\n"
            "GOTO done\n"
            "*alpha\n"
            "PRINT \"alpha\"\n"
            "GOTO done\n"
            "*beta\n"
            "PRINT \"beta\"\n"
            "*done\n"
        )
        out = run_program(code)
        assert "fell through" in out.raw

    def test_on_gosub(self):
        code = (
            "LET X = 2\n"
            "ON X GOSUB sub1, sub2\n"
            "PRINT \"back\"\n"
            "GOTO done\n"
            "*sub1\n"
            "PRINT \"sub1\"\n"
            "RETURN\n"
            "*sub2\n"
            "PRINT \"sub2\"\n"
            "RETURN\n"
            "*done\n"
        )
        out = run_program(code)
        assert "sub2" in out.raw
        assert "back" in out.raw
        assert "sub1" not in out.raw


# =====================================================================
#  v2.0 — TAB / SPC
# =====================================================================

class TestTabSpc:
    def test_tab_inserts_spaces(self):
        code = "TAB 5\nPRINT \"X\""
        out = run_program(code)
        assert "     " in out.raw  # 5 spaces

    def test_spc_inserts_spaces(self):
        code = "SPC 3\nPRINT \"Y\""
        out = run_program(code)
        assert "   " in out.raw  # 3 spaces


# =====================================================================
#  v2.0 — CLS
# =====================================================================

class TestCls:
    def test_cls_clears_output(self):
        code = "PRINT \"before\"\nCLS\nPRINT \"after\""
        out = run_program(code)
        # CLS clears the widget, so "before" should be gone
        assert "before" not in out.raw
        assert "after" in out.raw


# =====================================================================
#  v2.0 — STEP 0 guard
# =====================================================================

class TestStep0Guard:
    def test_step_zero_error(self):
        code = "FOR I = 1 TO 10 STEP 0\nPRINT I\nNEXT I"
        out = run_program(code)
        assert "STEP" in out.raw and "0" in out.raw


# =====================================================================
#  v2.0 — String variables (A$)
# =====================================================================

class TestStringVariables:
    def test_let_string_dollar(self):
        code = 'LET A$ = "hello"\nPRINT A$'
        assert run_program(code).last_line == "hello"

    def test_string_dollar_concat(self):
        code = 'LET A$ = "foo"\nLET B$ = "bar"\nPRINT A$; B$'
        out = run_program(code)
        assert "foobar" in out.raw


# =====================================================================
#  v2.0 — TIMER pseudo-variable
# =====================================================================

class TestTimer:
    def test_timer_returns_number(self):
        code = "LET T = TIMER\nPRINT T"
        out = run_program(code)
        # TIMER should be a small non-negative float (elapsed seconds)
        val = float(out.last_line)
        assert val >= 0.0


# =====================================================================
#  v2.0 — DATE$ and TIME$ pseudo-variables
# =====================================================================

class TestDateTimeVars:
    def test_date_dollar(self):
        code = 'PRINT DATE$'
        out = run_program(code)
        # Should look like YYYY-MM-DD
        assert len(out.last_line) == 10
        assert out.last_line[4] == "-"

    def test_time_dollar(self):
        code = 'PRINT TIME$'
        out = run_program(code)
        # Should look like HH:MM:SS
        assert ":" in out.last_line
        assert len(out.last_line) == 8


# =====================================================================
#  v2.0 — TYPE() function
# =====================================================================

class TestTypeFunction:
    def test_type_string(self):
        code = 'PRINT TYPE("hello")'
        assert run_program(code).last_line == "STRING"

    def test_type_number(self):
        code = "LET X = 42\nPRINT TYPE(X)"
        assert run_program(code).last_line == "NUMBER"


# =====================================================================
#  v2.0 — Logo boundary modes
# =====================================================================

class TestLogoBoundaryModes:
    def test_wrap_mode(self):
        out, interp = run_with_interp("WRAP\nFORWARD 1")
        tg = interp.turtle_graphics
        assert tg is not None
        assert tg.get("boundary_mode") == "wrap"

    def test_window_mode(self):
        out, interp = run_with_interp("WINDOW\nFORWARD 1")
        tg = interp.turtle_graphics
        assert tg is not None
        assert tg.get("boundary_mode") == "window"

    def test_fence_mode(self):
        out, interp = run_with_interp("FENCE\nFORWARD 1")
        tg = interp.turtle_graphics
        assert tg is not None
        assert tg.get("boundary_mode") == "fence"


# =====================================================================
#  v2.0 — Logo PENCOLOR? / PENSIZE? queries
# =====================================================================

class TestPenQueries:
    def test_pencolor_query(self):
        code = "SETCOLOR red\nPENCOLOR?"
        out = run_program(code)
        assert "red" in out.raw.lower()

    def test_pensize_query(self):
        code = "SETPENSIZE 5\nPENSIZE?"
        out = run_program(code)
        assert "5" in out.raw


# =====================================================================
#  v2.0 — Logo LABEL
# =====================================================================

class TestLogoLabel:
    def test_label_creates_text(self):
        """LABEL should not crash and should add to turtle lines list."""
        out, interp = run_with_interp('LABEL "hello"')
        tg = interp.turtle_graphics
        assert tg is not None
        # turtle_text appends to "lines" and headless canvas records text items
        canvas = tg.get("canvas")
        text_items = [c for c in canvas.created if c["type"] == "text"]
        assert len(text_items) > 0


# =====================================================================
#  v2.0 — DATA / READ improvements
# =====================================================================

class TestDataReadImproved:
    def test_read_before_data(self):
        """READ should work even if DATA comes after READ in program order."""
        code = "READ X\nPRINT X\nGOTO done\nDATA 42\n*done"
        assert run_program(code).last_line == "42"

    def test_restore_resets(self):
        code = "DATA 10, 20\nREAD X\nRESTORE\nREAD Y\nPRINT Y"
        assert run_program(code).last_line == "10"
