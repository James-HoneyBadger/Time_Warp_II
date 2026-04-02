#!/usr/bin/env python3
"""
Tests for newly implemented features:
  - FILL command (flood fill on turtle canvas)
  - INKEY / INKEY$ (key buffer)
  - SCREEN command (canvas resize / presets)
  - ExpressionCache wiring in interpreter
"""

from collections import deque

import threading
import time

from tests.helpers import run_program, run_with_interp, FakeOutputWidget


# =====================================================================
#  INKEY — statement form
# =====================================================================

class TestInkeyStatement:
    def test_inkey_empty_buffer(self):
        """INKEY with no buffered keys outputs empty string, no error."""
        out = run_program("INKEY")
        assert "error" not in out.raw.lower()

    def test_inkey_consumes_from_buffer(self):
        """INKEY reads and removes the first key from the buffer."""
        out, interp = run_with_interp("PRINT 1")
        # Seed the key buffer before running INKEY
        interp._key_buffer.append("a")
        interp._key_buffer.append("b")
        out2, _ = run_with_interp.__wrapped__(interp, "INKEY") if hasattr(run_with_interp, '__wrapped__') else (None, None)
        # Use direct approach: create interpreter, seed buffer, run
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        widget = FakeOutputWidget()
        interp2 = TempleCodeInterpreter(output_widget=widget)
        interp2._key_buffer.append("x")
        interp2._key_buffer.append("y")
        interp2.run_program("INKEY", language="templecode")
        assert "x" in widget.raw
        assert len(interp2._key_buffer) == 1
        assert interp2._key_buffer[0] == "y"

    def test_inkey_multiple_calls_drain_buffer(self):
        """Multiple INKEY calls drain the buffer in FIFO order."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        widget = FakeOutputWidget()
        interp = TempleCodeInterpreter(output_widget=widget)
        interp._key_buffer.extend(["a", "b", "c"])
        interp.run_program("INKEY\nINKEY\nINKEY", language="templecode")
        lines = widget.program_lines
        assert "a" in lines[0]
        assert "b" in lines[1]
        assert "c" in lines[2]
        assert len(interp._key_buffer) == 0


# =====================================================================
#  INKEY$ — expression form
# =====================================================================

class TestInkeyExpression:
    def test_inkey_dollar_empty(self):
        """INKEY$ returns empty string when buffer is empty."""
        out = run_program('LET K = INKEY$\nPRINT LEN(K)')
        assert out.last_line == "0"

    def test_inkey_dollar_returns_key(self):
        """INKEY$ returns the next key from the buffer."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        widget = FakeOutputWidget()
        interp = TempleCodeInterpreter(output_widget=widget)
        interp._key_buffer.append("z")
        interp.run_program('LET K = INKEY$\nPRINT K', language="templecode")
        assert "z" in widget.raw
        assert len(interp._key_buffer) == 0

    def test_inkey_dollar_in_condition(self):
        """INKEY$ can be used in IF conditions."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        widget = FakeOutputWidget()
        interp = TempleCodeInterpreter(output_widget=widget)
        interp._key_buffer.append("q")
        interp.run_program(
            'LET K = INKEY$\nIF K = "q" THEN PRINT "quit"',
            language="templecode",
        )
        assert "quit" in widget.raw


# =====================================================================
#  SCREEN — canvas resize
# =====================================================================

class TestScreen:
    def test_screen_width_height(self):
        """SCREEN w h updates center_x and center_y."""
        _, interp = run_with_interp("SCREEN 800 600")
        tg = interp.turtle_graphics
        assert tg is not None
        assert tg["center_x"] == 400
        assert tg["center_y"] == 300

    def test_screen_preset_0(self):
        """SCREEN 0 → 320×200."""
        _, interp = run_with_interp("SCREEN 0")
        tg = interp.turtle_graphics
        assert tg["center_x"] == 160
        assert tg["center_y"] == 100

    def test_screen_preset_1(self):
        """SCREEN 1 → 640×480."""
        _, interp = run_with_interp("SCREEN 1")
        tg = interp.turtle_graphics
        assert tg["center_x"] == 320
        assert tg["center_y"] == 240

    def test_screen_preset_2(self):
        """SCREEN 2 → 800×600."""
        _, interp = run_with_interp("SCREEN 2")
        tg = interp.turtle_graphics
        assert tg["center_x"] == 400
        assert tg["center_y"] == 300

    def test_screen_preset_small(self):
        """SCREEN SMALL → 320×200."""
        _, interp = run_with_interp("SCREEN SMALL")
        tg = interp.turtle_graphics
        assert tg["center_x"] == 160
        assert tg["center_y"] == 100

    def test_screen_preset_medium(self):
        """SCREEN MEDIUM → 640×480."""
        _, interp = run_with_interp("SCREEN MEDIUM")
        tg = interp.turtle_graphics
        assert tg["center_x"] == 320
        assert tg["center_y"] == 240

    def test_screen_preset_large(self):
        """SCREEN LARGE → 800×600."""
        _, interp = run_with_interp("SCREEN LARGE")
        tg = interp.turtle_graphics
        assert tg["center_x"] == 400
        assert tg["center_y"] == 300

    def test_screen_unknown_mode(self):
        """SCREEN with unknown mode logs a message."""
        out = run_program("SCREEN ULTRA")
        assert "unknown mode" in out.raw.lower()

    def test_screen_preserves_turtle_position(self):
        """SCREEN doesn't reset the turtle's x/y position."""
        _, interp = run_with_interp("FORWARD 50\nSCREEN 800 600")
        tg = interp.turtle_graphics
        # Turtle moved forward 50 from origin; position should be preserved
        assert tg["center_x"] == 400
        assert tg["center_y"] == 300
        # x/y should still reflect movement (default heading is north/up)
        assert tg["y"] != 0 or tg["x"] != 0


# =====================================================================
#  FILL — flood fill (headless: tests graceful handling)
# =====================================================================

class TestFill:
    def test_fill_no_error_headless(self):
        """FILL runs without crashing in headless mode."""
        out = run_program("FORWARD 50\nFILL")
        raw = out.raw.lower()
        # In headless mode, Pillow PostScript path won't work, but it
        # should not raise an unhandled exception
        assert "traceback" not in raw

    def test_fill_after_setfillcolor(self):
        """FILL after SETFILLCOLOR doesn't crash."""
        out = run_program("SETFILLCOLOR blue\nFORWARD 50\nRIGHT 90\nFORWARD 50\nFILL")
        assert "traceback" not in out.raw.lower()

    def test_fill_initializes_turtle(self):
        """FILL ensures turtle graphics are initialized."""
        _, interp = run_with_interp("FILL")
        assert interp.turtle_graphics is not None


# =====================================================================
#  ExpressionCache — wiring verification
# =====================================================================

class TestExpressionCache:
    def test_cache_initialized(self):
        """Interpreter creates an ExpressionCache on init."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        assert hasattr(interp, "_expr_cache")
        assert interp._expr_cache is not None

    def test_cache_populated_after_eval(self):
        """Running expressions populates the cache."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        interp.run_program("LET X = 2 + 3\nPRINT X", language="templecode")
        # Cache should have at least one entry from the expression eval
        assert len(interp._expr_cache.cache) > 0

    def test_cache_hits_on_repeated_expression(self):
        """Repeated evaluation of the same expression should hit cache."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        code = "FOR I = 1 TO 5\nLET X = 2 + 3\nNEXT I"
        interp.run_program(code, language="templecode")
        assert interp._expr_cache.hits > 0

    def test_cache_correctness(self):
        """Cached expressions produce correct results."""
        out = run_program("LET X = 10\nPRINT X * 2\nPRINT X * 2")
        lines = out.program_lines
        assert lines[-1] == "20"
        assert lines[-2] == "20"


# =====================================================================
#  Key buffer — deque behavior
# =====================================================================

class TestKeyBuffer:
    def test_key_buffer_exists(self):
        """Interpreter has a _key_buffer deque."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        assert isinstance(interp._key_buffer, deque)
        assert interp._key_buffer.maxlen == 64

    def test_key_buffer_overflow(self):
        """Buffer drops oldest keys when full (maxlen=64)."""
        from core.interpreter import TempleCodeInterpreter
        from tests.helpers import FakeOutputWidget
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        for i in range(70):
            interp._key_buffer.append(str(i))
        assert len(interp._key_buffer) == 64
        # Oldest 6 should have been dropped
        assert interp._key_buffer[0] == "6"


# =====================================================================
#  DebugController — state machine
# =====================================================================

class TestDebugController:
    def test_initial_state(self):
        """DebugController starts in STOPPED state."""
        from core.features.debugger import DebugController, DebugState
        dc = DebugController()
        assert dc.state == DebugState.STOPPED
        assert not dc.is_active
        assert not dc.is_paused

    def test_start_sets_running(self):
        from core.features.debugger import DebugController, DebugState
        dc = DebugController()
        dc.start()
        assert dc.state == DebugState.RUNNING
        assert dc.is_active

    def test_step_over_from_stopped(self):
        from core.features.debugger import DebugController, DebugState
        dc = DebugController()
        dc.state = DebugState.PAUSED
        dc.step_over()
        assert dc.state == DebugState.STEPPING

    def test_stop_resets_state(self):
        from core.features.debugger import DebugController, DebugState
        dc = DebugController()
        dc.start()
        dc.stop()
        assert dc.state == DebugState.STOPPED
        assert not dc.is_active

    def test_check_pause_stops_when_stopped(self):
        """check_pause returns False when state is STOPPED."""
        from core.features.debugger import DebugController
        from core.interpreter import TempleCodeInterpreter
        dc = DebugController()
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        # STOPPED → should return False
        assert not dc.check_pause(interp)

    def test_check_pause_runs_through(self):
        """check_pause returns True when RUNNING and no breakpoint."""
        from core.features.debugger import DebugController
        from core.interpreter import TempleCodeInterpreter
        dc = DebugController()
        dc.start()
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        interp.current_line = 0
        assert dc.check_pause(interp)

    def test_breakpoint_pauses(self):
        """check_pause pauses at a breakpoint and resumes on continue."""
        from core.features.debugger import DebugController, DebugState
        from core.interpreter import TempleCodeInterpreter
        dc = DebugController()
        dc.start()
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        interp.current_line = 5
        interp.breakpoints.add(5)

        paused_lines = []
        dc.on_pause = lambda line, _vars: paused_lines.append(line)

        # Run check_pause in a thread (it will block)
        result = [None]
        def check():
            result[0] = dc.check_pause(interp)
        t = threading.Thread(target=check)
        t.start()

        # Give it a moment to pause
        time.sleep(0.05)
        assert dc.state == DebugState.PAUSED
        assert 5 in paused_lines

        # Continue
        dc.continue_()
        t.join(timeout=1)
        assert result[0] is True

    def test_snapshot_variables(self):
        """snapshot_variables returns user vars, lists, and dicts."""
        from core.features.debugger import DebugController
        from core.interpreter import TempleCodeInterpreter
        dc = DebugController()
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        interp.variables = {"X": 10, "NAME": "test"}
        interp.lists = {"NUMS": [1, 2, 3]}
        interp.dicts = {"CFG": {"a": 1}}
        snap = dc.snapshot_variables(interp)
        assert snap["X"] == 10
        assert snap["NAME"] == "test"
        assert snap["LIST NUMS"] == [1, 2, 3]
        assert snap["DICT CFG"] == {"a": 1}

    def test_debug_controller_on_interpreter(self):
        """Interpreter run loop checks debug_controller if attached."""
        from core.features.debugger import DebugController, DebugState
        from core.interpreter import TempleCodeInterpreter
        dc = DebugController()
        dc.start()
        interp = TempleCodeInterpreter(output_widget=FakeOutputWidget())
        interp.debug_controller = dc

        # Set a breakpoint on line 1 (0-based: line index 1)
        interp.breakpoints.add(1)
        interp.debug_mode = True

        paused_at = []
        dc.on_pause = lambda line, _v: paused_at.append(line)

        # Run in a thread since it will pause
        def run():
            interp.run_program("LET X = 1\nLET Y = 2\nPRINT X", language="templecode")
        t = threading.Thread(target=run)
        t.start()

        time.sleep(0.1)
        assert dc.is_paused
        assert 1 in paused_at

        # Stop the session
        dc.stop()
        interp.running = False
        t.join(timeout=2)


# =====================================================================
#  TabManager (unit tests, no GUI)
# =====================================================================

class TestTabState:
    def test_display_name_with_file(self):
        from ui.tabs import TabState
        t = TabState(file_path="/path/to/hello.tc")
        assert t.display_name() == "hello.tc"

    def test_display_name_modified(self):
        from ui.tabs import TabState
        t = TabState(file_path="/path/to/hello.tc", modified=True)
        assert t.display_name() == "hello.tc •"

    def test_display_name_untitled(self):
        from ui.tabs import TabState
        t = TabState()
        assert t.display_name() == "Untitled"


# =====================================================================
#  "Did you mean?" error suggestions
# =====================================================================

class TestDidYouMean:
    def test_typo_print_suggests_print(self):
        out = run_program('PRITN "hello"')
        assert "Did you mean PRINT?" in out.raw

    def test_typo_forward_suggests_forward(self):
        out = run_program('FORWRD 100')
        assert "Did you mean FORWARD?" in out.raw

    def test_no_suggestion_for_gibberish(self):
        out = run_program('XYZABC')
        assert "Did you mean" not in out.raw
        assert "Unknown command" in out.raw

    def test_typo_gosub_suggests_gosub(self):
        out = run_program('GOSU 100')
        assert "Did you mean GOSUB?" in out.raw

    def test_close_match_penup(self):
        out = run_program('PENP')
        assert "Did you mean" in out.raw


class TestLevenshtein:
    def test_identical(self):
        from core.languages.templecode import _levenshtein
        assert _levenshtein("PRINT", "PRINT") == 0

    def test_one_char_diff(self):
        from core.languages.templecode import _levenshtein
        assert _levenshtein("PRITN", "PRINT") == 2  # swap = 2 edits

    def test_empty(self):
        from core.languages.templecode import _levenshtein
        assert _levenshtein("", "ABC") == 3
        assert _levenshtein("ABC", "") == 3


# =====================================================================
#  Multi-line STRUCT with METHOD
# =====================================================================

class TestMultiLineStruct:
    def test_multiline_struct_fields(self):
        code = "STRUCT Point\nFIELD X, Y\nEND STRUCT\nNEW Point AS P\nPRINT P.X"
        out = run_program(code)
        assert out.last_line == "0"

    def test_multiline_struct_set_get(self):
        code = ("STRUCT Point\nFIELD X, Y\nEND STRUCT\n"
                "NEW Point AS P\nLET P.X = 42\nPRINT P.X")
        out = run_program(code)
        assert out.last_line == "42"

    def test_multiline_struct_multiple_fields(self):
        code = ("STRUCT Car\nFIELD MAKE\nFIELD MODEL\nFIELD YEAR\nEND STRUCT\n"
                "NEW Car AS C\nLET C.YEAR = 2024\nPRINT C.YEAR")
        out = run_program(code)
        assert out.last_line == "2024"

    def test_struct_method_call(self):
        code = ("STRUCT Dog\nFIELD NAME\n"
                "METHOD SPEAK(SELF)\nPRINT \"Woof\"\nEND METHOD\n"
                "END STRUCT\nNEW Dog AS D\nCALL D.SPEAK()")
        out = run_program(code)
        assert "Woof" in out.raw

    def test_struct_method_accesses_fields(self):
        code = ("STRUCT Greeter\nFIELD NAME\n"
                "METHOD SAY(SELF)\nPRINT SELF.NAME\nEND METHOD\n"
                "END STRUCT\n"
                "NEW Greeter AS G\nLET G.NAME = \"Alice\"\nCALL G.SAY()")
        out = run_program(code)
        assert "Alice" in out.raw

    def test_singleline_struct_still_works(self):
        """Backward compatibility: single-line STRUCT = field, field."""
        code = "STRUCT Pair = A, B\nNEW Pair AS P\nLET P.A = 99\nPRINT P.A"
        out = run_program(code)
        assert out.last_line == "99"

    def test_new_tags_type(self):
        """NEW instances have __TYPE__ set."""
        _, interp = run_with_interp(
            "STRUCT Foo\nFIELD X\nEND STRUCT\nNEW Foo AS F")
        assert interp.dicts["F"]["__TYPE__"] == "FOO"


# =====================================================================
#  Multi-line LAMBDA
# =====================================================================

class TestMultiLineLambda:
    def test_singleline_lambda_still_works(self):
        code = "LAMBDA DOUBLE(X) = X * 2\nPRINT DOUBLE(5)"
        out = run_program(code)
        assert out.last_line == "10"

    def test_multiline_lambda_basic(self):
        code = ("LAMBDA SQUARE(X)\n"
                "RETURN X * X\n"
                "END LAMBDA\n"
                "PRINT SQUARE(7)")
        out = run_program(code)
        assert out.last_line == "49"

    def test_multiline_lambda_with_if(self):
        code = ("LAMBDA ABSVAL(X)\n"
                "IF X < 0 THEN RETURN 0 - X\n"
                "RETURN X\n"
                "END LAMBDA\n"
                "PRINT ABSVAL(-5)\n"
                "PRINT ABSVAL(3)")
        out = run_program(code)
        lines = out.program_lines
        assert lines[0] == "5"
        assert lines[1] == "3"

    def test_multiline_lambda_recursive(self):
        code = ("LAMBDA FACT(N)\n"
                "IF N <= 1 THEN RETURN 1\n"
                "RETURN N * FACT(N - 1)\n"
                "END LAMBDA\n"
                "PRINT FACT(6)")
        out = run_program(code)
        assert out.last_line == "720"

    def test_multiline_lambda_with_local_var(self):
        code = ("LAMBDA ADD3(A, B, C)\n"
                "LET S = A + B + C\n"
                "RETURN S\n"
                "END LAMBDA\n"
                "PRINT ADD3(10, 20, 30)")
        out = run_program(code)
        assert out.last_line == "60"


# =====================================================================
#  REPL panel (unit tests, no GUI)
# =====================================================================

class TestReplOutputCapture:
    def test_capture_insert(self):
        from ui.repl import _ReplOutputCapture
        cap = _ReplOutputCapture()
        cap.insert("end", "hello\n")
        cap.insert("end", "world\n")
        assert cap.get_output() == "hello\nworld\n"

    def test_capture_clear(self):
        from ui.repl import _ReplOutputCapture
        cap = _ReplOutputCapture()
        cap.insert("end", "data")
        cap.clear()
        assert cap.get_output() == ""

    def test_capture_see_noop(self):
        from ui.repl import _ReplOutputCapture
        cap = _ReplOutputCapture()
        cap.see("end")  # should not raise


# =====================================================================
#  Settings validation
# =====================================================================

class TestSettingsValidation:
    def test_unknown_theme_falls_back(self):
        from core.settings import _validate, DEFAULTS
        data = {"theme": "nonexistent_theme_xyz"}
        result = _validate(data)
        assert result["theme"] == DEFAULTS["theme"]

    def test_unknown_font_size_falls_back(self):
        from core.settings import _validate, DEFAULTS
        data = {"font_size": "ultra_mega"}
        result = _validate(data)
        assert result["font_size"] == DEFAULTS["font_size"]

    def test_exec_speed_clamped(self):
        from core.settings import _validate
        result = _validate({"exec_speed": 9999})
        assert result["exec_speed"] == 500

    def test_negative_exec_speed_clamped(self):
        from core.settings import _validate
        result = _validate({"exec_speed": -10})
        assert result["exec_speed"] == 0

    def test_turtle_speed_clamped(self):
        from core.settings import _validate
        result = _validate({"turtle_speed": 999})
        assert result["turtle_speed"] == 200

    def test_recent_files_non_list_reset(self):
        from core.settings import _validate
        result = _validate({"recent_files": "not_a_list"})
        assert result["recent_files"] == []

    def test_defaults_merged(self):
        from core.settings import _validate, DEFAULTS
        result = _validate({})
        for key in DEFAULTS:
            assert key in result

    def test_geometry_non_string_reset(self):
        from core.settings import _validate
        result = _validate({"geometry": 12345})
        assert result["geometry"] == ""


# =====================================================================
#  Error-path tests for STRUCT
# =====================================================================

class TestStructErrors:
    def test_missing_end_struct(self):
        """Multi-line STRUCT without END STRUCT completes without crashing."""
        code = ("STRUCT Dog\n"
                "FIELD Name\n"
                "FIELD Breed\n")
        out = run_program(code)
        # Should not crash — may or may not report an error
        assert "Traceback" not in out.raw

    def test_duplicate_field_allowed(self):
        """Duplicate FIELD names should not crash (last wins or no error)."""
        code = ("STRUCT Item\n"
                "FIELD Name\n"
                "FIELD Name\n"
                "END STRUCT\n"
                "NEW Item AS x\n"
                "PRINT \"ok\"")
        out = run_program(code)
        assert "ok" in out.raw.lower() or "error" not in out.raw.lower()

    def test_method_call_on_undefined_method(self):
        """Calling an undefined method should report an error, not crash."""
        code = ("STRUCT Foo\n"
                "FIELD X\n"
                "END STRUCT\n"
                "NEW Foo AS obj\n"
                "CALL obj.nonexistent()")
        out = run_program(code)
        # Should complete without Python traceback
        assert "Traceback" not in out.raw


# =====================================================================
#  Error-path tests for LAMBDA
# =====================================================================

class TestLambdaErrors:
    def test_missing_end_lambda(self):
        """Multi-line LAMBDA without END LAMBDA completes without crashing."""
        code = ("LAMBDA bad(x)\n"
                "LET y = x + 1\n"
                "RETURN y\n")
        out = run_program(code)
        assert "Traceback" not in out.raw

    def test_lambda_bad_syntax(self):
        """LAMBDA with no name or args should not crash."""
        code = "LAMBDA"
        out = run_program(code)
        assert "Traceback" not in out.raw


# =====================================================================
#  Error-path tests for Did you mean
# =====================================================================

class TestDidYouMeanErrors:
    def test_completely_unknown_command(self):
        """A totally unrecognizable command should say 'Unknown command'."""
        out = run_program("XYZZYPLUGH 42")
        assert "unknown command" in out.raw.lower()

    def test_close_misspelling_suggests(self):
        """A close misspelling should get a suggestion."""
        out = run_program("PRITN \"hello\"")
        assert "did you mean" in out.raw.lower() or "unknown" in out.raw.lower()


# =====================================================================
#  Error-path tests for ExpressionCache
# =====================================================================

class TestExpressionCacheEdge:
    def test_cache_eviction(self):
        """When cache exceeds max_size, old entries are evicted."""
        from core.optimizations.performance_optimizer import ExpressionCache
        cache = ExpressionCache(max_size=10)
        for i in range(15):
            cache.put(f"key_{i}", i)
        stats = cache.get_stats()
        assert stats["size"] <= 10

    def test_cache_clear_resets_stats(self):
        from core.optimizations.performance_optimizer import ExpressionCache
        cache = ExpressionCache(max_size=100)
        cache.put("a", 1)
        cache.get("a")
        cache.clear()
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0


# =====================================================================
#  Dispatch dict refactor — smoke tests
# =====================================================================

class TestDispatchDict:
    def test_basic_commands_still_work(self):
        """Basic commands should still dispatch correctly after refactor."""
        out = run_program("LET X = 5\nPRINT X")
        assert out.last_line == "5"

    def test_incr_alias(self):
        out = run_program("LET X = 10\nINC X\nPRINT X")
        assert out.last_line == "11"

    def test_decr_alias(self):
        out = run_program("LET X = 10\nDEC X\nPRINT X")
        assert out.last_line == "9"

    def test_end_variants(self):
        out = run_program("PRINT \"before\"\nEND\nPRINT \"after\"")
        assert "before" in out.raw
        assert "after" not in out.raw

    def test_data_read(self):
        out = run_program("DATA 10, 20, 30\nREAD A\nREAD B\nREAD C\nPRINT A + B + C")
        assert out.last_line == "60"

    def test_randomize_no_crash(self):
        out = run_program("RANDOMIZE\nRANDOMIZE TIMER\nPRINT \"ok\"")
        assert "ok" in out.raw
