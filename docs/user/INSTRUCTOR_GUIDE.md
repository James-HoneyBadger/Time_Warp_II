# Instructor Guide — Teaching with Time Warp II

A guide for teachers, tutors, and workshop leaders using Time Warp II and the TempleCode language in educational settings.

## Table of Contents

1. [Why Time Warp II?](#why-time-warp-ii)
2. [Setting Up a Classroom](#setting-up-a-classroom)
3. [Curriculum Integration](#curriculum-integration)
4. [Lesson Plans](#lesson-plans)
5. [Example Progression](#example-progression)
6. [Assessment Strategies](#assessment-strategies)
7. [Common Student Difficulties](#common-student-difficulties)
8. [Accessibility Features](#accessibility-features)
9. [Tips & Best Practices](#tips--best-practices)

---

## Why Time Warp II?

### Pedagogical Advantages

Time Warp II is designed for teaching programming fundamentals. The TempleCode language combines three historically important educational languages:

| Heritage | Year | Educational Strength |
|----------|------|---------------------|
| **BASIC** | 1964 | Variables, logic, loops — core programming concepts |
| **PILOT** | 1968 | Interactive dialogue — students see input/output immediately |
| **Logo** | 1967 | Turtle graphics — visual, tangible results from code |

### What Makes It Effective

- **Instant feedback** — every line produces visible output or drawing
- **No setup complexity** — single executable, no compiler, no project configuration
- **Visual results** — turtle graphics engage visual learners
- **Readable syntax** — English keywords (`PRINT`, `FORWARD`, `IF/THEN`)
- **Three on-ramps** — students can start with whichever style resonates (text output, Q&A interaction, or drawing)
- **Built-in examples** — 21 ready-to-run programs in Program → Load Example

---

## Setting Up a Classroom

### Installation

1. Ensure Python 3.10 or later is installed on each machine
2. Copy the `Time_Warp_II` folder to each workstation (or a shared network drive)
3. Run the setup script once:

```bash
cd Time_Warp_II
./run.sh          # Linux/macOS
run.bat           # Windows
```

This automatically installs dependencies (`pygame-ce`, `pygments`, `Pillow`) into a virtual environment.

### Recommended Setup

- **Font size:** Large (14pt) or Extra Large (16pt) for projection/screen sharing
- **Theme:** High Contrast or Light for well-lit classrooms; Dark for dimmed rooms
- **Speed controls:** Set execution delay to 50–100ms so students can follow program flow

All settings persist per-user in `~/.templecode_settings.json`.

### Network/Lab Considerations

- No internet connection required after initial setup
- The IDE is fully offline — no cloud accounts or telemetry
- Each student gets independent settings (stored in their home directory)
- File saves use standard OS file dialogs

---

## Curriculum Integration

### Age Groups & Levels

| Level | Age Range | Focus Areas | Recommended Heritage |
|-------|-----------|-------------|---------------------|
| **Beginner** | 8–11 | Drawing, colours, simple patterns | Logo turtle graphics |
| **Elementary** | 11–13 | Variables, input/output, basic logic | BASIC + Logo |
| **Intermediate** | 13–15 | Loops, conditionals, functions, data | All three heritages |
| **Advanced** | 15–18 | Algorithms, procedures, project work | Full TempleCode |

### Alignment with CS Standards

TempleCode naturally covers these computing curriculum areas:

- **Sequencing** — programs run top to bottom
- **Selection** — `IF/THEN/ELSE`, PILOT `Y:/N:` conditionals
- **Iteration** — `FOR/NEXT`, `WHILE/WEND`, `REPEAT []`
- **Variables** — `LET`, `MAKE`, `A:`
- **Input/Output** — `PRINT`/`INPUT`, `T:`/`A:`, turtle drawing
- **Procedures** — `GOSUB/RETURN`, Logo `TO...END`
- **Decomposition** — breaking problems into subroutines
- **Debugging** — built-in debug mode and error history

---

## Lesson Plans

### Lesson 1: Hello World (30 minutes)

**Objective:** Write and run a first program; understand the IDE layout.

**Activities:**

1. **Demo (5 min):** Open the IDE, point out the three panels (editor, output, canvas). Load and run the "Hello World" example.

2. **Guided practice (10 min):**
   ```
   PRINT "Hello, World!"
   PRINT "My name is "; "Alice"
   PRINT 2 + 3
   ```
   Students type, press F5, observe output.

3. **Exploration (10 min):**
   - Change the message text
   - Try `PRINT` with numbers and arithmetic
   - Try PILOT style: `T:Hello from PILOT!`

4. **Wrap-up (5 min):** Save the file, discuss what happened.

**Assessment:** Can the student write a `PRINT` statement and run it?

---

### Lesson 2: Turtle Graphics (45 minutes)

**Objective:** Draw shapes using Logo turtle commands.

**Activities:**

1. **Demo (5 min):** Run the "Turtle Graphics Spiral" example. Explain `FORWARD`, `RIGHT`, `LEFT`.

2. **Guided practice (15 min):**
   ```
   REM Draw a square
   FORWARD 100
   RIGHT 90
   FORWARD 100
   RIGHT 90
   FORWARD 100
   RIGHT 90
   FORWARD 100
   ```

3. **Challenge (15 min):**
   - Draw a triangle (hint: `RIGHT 120`)
   - Draw a hexagon (hint: `RIGHT 60`)
   - Experiment with `SETCOLOR "red"` and `SETPENSIZE 3`

4. **Extension (10 min):** Introduce `REPEAT`:
   ```
   REPEAT 4 [FORWARD 100 RIGHT 90]
   ```
   Ask: "How would you draw a circle?" → `REPEAT 360 [FORWARD 1 RIGHT 1]`

**Assessment:** Can the student draw a named shape using turtle commands?

---

### Lesson 3: Variables & Input (45 minutes)

**Objective:** Use variables to store and manipulate data; take user input.

**Activities:**

1. **Guided practice (15 min):**
   ```
   LET name = "Student"
   INPUT "What is your name? "; name
   PRINT "Hello, "; name; "!"
   INPUT "How old are you? "; age
   PRINT "Next year you will be "; age + 1
   ```

2. **PILOT alternative (10 min):**
   ```
   T:What is your favourite colour?
   A:
   T:Interesting! You said *$answer*
   ```

3. **Challenge (15 min):** Build a "Mad Libs" style story:
   ```
   INPUT "Enter an animal: "; animal
   INPUT "Enter a colour: "; colour
   INPUT "Enter a number: "; num
   PRINT "Once upon a time, a "; colour; " "; animal
   PRINT "jumped over "; num; " fences!"
   ```

4. **Wrap-up (5 min):** Discuss what variables are and why they're useful.

---

### Lesson 4: Conditionals (45 minutes)

**Objective:** Make programs that make decisions.

**Activities:**

1. **Demo (5 min):** Load the "Number Guessing Game" example.

2. **Guided practice (15 min):**
   ```
   INPUT "Enter your age: "; age
   IF age >= 18 THEN
       PRINT "You can vote!"
   ELSE
       PRINT "You can vote in "; 18 - age; " years."
   ENDIF
   ```

3. **PILOT pattern matching (10 min):**
   ```
   T:Do you like pizza? (yes or no)
   A:
   M:yes,yeah,yep
   Y:T:Me too! Pizza is great!
   N:T:Really? Most people love pizza!
   ```

4. **Challenge (15 min):** Build a simple quiz with scoring:
   ```
   LET score = 0
   INPUT "Capital of France? "; ans
   IF ans = "Paris" THEN
       PRINT "Correct!"
       LET score = score + 1
   ELSE
       PRINT "Sorry, it's Paris."
   ENDIF
   PRINT "Score: "; score; " out of 1"
   ```

---

### Lesson 5: Loops (45 minutes)

**Objective:** Repeat actions using loops.

**Activities:**

1. **FOR loops (15 min):**
   ```
   FOR i = 1 TO 10
       PRINT i; " x 7 = "; i * 7
   NEXT i
   ```

2. **WHILE loops (10 min):**
   ```
   LET guess = 0
   LET secret = 7
   WHILE guess <> secret
       INPUT "Guess the number (1-10): "; guess
   WEND
   PRINT "You got it!"
   ```

3. **REPEAT with turtle (10 min):**
   ```
   REPEAT 36 [
       FORWARD 50
       RIGHT 170
   ]
   ```

4. **Challenge (10 min):** Combine loops with conditionals — FizzBuzz.

---

### Lesson 6: Procedures & Functions (45 minutes)

**Objective:** Organise code into reusable blocks.

**Activities:**

1. **Logo procedures (20 min):**
   ```
   TO SQUARE :size
       REPEAT 4 [FORWARD :size RIGHT 90]
   END

   SQUARE 50
   RIGHT 45
   SQUARE 100
   ```

2. **BASIC subroutines (15 min):**
   ```
   GOSUB draw_border
   PRINT "Hello!"
   GOSUB draw_border
   END

   *draw_border
   PRINT "===================="
   RETURN
   ```

3. **Challenge (10 min):** Create a procedure that draws a house (square + triangle roof).

---

### Lesson 7: Capstone Project (90 minutes)

**Objective:** Combine all skills in a self-directed project.

**Suggested projects:**
- Interactive quiz with scoring (PILOT + BASIC)
- Turtle art gallery (Logo procedures)
- Text adventure game (BASIC conditionals + GOSUB)
- Animated drawing with speed controls (Logo + DELAY)
- Calculator program (BASIC + INPUT)

Students choose a project, plan, code, test, and present.

---

## Example Progression

A recommended order for introducing the built-in examples:

| Week | Example | Concepts Introduced |
|------|---------|--------------------|
| 1 | Hello World | PRINT, running programs |
| 1 | Turtle Graphics Spiral | FORWARD, RIGHT, REPEAT |
| 2 | Shapes Gallery | Multiple shapes, SETCOLOR |
| 2 | Quiz (PILOT style) | T:, A:, M:, Y:, N: |
| 3 | FizzBuzz | FOR loop, IF/THEN, MOD |
| 3 | Temperature Converter | INPUT, arithmetic, LET |
| 4 | Number Guessing Game | WHILE loop, RND, conditionals |
| 4 | Times Tables Trainer | Nested logic, scoring |
| 5 | Flower Garden | Logo procedures (TO...END) |
| 5 | Science Quiz | Multi-question PILOT quiz |
| 6 | Snowflake Fractal | Recursive procedures |
| 6 | Adventure Story | Complex branching, GOSUB |
| 7 | Kaleidoscope | Advanced turtle art |
| 7 | Mandelbrot (Turtle Art) | Mathematics + drawing |

---

## Assessment Strategies

### Formative Assessment

- **Predict-Run-Investigate:** Show code on screen, ask students to predict output before running
- **Fix the Bug:** Provide programs with intentional errors; students debug
- **Extend It:** Give a working program, ask students to add a feature
- **Code Reading:** Students explain what a program does line by line

### Summative Assessment

- **Portfolio:** Collect 5–8 programs demonstrating progression
- **Project:** Capstone program demonstrating multiple concepts
- **Practical Exam:** Solve a coding task in a set time
- **Peer Review:** Students review and improve each other's code

### Rubric Criteria

| Criterion | Beginner | Proficient | Advanced |
|-----------|----------|------------|---------|
| Output | Uses PRINT correctly | Uses PRINT with variables | Formatted, multi-line output |
| Variables | Creates variables | Uses in expressions | Multiple types, string ops |
| Control flow | Simple IF | Nested IF, loops | Loops with conditions, SELECT |
| Turtle graphics | Basic shapes | Colours, sizes, patterns | Procedures, complex art |
| Code quality | Runs without errors | Uses REM comments | Well-structured, reusable |

---

## Common Student Difficulties

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| "Nothing happens" | Forgot to press F5 | Remind: Run button or F5 |
| Syntax error on IF | Missing THEN or ENDIF | Show the IF/THEN/ENDIF pattern |
| Turtle doesn't draw | PEN is up | Check for PENUP without PENDOWN |
| Variable is empty | Typo in variable name | Variables are case-insensitive but check spelling |
| PILOT doesn't match | M: patterns are case-sensitive | Explain M: matching rules |
| Loop runs forever | WHILE condition never becomes false | Use debug mode + speed slider |
| "Untitled ●" in status bar | File not saved | Teach Ctrl+S habit |
| Numbers treated as strings | INPUT returns strings | Use VAL() to convert |
| Canvas is blank | Canvas was cleared/resized | Use CLEARSCREEN at program start |

### Using Debug Mode

Teach students to use **Debug → Enable Debug Mode** when programs behave unexpectedly. The verbose output shows each line as it executes, making it easier to find logic errors.

The **execution speed slider** (0–500ms) is also invaluable — set it to 100ms and watch the program flow step by step.

---

## Accessibility Features

Time Warp II includes several features that support diverse learners:

- **High Contrast theme** — pure black background with bright text for low-vision users
- **7 font sizes** — from 8pt up to 22pt (also adjustable via Ctrl+Scroll)
- **19 monospace font families** — choose the most readable font for each student
- **Split editor** — view two parts of code simultaneously
- **Keyboard-driven** — all features accessible via keyboard shortcuts
- **Command palette** (Ctrl+Shift+P) — search for any command by name
- **Auto Dark/Light** — follows OS accessibility settings
- **Colour-coded output** — errors, warnings, and success are visually distinct

---

## Tips & Best Practices

### For the Classroom

1. **Start with Logo** — visual output is immediately engaging
2. **Use the speed sliders** — slow execution helps students follow program flow
3. **Project on screen** — use Large or Extra Large font size
4. **Load examples together** — use Program → Load Example as class demos
5. **Save frequently** — teach Ctrl+S as a habit from day one
6. **Use the canvas export** — students can save their turtle art as PNG/SVG

### For Workshop Leaders

1. **Pre-install** on all machines before the session
2. **Prepare a USB drive** with the Time_Warp_II folder for offline install
3. **Start with "Hello World"** → "Square" → "Quiz" as a three-step intro
4. **Give handouts** with the keyboard shortcuts table
5. **End with free exploration** — let participants try different examples

### Differentiation

- **Struggling students:** Start with the Hello World and Turtle Spiral examples; focus on modifying existing programs
- **Confident students:** Jump to the Capstone projects; explore procedures and fractals
- **Advanced students:** Challenge them to create their own example programs; look at the Technical Reference for architecture understanding

---

## Resources

- **[Student Tutorial](STUDENT_TUTORIAL.md)** — hand this to students for self-paced learning
- **[User Guide](USER_GUIDE.md)** — comprehensive IDE features reference
- **[Language Tutorials](LANGUAGE_TUTORIALS.md)** — step-by-step TempleCode lessons
- **[TempleCode Reference](../languages/TEMPLECODE_REFERENCE.md)** — complete command reference
- **[Examples](../../examples/README.md)** — all 21 built-in example programs

---

*Time Warp II — Instructor Guide*
*Copyright © 2025–2026 Honey Badger Universe*
