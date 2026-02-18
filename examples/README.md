# Time Warp II - Code Examples

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
    ├── mandelbrot.tc              # Turtle art patterns with nested REPEAT
    ├── calculator.tc              # Four-function calculator in BASIC
    ├── countdown.tc               # Countdown timer with PILOT and BASIC
    ├── fizzbuzz.tc                # Classic FizzBuzz challenge
    ├── fibonacci.tc               # Fibonacci sequence with visualisation
    ├── timestables.tc             # Times tables trainer with scoring
    ├── temperature.tc             # Temperature converter using PILOT menus
    ├── dice.tc                    # Dice roller game with canvas graphics
    ├── science_quiz.tc            # Science quiz with PILOT and rewards
    ├── adventure.tc               # Branching text adventure story
    ├── interactive_drawing.tc     # User-driven shape drawing
    ├── rainbow.tc                 # Rainbow-coloured spiral
    ├── shapes.tc                  # Gallery of Logo shape commands
    ├── flower.tc                  # Flower garden with Logo procedures
    ├── kaleidoscope.tc            # Geometric kaleidoscope patterns
    ├── snowflake.tc               # Koch snowflake fractal
    ├── clock.tc                   # Analogue clock face drawing
    └── feature_showcase.tc        # Comprehensive feature showcase (795 lines)
```

---

## Example Programs

### Starter Programs

#### 1. hello.tc — Hello World

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

#### 2. spiral.tc — Colorful Spiral

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

#### 3. quiz.tc — Geography Quiz

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

#### 4. guess.tc — Number Guessing Game

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

#### 5. mandelbrot.tc — Turtle Art Patterns

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

### BASIC Programs

#### 6. calculator.tc — Calculator

A four-function calculator in BASIC style with division-by-zero checking and a loop for repeated calculations.

**Concepts:** `INPUT`, `IF/THEN`, `GOTO`, arithmetic, loops.

---

#### 7. fizzbuzz.tc — FizzBuzz

The classic programming challenge: print "Fizz" for multiples of 3, "Buzz" for 5, "FizzBuzz" for both.

**Concepts:** `FOR/NEXT`, `MOD` operator, `IF/THEN`, `GOTO`.

---

#### 8. fibonacci.tc — Fibonacci Sequence

Generates the Fibonacci sequence to a user-specified length, then draws a spiral visualisation on the canvas.

**Concepts:** `FOR/NEXT`, `INPUT`, variable swapping, Logo `FORWARD`/`RIGHT`.

---

### PILOT Programs

#### 9. science_quiz.tc — Science Quiz

A five-question science quiz using full PILOT interaction with score tracking and a visual reward based on performance.

**Concepts:** `T:`, `A:`, `M:`, `Y:`, `N:`, `C:` (compute), turtle graphics rewards.

---

#### 10. temperature.tc — Temperature Converter

A menu-driven temperature converter using PILOT labels and jumps for navigation between Celsius, Fahrenheit, and Kelvin conversions.

**Concepts:** `T:`, `A:`, `M:`, `Y:`, `J:` (jump), `C:` (compute), `*labels`.

---

#### 11. adventure.tc — Adventure Story

A branching interactive fiction game where the player explores a cave system with multiple endings, each illustrated with turtle graphics.

**Concepts:** `T:`, `A:`, `M:`, `Y:`, `N:`, `J:` (jump), `*labels`, Logo drawing.

---

### Mixed Programs

#### 12. countdown.tc — Countdown Timer

A countdown timer that combines PILOT input with BASIC loops and PILOT pause commands.

**Concepts:** `T:`, `A:`, `C:`, `P:` (pause), `WHILE/WEND`.

---

#### 13. timestables.tc — Times Tables Trainer

A randomised multiplication quiz that uses BASIC loops, `INPUT`, and scoring, with a gold star drawn for high scores.

**Concepts:** `FOR/NEXT`, `INPUT`, `RANDOMIZE`, `IF/THEN`, `GOTO`, Logo `STAR`.

---

#### 14. dice.tc — Dice Roller

A dice-rolling game combining BASIC random numbers, PILOT interaction for the game loop, and Logo drawing to display dice on the canvas.

**Concepts:** `RANDOMIZE`, `RND`, `INT()`, `RECT`, `LABEL`, `*labels`, `J:`.

---

#### 15. interactive_drawing.tc — Interactive Drawing

A menu-driven drawing program where the user picks shapes and colours. Demonstrates deep mixing of all three heritages.

**Concepts:** `T:`, `A:`, `M:`, `Y:`, `J:`, `FOR/NEXT`, Logo shapes, `SETCOLOR`.

---

### Turtle Graphics Showcase

#### 16. rainbow.tc — Rainbow Spiral

A colourful spiral that cycles through rainbow colours using `MOD` and `IF/THEN` to select colours on each iteration.

**Concepts:** `FOR/NEXT`, `MOD`, `IF/THEN`, `SETCOLOR`, `FORWARD`, `RIGHT`.

---

#### 17. shapes.tc — Shapes Gallery

A gallery displaying squares, triangles, circles, pentagons, hexagons, and stars at labelled positions. Shows all built-in shape commands.

**Concepts:** `SQUARE`, `TRIANGLE`, `CIRCLE`, `POLYGON`, `STAR`, `LABEL`, `SETXY`.

---

#### 18. flower.tc — Flower Garden

A garden of five flowers drawn using Logo procedures (`TO/END`) with stems and colour variations.

**Concepts:** `TO/END` procedures, `ARC`, `REPEAT`, `SETXY`, `PENUP`/`PENDOWN`, `DOT`.

---

#### 19. kaleidoscope.tc — Kaleidoscope

Multiple layered geometric patterns — rotating squares, triangles, starburst, and orbital circles — creating a kaleidoscope effect.

**Concepts:** Nested `REPEAT`, `HOME`, `PENUP`/`PENDOWN`, `CIRCLE`, `DOT`.

---

#### 20. snowflake.tc — Snowflake Fractal

A Koch snowflake drawn using Logo procedures to approximate fractal geometry.

**Concepts:** `TO/END` procedures, `SETHEADING`, `SETXY`, fractal patterns.

---

#### 21. clock.tc — Clock Face

A detailed analogue clock face with hour markers, minute ticks, and three hands (hour, minute, second) using precise Logo positioning.

**Concepts:** `FOR/NEXT`, `SETHEADING`, `SETXY`, `HOME`, `DOT`, `SETPENSIZE`, `CIRCLE`.

---

### Comprehensive Showcase

#### 22. feature_showcase.tc — Feature Showcase (795 lines)

The largest example program — a fully interactive **Personal Finance Tracker**
that demonstrates the widest possible spectrum of TempleCode features across
all three heritages and every modern extension.

**Features demonstrated:**

| Category | Features Used |
|----------|---------------|
| **BASIC** | `LET`, `PRINT`, `INPUT`, `IF/ELSEIF/ELSE/ENDIF`, `FOR/NEXT`, `WHILE/WEND`, `DO/LOOP`, `SELECT CASE`, `DIM`, `DATA/READ`, `SWAP`, `INCR/DECR`, `RANDOMIZE TIMER`, `GOSUB/RETURN`, `RESTORE` |
| **PILOT** | `T:`, `A:`, `M:`, `Y:`, `N:`, `C:`, `J:`, `P:`, `E:`, `*labels` |
| **Logo** | `FORWARD`, `RIGHT`, `LEFT`, `PENUP/PENDOWN`, `SETCOLOR`, `SETPENSIZE`, `SETXY`, `CIRCLE`, `RECT`, `LABEL`, `HIDETURTLE`, `REPEAT`, `TO/END` procedures |
| **Constants & Types** | `CONST`, `ENUM`, `STRUCT`, `TYPEOF`, `ISNUMBER`, `ISSTRING`, `TOSTR`, `TONUM`, `HEX`, `BIN`, `OCT`, `PI`, `E`, `TAU` |
| **Data Structures** | `LIST`, `PUSH`, `FOREACH/IN`, indexing; `DICT`, `SET`, `GET`, `HASKEY`, `KEYS` |
| **Functions** | `FUNCTION`, `SUB`, `LAMBDA`, `MAP`, `FILTER`, `REDUCE` |
| **Error Handling** | `TRY/CATCH`, `ASSERT`, `THROW` |
| **String Functions** | `LEN`, `LEFT$`, `MID$`, `UCASE$`, `LCASE$`, `TRIM$`, `REPLACE$`, `REPEAT$`, `CHR$`, `ASC`, `SPLIT`, `JOIN`, `FORMAT$`, `CONTAINS` |
| **Math Functions** | `SQR`, `ABS`, `ROUND`, `CLAMP`, `LERP`, `LOG2`, `CEIL`, `FLOOR`, `INT`, `RND` |
| **JSON** | `JSON STRINGIFY`, `JSON PARSE`, roundtrip verification |
| **Regex** | `REGEX MATCH`, fallback on invalid patterns |
| **Formatted Output** | `PRINTF` with positional placeholders |

**Program sections:**
1. Constants, enums & configuration
2. Data structures (structs, lists, dicts)
3. Helper functions & lambdas
4. Subroutines for formatting
5. Sample data via `DATA/READ`
6. Transaction processing with category totals
7. Formatted ledger reporting
8. Statistical analysis with `MAP`/`FILTER`/`REDUCE`
9. Logo bar chart visualisation
10. Interactive PILOT menu with `SELECT CASE` dispatch
11. Add-transaction form with validation (`TRY/CATCH/ASSERT`)
12. Regex-powered transaction search
13. JSON export & roundtrip parsing
14. Type system & function demonstration
15. PILOT interactive finance quiz (`M:`, `Y:`, `N:`)
16. Logo decorative drawing procedures

**What you'll see:** An interactive menu-driven application with text reports,
bar charts on the canvas, a quiz, and data export — all in one program.

---

## How to Run Examples

### From the IDE

1. **Launch Time Warp II:**
   ```bash
   python3 run.py
   ```

2. **Open an example:**
   - **File → Open File...** → navigate to `examples/templecode/`
   - Or **Program → Load Example** and select from the categorised menu

3. **Run the program:**
   Press **F5** or click **Program → Run Program**

4. **View results:**
   - Text output appears in the output panel
   - Turtle graphics appear on the canvas

### From the Command Line

```bash
cd /path/to/Time_Warp_II
python3 TimeWarpII.py
# Then open a .tc file from the File menu
```

---

## Learning Path

### Start Here
1. **hello.tc** — See how BASIC, PILOT, and Logo mix together
2. **spiral.tc** — Explore Logo turtle graphics
3. **quiz.tc** — Learn PILOT's interactive commands

### BASIC Fundamentals
4. **guess.tc** — Variables, `IF/THEN`, `GOTO`, `INPUT`
5. **calculator.tc** — Arithmetic and user interaction
6. **fizzbuzz.tc** — Loops and modulo logic
7. **fibonacci.tc** — Sequences and visualisation

### PILOT Mastery
8. **science_quiz.tc** — Pattern matching and scoring
9. **temperature.tc** — Menu navigation with labels and jumps
10. **adventure.tc** — Branching interactive stories

### Mixing It All Together
11. **countdown.tc** — PILOT input + BASIC loops + pause
12. **timestables.tc** — Random quizzes with turtle rewards
13. **dice.tc** — Randomness + canvas drawing
14. **interactive_drawing.tc** — Full user-driven drawing app

### Turtle Graphics Art
15. **rainbow.tc** — Colour cycling spirals
16. **shapes.tc** — Built-in shape gallery
17. **flower.tc** — Procedures and organic patterns
18. **kaleidoscope.tc** — Layered geometric art
19. **mandelbrot.tc** — Nested repeat patterns
20. **snowflake.tc** — Fractal geometry
21. **clock.tc** — Precise positioning and angles

### Everything Together
22. **feature_showcase.tc** — All features in one comprehensive program

---

## TempleCode Language Quick Reference

| Heritage | Key Commands |
|----------|-------------|
| **BASIC** | `PRINT`, `LET`, `IF/THEN`, `FOR/NEXT`, `WHILE/WEND`, `GOTO`, `GOSUB/RETURN`, `INPUT`, `DIM`, `END` |
| **PILOT** | `T:` (type), `A:` (accept), `M:` (match), `Y:` / `N:` (conditional), `J:` (jump), `C:` (compute), `P:` (pause), `E:` (end) |
| **Logo** | `FORWARD`/`FD`, `BACK`/`BK`, `LEFT`/`LT`, `RIGHT`/`RT`, `PENUP`/`PU`, `PENDOWN`/`PD`, `REPEAT [...]`, `SETCOLOR`, `CIRCLE`, `SQUARE`, `TRIANGLE`, `POLYGON`, `STAR`, `ARC`, `DOT`, `LABEL`, `TO ... END` |

For the full language reference, see [docs/languages/TEMPLECODE_REFERENCE.md](../docs/languages/TEMPLECODE_REFERENCE.md).

---

**Happy coding with TempleCode!** 🚀

© 2025-2026 Honey Badger Universe | Example Programs
