# TempleCode IDE - Code Examples

This directory contains example programs for the **TempleCode** language, demonstrating BASIC, PILOT, and Logo features — all in `.tc` files.

---

## Directory Structure

```
examples/
├── README.md                      # This file
└── templecode/
    ├── hello.tc                   # Hello World — mixes BASIC, PILOT, and Logo
    ├── spiral.tc                  # Colorful spiral with Logo turtle graphics
    ├── quiz.tc                    # Geography quiz using PILOT interaction
    ├── guess.tc                   # Number guessing game in BASIC
    └── mandelbrot.tc              # Turtle art patterns with nested REPEAT
```

---

## Example Programs

### 1. hello.tc — Hello World

Demonstrates all three TempleCode heritages in one program:
- **BASIC** `PRINT` statements with line numbers
- **PILOT** `T:` text output
- **Logo** `FORWARD` / `RIGHT` turtle drawing

```
10 PRINT "Welcome to TempleCode!"
T:This line uses PILOT-style output.
FORWARD 80
RIGHT 90
FORWARD 80
```

**What you'll see:** Text output plus a turtle-drawn shape on the canvas.

---

### 2. spiral.tc — Colorful Spiral

Uses Logo turtle graphics to draw a colorful spiral pattern.

```
SETCOLOR red
FOR I = 1 TO 36
    FORWARD I * 3
    RIGHT 91
NEXT I
```

**What you'll see:** A spiral drawn on the turtle graphics canvas.

---

### 3. quiz.tc — Geography Quiz

An interactive quiz built entirely with PILOT commands (`T:`, `A:`, `M:`, `Y:`, `N:`).

```
T:What is the capital of France?
A:
M:Paris
Y:T:Correct!
N:T:Sorry, the answer is Paris.
```

**What you'll see:** A text-based interactive quiz — type your answers when prompted.

---

### 4. guess.tc — Number Guessing Game

A classic guessing game written in BASIC style with line numbers, `INPUT`, `IF/THEN`, and `GOTO`.

```
30 LET SECRET = INT(RND * 100) + 1
110 INPUT GUESS
130 IF GUESS = SECRET THEN GOTO 200
140 IF GUESS < SECRET THEN PRINT "Too low!"
150 IF GUESS > SECRET THEN PRINT "Too high!"
160 GOTO 100
200 PRINT "Correct!"
```

**What you'll see:** An interactive game — enter guesses until you find the secret number.

---

### 5. mandelbrot.tc — Turtle Art Patterns

Complex geometric patterns using nested Logo `REPEAT` blocks with multiple colors.

```
SETCOLOR blue
REPEAT 8 [REPEAT 4 [FORWARD 50 RIGHT 90] RIGHT 45]
SETCOLOR red
REPEAT 6 [REPEAT 3 [FORWARD 60 RIGHT 120] RIGHT 60]
SETCOLOR green
REPEAT 36 [FORWARD 80 RIGHT 170]
```

**What you'll see:** Layered geometric art on the turtle graphics canvas.

---

## How to Run Examples

### From the IDE

1. **Launch TempleCode IDE:**
   ```bash
   python3 run.py
   ```

2. **Open an example:**
   - **File → Open File...** → navigate to `examples/templecode/`
   - Or **Program → Load Example** and select a `.tc` file

3. **Run the program:**
   Press **F5** or click **Program → Run Program**

4. **View results:**
   - Text output appears in the output panel
   - Turtle graphics appear on the canvas

### From the Command Line

```bash
cd /path/to/TempleCode
python3 TempleCode.py
# Then open a .tc file from the File menu
```

---

## Learning Path

### Start Here
1. **hello.tc** — See how BASIC, PILOT, and Logo mix together
2. **spiral.tc** — Explore Logo turtle graphics
3. **quiz.tc** — Learn PILOT's interactive commands

### Go Deeper
4. **guess.tc** — Practice BASIC control flow (`IF/THEN`, `GOTO`, `INPUT`)
5. **mandelbrot.tc** — Master nested `REPEAT` and multi-color drawing

---

## TempleCode Language Quick Reference

| Heritage | Key Commands |
|----------|-------------|
| **BASIC** | `PRINT`, `LET`, `IF/THEN`, `FOR/NEXT`, `GOTO`, `GOSUB/RETURN`, `INPUT`, `DIM`, `END` |
| **PILOT** | `T:` (type), `A:` (accept), `M:` (match), `Y:` / `N:` (conditional), `J:` (jump), `E:` (end) |
| **Logo** | `FORWARD`/`FD`, `BACK`/`BK`, `LEFT`/`LT`, `RIGHT`/`RT`, `PENUP`/`PU`, `PENDOWN`/`PD`, `REPEAT [...]`, `SETCOLOR`, `TO ... END` |

For the full language reference, see [docs/languages/TEMPLECODE_REFERENCE.md](../docs/languages/TEMPLECODE_REFERENCE.md).

---

**Happy coding with TempleCode!** 🚀

© 2025 Honey Badger Universe | Example Programs
