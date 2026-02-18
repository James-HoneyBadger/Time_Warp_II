# Frequently Asked Questions

Common questions about Time Warp II.

## General Questions

### What is Time Warp II?

Time Warp II is a special version of **Time Warp Classic** with various enhancements and revisions, designed specifically as a single-language IDE for the **TempleCode programming language**, a fusion of BASIC, PILOT, and Logo.

It's designed for learning programming, teaching, and exploring retro-inspired educational computing.

### Who is it for?

- **Students:** Learn programming fundamentals
- **Teachers:** Teach programming in an educational environment
- **Hobbyists:** Explore retro-inspired educational computing
- **Developers:** Understand classic language paradigms through TempleCode

### Is it free?

Yes! Time Warp II is open-source and completely free to use.

### What platforms does it support?

- **Windows** (Python 3.10+)
- **macOS** (Python 3.10+)
- **Linux** (Python 3.10+)

### Can I use it offline?

Yes, Time Warp II runs completely offline. No internet connection needed.

---

## Installation & Setup

### How do I install Time Warp II?

1. Ensure Python 3.10+ is installed
2. Install tkinter if needed
3. Download or clone the repository
4. Run: `python TimeWarpII.py`

See [QUICK_START.md](QUICK_START.md) for detailed instructions.

### Do I need to install anything else?

You need:
- Python 3.10 or higher
- tkinter (usually included with Python)
- pygame-ce (installed automatically)
- Pillow (installed automatically)
- pygments (installed automatically)

### How much disk space does it need?

About 50 MB for the application and examples.

### Can I run it from USB?

Yes, as long as Python is installed on the target computer.

---

## Using the IDE

### How do I write code?

1. Click in the editor area
2. Type your TempleCode program
3. Click Execute

### How do I select a language?

Time Warp II uses the TempleCode language exclusively. Simply write your code and run it — no language selection needed.

### What's the keyboard shortcut to run code?

See [USER_GUIDE.md](user/USER_GUIDE.md) for all shortcuts.

### Can I undo my changes?

Yes, use Ctrl+Z to undo and Ctrl+Y to redo.

### How do I clear the output?

Click the "Clear Output" button or use the menu.

### Can I save my code?

Yes, use File > Save or Ctrl+S to save your programs.

### What file formats are supported?

- `.tc` - TempleCode program files
- `.txt` - Universal text format

---

## Programming & Execution

### Why won't my code run?

Check:
1. Syntax errors in output panel
2. Missing keywords (END, ENDIF, etc.)
3. Check examples for syntax

### How do I debug my code?

1. Add PRINT statements to trace execution
2. Run simpler versions of your program
3. Check output for error messages
4. Compare with example programs

### Can I mix BASIC, PILOT, and Logo syntax?

Yes! TempleCode is a fusion of all three. You can freely mix BASIC commands (PRINT, LET, IF), PILOT commands (T:, A:, M:), and Logo turtle graphics (FORWARD, RIGHT) in a single program.

### Does PILOT `A:` input work with arithmetic?

Yes. When the user enters a number via `A:`, it is automatically converted to a numeric type (integer or float). You can use `ANSWER` directly in arithmetic expressions without needing `TONUM()`:

```
A:
C:SECONDS = ANSWER
LET X = ANSWER * 2
```

This matches the behaviour of the BASIC `INPUT` command.

### Can I run programs without the GUI?

Yes! Time Warp II includes a full command-line interface. Use `templecode run <file>` to execute programs, `templecode repl` for an interactive session, `templecode check <file>` to syntax-check, and `templecode format <file>` to auto-indent. See the [User Guide](user/USER_GUIDE.md#command-line-interface-cli) for details.

### How big can programs be?

You can write very large programs, but performance depends on:
- Program complexity
- Data volume
- Computer resources
- Language efficiency

### Is there a time limit for execution?

No, programs run until completion or manual stop.

### What happens if I create an infinite loop?

The program will run forever. Stop it by:
1. Pressing Ctrl+C in terminal
2. Force-quitting the application
3. System kill if needed

---

## Language-Specific Questions

### What can I do with TempleCode?

TempleCode combines three classic paradigms:
- **BASIC heritage:** Variables, control flow, I/O, math, line numbers
- **PILOT heritage:** Interactive text, input, pattern matching for quizzes
- **Logo heritage:** Turtle graphics for visual programming

See [TEMPLECODE_REFERENCE.md](languages/TEMPLECODE_REFERENCE.md) for the full language reference.

### Can I use graphics in TempleCode?

Yes! TempleCode includes Logo-style turtle graphics commands like FORWARD, RIGHT, PENUP, PENDOWN, and REPEAT for drawing on the canvas.

---

## Files & Projects

### Where are my files saved?

In the directory you specify. Usually current directory or Documents.

### Can I open files from other editors?

Yes, Time Warp II can open any text file with appropriate code.

### Can I share my programs?

Yes! Save as `.txt` or language extension and share with others.

### What's the examples directory for?

`examples/` contains comprehensive demo programs for each language showing:
- All major features
- Working examples
- Good practices

**See them:** [examples/README.md](../examples/README.md)

---

## Errors & Troubleshooting

### I see "Syntax Error" but my code looks correct

Check:
1. Matching parentheses/brackets
2. Correct keywords (ENDIF not ENDFI)
3. Proper indentation
4. Compare with examples

For more help: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### What does "Unknown command" mean?

The interpreter couldn't recognize a command. Try:
1. Checking your syntax against the TempleCode reference
2. Using valid BASIC, PILOT, or Logo commands
3. Consulting the example programs

### Can I modify the application?

Yes, it's open-source! Check [TECHNICAL_REFERENCE.md](dev/TECHNICAL_REFERENCE.md) for architecture details.

### Where do I report bugs?

File an issue on the GitHub repository with:
- What you were trying to do
- What happened
- What you expected
- Your Python version

---

## Performance & Optimization

### Why is my program slow?

Possible causes:
- Large loops (reduce iterations)
- Complex calculations
- Graphics rendering (Logo)
- System resources

Solutions:
- Optimize algorithm
- Reduce output
- Upgrade computer

### How much output is too much?

Generally works well up to thousands of lines. Very large output may slow display.

### Can I run programs in the background?

Not currently, but you can:
1. Split into smaller programs
2. Run multiple instances
3. Save output to file for later review

---

## Customization & Preferences

### Can I change the font?

Yes, in Preferences:
- Font family
- Font size
- Font style

### Can I change the color scheme?

Yes, use Preferences > Theme to:
- Select built-in themes
- Customize colors
- Save custom themes

### Can I add keyboard shortcuts?

Check Preferences for shortcuts configuration.

### Can I change the default language?

Time Warp II uses the TempleCode language exclusively, so no language switching is needed.

---

## Features & Capabilities

### Can I import external libraries?

TempleCode programs run within the IDE's built-in interpreter. External library imports are not supported.

### Can I use the internet in my programs?

Not currently. TempleCode programs run within the IDE's sandboxed environment.

### Can I create graphical user interfaces?

TempleCode includes turtle graphics for visual output. General GUI creation is not supported.

### Can I create games?

Yes! You can create text-based games using BASIC/PILOT commands and graphical games using Logo turtle graphics.

---

## Getting Help & Learning

### Where should I start?

1. Read [QUICK_START.md](QUICK_START.md)
2. Run example programs
3. Try [LANGUAGE_TUTORIALS.md](user/LANGUAGE_TUTORIALS.md)
4. Read [USER_GUIDE.md](user/USER_GUIDE.md)

### Where are the complete language references?

In `docs/languages/` directory:
- [TEMPLECODE_REFERENCE.md](languages/TEMPLECODE_REFERENCE.md)

### Can I explore different programming styles?

Yes! TempleCode combines three classic paradigms in one language, so you can learn imperative (BASIC), interactive (PILOT), and visual (Logo) programming all in one environment.

### Are there exercises or challenges?

Yes! Examples directory has programs to study and modify.

### Is there a community?

Check GitHub repository for discussions and community links.

---

## Advanced Topics

### How do I extend Time Warp II?

See [TECHNICAL_REFERENCE.md](dev/TECHNICAL_REFERENCE.md) for:
- Architecture overview
- Adding new features
- Plugin development

### Can I extend the TempleCode language?

Yes, see [TECHNICAL_REFERENCE.md](dev/TECHNICAL_REFERENCE.md) for architecture details on how the language is implemented and how to add new commands.

### How does the language detection work?

Time Warp II uses the TempleCode language exclusively. The interpreter parses your program and recognizes BASIC, PILOT, and Logo commands as part of the unified TempleCode syntax.

### Can I use TempleCode in a classroom?

Yes! It's designed for education. Multiple students can:
- Use same installation
- Create own programs
- Learn programming fundamentals
- Explore different paradigms within TempleCode

---

## Statistics & Facts

### How many languages are supported?

**1 language: TempleCode** — a fusion of BASIC, PILOT, and Logo into one educational programming language.

### How many lines of code in Time Warp II?

Several thousand lines of Python implementing the interpreter and IDE.

### When was it created?

Time Warp II is a modern retro-computing project honoring classic languages.

---

## Before You Go

### Quick Tips

1. **Use examples:** They show best practices
2. **Read errors carefully:** They're usually helpful
3. **Try simple first:** Build up complexity gradually
4. **Experiment:** Try variations on examples
5. **Have fun:** Programming is creative!

### Useful Resources

- [INDEX.md](INDEX.md) - Documentation index
- [examples/README.md](../examples/README.md) - Program examples
- [QUICK_START.md](QUICK_START.md) - Get started in 5 minutes
- [USER_GUIDE.md](user/USER_GUIDE.md) - Complete IDE guide

---

**Have a question not answered here? Check the other documentation files or create an issue on GitHub.**

**Happy Programming! 🚀**
