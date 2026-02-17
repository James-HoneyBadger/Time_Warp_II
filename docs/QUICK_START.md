# Quick Start Guide - 5 Minute Setup

Get Time Warp II running and write your first program in 5 minutes!

## ⚡ Super Quick Start (90 Seconds)

### Step 1: Install (30 seconds)
```bash
cd /path/to/Time_Warp_II
python3 run.py
```
That's it! The script handles everything automatically.

### Step 2: Write Code (30 seconds)
```
1. Copy this code into the editor:

PRINT "Hello, TempleCode!"
PRINT "2 + 3 ="; 2 + 3
END

2. Click "Run"
```

### Step 3: Run (30 seconds)
```
Click the "Run" button
→ See output appear!
```

## 📋 Full Quick Start

### Prerequisites
- Python 3.10 or higher
- About 2 minutes
- Internet connection (first run only)

### Installation

**Option 1: Python Launcher (Recommended)**
```bash
python3 run.py
```

**Option 2: Bash Script (Linux/macOS)**
```bash
./run.sh
```

**Option 3: Batch Script (Windows)**
```cmd
run.bat
```

All scripts will:
1. Create a virtual environment
2. Install dependencies
3. Verify installation
4. Launch the IDE

### First Program - Hello World in TempleCode

```basic
PRINT "Welcome to Time Warp II!"
PRINT "Today is:"; DATE$
PRINT "Let's do math: 5 + 3 ="; 5 + 3
END
```

**Steps:**
1. Paste code into editor
2. Click **Run** button
3. See output in Output panel

### First Program - Interactive Quiz in TempleCode

```
T:Welcome to the TempleCode Quiz!
T:What is the capital of France?
A:
M:Paris
Y:T:Correct! Well done!
N:T:Not quite. The answer is Paris.
E:
```

**Steps:**
1. Paste code into editor
2. Click **Run** button
3. Answer the question!

### First Program - Graphics in TempleCode

```logo
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
```

**Steps:**
1. Paste code into editor
2. Click **Run**
3. See square drawn on canvas!

## 🎯 Next Steps

### Learn More
- Check [LANGUAGE_TUTORIALS.md](user/LANGUAGE_TUTORIALS.md)
- Run examples in [../examples/](../examples/) directory
- Explore BASIC, PILOT, and Logo commands within TempleCode

### Master the IDE
- Read [USER_GUIDE.md](user/USER_GUIDE.md) for features
- Learn [KEYBOARD_SHORTCUTS.md](user/KEYBOARD_SHORTCUTS.md)
- Customize [THEMES_AND_FONTS.md](user/THEMES_AND_FONTS.md)

### Run Examples
```bash
# Open any example program
# Examples are in examples/templecode/

# E.g., for a guessing game:
# Open examples/templecode/guess.tc
```

### Troubleshooting
If something doesn't work:
1. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Check [FAQ.md](FAQ.md)
3. Review full [SETUP.md](../SETUP.md)

## 🚀 IDE Overview

### Main Components

**Editor (Left)**
- Write code here
- Syntax highlighting
- Line numbers
- Find & Replace

**Output (Bottom)**
- See program results
- Error messages
- Debug information

**Canvas (Right)**
- Turtle graphics
- Visual output for Logo-style commands

**Toolbar**
- Run button
- File operations
- Settings

### Your First Real Program

Let's calculate factorial in TempleCode:

```basic
PRINT "Factorial Calculator"
FOR I = 1 TO 6
  LET F = 1
  FOR J = 1 TO I
    LET F = F * J
  NEXT J
  PRINT I; "! ="; F
NEXT I
END
```

**Try it:**
1. Paste code into editor
2. Click Run
3. See results!

## 💡 Pro Tips

### Tip 1: Copy Examples
Example programs are in `examples/templecode/`
```
examples/templecode/hello.tc
examples/templecode/guess.tc
examples/templecode/quiz.tc
examples/templecode/spiral.tc
examples/templecode/mandelbrot.tc
```

### Tip 2: Use Keyboard Shortcuts
- Ctrl+Enter: Run program
- Ctrl+F: Find
- Ctrl+H: Find & Replace
- Ctrl+S: Save file

### Tip 3: Check Output Carefully
The output explains what each command does!

### Tip 4: Modify & Experiment
Don't just read examples - modify them!
Change numbers, add loops, try new things.

## ❓ Common First Questions

**Q: Which language should I start with?**
A: TempleCode is the only language — just start writing!

**Q: Where are the examples?**
A: In `examples/templecode/`

**Q: How do I save my code?**
A: File menu → Save, or Ctrl+S

**Q: Can I load from a file?**
A: Yes! File menu → Open File

**Q: Why no output?**
A: Check you're using PRINT or T: commands

**Q: Can I mix BASIC, PILOT, and Logo syntax?**
A: Yes! TempleCode fuses all three — mix freely in one program

## 📞 Need More Help?

- **Full user guide:** [USER_GUIDE.md](user/USER_GUIDE.md)
- **Language tutorials:** [LANGUAGE_TUTORIALS.md](user/LANGUAGE_TUTORIALS.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **FAQ:** [FAQ.md](FAQ.md)
- **Full documentation:** [INDEX.md](INDEX.md)

## 🎓 Learning Path

**5 minutes (now)**
→ You're reading this!

**15 minutes (next)**
→ Run your first program
→ Try different TempleCode styles (BASIC, PILOT, Logo)
→ Modify an example

**30 minutes**
→ Read [USER_GUIDE.md](user/USER_GUIDE.md)
→ Learn IDE features
→ Customize your workspace

**1 hour**
→ Follow [LANGUAGE_TUTORIALS.md](user/LANGUAGE_TUTORIALS.md)
→ Write a small program
→ Combine language features

**Ongoing**
→ Master the TempleCode language
→ Build larger projects
→ Master advanced features

---

**You're ready! 🚀**

[Next: Try your first program →](#super-quick-start-90-seconds)

Or jump to:
- [Full User Guide](user/USER_GUIDE.md)
- [Language Tutorials](user/LANGUAGE_TUTORIALS.md)
- [All Documentation](INDEX.md)
