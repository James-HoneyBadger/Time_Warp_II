# Time Warp II

> **A Special Version of Time Warp Classic — Built Specifically for the TempleCode Language**
> **BASIC + PILOT + Logo fused into one — as if from the early 1990s.**

Time Warp II is an educational IDE and a special version of **Time Warp Classic** with various enhancements and revisions, designed specifically for the **TempleCode language** — a fusion of BASIC, PILOT, and Logo. Write programs that mix line-numbered BASIC statements, PILOT interactive commands, and Logo turtle graphics — all in a single `.tc` file.

[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](https://github.com/James-HoneyBadger/Time_Warp_II)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 🌟 Features

### The TempleCode Language
A single unified language drawing from three classic educational languages:
- **BASIC heritage** — `PRINT`, `LET`, `IF/THEN`, `FOR/NEXT`, `GOTO`, `GOSUB/RETURN`, `DIM`, `INPUT`, `REM`, `END`, optional line numbers
- **PILOT heritage** — `T:` (type), `A:` (accept), `M:` (match), `Y:` / `N:` (conditional), `J:` (jump), `C:` (compute), `E:` (end), `*label` labels
- **Logo heritage** — `FORWARD`/`FD`, `BACK`/`BK`, `LEFT`/`LT`, `RIGHT`/`RT`, `PENUP`/`PU`, `PENDOWN`/`PD`, `REPEAT [...]`, `SETCOLOR`, `CIRCLE`, `HOME`, `TO procname ... END` procedures

All three styles can be freely mixed in a single program.

### Professional IDE Interface
- **Refined Menu System** — File, Edit, View, Program, Debug, Test, Preferences, About, Help
- **Integrated Editor** — Syntax-aware code editing with undo/redo
- **Syntax Highlighting** — Real-time syntax coloring for TempleCode
- **Line Numbers** — Always-visible line numbering for easy navigation
- **Real-time Output** — Immediate program execution feedback
- **Turtle Graphics Canvas** — Visual programming with integrated graphics display
- **Theme Support** — 9 color themes with persistence
- **Debug Tools** — Debug mode, breakpoints, error history tracking
- **Enhanced Error Messages** — Detailed error reporting with line numbers
- **Customizable Fonts** — 7 font sizes plus system monospace choices
- **Panel Management** — Resizable output and graphics panels

### Educational Focus
- **Enhanced Error Messages** — Detailed error reporting with line numbers and context
- **Debug Tools** — Step-through debugging, breakpoint management, error history
- **Testing Framework** — Built-in test suite with smoke tests and comprehensive coverage
- Example programs demonstrating all three language heritages
- Immediate execution feedback
- Visual turtle graphics programming
- Interactive learning environment

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- tkinter (usually included with Python)
- pip package manager

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/James-HoneyBadger/Time_Warp_II.git
   cd Time_Warp_II
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or use a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Launch the IDE:**
   ```bash
   python TimeWarpII.py
   ```

## 🧪 Testing

Time Warp II includes a comprehensive test suite to ensure code quality and reliability.

### Running Tests

#### From Command Line
```bash
# Run all tests
python scripts/run_tests.py

# Run specific test types
python scripts/run_tests.py unit        # Unit tests only
python scripts/run_tests.py integration # Integration tests only
python scripts/run_tests.py smoke       # Quick smoke test

# Run with coverage
python scripts/run_tests.py --coverage
```

#### From Within the Application
Use the **Test** menu in the IDE:
- **Run Smoke Test** — Quick functionality check
- **Open Examples Directory** — Browse example files

### Test Structure
```
tests/
├── __init__.py              # Test package init
├── helpers.py               # HeadlessApp fixture, run_tc helper
├── test_interpreter.py      # Core interpreter tests
└── test_all_commands.py     # Full TempleCode command coverage
```

---

## 🚀 Getting Started

### Using the GUI

When you launch TimeWarpII.py, you'll see the main IDE interface:

1. **Write Code** — Use the editor panel to write TempleCode (`.tc`)
2. **Run Program** — Press **F5** or use **Program → Run Program**
3. **View Results** — See output in the output panel and turtle graphics below

### Quick Examples

Draw a square with Logo commands:
```
REPEAT 4 [FORWARD 100 RIGHT 90]
```

A BASIC program:
```
10 PRINT "Hello from TempleCode!"
20 FOR I = 1 TO 5
30   PRINT "Count: "; I
40 NEXT I
50 END
```

A PILOT quiz:
```
T:What is the capital of France?
A:
M:Paris
Y:T:Correct!
N:T:Sorry, the answer is Paris.
```

Mix all three in one program:
```
10 PRINT "Welcome to TempleCode!"
T:This line uses PILOT output.
REPEAT 4 [FORWARD 80 RIGHT 90]
20 END
```

### Loading Examples

**Via Menu:**
1. **Program → Load Example**
2. Choose an example program (`.tc` files)

**Via File Menu:**
1. **File → Open File...**
2. Navigate to `examples/templecode/`
3. Select a `.tc` file

---

## 📚 Documentation

### User Documentation
- **[Quick Start Guide](docs/QUICK_START.md)** — Get up and running quickly
- **[User Guide](docs/user/USER_GUIDE.md)** — Complete IDE features and usage
- **[Student Tutorial](docs/user/STUDENT_TUTORIAL.md)** — Learn to code step by step
- **[Instructor Guide](docs/user/INSTRUCTOR_GUIDE.md)** — Teaching with Time Warp II
- **[Language Tutorials](docs/user/LANGUAGE_TUTORIALS.md)** — Learn the TempleCode language
- **[Keyboard Shortcuts](docs/user/KEYBOARD_SHORTCUTS.md)** — All keyboard shortcuts
- **[Themes & Fonts](docs/user/THEMES_AND_FONTS.md)** — Customisation guide
- **[Example Programs](examples/README.md)** — 21 guided example programs

### Language Reference
- **[TempleCode Reference](docs/languages/TEMPLECODE_REFERENCE.md)** — Complete language reference

### Technical Documentation
- **[Technical Reference](docs/dev/TECHNICAL_REFERENCE.md)** — Architecture and implementation details

### Additional References
- **[Documentation Index](docs/INDEX.md)** — Doc suite overview
- **[FAQ](docs/FAQ.md)** — Frequently asked questions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** — Common issues and solutions

## 🎨 The TempleCode Language

### BASIC Heritage
Classic programming with optional line numbers, variables, loops, and subroutines.
```
10 PRINT "Drawing a square..."
20 FOR I = 1 TO 4
30   FORWARD 100
40   RIGHT 90
50 NEXT I
60 END
```

### PILOT Heritage
Interactive text output, user input, and pattern matching for quizzes and lessons.
```
T:Welcome to TempleCode!
A:What is your name?
T:Hello, *answer*!
```

### Logo Heritage
Turtle graphics with movement, pen control, and repeating patterns.
```
SETCOLOR red
REPEAT 36 [FORWARD 100 RIGHT 170]
```

---

## 🗂️ Project Structure

```
Time_Warp_II/
├── TimeWarpII.py              # Main application entry point
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Python project configuration
│
├── core/                    # Core interpreter engine
│   ├── interpreter.py       # TempleCodeInterpreter class
│   ├── languages/           # Language executor
│   │   └── templecode.py    # TempleCodeExecutor (BASIC + PILOT + Logo)
│   ├── features/            # IDE features
│   │   ├── code_templates.py
│   │   └── syntax_highlighting.py
│   ├── optimizations/       # Performance optimization
│   └── utilities/           # Helper utilities
│
├── examples/                # Example programs
│   ├── README.md           # Examples documentation
│   └── templecode/         # 21 TempleCode examples (.tc files)
│       ├── hello.tc, spiral.tc, quiz.tc, guess.tc, mandelbrot.tc
│       ├── calculator.tc, countdown.tc, fizzbuzz.tc, fibonacci.tc
│       ├── timestables.tc, temperature.tc, dice.tc
│       ├── science_quiz.tc, adventure.tc, interactive_drawing.tc
│       └── rainbow.tc, shapes.tc, flower.tc, kaleidoscope.tc, ...
│
├── docs/                   # Documentation
│   ├── INDEX.md            # Documentation index
│   ├── QUICK_START.md, FAQ.md, TROUBLESHOOTING.md
│   ├── languages/          # Language reference
│   │   └── TEMPLECODE_REFERENCE.md
│   ├── user/               # User guides & tutorials
│   │   ├── USER_GUIDE.md, LANGUAGE_TUTORIALS.md
│   │   ├── STUDENT_TUTORIAL.md, INSTRUCTOR_GUIDE.md
│   │   ├── KEYBOARD_SHORTCUTS.md, THEMES_AND_FONTS.md
│   └── dev/                # Developer docs
│       └── TECHNICAL_REFERENCE.md
│
└── scripts/                # Launcher scripts
    ├── launch.py           # Python launcher
    ├── launch_TimeWarpII.sh # Shell launcher
    └── start.sh            # Simple launcher
```

---

## ⌨️ Keyboard Shortcuts

### Program Execution
- **F5** — Run current program

### File Operations
- **Ctrl+N** — New file
- **Ctrl+O** — Open file
- **Ctrl+S** — Save file
- **Ctrl+Q** — Exit application

### Editing
- **Ctrl+Z** — Undo
- **Ctrl+Y** — Redo
- **Ctrl+X** — Cut
- **Ctrl+C** — Copy
- **Ctrl+V** — Paste
- **Ctrl+A** — Select all

---

## 🎯 Use Cases

### Education
- **Learn Programming Fundamentals** — BASIC syntax makes it easy to start
- **Interactive Lessons** — PILOT commands are perfect for quizzes and tutorials
- **Visual Learning** — Logo turtle graphics provide immediate visual feedback
- **Historical Perspective** — Experience BASIC, PILOT, and Logo traditions in one language

### Hobbyist Programming
- **Retro Computing** — A language that feels like the early 1990s
- **Creative Coding** — Use turtle graphics for artistic expression
- **Quick Prototyping** — Write programs fast with simple syntax

### Teaching
- **Classroom Tool** — One language covering structured programming, interaction, and graphics
- **Interactive Quizzes** — PILOT-style accept/match for student exercises
- **Hands-on Practice** — Immediate execution and visual feedback

---

## 🔧 System Requirements

### Minimum Requirements
- **OS:** Windows 7+, macOS 10.12+, Linux (any modern distribution)
- **Python:** 3.9 or higher
- **RAM:** 512 MB
- **Display:** 1024x768 or higher

### Recommended Requirements
- **OS:** Windows 10+, macOS 11+, Ubuntu 20.04+
- **Python:** 3.11 or higher
- **RAM:** 2 GB
- **Display:** 1920x1080 or higher

### Required Python Packages
- **tkinter** — GUI framework (usually included with Python)
- **pygame-ce** — Graphics and multimedia support (community edition, installed automatically)
- **pygments** — Syntax highlighting (installed automatically)
- **Pillow** — Image processing (installed automatically)

### Development Packages (Optional)
- **pytest** — Testing framework
- **black** — Code formatting
- **flake8** — Linting

---

## 🤝 Contributing

Contributions are welcome! See the **[Technical Reference](docs/dev/TECHNICAL_REFERENCE.md)** for architecture details.

### Quick Contributing Guide

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and test thoroughly
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Time_Warp_II.git
cd Time_Warp_II

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **BASIC** — Tribute to Kemeny and Kurtz's accessible programming vision (1964)
- **PILOT** — Inspired by John Amsden Starkweather's original design (1968)
- **Logo** — Honoring Seymour Papert's educational computing legacy (1967)
- **Classic Computing Community** — For keeping vintage computing alive
- **Open Source Contributors** — Everyone who helps improve Time Warp II

---

## 📞 Support

- **Documentation:** See the `docs/` directory
- **Issues:** Report bugs on [GitHub Issues](https://github.com/James-HoneyBadger/Time_Warp_II/issues)
- **Questions:** Check the [FAQ](docs/FAQ.md) first
- **Community:** Share your `.tc` programs and experiences!

---

## 🎓 Learning Resources

### For Beginners
Start with the BASIC commands (`PRINT`, `LET`, `FOR/NEXT`), then explore PILOT for interactive programs and Logo for turtle graphics.

### For Visual Learners
Try the Logo turtle commands — `FORWARD`, `RIGHT`, `REPEAT` — for immediate graphical feedback.

### For Educators
Use PILOT's `T:`/`A:`/`M:` commands to build interactive quizzes and lessons.

---

## 🚧 Roadmap

- [x] Tab completion for keywords
- [x] Syntax highlighting (Pygments-powered)
- [x] Debugger with breakpoints and error history
- [x] 21 example programs across all heritages
- [x] Canvas export (PNG and SVG)
- [x] Command palette, split editor, code folding
- [ ] Export programs to standalone executables
- [ ] Web-based version

---

**Time Warp II** — *One IDE, one language, three heritages.* 🕰️

© 2025–2026 Honey Badger Universe | Educational Software
