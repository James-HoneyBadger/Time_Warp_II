# TempleCode Language Reference

Complete reference for the **TempleCode** programming language — a fusion of BASIC, PILOT, and Logo that has grown from educational roots into a practical, modern programming language.

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
10. [Procedures & Functions](#procedures--functions)
11. [Lists (Dynamic Arrays)](#lists-dynamic-arrays)
12. [Dictionaries (Maps)](#dictionaries-maps)
13. [File I/O](#file-io)
14. [Error Handling](#error-handling)
15. [Functional Programming](#functional-programming)
16. [JSON Support](#json-support)
17. [Regular Expressions](#regular-expressions)
18. [Structs & Enums](#structs--enums)
19. [Constants & Type System](#constants--type-system)
20. [Modules (IMPORT)](#modules-import)
21. [Formatted Output](#formatted-output)
22. [Mixing Styles](#mixing-styles)
23. [Example Programs](#example-programs)

---

## Overview

TempleCode is a unified language that blends three classic educational languages and extends them with modern programming features:

| Heritage | Era | What it contributes |
|----------|-----|---------------------|
| **BASIC** | 1964 | Variables, arithmetic, control flow, I/O, line numbers |
| **PILOT** | 1968 | Interactive text output, input, pattern matching, labels |
| **Logo** | 1967 | Turtle graphics, visual drawing, procedures |
| **Modern** | 2025+ | Functions, lists, dicts, file I/O, JSON, regex, error handling |

All styles can be **freely mixed** in a single `.tc` program. The interpreter auto-detects which sub-system handles each line.

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
Conditional execution (single-line and block forms).
```basic
IF x > 10 THEN PRINT "Big"
IF x > 10 THEN
    PRINT "Big"
ELSEIF x > 5 THEN
    PRINT "Medium"
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

### WHILE / WEND
```basic
WHILE x < 100
    LET x = x * 2
WEND
```

### DO / LOOP
```basic
DO WHILE x < 100
    LET x = x + 1
LOOP

DO
    LET x = x + 1
LOOP UNTIL x >= 100
```

### SELECT CASE
```basic
SELECT CASE grade
    CASE "A"
        PRINT "Excellent!"
    CASE "B"
        PRINT "Good"
    CASE ELSE
        PRINT "Keep trying"
END SELECT
```

### GOTO / GOSUB / RETURN
```basic
10 PRINT "Hello"
20 GOTO 10

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

### DATA / READ / RESTORE
Embed data values in the program.
```basic
DATA 10, 20, 30, "Hello"
READ A
READ B
READ C
READ D$
RESTORE
```

### SWAP / INCR / DECR
```basic
SWAP A, B
INCR counter
DECR lives, 2
```

### EXIT
Break out of a loop.
```basic
EXIT FOR
EXIT WHILE
EXIT DO
```

### BREAK
Break out of a FOREACH or other loop.
```basic
FOREACH item IN mylist
    IF item = "stop" THEN BREAK
NEXT item
```

### Other BASIC Commands
| Command | Description |
|---------|-------------|
| `CLS` | Clear the output screen |
| `BEEP` | Emit a system bell |
| `DELAY n` | Pause for n milliseconds |
| `SLEEP n` | Pause for n seconds |
| `TAB n` | Move to column n |
| `SPC n` | Print n spaces |
| `REM` / `'` | Comment |
| `END` | End program execution |
| `STOP` | Stop program execution |
| `RANDOMIZE TIMER` | Seed the random number generator |

---

## PILOT Commands

PILOT commands use a single letter followed by a colon. They are ideal for interactive lessons and quizzes.

| Command | Description |
|---------|-------------|
| `T:text` | Type / print text (with `$VAR` interpolation) |
| `A:` / `A:prompt` | Accept user input |
| `M:pattern` | Match input against pattern(s) |
| `Y:command` | Execute if last match succeeded |
| `N:command` | Execute if last match failed |
| `J:label` | Jump to label |
| `C:expr` / `C:*label` | Compute expression or call subroutine |
| `E:` | End program/subroutine |
| `R:text` | Remark (comment) |
| `U:var=expr` | Use / set variable |
| `L:label` | Label definition |
| `G:command` | Graphics (inline turtle command) |
| `S:OP var` | String operation (UPPER, LOWER, LEN, REVERSE, TRIM) |
| `D:ARR(n)` | Dimension an array |
| `P:ms` | Pause for milliseconds |
| `X:command` | Execute BASIC or Logo command |

### Labels
```pilot
*start
T:Welcome!
J:start
```

---

## Logo Turtle Graphics

### Movement
| Command | Alias | Description |
|---------|-------|-------------|
| `FORWARD n` | `FD n` | Move forward n pixels |
| `BACK n` | `BK n` | Move backward n pixels |
| `LEFT n` | `LT n` | Turn left n degrees |
| `RIGHT n` | `RT n` | Turn right n degrees |
| `HOME` | | Return to center, heading north |
| `SETXY x y` | `SETPOS` | Move to position (x, y) |
| `SETX x` | | Set x coordinate |
| `SETY y` | | Set y coordinate |
| `SETHEADING n` | `SETH n` | Set heading in degrees |
| `TOWARDS x y` | | Point towards (x, y) |

### Pen Control
| Command | Alias | Description |
|---------|-------|-------------|
| `PENUP` | `PU` | Lift pen (stop drawing) |
| `PENDOWN` | `PD` | Lower pen (start drawing) |
| `SETCOLOR name` | `SETPC` | Set pen color |
| `SETPENSIZE n` | `SETWIDTH` | Set pen width |
| `SETFILLCOLOR color` | `SETFC` | Set fill color |
| `SETBACKGROUND color` | `SETBG` | Set background color |
| `SHOWTURTLE` | `ST` | Show the turtle cursor |
| `HIDETURTLE` | `HT` | Hide the turtle cursor |

### Drawing Shapes
| Command | Description |
|---------|-------------|
| `CIRCLE r` | Draw circle with radius r |
| `ARC angle [radius]` | Draw an arc |
| `DOT [size]` | Draw a dot |
| `SQUARE side` | Draw a square |
| `TRIANGLE side` | Draw equilateral triangle |
| `POLYGON sides length` | Draw regular polygon |
| `STAR points length` | Draw a star |
| `RECT width [height]` | Draw rectangle |
| `LABEL "text" [size]` | Draw text at turtle position |

### REPEAT
```logo
REPEAT 4 [FORWARD 100 RIGHT 90]
REPEAT 36 [FORWARD 10 RIGHT 10]
```

### TO / END — Logo Procedures
```logo
TO SQUARE :size
    REPEAT 4 [FORWARD :size RIGHT 90]
END

SQUARE 100
```

---

## Variables & Data Types

### Types
| Type | Examples |
|------|---------|
| Integer | `42`, `-7`, `0` |
| Float | `3.14`, `-0.5` |
| String | `"Hello"`, `"world"` |
| List | Created with `LIST` command |
| Dictionary | Created with `DICT` command |

### Constants
Mathematical constants available in expressions:
| Constant | Value |
|----------|-------|
| `PI` | 3.14159265... |
| `E` | 2.71828182... |
| `TAU` | 6.28318530... (2π) |
| `INF` | Infinity |

### Pseudo-variables
| Variable | Description |
|----------|-------------|
| `TIMER` | Seconds since program start |
| `DATE$` | Current date (YYYY-MM-DD) |
| `TIME$` | Current time (HH:MM:SS) |
| `RESULT` | Return value of last FUNCTION call |
| `ERROR$` | Message from last caught error |
| `EOF` | End-of-file flag (1 = end reached) |

---

## Operators

### Arithmetic
| Operator | Description |
|----------|-------------|
| `+` | Addition / string concatenation |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `MOD` | Modulo (remainder) |
| `^` | Exponentiation |

### Comparison
| Operator | Description |
|----------|-------------|
| `=` / `==` | Equal to |
| `<>` / `!=` | Not equal to |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

### Logical
| Operator | Description |
|----------|-------------|
| `AND` | Logical AND |
| `OR` | Logical OR |
| `NOT` | Logical NOT |

---

## String Functions

### Classic String Functions
| Function | Description | Example |
|----------|-------------|---------|
| `LEN(s)` | Length of string | `LEN("Hello")` → 5 |
| `LEFT$(s, n)` | First n characters | `LEFT$("Hello", 3)` → `"Hel"` |
| `RIGHT$(s, n)` | Last n characters | `RIGHT$("Hello", 3)` → `"llo"` |
| `MID$(s, pos, n)` | Substring | `MID$("Hello", 2, 3)` → `"ell"` |
| `UCASE$(s)` | Uppercase | `UCASE$("hello")` → `"HELLO"` |
| `LCASE$(s)` | Lowercase | `LCASE$("HELLO")` → `"hello"` |
| `INSTR(s, sub)` | Find substring (1-based) | `INSTR("Hello", "ll")` → 3 |
| `STR$(n)` | Number to string | `STR$(42)` → `"42"` |
| `VAL(s)` | String to number | `VAL("42")` → 42 |
| `CHR$(n)` | ASCII code to character | `CHR$(65)` → `"A"` |
| `ASC(s)` | Character to ASCII code | `ASC("A")` → 65 |

### Modern String Functions
| Function | Description | Example |
|----------|-------------|---------|
| `TRIM$(s)` | Remove leading/trailing whitespace | `TRIM$("  hi  ")` → `"hi"` |
| `REPLACE$(s, old, new)` | Replace occurrences | `REPLACE$("hello", "l", "r")` → `"herro"` |
| `STARTSWITH(s, prefix)` | Check prefix (1/0) | `STARTSWITH("Hello", "He")` → 1 |
| `ENDSWITH(s, suffix)` | Check suffix (1/0) | `ENDSWITH("Hello", "lo")` → 1 |
| `CONTAINS(s, sub)` | Check contains (1/0) | `CONTAINS("Hello", "ell")` → 1 |
| `REPEAT$(s, n)` | Repeat string n times | `REPEAT$("ab", 3)` → `"ababab"` |
| `FORMAT$(val, spec)` | Format a value | `FORMAT$(3.14159, ".2f")` → `"3.14"` |
| `SPLIT(s, delim)` | Split into list | `SPLIT("a,b,c", ",")` → list |
| `JOIN(list, delim)` | Join list to string | `JOIN(ITEMS, ", ")` → string |

---

## Math Functions

### Classic Math Functions
| Function | Description |
|----------|-------------|
| `ABS(x)` | Absolute value |
| `INT(x)` | Integer part (truncate) |
| `SQR(x)` / `SQRT(x)` | Square root |
| `SIN(x)` / `COS(x)` / `TAN(x)` | Trigonometry (radians) |
| `ATN(x)` / `ATAN(x)` | Arctangent |
| `LOG(x)` | Natural logarithm |
| `EXP(x)` | e^x |
| `RND` / `RND(n)` | Random number (0–1 or 1–n) |
| `SGN(x)` | Sign (-1, 0, 1) |
| `CEIL(x)` | Ceiling |
| `FIX(x)` | Truncate towards zero |

### Modern Math Functions
| Function | Description | Example |
|----------|-------------|---------|
| `ROUND(x [, d])` | Round to d decimal places | `ROUND(3.456, 2)` → 3.46 |
| `FLOOR(x)` | Floor (round down) | `FLOOR(3.7)` → 3 |
| `POWER(base, exp)` | Exponentiation | `POWER(2, 10)` → 1024 |
| `CLAMP(x, lo, hi)` | Constrain to range | `CLAMP(15, 0, 10)` → 10 |
| `LERP(a, b, t)` | Linear interpolation | `LERP(0, 100, 0.5)` → 50 |
| `RANDOM(lo, hi)` | Random integer in range | `RANDOM(1, 6)` → 1–6 |
| `LOG2(x)` | Log base 2 | `LOG2(256)` → 8 |
| `LOG10(x)` | Log base 10 | `LOG10(1000)` → 3 |
| `EXP2(x)` | 2^x | `EXP2(8)` → 256 |

### Conversion Functions
| Function | Description |
|----------|-------------|
| `BIN(n)` | Integer to binary string |
| `OCT(n)` | Integer to octal string |
| `HEX(n)` | Integer to hex string |
| `TONUM(s)` | Convert to number |
| `TOSTR(x)` | Convert to string |

---

## Control Flow

### IF / THEN (single-line)
```basic
IF x > 0 THEN PRINT "Positive"
IF x > 0 THEN PRINT "yes" ELSE PRINT "no"
```

### IF / ELSEIF / ELSE / END IF (block)
```basic
IF score >= 90 THEN
    PRINT "A"
ELSEIF score >= 80 THEN
    PRINT "B"
ELSEIF score >= 70 THEN
    PRINT "C"
ELSE
    PRINT "F"
END IF
```

### FOR / NEXT
```basic
FOR i = 1 TO 10 STEP 2
    PRINT i
NEXT i
```

### FOREACH / IN / NEXT
Iterate over lists or dictionaries.
```basic
LIST items = "apple", "banana", "cherry"
FOREACH item IN items
    PRINT item
NEXT item

DICT scores = "Alice":95, "Bob":82
FOREACH name, score IN scores
    PRINT name; " = "; score
NEXT name
```

### WHILE / WEND
```basic
WHILE condition
    REM body
WEND
```

### DO / LOOP
```basic
DO WHILE condition
    REM body
LOOP

DO
    REM body
LOOP UNTIL condition
```

### SELECT CASE
```basic
SELECT CASE x
    CASE 1
        PRINT "One"
    CASE 2
        PRINT "Two"
    CASE ELSE
        PRINT "Other"
END SELECT
```

### ON GOTO / ON GOSUB
```basic
ON choice GOTO label1, label2, label3
ON choice GOSUB sub1, sub2, sub3
```

### REPEAT (Logo)
```logo
REPEAT 4 [FORWARD 100 RIGHT 90]
```

---

## Procedures & Functions

### SUB — Subroutines (no return value)
```basic
SUB Greet(name)
    PRINT "Hello, "; name; "!"
    PRINT "Welcome!"
END SUB

CALL Greet("Alice")
CALL Greet("Bob")
```

### FUNCTION — Functions (with return value)
```basic
FUNCTION Double(x)
    RETURN x * 2
END FUNCTION

LET result = Double(21)
PRINT result    ' prints 42
```

### Recursive Functions
```basic
FUNCTION Factorial(n)
    IF n <= 1 THEN RETURN 1
    RETURN n * Factorial(n - 1)
END FUNCTION

PRINT Factorial(10)
```

### LAMBDA — Inline Functions
```basic
LAMBDA Square(x) = x * x
LAMBDA Add(a, b) = a + b

PRINT Square(5)     ' prints 25
PRINT Add(10, 20)   ' prints 30
```

### CALL — Invoke a SUB or FUNCTION
```basic
CALL MySub(arg1, arg2)
LET result = MyFunc(arg1)
```

### Logo Procedures (TO / END)
```logo
TO HEXAGON :size
    REPEAT 6 [FORWARD :size RIGHT 60]
END

HEXAGON 80
```

### GOSUB / RETURN (Classic BASIC)
```basic
GOSUB MySub
END

MySub:
    PRINT "In subroutine"
    RETURN
```

---

## Lists (Dynamic Arrays)

Lists are ordered, resizable collections that can hold mixed types.

### Creating Lists
```basic
LIST fruits = "apple", "banana", "cherry"
LIST empty
LIST numbers = 1, 2, 3, 4, 5
```

### Modifying Lists
| Command | Description | Example |
|---------|-------------|---------|
| `PUSH lst, val` | Append to end | `PUSH fruits, "date"` |
| `POP lst [, var]` | Remove from end | `POP fruits, last` |
| `UNSHIFT lst, val` | Prepend to front | `UNSHIFT fruits, "avocado"` |
| `SHIFT lst [, var]` | Remove from front | `SHIFT fruits, first` |
| `SPLICE lst, i, n` | Remove n items at index i | `SPLICE fruits, 1, 2` |
| `SORT lst [DESC]` | Sort in place | `SORT numbers DESC` |
| `REVERSE lst` | Reverse in place | `REVERSE fruits` |

### List Functions (in expressions)
| Function | Description |
|----------|-------------|
| `LENGTH(lst)` | Number of elements |
| `INDEXOF(lst, val)` | Index of value (-1 if not found) |
| `CONTAINS(lst, val)` | Check membership (1/0) |
| `SLICE(lst, start, end)` | Extract sub-list |
| `JOIN(lst, delim)` | Join elements into string |

### Iterating Lists
```basic
LIST scores = 95, 82, 91, 78, 88
FOREACH score IN scores
    PRINT score
NEXT score
```

### Element Access (in LET)
```basic
LET fruits[0] = "apricot"
```

### Auto-variable
After modifying a list, `LISTNAME_LENGTH` is automatically set:
```basic
PUSH items, "new"
PRINT items_LENGTH    ' prints updated length
```

---

## Dictionaries (Maps)

Dictionaries store key-value pairs.

### Creating Dictionaries
```basic
DICT config = "theme":"dark", "fontSize":"14"
DICT empty
```

### Modifying Dictionaries
```basic
SET config.language = "en"
SET config, "maxLines", "1000"

GET config.theme INTO myTheme
GET config, "fontSize", mySize

DELETE config.maxLines
DELETE config, "fontSize"
```

### Dictionary Functions (in expressions)
| Function | Description |
|----------|-------------|
| `LENGTH(dict)` | Number of keys |
| `HASKEY(dict, key)` | Check if key exists (1/0) |
| `KEYS(dict)` | Get list of keys |
| `VALUES(dict)` | Get list of values |

### Iterating Dictionaries
```basic
FOREACH key, value IN config
    PRINT key; " = "; value
NEXT key
```

---

## File I/O

### Handle-based I/O
```basic
OPEN "data.txt" FOR INPUT AS #1
READLINE #1, line$
CLOSE #1

OPEN "output.txt" FOR OUTPUT AS #2
WRITELINE #2, "Hello, file!"
CLOSE #2

OPEN "log.txt" FOR APPEND AS #3
WRITELINE #3, "New log entry"
CLOSE #3
```

### Quick File Operations
```basic
WRITEFILE "data.txt", "File contents here"
READFILE "data.txt", contents$
APPENDFILE "log.txt", "Appended line"
```

### File Functions
| Function | Description |
|----------|-------------|
| `FILEEXISTS("path")` | Check if file exists (1/0) |
| `EOF` | End-of-file flag after READLINE |

### CLOSE ALL
Close all open file handles at once:
```basic
CLOSE ALL
```

---

## Error Handling

### TRY / CATCH / END TRY
```basic
TRY
    LET x = 10 / 0
    PRINT "This won't execute"
CATCH err
    PRINT "Caught error: "; err
END TRY
PRINT "Program continues normally"
```

### THROW
Raise a custom error:
```basic
FUNCTION Divide(a, b)
    IF b = 0 THEN THROW "Division by zero!"
    RETURN a / b
END FUNCTION

TRY
    PRINT Divide(10, 0)
CATCH e
    PRINT "Error: "; e
END TRY
```

### ASSERT
Validate conditions (useful for testing):
```basic
ASSERT x > 0, "x must be positive"
ASSERT LEN(name) > 0, "name required"
```

### ERROR$ Variable
After a CATCH, `ERROR$` contains the error message:
```basic
TRY
    THROW "something went wrong"
CATCH e
    PRINT ERROR$    ' same as e
END TRY
```

---

## Functional Programming

### LAMBDA
Define inline functions:
```basic
LAMBDA Double(x) = x * 2
LAMBDA IsEven(x) = x - INT(x / 2) * 2 = 0
```

### MAP
Apply a function to every element of a list:
```basic
LAMBDA Square(x) = x * x
LIST nums = 1, 2, 3, 4, 5
MAP Square ON nums INTO squared
' squared = [1, 4, 9, 16, 25]
```

### FILTER
Keep only elements where the function returns true:
```basic
LAMBDA IsPositive(x) = x > 0
LIST data = -5, 3, -1, 7, 0, 4
FILTER IsPositive ON data INTO positives
' positives = [3, 7, 4]
```

### REDUCE
Accumulate list elements into a single value:
```basic
LAMBDA Add(a, b) = a + b
LIST values = 10, 20, 30, 40
REDUCE Add ON values INTO total FROM 0
PRINT total    ' prints 100
```

---

## JSON Support

### JSON PARSE
Parse a JSON string into a dictionary or list:
```basic
LET data$ = '{"name":"Alice","score":95}'
JSON PARSE data$ INTO record
GET record.name INTO n
PRINT n    ' prints Alice
```

### JSON STRINGIFY
Convert a dict or list to a JSON string:
```basic
DICT user = "name":"Bob", "age":"30"
JSON STRINGIFY user INTO jsonStr
PRINT jsonStr
```

### JSON GET
Quick access to parsed JSON fields:
```basic
JSON GET record.name INTO playerName
```

---

## Regular Expressions

### REGEX MATCH
Find the first match of a pattern:
```basic
LET text = "Call 555-1234 today"
REGEX MATCH "\d{3}-\d{4}" IN text INTO phone
PRINT phone         ' prints 555-1234
PRINT phone_POS     ' prints character position
```

### REGEX REPLACE
Replace all matches of a pattern:
```basic
LET html = "<b>Hello</b>"
REGEX REPLACE "<[^>]+>" WITH "" IN html INTO plain
PRINT plain    ' prints Hello
```

### REGEX FIND
Find all matches (results stored in a list):
```basic
LET text = "a1 b2 c3 d4"
REGEX FIND "\w\d" IN text INTO matches
FOREACH m IN matches
    PRINT m
NEXT m
```

### REGEX SPLIT
Split a string using a regex delimiter:
```basic
LET csv = "one,two,,three"
REGEX SPLIT "," IN csv INTO parts
```

---

## Structs & Enums

### STRUCT
Define a record type with named fields:
```basic
STRUCT Point = X, Y
NEW Point AS p1
SET p1.X = 10
SET p1.Y = 20
GET p1.X INTO px
PRINT "x="; px
```

### ENUM
Define a set of named constants:
```basic
ENUM Color = RED, GREEN, BLUE, YELLOW
LET myColor = COLOR_GREEN
IF myColor = COLOR_GREEN THEN PRINT "Green!"
PRINT "Total colors: "; COLOR_COUNT
```
Enum values are auto-numbered starting from 0. Each value creates a constant `ENUMNAME_VALUENAME`.

---

## Constants & Type System

### CONST
Declare immutable variables:
```basic
CONST MAX_SIZE = 100
CONST APP_NAME = "MyApp"
LET MAX_SIZE = 200    ' ERROR: Cannot reassign constant
```

### TYPEOF
Introspect the type of a value:
```basic
TYPEOF 42            ' prints INTEGER
TYPEOF "hello"       ' prints STRING
TYPEOF 3.14          ' prints FLOAT

TYPEOF myVar INTO typeStr
IF typeStr = "STRING" THEN PRINT "It's a string"
```

### Type-checking Functions
| Function | Description |
|----------|-------------|
| `ISNUMBER(x)` | Returns 1 if numeric, 0 otherwise |
| `ISSTRING(x)` | Returns 1 if string, 0 otherwise |
| `TONUM(x)` | Convert to number |
| `TOSTR(x)` | Convert to string |
| `TYPE(x)` | Returns type name |

---

## Modules (IMPORT)

Include and execute another TempleCode file:
```basic
IMPORT "mathlib.tc"
IMPORT "utils/helpers.tc"
```

- Imported files are executed once (duplicate imports are skipped)
- SUB/FUNCTION definitions from imported files become available
- Variables set in imported files are accessible

---

## Formatted Output

### PRINTF
C-style formatted output with positional and variable interpolation:
```basic
LET name = "Alice"
LET score = 95

PRINTF "Hello {NAME}, you scored {1}!", score
PRINTF "Pi ≈ {0}", 3.14159
PRINTF "{0} + {1} = {2}", 10, 20, 30
```

Supports:
- `{0}`, `{1}`, ... — positional arguments
- `{VAR_NAME}` — variable interpolation
- `\n`, `\t` — escape sequences

---

## Mixing Styles

TempleCode's power comes from mixing BASIC, PILOT, and Logo plus modern features:

```
REM A fully mixed TempleCode program
CONST PI = 3.14159

FUNCTION CircleArea(r)
    RETURN PI * r * r
END FUNCTION

T:Welcome to the Circle Calculator!
A:Enter radius

TRY
    LET R = TONUM(ANSWER)
    LET AREA = CircleArea(R)
    PRINTF "Area of circle with radius {0}: {1}", R, ROUND(AREA, 2)

    REM Draw the circle with Logo
    SETCOLOR blue
    CIRCLE R * 2
    PRINT "Circle drawn!"
CATCH ERR
    T:Error: $ERR
END TRY

END
```

### Rules
- Lines starting with a digit are parsed as BASIC (with line numbers)
- Lines with a letter + colon (e.g., `T:`, `A:`, `M:`) are PILOT commands
- Logo keywords (`FORWARD`, `REPEAT`, `TO`, etc.) trigger the turtle graphics
- Modern commands (`LIST`, `DICT`, `SUB`, `FUNCTION`, `TRY`, etc.) extend BASIC
- `REM`, `'`, and `;` start comments in any context
- All styles can be freely mixed in a single program

---

## Example Programs

See the `examples/templecode/` directory:

| File | Description |
|------|-------------|
| `hello.tc` | Hello World demo mixing all three styles |
| `spiral.tc` | Colorful spiral with Logo turtle graphics |
| `quiz.tc` | Geography quiz using PILOT interaction |
| `guess.tc` | Number guessing game in BASIC |
| `mandelbrot.tc` | Fractal art with nested REPEAT |
| `todo_list.tc` | Todo list manager with lists, subs, file I/O |
| `data_pipeline.tc` | Data processing with lambdas, map/filter/reduce |
| `gradebook.tc` | Student grades with structs, dicts, functions |
| `text_processor.tc` | Text analysis with regex and string functions |
| `config_manager.tc` | JSON config file manager with error handling |

---

**TempleCode** — *Three heritages, one modern language.*
