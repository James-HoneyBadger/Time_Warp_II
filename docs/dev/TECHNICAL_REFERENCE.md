# Technical Reference - TempleCode Architecture

Complete technical documentation for developers extending TempleCode IDE.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Structure](#module-structure)
3. [Core Interpreter](#core-interpreter)
4. [TempleCode Executor](#templecode-executor)
5. [GUI System](#gui-system)
6. [Data Flow](#data-flow)
7. [Extension Points](#extension-points)
8. [Performance Optimization](#performance-optimization)

---

## Architecture Overview

### High-Level Design

TempleCode IDE uses a **single-language interpreter architecture** where:
- A central interpreter engine (`TempleCodeInterpreter`) manages program execution
- A single executor (`TempleCodeExecutor`) handles the TempleCode language (BASIC + PILOT + Logo fusion)
- A tkinter GUI provides the IDE interface
- Utility modules handle optimization, highlighting, and templates

### Design Philosophy

1. **Unified Language:** One language combining BASIC, PILOT, and Logo traditions
2. **Clean Separation:** UI, interpreter logic, and language execution are separate layers
3. **Simplicity:** Single executor means straightforward code path
4. **Performance:** Built-in optimization and caching mechanisms

### Component Relationships

```
┌─────────────────────────────────────────────┐
│           GUI Frontend (tkinter)            │
├─────────────────────────────────────────────┤
│              IDE Features                    │
│  - Editor  - Output - Buttons - Menu        │
├─────────────────────────────────────────────┤
│     Core Interpreter (interpreter.py)        │
│  TempleCodeInterpreter                       │
│  - Parse code - Route commands - Execute    │
├─────────────────────────────────────────────┤
│     TempleCode Executor (templecode.py)      │
│  TempleCodeExecutor                          │
│  - BASIC commands  - PILOT commands          │
│  - Logo turtle graphics                      │
├─────────────────────────────────────────────┤
│         Support Modules                      │
│  - Syntax Highlighting - Templates - Utils  │
└─────────────────────────────────────────────┘
```

---

## Module Structure

### Directory Organization

```
TempleCode/
├── TempleCode.py              # Main entry point (GUI)
├── core/                     # Core interpreter
│   ├── __init__.py
│   ├── interpreter.py        # TempleCodeInterpreter class
│   ├── features/             # IDE features
│   │   ├── code_templates.py
│   │   └── syntax_highlighting.py
│   ├── languages/            # Language executor
│   │   ├── __init__.py
│   │   └── templecode.py     # TempleCodeExecutor (BASIC + PILOT + Logo)
│   ├── optimizations/        # Performance optimization
│   │   ├── __init__.py
│   │   ├── performance_optimizer.py
│   │   ├── memory_manager.py
│   │   └── gui_optimizer.py
│   └── utilities/
│       └── __init__.py
└── docs/                     # Documentation
```

### Core Module Descriptions

#### interpreter.py
Central interpreter engine.

**Key Classes:**
- `TempleCodeInterpreter` — Main interpreter class
- Handles code execution, line parsing, state management

**Key Methods:**
- `execute()` — Run TempleCode program, return output
- `execute_line()` — Execute a single line/command
- `reset()` — Reset interpreter state for a new program

#### languages/templecode.py
The single language executor for TempleCode.

**Key Class:**
- `TempleCodeExecutor` — Unified executor combining BASIC, PILOT, and Logo

**How it works:**
Each line is routed to the correct sub-system based on syntax:
- Lines starting with a digit → BASIC (line-numbered)
- Lines with `letter:` pattern (e.g., `T:`, `A:`, `M:`) → PILOT
- Lines starting with Logo keywords (`FORWARD`, `REPEAT`, `TO`, etc.) → Logo turtle
- Other lines → BASIC (unnumbered)

**Key Methods:**
- `execute_command(command)` — Route and execute a single command
- `_dispatch_pilot(command)` — Handle PILOT colon-commands
- `_handle_logo_define(command)` — Handle Logo `TO ... END` procedure definitions
- Logo movement/pen methods — `FORWARD`, `BACK`, `LEFT`, `RIGHT`, `PENUP`, `PENDOWN`, etc.

**Internal State:**
```python
class TempleCodeExecutor:
    def __init__(self, interpreter):
        self.interpreter = interpreter

        # BASIC state
        self.arrays = {}
        self.return_stack = []

        # PILOT state
        self.system_vars = {
            "answer": "",
            "matched": "",
            "status": 0,
        }

        # Logo state
        self.logo_procedures = {}  # TO ... END definitions
```

#### features/syntax_highlighting.py
Syntax highlighting for the TempleCode language.

**Key Classes:**
- `SyntaxHighlighter` — Text coloring based on TempleCode syntax
- Highlights BASIC keywords, PILOT commands, Logo keywords, strings, numbers, comments

#### features/code_templates.py
Code templates and snippets for TempleCode.

**Key Functions:**
- `get_template()` — Get a starter template for TempleCode

#### optimizations/performance_optimizer.py
Performance optimization.

**Optimizations:**
- Code caching
- Statement optimization

#### optimizations/memory_manager.py
Memory and resource management.

**Features:**
- Variable scope management
- Memory limit enforcement

#### optimizations/gui_optimizer.py
GUI performance optimization.

**Features:**
- Output buffering
- Refresh rate optimization
- Widget optimization

---

## Core Interpreter

### TempleCodeInterpreter Class Overview

```python
class TempleCodeInterpreter:
    def __init__(self):
        self.executor = TempleCodeExecutor(self)
        self.output = []         # Execution output
        self.variables = {}      # Program variables
        self.program_lines = []  # Parsed program

    def execute(self, code):
        """Execute a TempleCode program"""

    def execute_line(self, line):
        """Execute a single line, routing to executor"""

    def reset(self):
        """Reset state for a new program"""
```

### Execution Flow

1. **Code Input:** User submits `.tc` code
2. **Parsing:** Split into lines, identify line numbers if present
3. **Routing:** Each line routed to BASIC, PILOT, or Logo sub-system
4. **Execution:** `TempleCodeExecutor.execute_command()` runs each line
5. **Output Processing:** Format and display results
6. **Error Handling:** Catch and display exceptions with line context

### Line Routing Strategy

The executor determines which sub-system handles each line:

| Pattern | Sub-system | Example |
|---------|-----------|---------|
| Starts with digit | BASIC (numbered) | `10 PRINT "Hello"` |
| `X:` (letter + colon) | PILOT | `T:Hello!`, `A:`, `M:yes` |
| Logo keyword first | Logo turtle | `FORWARD 100`, `REPEAT 4 [...]` |
| `TO procname` | Logo procedure def | `TO SQUARE :size` |
| `REM`, `'`, `;` | Comment | `REM this is a comment` |
| Other | BASIC (unnumbered) | `PRINT "Hello"`, `LET x = 5` |

### Error Handling

- **Syntax Errors:** Invalid syntax, caught during parsing
- **Runtime Errors:** Execution errors, caught during execution
- **System Errors:** OS-level errors, wrapped with context

All errors display:
- Error message
- Line number (if available)
- Suggestion for fix (where applicable)

---

## TempleCode Executor

### Sub-system Details

#### BASIC Sub-system
Handles structured programming commands:
- `PRINT`, `LET`, `INPUT`, `IF/THEN/ELSE`, `FOR/NEXT`
- `GOTO`, `GOSUB/RETURN`, `DIM`, `END`
- Math functions: `ABS`, `INT`, `SQR`, `SIN`, `COS`, `RND`, etc.
- String functions: `LEN`, `LEFT`, `RIGHT`, `MID`, `UPPER`, `LOWER`, etc.

#### PILOT Sub-system
Handles interactive/educational commands:
- `T:` — Type text (output), with `*var*` interpolation
- `A:` — Accept input from user
- `M:` — Match input against patterns
- `Y:` / `N:` — Conditional execution based on last match
- `J:` — Jump to a `*label`
- `C:` — Compute (evaluate expression)
- `E:` — End program

#### Logo Sub-system
Handles turtle graphics:
- Movement: `FORWARD`/`FD`, `BACK`/`BK`, `LEFT`/`LT`, `RIGHT`/`RT`, `HOME`
- Pen: `PENUP`/`PU`, `PENDOWN`/`PD`, `SETCOLOR`, `SETPENSIZE`
- Drawing: `CIRCLE`, `CLEARSCREEN`/`CS`
- Control: `REPEAT [...]`
- Procedures: `TO procname ... END`

---

## GUI System

### Main Window Structure

```
TempleCode.py
├── Root Window (tk.Tk)
├── Menu Bar
│   ├── File Menu
│   ├── Edit Menu
│   ├── Program Menu
│   ├── Debug Menu
│   ├── Test Menu
│   ├── Preferences Menu
│   └── About Menu
├── Editor (Text Widget)
│   ├── Text content (.tc code)
│   └── Line numbers
├── Output Area (Frame)
│   ├── Output Text
│   ├── Error Display
│   └── Clear Button
├── Turtle Graphics Canvas
└── Status Bar
    └── Line/Column indicator
```

### Key GUI Components

#### Editor Widget
- Text input with line numbers
- Syntax highlighting for TempleCode
- Find & Replace
- Keyboard shortcuts

#### Output Widget
- Scrollable text display
- Automatic scrolling
- Clear button
- Error highlighting

#### Turtle Graphics Canvas
- Renders Logo turtle drawing commands
- Shows turtle position and heading
- Supports colors and pen sizes

### GUI Event Handlers

- **Execute Button / F5:** Runs current `.tc` code
- **Clear Button:** Clears output
- **File Operations:** Open, save, new `.tc` files
- **Edit Operations:** Undo, redo, cut, copy, paste

### Customization

Users can customize:
- Font (size, family)
- Colors (9 themes)
- Window layout
- Keyboard shortcuts

---

## Data Flow

### Execution Pipeline

```
User Input Code (.tc)
    ↓
[GUI] Text Widget
    ↓
Execute (F5 / Run button)
    ↓
[Core] TempleCodeInterpreter.execute()
    ↓
Parse lines
    ↓
For each line:
    ↓
[Core] TempleCodeExecutor.execute_command()
    ↓
Route to BASIC / PILOT / Logo sub-system
    ↓
Execute command
    ↓
Capture output / turtle drawing
    ↓
[GUI] Output Widget + Canvas
    ↓
Display result
```

### Variable Scope

```
Program Scope
├── BASIC variables (LET)
├── PILOT system vars (answer, matched, status)
├── Arrays (DIM)
└── Logo procedures (TO ... END)
```

### Output Capture

Output is generated by:
1. **BASIC `PRINT`:** Direct text output
2. **PILOT `T:`:** Text output with variable interpolation
3. **Logo turtle:** Visual output on graphics canvas
4. **Error messages:** Displayed in output panel

---

## Extension Points

### Adding IDE Features

1. Add feature module to `core/features/`
2. Integrate in GUI (`TempleCode.py`)
3. Add menu items/buttons
4. Implement event handlers

### Adding New TempleCode Commands

To add new commands to TempleCode:

1. **Edit `core/languages/templecode.py`**
2. Add routing logic in `execute_command()`
3. Implement the command handler method
4. Update syntax highlighting in `core/features/syntax_highlighting.py`

### Adding Optimizations

1. Create module in `core/optimizations/`
2. Integrate in interpreter initialization
3. Hook into execution pipeline
4. Benchmark improvements

---

## Performance Optimization

### Built-in Optimizations

#### 1. Code Caching
```python
# Interpreter caches parsed programs
self.code_cache = {}
```

#### 2. Memory Management
- Track variable memory usage
- Cleanup unused variables
- Limit memory per execution

#### 3. GUI Optimization
- Output buffering
- Refresh rate limiting
- Lazy rendering

### Performance Monitoring

Track:
- Execution time
- Memory usage
- Output size
- Cache hits

### Profiling

Identify bottlenecks:
```python
import cProfile
cProfile.run('interpreter.execute(code)')
```

---

## Development Workflow

### Setting Up Development Environment

1. **Clone repository:**
```bash
git clone <repo>
cd TempleCode
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run tests:**
```bash
python scripts/run_tests.py
```

4. **Start development:**
```bash
python TempleCode.py
```

### Testing

- **Unit tests:** Test interpreter and executor components
- **Integration tests:** Test full program execution
- **GUI tests:** Verify UI functionality

### Code Standards

- Python 3.9+ compatibility
- Type hints where practical
- Docstring documentation
- PEP 8 style guide
- Meaningful variable names

### Contribution Process

1. Create feature branch
2. Implement changes with tests
3. Run full test suite
4. Submit pull request
5. Code review
6. Merge to main

---

**For questions, see:** [../../README.md](../../README.md)
