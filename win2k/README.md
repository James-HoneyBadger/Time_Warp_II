# Time Warp II -- Retro Edition  (v2.0.0-win2k)

**A TempleCode IDE for Windows 2000 and other retro systems.**

> *Fully-featured TempleCode IDE back-ported to Python 2.7.*

---

## What Is This?

Time Warp II -- Retro Edition is a self-contained build of the
Time Warp II TempleCode IDE, back-ported to **Python 2.7** so it can run on
operating systems as old as **Windows 2000**.

TempleCode is a multi-heritage programming language that blends:

- **BASIC** — line numbers, PRINT, FOR/NEXT, IF/THEN, INPUT …
- **PILOT** — T: (type), A: (accept), M: (match), G: (graphics), S: (string) …
- **Logo** — FORWARD, RIGHT, PENUP, SETCOLOR, REPEAT […], TO/END …
- **Modern** — STRUCT, LAMBDA, File I/O, REGEX, Prolog predicates …

All four heritages can be mixed freely in a single `.tc` file.

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
| **Ctrl+Z** | Undo |
| **Ctrl+Y** | Redo |
| **Ctrl+A** | Select all |
| **Ctrl+F** | Find |
| **Ctrl+H** | Find and Replace |
| **Ctrl+G** | Go to line |
| **Enter** (in input bar) | Submit input |

---

## Supported Language Features

### BASIC Commands

```
PRINT expression ; expression ...
LET variable = expression
INPUT "prompt"; variable
IF condition THEN statement [ELSE statement]
IF condition THEN / ELSE / ELSEIF / END IF  (multi-line)
FOR var = start TO end [STEP s] / NEXT var
WHILE condition / WEND
DO [WHILE|UNTIL cond] / LOOP [WHILE|UNTIL cond]
GOTO line_number_or_label
GOSUB line_number_or_label / RETURN
ON expr GOTO label1, label2, ...
ON expr GOSUB label1, label2, ...
DIM array(size)
DATA value, value, ... / READ var / RESTORE
RANDOMIZE [TIMER]
SELECT CASE expression / CASE value / CASE ELSE / END SELECT
SWAP var1, var2
INC var [, amount]  /  DEC var [, amount]
DELAY milliseconds  /  SLEEP seconds
PAUSE milliseconds
COLOR foreground [, background]
TAB(n)  /  SPC(n)
WRITE expression             (no newline)
WRITELN expression           (with newline)
READLN variable              (read a line)
LOAD "filename"              (load and run a file)
SAVE "filename"              (save program to file)
CHAIN "filename"             (chain to another program)
PLAYNOTE freq, duration      (play a sound)
BEEP
CLS
HELP [keyword]
INKEY                        (get key from buffer)
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
| `POWER(x,n)`, `FLOOR(x)`, `FIX(x)` | `SPLIT(s,d)`, `JOIN(l,d)` |
| `RANDOM(n)`, `RANDINT(a,b)` | `CONTAINS(s,sub)`, `STARTSWITH(s,p)` |
| `TONUM(s)`, `TOSTR(n)` | `ENDSWITH(s,suf)`, `ISNUMBER(x)` |

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
G:command      Graphics — execute Logo turtle commands.
S:command      String operations (UPPER/LOWER/LENGTH/etc.).
D:name=SIZE    Dimension — create array.
X:filename     Execute another PILOT program.
E:             End program.
R:text         Remark (comment).
L:text         Label (print, same as T:).
```

### Logo Commands

```
FORWARD n / FD n         BACK n / BK n
LEFT n / LT n            RIGHT n / RT n
PENUP / PU               PENDOWN / PD
HOME                     CLEAN  /  CLEARSCREEN / CS
SETCOLOR color           SETPENSIZE n
SETXY x y                SETHEADING n / SETH n
CIRCLE radius            CIRCLEFILL radius
ARC angle radius         FILL / FILLED color [...]
DOT [size]               LABEL text
SQUARE size              TRIANGLE size
POLYGON sides size       STAR points size
RECT width height        RECTFILL width height
PSET x y color           PRESET x y
POINT(x, y)              TOWARDS x y
SCREEN width height      SETBACKGROUND color / SETBG
SETFILLCOLOR color / SETFC
MAKE "var value
REPEAT n [commands]      (nestable)
TO name :param ... / END (define procedures)
HIDETURTLE / HT          SHOWTURTLE / ST
STAMP                    WRAP / WINDOW / FENCE
```

### Modern Extensions

```
SUB name(params) / END SUB
FUNCTION name(params) / END FUNCTION
LAMBDA name(params) = expression         (single-line)
LAMBDA name(params) ... END LAMBDA       (multi-line)
STRUCT name / FIELD name / METHOD name / END STRUCT
NEW instance = StructName
CALL name(args)
RETURN [value]
CONST name = value
VAR name = value
FOREACH var IN list_expr
LIST var = [items]      PUSH var, value
POP var                 SHIFT var       UNSHIFT var, value
SORT var                REVERSE var     SPLICE var, pos, count
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
REGEX REPLACE var, pattern, replace, string
REGEX FIND var, pattern, string
REGEX SPLIT var, pattern, string
```

### File I/O

```
OPEN handle, "filename", "mode"     (mode: r, w, a)
CLOSE handle
READLINE var, handle
WRITELINE handle, text
READFILE var, "filename"
WRITEFILE "filename", text
APPENDFILE "filename", text
FILEEXISTS("filename")
COPYFILE "source", "dest"
DELETEFILE "filename"
```

### Prolog-Style Predicates

```
ASSERTA fact(args)        (add fact at beginning)
ASSERTZ fact(args)        (add fact at end)
RETRACT fact(args)        (remove a fact)
QUERY fact(args)          (query facts)
FACTS                     (list all facts)
```

### Advanced Expressions

```
INKEY$ / INKEY            Timer: TIMER
Date/Time: DATE$, TIME$, NOW
Constants: PI, TAU, INF, TRUE, FALSE
List ops: LENGTH, INDEXOF, SLICE, CONTAINS
String ops: STARTSWITH, ENDSWITH, SPLIT, JOIN
Type checks: ISNUMBER, ISSTRING, TYPE
Conversion: TONUM, TOSTR
Math: POWER, FLOOR, TRUNC, FIX, ROUND
Dict ops: KEYS, VALUES, HASKEY
RANGE(n), RANGE(a,b), RANGE(a,b,step)
EVAL "expression"
PROGRAMINFO
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

## IDE Features

- **Syntax highlighting** — Keywords, strings, comments, numbers, PILOT labels,
  and function names are colour-coded in the editor.
- **Line numbers** — Gutter showing line numbers alongside the code editor.
- **Find & Replace** — Ctrl+F to find, Ctrl+H to find and replace.
- **Go to Line** — Ctrl+G to jump to a specific line number.
- **INKEY$ support** — Keystrokes are buffered when a program is running for
  real-time keyboard input (games, interactive programs).
- **Extended canvas** — Filled circles/rectangles, pixel drawing, background
  colour, canvas resizing.
- **"Did you mean?"** — Misspelled commands show suggestions.
- **Status bar** — Shows cursor position (line/column) and run state.

---

## Known Limitations

- No step-through debugger (single-step mode is not available).
- No multi-tab editing (one file open at a time).
- `SLEEP`/`DELAY` blocks the interpreter thread; the GUI stays responsive
  but no other TempleCode commands run until the delay finishes.
- PLAYNOTE/SOUND outputs the system bell only (no frequency control on Win2K).
- Performance may be slower than the modern Python 3 edition.
- Canvas does not support sprite or image loading.

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
