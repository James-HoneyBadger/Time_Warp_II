# TempleCode Language Reference

Complete reference for the **TempleCode** programming language — a fusion of BASIC, PILOT, and Logo designed for educational programming.

**File Extension:** `.tc`
**Executor:** `TempleCodeExecutor` in `core/languages/templecode.py`

---

## Table of Contents

1. [Overview](#overview)
2. [BASIC Commands](#basic-commands)
3. [PILOT Commands](#pilot-commands)
4. [Logo Turtle Graphics](#logo-turtle-graphics)
5. [Variables & Data Types](#variables--data-types)
6. [Operators](#operators)
7. [String Functions](#string-functions)
8. [Math Functions](#math-functions)
9. [Control Flow](#control-flow)
10. [Procedures](#procedures)
11. [Mixing Styles](#mixing-styles)

---

## Overview

TempleCode is a unified language that blends three classic educational languages into one cohesive environment:

| Heritage | Era | What it contributes |
|----------|-----|---------------------|
| **BASIC** | 1964 | Variables, arithmetic, control flow, I/O, line numbers |
| **PILOT** | 1968 | Interactive text output, input, pattern matching, labels |
| **Logo** | 1967 | Turtle graphics, visual drawing, procedures |

All three styles can be **freely mixed** in a single `.tc` program. The interpreter auto-detects which sub-system handles each line.

---

## BASIC Commands

### PRINT
Output text or expressions to the console.
```basic
PRINT "Hello, World!"
PRINT 2 + 3
PRINT "Name: "; name
```

### LET
Assign a value to a variable.
```basic
LET x = 10
LET name = "Alice"
LET result = x * 2 + 5
```

### INPUT
Read user input into a variable.
```basic
INPUT "Enter your name: "; name
INPUT x
```

### IF / THEN / ELSE
Conditional execution.
```basic
IF x > 10 THEN PRINT "Big"
IF x > 10 THEN
    PRINT "Big"
ELSE
    PRINT "Small"
END IF
```

### FOR / NEXT
Counted loop.
```basic
FOR i = 1 TO 10
    PRINT i
NEXT i

FOR j = 10 TO 1 STEP -1
    PRINT j
NEXT j
```

### GOTO
Jump to a line number.
```basic
10 PRINT "Hello"
20 GOTO 10
```

### GOSUB / RETURN
Call and return from a subroutine.
```basic
100 GOSUB 500
110 END

500 PRINT "In subroutine"
510 RETURN
```

### DIM
Declare an array.
```basic
DIM numbers(10)
LET numbers(1) = 42
```

### REM
Comment (remark). Ignored by the interpreter.
```basic
REM This is a comment
' This is also a comment
```

### END
Terminate program execution.
```basic
END
```

### RANDOMIZE / RND
Generate random numbers.
```basic
RANDOMIZE TIMER
LET x = INT(RND * 100) + 1
```

### Line Numbers (Optional)
Lines may optionally be numbered. Numbered and unnumbered lines can be mixed.
```basic
10 PRINT "Line ten"
20 PRINT "Line twenty"
PRINT "No line number needed"
```

---

## PILOT Commands

PILOT commands use a single letter followed by a colon. They are ideal for interactive lessons and quizzes.

### T: — Type (Output)
Display text.
```pilot
T:Hello, welcome to the quiz!
T:The answer was *answer*
```
Variables are interpolated with `*varname*` syntax.

### A: — Accept (Input)
Read user input (stored in the `answer` system variable).
```pilot
A:
A:Enter your name
```

### M: — Match
Match the most recent input against a pattern.
```pilot
M:Paris
M:yes,yeah,yep
```
Sets the match flag used by `Y:` and `N:`.

### Y: — Yes (Conditional on Match)
Execute only if the last `M:` matched.
```pilot
Y:T:Correct!
Y:J:*next_question
```

### N: — No (Conditional on No Match)
Execute only if the last `M:` did not match.
```pilot
N:T:Sorry, that's wrong.
```

### J: — Jump
Jump to a label.
```pilot
J:*start
```

### C: — Compute
Evaluate an expression and store the result.
```pilot
C:score = score + 1
```

### E: — End
End the program.
```pilot
E:
```

### Labels
Labels are defined with `*name` on their own line.
```pilot
*start
T:Welcome!
J:*start
```

---

## Logo Turtle Graphics

Logo commands control a virtual turtle that draws on a canvas.

### Movement

| Command | Alias | Description |
|---------|-------|-------------|
| `FORWARD n` | `FD n` | Move forward n pixels |
| `BACK n` | `BK n` | Move backward n pixels |
| `LEFT n` | `LT n` | Turn left n degrees |
| `RIGHT n` | `RT n` | Turn right n degrees |
| `HOME` | | Return turtle to center, heading up |

### Pen Control

| Command | Alias | Description |
|---------|-------|-------------|
| `PENUP` | `PU` | Lift pen (stop drawing) |
| `PENDOWN` | `PD` | Lower pen (start drawing) |
| `SETCOLOR color` | `SETPC` | Set pen color (e.g., `red`, `blue`, `green`) |
| `SETPENSIZE n` | | Set pen width in pixels |

### Drawing

| Command | Description |
|---------|-------------|
| `CIRCLE n` | Draw a circle with radius n |
| `CLEARSCREEN` / `CS` | Clear the canvas |

### REPEAT
Repeat a block of commands.
```logo
REPEAT 4 [FORWARD 100 RIGHT 90]
REPEAT 36 [FORWARD 10 RIGHT 10]
```

### TO / END — Procedures
Define reusable procedures.
```logo
TO SQUARE :size
    REPEAT 4 [FORWARD :size RIGHT 90]
END

SQUARE 100
```

### Nested REPEAT
```logo
REPEAT 8 [REPEAT 4 [FORWARD 50 RIGHT 90] RIGHT 45]
```

---

## Variables & Data Types

### Numeric Variables
```basic
LET x = 42
LET pi = 3.14159
```

### String Variables
```basic
LET name = "Alice"
LET greeting = "Hello, " + name
```

### Arrays
```basic
DIM scores(5)
LET scores(1) = 100
LET scores(2) = 95
```

### System Variables (PILOT)
- `answer` — last input from `A:`
- `matched` — matched portion from `M:`
- `status` — match flag (1 = matched, 0 = not)

---

## Operators

### Arithmetic
| Operator | Description |
|----------|-------------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `MOD` | Modulo (remainder) |
| `^` | Exponentiation |

### Comparison
| Operator | Description |
|----------|-------------|
| `=` | Equal to |
| `<>` | Not equal to |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

### String
| Operator | Description |
|----------|-------------|
| `+` | Concatenation |

---

## String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `LEN(s)` | Length of string | `LEN("Hello")` → 5 |
| `LEFT(s, n)` | First n characters | `LEFT("Hello", 3)` → `"Hel"` |
| `RIGHT(s, n)` | Last n characters | `RIGHT("Hello", 3)` → `"llo"` |
| `MID(s, pos, n)` | Substring | `MID("Hello", 2, 3)` → `"ell"` |
| `UPPER(s)` | Uppercase | `UPPER("hello")` → `"HELLO"` |
| `LOWER(s)` | Lowercase | `LOWER("HELLO")` → `"hello"` |
| `INSTR(s, sub)` | Find substring position | `INSTR("Hello", "ll")` → 3 |
| `STR$(n)` | Number to string | `STR$(42)` → `"42"` |
| `VAL(s)` | String to number | `VAL("42")` → 42 |

---

## Math Functions

| Function | Description |
|----------|-------------|
| `ABS(x)` | Absolute value |
| `INT(x)` | Integer part (floor) |
| `SQR(x)` / `SQRT(x)` | Square root |
| `SIN(x)` | Sine (radians) |
| `COS(x)` | Cosine (radians) |
| `TAN(x)` | Tangent (radians) |
| `ATN(x)` | Arctangent |
| `LOG(x)` | Natural logarithm |
| `EXP(x)` | e^x |
| `RND` | Random number 0–1 |

---

## Control Flow

### IF / THEN (single-line)
```basic
IF x > 0 THEN PRINT "Positive"
```

### IF / THEN / ELSE (block)
```basic
IF x > 0 THEN
    PRINT "Positive"
ELSE
    PRINT "Non-positive"
END IF
```

### FOR / NEXT
```basic
FOR i = 1 TO 10
    PRINT i
NEXT i
```

### WHILE / WEND
```basic
LET i = 1
WHILE i <= 10
    PRINT i
    LET i = i + 1
WEND
```

### GOTO
```basic
10 PRINT "Loop!"
20 GOTO 10
```

### GOSUB / RETURN
```basic
GOSUB MySub
END

MySub:
    PRINT "In subroutine"
    RETURN
```

### REPEAT (Logo)
```logo
REPEAT 4 [FORWARD 100 RIGHT 90]
```

### PILOT Conditional (Y: / N:)
```pilot
M:yes
Y:T:You said yes!
N:T:You didn't say yes.
```

---

## Procedures

### Logo Procedures
```logo
TO TRIANGLE :size
    REPEAT 3 [FORWARD :size RIGHT 120]
END

TRIANGLE 80
```

### BASIC Subroutines
```basic
GOSUB DrawBox
END

DrawBox:
    REPEAT 4 [FORWARD 50 RIGHT 90]
    RETURN
```

---

## Mixing Styles

TempleCode's power comes from mixing BASIC, PILOT, and Logo in a single program:

```
10 REM A mixed TempleCode program
20 PRINT "Welcome to TempleCode!"
T:This line uses PILOT output.
A:What is your name?
T:Hello, *answer*!
30 PRINT "Let me draw a square for you."
REPEAT 4 [FORWARD 80 RIGHT 90]
40 PRINT "Done!"
50 END
```

### Rules
- Lines starting with a digit are parsed as BASIC (with line numbers)
- Lines with a letter + colon (e.g., `T:`, `A:`, `M:`) are PILOT commands
- Logo keywords (`FORWARD`, `REPEAT`, `TO`, etc.) trigger the turtle graphics system
- `REM`, `'`, and `;` start comments in any context

---

## Example Programs

See the `examples/templecode/` directory:

| File | Description |
|------|-------------|
| `hello.tc` | Hello World demo mixing all three styles |
| `spiral.tc` | Colorful spiral with Logo turtle graphics |
| `quiz.tc` | Geography quiz using PILOT interaction |
| `guess.tc` | Number guessing game in BASIC |
| `mandelbrot.tc` | Turtle art patterns with nested REPEAT |

---

**TempleCode** — *One language, three heritages.*
