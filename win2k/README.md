# Time Warp II -- Retro Edition

**A TempleCode IDE for Windows 2000 and other retro systems.**

> *Experimental side-project — a novelty for genuine old-school use.*

---

## What Is This?

Time Warp II -- Retro Edition is a self-contained, stripped-down build of the
Time Warp II TempleCode IDE, back-ported to **Python 2.7** so it can run on
operating systems as old as **Windows 2000**.

TempleCode is a multi-heritage programming language that blends:

- **BASIC** — line numbers, PRINT, FOR/NEXT, IF/THEN, INPUT …
- **PILOT** — T: (type), A: (accept), M: (match), Y:/N: (conditional) …
- **Logo** — FORWARD, RIGHT, PENUP, SETCOLOR, REPEAT […], TO/END …

All three heritages can be mixed freely in a single `.tc` file.

---

## Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| **OS** | Windows 2000 SP4 or later | Also works on XP, Vista, 7, 8, 10, 11 |
| **Python** | 2.7.1 – 2.7.8 | 2.7.9+ requires Windows XP |
| **Tkinter** | Ships with Python 2.7 | No extra install needed |

### Installing Python 2.7.8

1. Download the MSI installer:
   **<https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi>**

2. Run the installer.  On the "Customize" page, enable **"Add python.exe to
   Path"** (it is off by default).

3. Verify the install — open a Command Prompt and type:
   ```
   python --version
   ```
   You should see `Python 2.7.8`.

---

## Quick Start

1. Copy the entire `win2k/` folder to your Windows 2000 machine
   (floppy, ZIP on CD, USB stick, network share, etc.).

2. Double-click **`run.bat`**  
   — or —  
   open a Command Prompt in the folder and type:
   ```
   python TimeWarpII.pyw
   ```

3. The IDE opens. Type code in the left panel and press **F5** to run.

You can also run the install check first:
```
install.bat
```
This will verify Python and Tkinter are available.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **F5** | Run program |
| **F6** | Stop program |
| **Ctrl+N** | New file |
| **Ctrl+O** | Open file |
| **Ctrl+S** | Save file |
| **Enter** (in input bar) | Submit input |

---

## Supported Language Features

### BASIC Commands

```
PRINT expression ; expression ...
LET variable = expression
INPUT "prompt"; variable
IF condition THEN statement [ELSE statement]
IF condition THEN / ELSE / END IF       (multi-line)
FOR var = start TO end [STEP s] / NEXT var
WHILE condition / WEND
DO [WHILE|UNTIL cond] / LOOP [WHILE|UNTIL cond]
GOTO line_number_or_label
GOSUB line_number_or_label / RETURN
DIM array(size)
DATA value, value, ... / READ var / RESTORE
RANDOMIZE [TIMER]
SELECT CASE expression / CASE value / CASE ELSE / END SELECT
SWAP var1, var2
INCR var [, amount]  /  DECR var [, amount]
DELAY milliseconds  /  SLEEP seconds
CLS
REM comment
END
```

#### Built-in Functions

| Math | String |
|------|--------|
| `ABS(x)`, `INT(x)`, `SQR(x)` | `LEN(s)`, `LEFT$(s,n)`, `RIGHT$(s,n)` |
| `SIN(x)`, `COS(x)`, `TAN(x)` | `MID$(s,start,len)`, `INSTR(s,sub)` |
| `LOG(x)`, `EXP(x)`, `RND` | `UCASE$(s)`, `LCASE$(s)`, `TRIM$(s)` |
| `ROUND(x,n)`, `SGN(x)`, `PI` | `CHR$(n)`, `ASC(s)`, `STR$(n)`, `VAL(s)` |

### PILOT Commands

```
T:text         Type (print) text. Use $VAR for variable substitution.
A:             Accept input into the ANSWER variable.
A:VARNAME      Accept input into a named variable.
M:word1,word2  Match ANSWER against word list.  Sets match flag.
Y:command      Execute only if last match succeeded.
N:command      Execute only if last match failed.
J:*label       Jump to a *label.
C:statement    Compute — execute a BASIC statement.
P:milliseconds Pause.
E:             End program.
R:text         Remark (comment).
L:text         Label (print, same as T:).
```

### Logo Commands

```
FORWARD n / FD n         BACK n / BK n
LEFT n / LT n            RIGHT n / RT n
PENUP / PU               PENDOWN / PD
HOME                     CLEARSCREEN / CS
SETCOLOR color           SETPENSIZE n
SETXY x y                SETHEADING n / SETH n
CIRCLE radius            ARC angle radius
DOT [size]               LABEL text
SQUARE size              TRIANGLE size
POLYGON sides size       STAR points size
RECT width height
REPEAT n [commands]      (nestable)
TO name :param ... / END (define procedures)
HIDETURTLE / HT          SHOWTURTLE / ST
```

### Modern Extensions

```
SUB name(params) / END SUB
FUNCTION name(params) / END FUNCTION
CALL name(args)
RETURN [value]
CONST name = value
FOREACH var IN list_expr
LIST var = [items]      PUSH var, value
POP var                 SORT var
DICT var = {key:val}    SET var, key, value
GET var, key            DELETE var, key
TRY / CATCH var / END TRY
THROW message
TYPEOF(expr)
PRINTF "format", args
MAP result = func, list
FILTER result = func, list
REDUCE result = func, list, init
SPLIT result = string, delimiter
JOIN result = list, delimiter
JSON STRINGIFY var, expr
JSON PARSE var, string
REGEX MATCH var, pattern, string
```

---

## Example Programs

The `examples/` folder contains several ready-to-run programs:

| File | Description |
|------|-------------|
| `hello.tc` | Hello World — all three heritages |
| `spiral.tc` | Colorful spiral with Logo turtle |
| `guess.tc` | Number guessing game (BASIC) |
| `quiz.tc` | Geography quiz (PILOT) |
| `countdown.tc` | Countdown timer (BASIC + PILOT) |
| `shapes.tc` | Shape gallery (Logo) |

Open them from **Examples** in the menu bar.

---

## Known Limitations

- No syntax highlighting in the editor (plain text only).
- The turtle canvas does not resize dynamically.
- `SLEEP`/`DELAY` blocks the interpreter thread; the GUI stays responsive
  but no other TempleCode commands run until the delay finishes.
- File I/O commands (`OPEN`, `CLOSE`, `WRITE#`, `READ#`) are not
  implemented in this edition.
- No debugger or step-through mode.
- Performance may be slower than the modern Python 3 edition.

---

## File Listing

```
win2k/
  README.md           This file
  TimeWarpII.pyw      Main IDE application
  templecode27.py     TempleCode interpreter engine
  run.bat             Windows launcher
  install.bat         Pre-flight install check
  examples/
    hello.tc          Hello World
    spiral.tc         Logo spiral
    guess.tc          Guessing game
    quiz.tc           Geography quiz
    countdown.tc      Countdown timer
    shapes.tc         Shapes gallery
```

---

## License

Same license as the main Time Warp II project.  
Copyright (c) 2025-2026 Honey Badger Universe.
