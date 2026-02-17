# Student Tutorial — Learn to Code with Time Warp II

Welcome! This tutorial will teach you programming from scratch using Time Warp II and the TempleCode language. No experience needed — just follow along step by step.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Your First Program](#your-first-program)
3. [Drawing with the Turtle](#drawing-with-the-turtle)
4. [Variables — Remembering Things](#variables--remembering-things)
5. [Asking Questions](#asking-questions)
6. [Making Decisions](#making-decisions)
7. [Repeating Things — Loops](#repeating-things--loops)
8. [Colours and Creativity](#colours-and-creativity)
9. [Building Your Own Commands](#building-your-own-commands)
10. [Putting It All Together](#putting-it-all-together)
11. [Challenge Projects](#challenge-projects)
12. [Quick Reference Card](#quick-reference-card)

---

## Getting Started

### Opening Time Warp II

Your teacher will show you how to start the program. Once it's open, you'll see three areas:

- **Left panel** — this is where you type your code
- **Middle panel** — this shows text output from your program
- **Right panel** — this is the drawing canvas for turtle graphics

### How to Run Your Code

1. Type your code in the left panel
2. Press **F5** (or click the **▶ Run** button)
3. Watch the result appear!

### How to Stop a Program

Press **Escape** or click the **■ Stop** button.

### How to Save Your Work

Press **Ctrl+S** to save. Give your file a name ending in `.tc` (for TempleCode).

---

## Your First Program

Type this in the editor:

```
PRINT "Hello, World!"
```

Press **F5**. You should see:

```
Hello, World!
```

Congratulations — you just wrote your first program!

### Try These

```
PRINT "My name is Alex"
PRINT 2 + 3
PRINT 10 * 5
PRINT "I am "; 12; " years old"
```

Each `PRINT` line shows something in the output panel.

### What's Happening?

- `PRINT` tells the computer to display something
- Text in `"quotes"` is shown exactly as written
- Numbers and maths are calculated first, then shown
- Use `;` to join pieces together on one line

### PILOT Style

There's another way to print text — PILOT style:

```
T:Hello from PILOT!
T:This is another way to show text.
```

`T:` means "Type" — it prints whatever comes after the colon.

---

## Drawing with the Turtle

Imagine a tiny turtle sitting in the middle of the canvas holding a pen. You tell it where to go, and it draws a line as it moves!

### Basic Movement

```
FORWARD 100
```

This moves the turtle forward 100 steps, drawing a line. Try it!

Now try turning:

```
FORWARD 100
RIGHT 90
FORWARD 100
```

The turtle moves forward, turns right 90 degrees, then moves forward again. You've drawn a corner!

### Draw a Square

```
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
```

### Movement Commands

| Command | What it does |
|---------|-------------|
| `FORWARD 100` | Move forward 100 steps |
| `BACK 50` | Move backward 50 steps |
| `RIGHT 90` | Turn right 90 degrees |
| `LEFT 90` | Turn left 90 degrees |
| `HOME` | Go back to the centre |
| `CLEARSCREEN` | Erase all drawings and go home |

### Short Names

You can use short names to save typing:

| Long | Short |
|------|-------|
| `FORWARD` | `FD` |
| `BACK` | `BK` |
| `RIGHT` | `RT` |
| `LEFT` | `LT` |
| `CLEARSCREEN` | `CS` |

So `FD 100` does the same as `FORWARD 100`.

### Try These Shapes

**Triangle:**
```
FD 100
RT 120
FD 100
RT 120
FD 100
```

**Pentagon (5 sides):**
```
FD 80
RT 72
FD 80
RT 72
FD 80
RT 72
FD 80
RT 72
FD 80
```

**Experiment:** What happens if you change the angle? Try `RT 60` for a hexagon!

---

## Variables — Remembering Things

A **variable** is like a labelled box that holds a value. You can put things in and take them out.

### Creating Variables

```
LET name = "Alice"
LET age = 12
LET score = 0
```

### Using Variables

```
LET name = "Alice"
LET age = 12
PRINT "Hello, "; name
PRINT "You are "; age; " years old"
PRINT "Next year you'll be "; age + 1
```

### Changing Variables

```
LET score = 0
PRINT "Score: "; score
LET score = score + 10
PRINT "Score: "; score
LET score = score + 5
PRINT "Score: "; score
```

Output:
```
Score: 0
Score: 10
Score: 15
```

### Maths with Variables

| Operation | Symbol | Example |
|-----------|--------|---------|
| Add | `+` | `LET x = 5 + 3` |
| Subtract | `-` | `LET x = 10 - 4` |
| Multiply | `*` | `LET x = 6 * 7` |
| Divide | `/` | `LET x = 20 / 4` |
| Remainder | `MOD` | `LET x = 10 MOD 3` → 1 |
| Power | `^` | `LET x = 2 ^ 3` → 8 |

---

## Asking Questions

### BASIC Style — INPUT

```
INPUT "What is your name? "; name
PRINT "Hello, "; name; "!"

INPUT "Pick a number: "; num
PRINT num; " times 2 is "; num * 2
```

When the program reaches `INPUT`, it pauses and waits for you to type something in the input bar at the bottom of the output panel. Type your answer and press **Enter**.

### PILOT Style — A: and T:

```
T:What is your favourite animal?
A:
T:Cool! You said *$answer*
```

- `A:` waits for your answer and remembers it as `$answer`
- `*$answer*` inside `T:` gets replaced with what you typed

### Try It: Mad Libs!

```
INPUT "Enter an animal: "; animal
INPUT "Enter a colour: "; colour
INPUT "Enter a number: "; num
PRINT ""
PRINT "Once upon a time, a "; colour; " "; animal
PRINT "ate "; num; " pancakes for breakfast!"
```

---

## Making Decisions

Programs can make choices! The `IF` command checks a condition and does different things.

### Simple IF

```
INPUT "How old are you? "; age

IF age >= 13 THEN
    PRINT "You're a teenager!"
ENDIF
```

### IF / ELSE

```
INPUT "How old are you? "; age

IF age >= 18 THEN
    PRINT "You can vote!"
ELSE
    PRINT "You can vote in "; 18 - age; " years."
ENDIF
```

### Multiple Choices with ELSEIF

```
INPUT "Enter your score (0-100): "; score

IF score >= 90 THEN
    PRINT "Grade: A - Excellent!"
ELSEIF score >= 80 THEN
    PRINT "Grade: B - Great job!"
ELSEIF score >= 70 THEN
    PRINT "Grade: C - Good"
ELSEIF score >= 60 THEN
    PRINT "Grade: D - Keep trying"
ELSE
    PRINT "Grade: F - Study more!"
ENDIF
```

### Comparison Operators

| Symbol | Meaning |
|--------|---------|
| `=` | equals |
| `<>` | not equals |
| `<` | less than |
| `>` | greater than |
| `<=` | less than or equal |
| `>=` | greater than or equal |

### PILOT Pattern Matching

PILOT has its own way of checking answers:

```
T:What is the capital of France?
A:
M:Paris,paris
Y:T:Correct! Well done!
N:T:Sorry, the answer is Paris.
```

- `M:` checks if the answer matches any of the patterns (separated by commas)
- `Y:` runs only if it matched
- `N:` runs only if it didn't match

---

## Repeating Things — Loops

### FOR Loop — Count from A to B

```
FOR i = 1 TO 5
    PRINT "Line number "; i
NEXT i
```

Output:
```
Line number 1
Line number 2
Line number 3
Line number 4
Line number 5
```

### Times Tables

```
INPUT "Which times table? "; n

FOR i = 1 TO 12
    PRINT n; " x "; i; " = "; n * i
NEXT i
```

### Counting by Steps

```
FOR i = 0 TO 100 STEP 10
    PRINT i
NEXT i
```

This counts: 0, 10, 20, 30, ... 100.

### WHILE Loop — Repeat Until a Condition

```
LET secret = 7
LET guess = 0

WHILE guess <> secret
    INPUT "Guess the number (1-10): "; guess
WEND

PRINT "You got it!"
```

### REPEAT for Turtle Graphics

```
REPEAT 4 [FD 100 RT 90]
```

This draws a square! The commands inside `[ ]` repeat 4 times.

More examples:

```
REM Circle
REPEAT 360 [FD 1 RT 1]

REM Star
REPEAT 5 [FD 100 RT 144]

REM Spiral
REPEAT 50 [FD i * 2 RT 91]
```

### Nested Loops

Put a loop inside another loop:

```
REPEAT 36 [
    REPEAT 4 [FD 50 RT 90]
    RT 10
]
```

This draws 36 squares, each rotated 10 degrees — making a beautiful pattern!

---

## Colours and Creativity

### Setting Colours

```
SETCOLOR "red"
FD 100
SETCOLOR "blue"
FD 100
SETCOLOR "green"
FD 100
```

### Available Colours

`"red"`, `"blue"`, `"green"`, `"yellow"`, `"orange"`, `"purple"`, `"pink"`, `"white"`, `"black"`, `"cyan"`, `"magenta"`, and many more.

### Pen Size

```
SETPENSIZE 1
FD 50
SETPENSIZE 5
FD 50
SETPENSIZE 10
FD 50
```

### Pen Up and Down

```
FD 50
PENUP           REM Stop drawing
FD 50           REM Move without drawing
PENDOWN         REM Start drawing again
FD 50
```

Short names: `PU` for PENUP, `PD` for PENDOWN.

### Drawing Shapes Directly

```
CIRCLE 50           REM Circle with radius 50
SQUARE 80           REM Square with side 80
TRIANGLE 60         REM Triangle with side 60
RECT 100 50         REM Rectangle 100 wide, 50 tall
STAR 40             REM Five-pointed star
POLYGON 6 50        REM Hexagon with radius 50
```

### Adding Text to Your Drawing

```
LABEL "Hello!"
```

This prints text at the turtle's current position.

### Rainbow Art

```
SETPENSIZE 3
SETCOLOR "red"
FD 50 RT 60
SETCOLOR "orange"
FD 50 RT 60
SETCOLOR "yellow"
FD 50 RT 60
SETCOLOR "green"
FD 50 RT 60
SETCOLOR "blue"
FD 50 RT 60
SETCOLOR "purple"
FD 50 RT 60
```

---

## Building Your Own Commands

### Logo Procedures

You can create your own commands with `TO` and `END`:

```
TO SQUARE
    REPEAT 4 [FD 50 RT 90]
END

REM Now use your new command:
SQUARE
RT 45
SQUARE
```

### Procedures with Parameters

Use `:name` for parameters:

```
TO SQUARE :size
    REPEAT 4 [FD :size RT 90]
END

SQUARE 30
PENUP
FD 60
PENDOWN
SQUARE 80
```

### Building Complex Shapes

```
TO TRIANGLE :size
    REPEAT 3 [FD :size RT 120]
END

TO HOUSE :size
    SQUARE :size
    FD :size
    RT 30
    TRIANGLE :size
END

HOUSE 80
```

### BASIC Subroutines

```
GOSUB greeting
PRINT ""
GOSUB greeting
END

*greeting
PRINT "========================"
PRINT "  Welcome to my program!"
PRINT "========================"
RETURN
```

- `GOSUB greeting` jumps to the label `*greeting`
- `RETURN` jumps back to where you were

---

## Putting It All Together

TempleCode lets you mix all three styles! Here's a program that uses BASIC, PILOT, and Logo together:

```
REM === My Interactive Art Program ===

T:Welcome to the Shape Drawer!
T:What shape would you like?
T:(square, triangle, or circle)
A:

M:square
Y:GOSUB draw_square
M:triangle
Y:GOSUB draw_triangle
M:circle
Y:GOSUB draw_circle
N:T:I don't know that shape. Drawing a square instead.
N:GOSUB draw_square

INPUT "What colour? "; col
SETCOLOR col

T:Enjoy your artwork!
END

*draw_square
REPEAT 4 [FD 80 RT 90]
RETURN

*draw_triangle
REPEAT 3 [FD 80 RT 120]
RETURN

*draw_circle
REPEAT 360 [FD 1 RT 1]
RETURN
```

---

## Challenge Projects

Ready to build something on your own? Try these challenges:

### Challenge 1: Personalised Greeting Card
Write a program that asks for someone's name, age, and favourite colour, then draws a birthday card on the canvas with a message in the output.

**Skills:** INPUT, PRINT, SETCOLOR, LABEL, turtle drawing

### Challenge 2: Maths Quiz
Create a 5-question maths quiz. Keep score and print the final result.

**Skills:** Variables, INPUT, IF/THEN, FOR loop

### Challenge 3: Turtle Art Gallery
Use procedures to create at least 4 different shapes, then arrange them into a picture.

**Skills:** TO/END, REPEAT, SETCOLOR, PENUP/PENDOWN

### Challenge 4: Number Guessing Game
The computer picks a random number 1–100. The player guesses, and the program says "too high" or "too low" until they get it right.

**Skills:** RND, WHILE loop, IF/THEN/ELSE, INPUT

```
LET secret = INT(RND * 100) + 1
LET guess = 0
LET tries = 0

WHILE guess <> secret
    INPUT "Your guess (1-100): "; guess
    LET tries = tries + 1
    IF guess < secret THEN
        PRINT "Too low!"
    ELSEIF guess > secret THEN
        PRINT "Too high!"
    ELSE
        PRINT "Correct! You got it in "; tries; " tries!"
    ENDIF
WEND
```

### Challenge 5: Interactive Drawing Tool
Build a program that asks the user what to draw, how big, and what colour — then draws it. Use PILOT for the questions and Logo for the drawing.

**Skills:** T:, A:, M:, Y:, N:, FORWARD, REPEAT, SETCOLOR

### Challenge 6: Fractal Explorer
Draw a Koch snowflake or a Sierpinski triangle using recursive procedures.

**Skills:** TO/END with parameters, nested REPEAT

---

## Quick Reference Card

### Output

| Command | Example |
|---------|---------|
| `PRINT` | `PRINT "Hello"` |
| `T:` | `T:Hello from PILOT` |

### Input

| Command | Example |
|---------|---------|
| `INPUT` | `INPUT "Name? "; name` |
| `A:` | `A:` → stored in `$answer` |

### Variables

| Command | Example |
|---------|---------|
| `LET` | `LET x = 10` |
| `MAKE` | `MAKE "x 10` (Logo style) |

### Decisions

| Command | Example |
|---------|---------|
| `IF / THEN / ENDIF` | `IF x > 5 THEN ... ENDIF` |
| `IF / ELSE / ENDIF` | `IF x > 5 THEN ... ELSE ... ENDIF` |
| `M:` / `Y:` / `N:` | Pattern matching (PILOT) |

### Loops

| Command | Example |
|---------|---------|
| `FOR / NEXT` | `FOR i = 1 TO 10 ... NEXT i` |
| `WHILE / WEND` | `WHILE x < 10 ... WEND` |
| `REPEAT` | `REPEAT 4 [FD 50 RT 90]` |

### Turtle Movement

| Command | Short | Example |
|---------|-------|---------|
| `FORWARD` | `FD` | `FD 100` |
| `BACK` | `BK` | `BK 50` |
| `RIGHT` | `RT` | `RT 90` |
| `LEFT` | `LT` | `LT 45` |
| `HOME` | — | `HOME` |
| `CLEARSCREEN` | `CS` | `CS` |

### Turtle Drawing

| Command | Example |
|---------|---------|
| `SETCOLOR` | `SETCOLOR "red"` |
| `SETPENSIZE` | `SETPENSIZE 3` |
| `PENUP` / `PU` | `PU` |
| `PENDOWN` / `PD` | `PD` |
| `CIRCLE` | `CIRCLE 50` |
| `SQUARE` | `SQUARE 80` |
| `LABEL` | `LABEL "Hi!"` |

### Procedures

```
TO MYSHAPE :size
    REPEAT 4 [FD :size RT 90]
END

MYSHAPE 100
```

### Keyboard Shortcuts

| Keys | What it does |
|------|-------------|
| **F5** | Run your program |
| **Escape** | Stop your program |
| **Ctrl+S** | Save your file |
| **Ctrl+Z** | Undo (take back last change) |
| **Ctrl+N** | New file |
| **Ctrl+O** | Open a file |
| **Tab** | Auto-complete a keyword |

---

## What's Next?

- **Try the built-in examples:** Go to **Program → Load Example** and try each one
- **Read the full language reference:** [TempleCode Reference](../languages/TEMPLECODE_REFERENCE.md)
- **Explore advanced features:** [Language Tutorials](LANGUAGE_TUTORIALS.md)
- **Learn about the IDE:** [User Guide](USER_GUIDE.md)

Happy coding!

---

*Time Warp II — Student Tutorial*
*Copyright © 2025–2026 Honey Badger Universe*
