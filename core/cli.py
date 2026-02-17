#!/usr/bin/env python3
"""
TempleCode CLI — command-line interface for Time Warp II.

Run ``.tc`` programs, launch an interactive REPL, or inspect
TempleCode source without the full GUI.

Usage examples
--------------
::

    # Run a program file
    templecode run examples/templecode/hello.tc

    # Run with debug tracing
    templecode run examples/templecode/fibonacci.tc --debug

    # Interactive REPL
    templecode repl

    # Show version
    templecode --version

Copyright © 2025-2026 Honey Badger Universe. All rights reserved.
"""

import argparse
import sys
import os
import time
from pathlib import Path

# ---------------------------------------------------------------------------
#  Version — kept in sync with pyproject.toml
# ---------------------------------------------------------------------------
__version__ = "2.0.0"


# ---------------------------------------------------------------------------
#  Headless output collector (reuses the same interface as FakeOutputWidget)
# ---------------------------------------------------------------------------

class _CLIOutputWidget:
    """Thin adapter that prints interpreter output directly to a stream."""

    def __init__(self, stream=None, colour: bool = True):
        self._stream = stream or sys.stdout
        self._colour = colour and hasattr(self._stream, "isatty") and self._stream.isatty()

    # -- tkinter Text interface subset expected by the interpreter -----------
    def insert(self, _index, text):  # noqa: D401
        """Write *text* to the output stream."""
        self._stream.write(str(text))
        self._stream.flush()

    def see(self, _index):
        """No-op (scroll-to-end)."""

    def delete(self, _start, _end):
        """No-op (clear)."""


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _make_interpreter(*, debug: bool = False, colour: bool = True):
    """Create a headless TempleCodeInterpreter wired to stdout."""
    from core.interpreter import TempleCodeInterpreter  # noqa: C0415

    widget = _CLIOutputWidget(colour=colour)
    interp = TempleCodeInterpreter(output_widget=widget)
    if debug:
        interp.set_debug_mode(True)
    return interp


def _resolve_file(path_str: str) -> Path:
    """Resolve a file path, searching common locations if not found."""
    p = Path(path_str)
    if p.is_file():
        return p.resolve()

    # Try relative to CWD
    cwd_p = Path.cwd() / path_str
    if cwd_p.is_file():
        return cwd_p.resolve()

    # Try inside examples/templecode/
    project_root = Path(__file__).resolve().parent.parent
    example_p = project_root / "examples" / "templecode" / path_str
    if example_p.is_file():
        return example_p.resolve()

    # Try with .tc extension
    if not path_str.endswith(".tc"):
        return _resolve_file(path_str + ".tc")

    print(f"Error: file not found: {path_str}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
#  Sub-commands
# ---------------------------------------------------------------------------

def cmd_run(args):
    """Execute a .tc program file."""
    filepath = _resolve_file(args.file)
    source = filepath.read_text(encoding="utf-8")

    interp = _make_interpreter(debug=args.debug)

    # Attach profiler if requested
    if getattr(args, 'profile', False):
        from core.features.ide_features import Profiler  # noqa: C0415
        profiler = Profiler()
        profiler.enabled = True
        interp.profiler = profiler

    if args.time:
        t0 = time.perf_counter()

    interp.run_program(source)

    if args.time:
        elapsed = time.perf_counter() - t0
        print(f"\n⏱  Elapsed: {elapsed:.3f}s")

    # Export canvas to PNG if requested
    if getattr(args, 'export_canvas', None):
        _export_headless_canvas(interp, args.export_canvas)

    # Non-zero exit if there were errors
    if interp.error_history:
        sys.exit(1)


def cmd_repl(args):
    """Start an interactive TempleCode REPL."""
    interp = _make_interpreter(debug=args.debug)
    interp.running = True

    print(f"TempleCode REPL v{__version__}")
    print("Type TempleCode commands.  Enter 'QUIT' or Ctrl-D to exit.")
    print("Enter 'RUN' to execute accumulated numbered lines.")
    print("Enter 'LIST' to show accumulated program.")
    print("Enter 'CLEAR' to reset.\n")

    numbered_lines: dict[int, str] = {}

    try:
        while True:
            try:
                line = input("tc> ")
            except EOFError:
                print()
                break

            stripped = line.strip()
            if not stripped:
                continue

            upper = stripped.upper()
            if upper in ("QUIT", "EXIT", "BYE"):
                break

            if upper == "CLEAR":
                interp.reset()
                numbered_lines.clear()
                print("Cleared.")
                continue

            if upper == "LIST":
                if not numbered_lines:
                    print("(no program lines)")
                else:
                    for num in sorted(numbered_lines):
                        print(f"{num} {numbered_lines[num]}")
                continue

            if upper == "RUN":
                if not numbered_lines:
                    print("(no program lines to run)")
                    continue
                program = "\n".join(
                    f"{num} {cmd}" for num, cmd in sorted(numbered_lines.items())
                )
                interp.reset()
                interp.run_program(program)
                continue

            if upper == "DEBUG ON":
                interp.set_debug_mode(True)
                print("Debug mode ON")
                continue
            if upper == "DEBUG OFF":
                interp.set_debug_mode(False)
                print("Debug mode OFF")
                continue

            if upper == "VARS":
                if not interp.variables:
                    print("(no variables)")
                else:
                    for k, v in sorted(interp.variables.items()):
                        print(f"  {k} = {v!r}")
                continue

            if upper == "HELP":
                _repl_help()
                continue

            # Check for numbered line → store in program buffer
            import re  # noqa: C0415
            m = re.match(r"^(\d+)\s+(.*)", stripped)
            if m:
                num = int(m.group(1))
                cmd = m.group(2).strip()
                if not cmd:
                    # Delete line
                    numbered_lines.pop(num, None)
                    print(f"  Line {num} deleted")
                else:
                    numbered_lines[num] = cmd
                    print(f"  {num} {cmd}")
                continue

            # Immediate execution
            try:
                interp.execute_line(stripped)
            except Exception as exc:
                print(f"Error: {exc}")

    except KeyboardInterrupt:
        print("\nInterrupted.")

    print("Goodbye!")


def _repl_help():
    """Print REPL help text."""
    print("""
REPL Commands
─────────────────────────────────────
  <command>          Execute immediately
  <num> <command>    Store as program line
  <num>              Delete program line
  RUN                Execute stored program
  LIST               Show stored program
  CLEAR              Reset interpreter & program
  VARS               Show all variables
  DEBUG ON / OFF     Toggle debug tracing
  HELP               This message
  QUIT / EXIT        Leave the REPL
""")


def _export_headless_canvas(interp, output_path: str) -> None:
    """Export the headless canvas drawing data to a PNG file.

    Uses PIL to render collected canvas items (lines, ovals, etc.)
    onto a blank image.
    """
    try:
        from PIL import Image, ImageDraw  # noqa: C0415
    except ImportError:
        print("Error: Pillow is required for canvas export. Install with: pip install Pillow",
              file=sys.stderr)
        sys.exit(1)

    canvas = interp.ide_turtle_canvas
    if canvas is None or not hasattr(canvas, 'created'):
        print("No canvas data to export.", file=sys.stderr)
        return

    width, height = 600, 400
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    for item in canvas.created:
        kind = item["type"]
        args = item["args"]
        kwargs = item.get("kwargs", {})
        fill = kwargs.get("fill", "black")
        outline = kwargs.get("outline", "")
        line_width = kwargs.get("width", 1)

        if kind == "line" and len(args) >= 4:
            draw.line(list(args), fill=fill or "black", width=int(line_width))
        elif kind == "oval" and len(args) >= 4:
            draw.ellipse(list(args[:4]), fill=fill or None, outline=outline or "black")
        elif kind == "rectangle" and len(args) >= 4:
            draw.rectangle(list(args[:4]), fill=fill or None, outline=outline or "black")
        elif kind == "polygon" and len(args) >= 4:
            draw.polygon(list(args), fill=fill or None, outline=outline or "black")
        elif kind == "text" and len(args) >= 2:
            text_str = kwargs.get("text", "")
            if text_str:
                draw.text((args[0], args[1]), text_str, fill=fill or "black")

    img.save(output_path, "PNG")
    print(f"📸 Canvas exported to {output_path}")


def cmd_format(args):
    """Format / auto-indent a .tc source file."""
    from core.features.ide_features import format_code  # noqa: C0415

    filepath = _resolve_file(args.file)
    source = filepath.read_text(encoding="utf-8")
    formatted = format_code(source, indent_width=args.indent)

    if args.check:
        if source == formatted:
            print(f"✅ {filepath.name} is already formatted.")
        else:
            print(f"⚠️  {filepath.name} needs formatting.")
            sys.exit(1)
        return

    if args.inplace:
        filepath.write_text(formatted, encoding="utf-8")
        print(f"✅ Formatted {filepath.name} in-place.")
    else:
        print(formatted)


def cmd_check(args):
    """Syntax-check a .tc file without executing."""
    filepath = _resolve_file(args.file)
    source = filepath.read_text(encoding="utf-8")

    issues: list[str] = []
    lines = source.strip().split("\n")

    # Track balanced constructs
    for_count = 0
    if_count = 0
    while_count = 0
    sub_count = 0
    try_count = 0
    select_count = 0

    import re  # noqa: C0415
    for i, raw in enumerate(lines, 1):
        _, cmd = _parse_line_number(raw)
        upper = cmd.upper().strip()

        if re.match(r'^FOR\b', upper):
            for_count += 1
        elif re.match(r'^NEXT\b', upper):
            for_count -= 1
            if for_count < 0:
                issues.append(f"  Line {i}: NEXT without matching FOR")
                for_count = 0

        if re.match(r'^IF\b', upper) and "THEN" in upper:
            # Single-line IF/THEN doesn't need ENDIF
            rest_after_then = upper.split("THEN", 1)[1].strip()
            if not rest_after_then:
                if_count += 1
        elif upper == "ENDIF" or upper == "END IF":
            if_count -= 1
            if if_count < 0:
                issues.append(f"  Line {i}: ENDIF without matching IF")
                if_count = 0

        if re.match(r'^WHILE\b', upper):
            while_count += 1
        elif upper == "WEND":
            while_count -= 1
            if while_count < 0:
                issues.append(f"  Line {i}: WEND without matching WHILE")
                while_count = 0

        if re.match(r'^SUB\b', upper) or re.match(r'^FUNCTION\b', upper):
            sub_count += 1
        elif upper == "END SUB" or upper == "END FUNCTION":
            sub_count -= 1
            if sub_count < 0:
                issues.append(f"  Line {i}: END SUB/FUNCTION without matching SUB/FUNCTION")
                sub_count = 0

        if upper == "TRY":
            try_count += 1
        elif upper == "END TRY":
            try_count -= 1
            if try_count < 0:
                issues.append(f"  Line {i}: END TRY without matching TRY")
                try_count = 0

        if re.match(r'^SELECT\b', upper):
            select_count += 1
        elif upper == "END SELECT":
            select_count -= 1
            if select_count < 0:
                issues.append(f"  Line {i}: END SELECT without matching SELECT")
                select_count = 0

    # Report unclosed blocks
    if for_count > 0:
        issues.append(f"  {for_count} unclosed FOR loop(s) (missing NEXT)")
    if if_count > 0:
        issues.append(f"  {if_count} unclosed IF block(s) (missing ENDIF)")
    if while_count > 0:
        issues.append(f"  {while_count} unclosed WHILE loop(s) (missing WEND)")
    if sub_count > 0:
        issues.append(f"  {sub_count} unclosed SUB/FUNCTION(s) (missing END SUB/FUNCTION)")
    if try_count > 0:
        issues.append(f"  {try_count} unclosed TRY block(s) (missing END TRY)")
    if select_count > 0:
        issues.append(f"  {select_count} unclosed SELECT block(s) (missing END SELECT)")

    print(f"Checking {filepath.name}  ({len(lines)} lines)")
    if issues:
        print(f"⚠️  {len(issues)} issue(s) found:")
        for issue in issues:
            print(issue)
        sys.exit(1)
    else:
        print("✅ No issues found.")


def _parse_line_number(line: str):
    """Split optional leading line number from command text."""
    import re  # noqa: C0415
    line = line.strip()
    m = re.match(r"^(\d+)\s+(.*)", line)
    if m:
        return int(m.group(1)), m.group(2).strip()
    return None, line


# ---------------------------------------------------------------------------
#  Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="templecode",
        description="TempleCode CLI — run .tc programs or start an interactive REPL.",
        epilog="Examples:\n"
               "  templecode run hello.tc\n"
               "  templecode run fibonacci.tc --debug --time\n"
               "  templecode repl\n"
               "  templecode check myprogram.tc\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"TempleCode CLI v{__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- run ---
    run_p = subparsers.add_parser("run", help="Execute a .tc program file")
    run_p.add_argument("file", help="Path to .tc file (also searches examples/)")
    run_p.add_argument("--debug", "-d", action="store_true",
                       help="Enable debug tracing")
    run_p.add_argument("--time", "-t", action="store_true",
                       help="Print elapsed execution time")
    run_p.add_argument("--profile", "-p", action="store_true",
                       help="Enable profiler (per-line timing)")
    run_p.add_argument("--export-canvas", "-e", metavar="FILE",
                       help="Export turtle canvas to PNG after execution")

    # --- repl ---
    repl_p = subparsers.add_parser("repl", help="Interactive TempleCode REPL")
    repl_p.add_argument("--debug", "-d", action="store_true",
                        help="Start with debug mode enabled")

    # --- check ---
    check_p = subparsers.add_parser("check", help="Syntax-check a .tc file")
    check_p.add_argument("file", help="Path to .tc file")

    # --- format ---
    format_p = subparsers.add_parser("format", help="Format / auto-indent a .tc file")
    format_p.add_argument("file", help="Path to .tc file")
    format_p.add_argument("--indent", "-i", type=int, default=2,
                          help="Indentation width (default: 2)")
    format_p.add_argument("--inplace", "-w", action="store_true",
                          help="Write formatted output back to file")
    format_p.add_argument("--check", "-c", action="store_true",
                          help="Check formatting without modifying (exit 1 if unformatted)")

    # --- gui ---
    subparsers.add_parser("gui", help="Launch the full GUI IDE")

    return parser


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

def main(argv=None):
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        cmd_run(args)
    elif args.command == "repl":
        cmd_repl(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "format":
        cmd_format(args)
    elif args.command == "gui":
        # Launch the GUI via the existing TimeWarpII module
        project_root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(project_root))
        os.chdir(project_root)
        import subprocess  # noqa: C0415
        subprocess.run([sys.executable, str(project_root / "TimeWarpII.py")])
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
