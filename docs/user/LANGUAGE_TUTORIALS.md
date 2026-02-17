# TempleCode Language Tutorial

Learn the **TempleCode** language — a fusion of BASIC, PILOT, and Logo. This tutorial covers all three heritages and shows how to mix them in a single `.tc` program.

## Table of Contents

1. [Introduction](#introduction)
2. [BASIC Commands](#basic-commands)
3. [PILOT Commands](#pilot-commands)
4. [Logo Turtle Graphics](#logo-turtle-graphics)
5. [Mixing Styles](#mixing-styles)
6. [Practice Exercises](#practice-exercises)
7. [Next Steps](#next-steps)

---

## Introduction

TempleCode combines three classic educational languages:

| Heritage | What you get |
|----------|-------------|
| **BASIC** (1964) | Variables, arithmetic, loops, conditionals, I/O, subroutines |
| **PILOT** (1968) | Interactive text output, user input, pattern matching, labels |
| **Logo** (1967) | Turtle graphics — drawing with movement and pen commands |

All three styles work together in a single `.tc` file. The interpreter auto-detects which sub-system handles each line.

### Your First Program

```
PRINT "Hello from BASIC!"
T:Hello from PILOT!
FORWARD 100
```

This program uses all three heritages: BASIC `PRINT`, PILOT `T:`, and Logo `FORWARD`.

---

## BASIC Commands

BASIC gives TempleCode its core programming capabilities: variables, math, control flow, and text I/O.

### PRINT — Output Text

```basic
PRINT "Hello, World!"
PRINT 2 + 3
PRINT "Name: "; name
```

### LET — Assign Variables

```basic
LET x = 10
LET name = "Alice"
LET result = x * 2 + 5
```

### INPUT — Read User Input

```basic
INPUT "Enter your name: "; name
PRINT "Hello, "; name
```

### Arithmetic

```basic
LET x = 10
LET y = 3

PRINT x + y    REM Addition
PRINT x - y    REM Subtraction
PRINT x * y    REM Multiplication
PRINT x / y    REM Division
PRINT x MOD y  REM Modulo (remainder)
PRINT x ^ 2    REM Power
```

### String Operations

```basic
LET msg = "Hello"
PRINT LEN(msg)        REM Length: 5
PRINT UPPER(msg)      REM HELLO
PRINT LOWER(msg)      REM hello
PRINT LEFT(msg, 3)    REM Hel
PRINT MID(msg, 2, 3)  REM ell
```

### IF / THEN / ELSE

```basic
LET age = 20

IF age >= 18 THEN
    PRINT "Adult"
ELSE
    PRINT "Minor"
END IF
```

Single-line form:
```basic
IF age >= 18 THEN PRINT "Adult"
```

### FOR / NEXT Loops

```basic
REM Count from 1 to 5
FOR i = 1 TO 5
    PRINT i
NEXT i

REM Count down
FOR j = 10 TO 1 STEP -1
    PRINT j
NEXT j
```

### GOTO — Jump to a Line

```basic
10 PRINT "Hello"
20 GOTO 10
```

### GOSUB / RETURN — Subroutines

```basic
GOSUB Greet
PRINT "Back in main"
END

Greet:
    PRINT "Hello from subroutine!"
    RETURN
```

### Arrays

```basic
DIM scores(5)
LET scores(1) = 100
LET scores(2) = 95
LET scores(3) = 87
PRINT scores(1)
```

### REM — Comments

```basic
REM This is a comment
' This is also a comment
```

### Line Numbers (Optional)

Lines can optionally be numbered. Numbered and unnumbered lines can be mixed:

```basic
10 PRINT "Line ten"
PRINT "No number needed"
20 PRINT "Line twenty"
```

### Practice: Factorial Calculator

```basic
INPUT "Enter a number: "; n
LET result = 1
FOR i = 1 TO n
    LET result = result * i
NEXT i
PRINT "Factorial: "; result
END
```

### Practice: Guessing Game

```basic
RANDOMIZE TIMER
LET secret = INT(RND * 100) + 1
LET guess = 0

WHILE guess <> secret
    INPUT "Guess (1-100): "; guess
    IF guess > secret THEN PRINT "Too high!"
    IF guess < secret THEN PRINT "Too low!"
WEND

PRINT "Correct!"
END
```

---

## PILOT Commands

PILOT gives TempleCode interactive text commands — perfect for quizzes, tutorials, and lessons.

### T: — Type (Output Text)

```pilot
T:Hello, welcome to the quiz!
T:Your score is *score*
```

Variables are interpolated with `*varname*` syntax.

### A: — Accept (Read Input)

```pilot
T:What is your name?
A:
T:Hello, *answer*!
```

`A:` stores the user's response in the `answer` system variable.

### M: — Match (Pattern Matching)

```pilot
T:What is the capital of France?
A:
M:Paris
Y:T:Correct! Paris is right.
N:T:Sorry, the answer is Paris.
```

`M:` checks if the last input matches the pattern. Multiple patterns can be separated by commas:
```pilot
M:yes,yeah,yep
```

### Y: and N: — Conditional Execution

`Y:` runs only if the last `M:` matched. `N:` runs only if it didn't match.

```pilot
M:yes
Y:T:You said yes!
N:T:You didn't say yes.
```

These can prefix any PILOT command:
```pilot
Y:J:*next_question
N:T:Try again!
```

### J: — Jump to Label

```pilot
J:*start
```

### Labels

Labels are defined with `*name`:

```pilot
*start
T:Welcome!
T:Type 'quit' to exit.
A:
M:quit
Y:E:
N:J:*start
```

### C: — Compute

```pilot
C:score = score + 1
C:total = 10 * 5
```

### E: — End

```pilot
E:
```

### Practice: Simple Quiz

```pilot
T:=== Science Quiz ===
T:
T:What planet is closest to the sun?
A:
M:Mercury
Y:T:Correct!
N:T:Sorry, it's Mercury.
T:
T:What gas do plants breathe in?
A:
M:carbon dioxide,CO2
Y:T:Correct!
N:T:It's carbon dioxide (CO2).
T:
T:Thanks for playing!
E:
```

---

## Logo Turtle Graphics

Logo gives TempleCode visual drawing capabilities through a virtual turtle that moves on a canvas.

### Movement Commands

```logo
FORWARD 100    REM Move forward 100 pixels (or FD 100)
BACK 50        REM Move backward 50 pixels (or BK 50)
RIGHT 90       REM Turn right 90 degrees (or RT 90)
LEFT 45        REM Turn left 45 degrees (or LT 45)
HOME           REM Return to center, facing up
```

### Pen Control

```logo
PENUP          REM Stop drawing (or PU)
PENDOWN        REM Start drawing (or PD)
SETCOLOR red   REM Change pen color
SETPENSIZE 3   REM Change pen width
```

### Drawing a Square

```logo
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
```

### REPEAT — Repeat Commands

Much easier with `REPEAT`:

```logo
REPEAT 4 [FORWARD 100 RIGHT 90]
```

Draw a triangle:
```logo
REPEAT 3 [FORWARD 100 RIGHT 120]
```

Draw a circle approximation:
```logo
REPEAT 36 [FORWARD 10 RIGHT 10]
```

### Nested REPEAT

```logo
REPEAT 8 [REPEAT 4 [FORWARD 50 RIGHT 90] RIGHT 45]
```

This draws 8 squares, each rotated 45 degrees — creating a pinwheel pattern.

### SETCOLOR — Colors

```logo
SETCOLOR red
REPEAT 4 [FORWARD 80 RIGHT 90]
SETCOLOR blue
REPEAT 3 [FORWARD 80 RIGHT 120]
```

### TO / END — Define Procedures

Create reusable drawing procedures:

```logo
TO SQUARE :size
    REPEAT 4 [FORWARD :size RIGHT 90]
END

SQUARE 100
SQUARE 50
```

Parameters use `:name` syntax.

### Practice: Colorful Star

```logo
SETCOLOR red
REPEAT 5 [FORWARD 100 RIGHT 144]
```

### Practice: Spiral

```logo
SETCOLOR blue
FOR I = 1 TO 50
    FORWARD I * 2
    RIGHT 91
NEXT I
```

(Note how BASIC `FOR/NEXT` and Logo `FORWARD`/`RIGHT` work together!)

### Practice: Flower

```logo
SETCOLOR red
REPEAT 36 [
    REPEAT 4 [FORWARD 30 RIGHT 90]
    RIGHT 10
]
```

---

## Mixing Styles

TempleCode's real power is mixing BASIC, PILOT, and Logo in one program.

### Example: Interactive Drawing

```
10 PRINT "=== Interactive Drawing ==="
T:I'll draw shapes based on your choice.
T:Type 'square' or 'triangle':
A:
M:square
Y:REPEAT 4 [FORWARD 80 RIGHT 90]
Y:T:Drew a square!
M:triangle
Y:REPEAT 3 [FORWARD 80 RIGHT 120]
Y:T:Drew a triangle!
N:T:I don't know that shape.
20 END
```

### Example: Quiz with Graphics Reward

```
T:What is 7 * 8?
A:
M:56
Y:T:Correct! Here's a star:
Y:SETCOLOR gold
Y:REPEAT 5 [FORWARD 60 RIGHT 144]
N:T:Sorry, 7 * 8 = 56.
E:
```

### Example: BASIC Loop with Turtle

```
10 PRINT "Drawing a spiral..."
20 FOR I = 1 TO 36
30     FORWARD I * 3
40     RIGHT 91
50 NEXT I
60 PRINT "Done!"
70 END
```

### Rules for Mixing

| Line pattern | Handled by |
|-------------|-----------|
| Starts with a digit | BASIC (numbered line) |
| `Letter:` (e.g., `T:`, `A:`, `M:`) | PILOT |
| Logo keyword first (`FORWARD`, `REPEAT`, `TO`, etc.) | Logo |
| `REM`, `'`, `;` | Comment |
| Anything else | BASIC (unnumbered) |

---

## Practice Exercises

### Exercise 1: Greeting Program
Write a program that asks for the user's name (PILOT `A:`) and draws a square for them (Logo).

### Exercise 2: Math Quiz  
Create a 3-question math quiz using PILOT (`T:`, `A:`, `M:`, `Y:`, `N:`). Keep score with `C:`.

### Exercise 3: Shape Artist
Use BASIC `FOR/NEXT` with Logo turtle commands to draw a series of shapes in different colors.

### Exercise 4: Number Guesser
Write a BASIC-style guessing game with `INPUT`, `IF/THEN`, and `GOTO`.

### Exercise 5: Geometric Art
Create complex patterns using nested `REPEAT` and multiple `SETCOLOR` commands.

---

## Next Steps

- **Language Reference:** [../languages/TEMPLECODE_REFERENCE.md](../languages/TEMPLECODE_REFERENCE.md) — Complete command reference
- **Example Programs:** [../../examples/README.md](../../examples/README.md) — Run the built-in examples
- **Troubleshooting:** [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md) — Common issues

---

**Happy coding with TempleCode!** 🚀
