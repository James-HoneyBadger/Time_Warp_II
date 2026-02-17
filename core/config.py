"""
Time Warp II - Theme & Font Definitions

Centralised configuration for colour themes, fonts, keywords, and
command-palette entries.  Edit this file to add new themes, keywords,
or palette commands.
"""

# ---------------------------------------------------------------------------
#  Colour Themes
# ---------------------------------------------------------------------------

THEMES = {
    "light": {
        "name": "Light",
        "text_bg": "white", "text_fg": "black",
        "canvas_bg": "white", "canvas_border": "#cccccc",
        "root_bg": "#f0f0f0", "frame_bg": "#f0f0f0",
        "editor_frame_bg": "white", "editor_frame_fg": "black",
        "input_bg": "white", "input_fg": "black",
        "statusbar_bg": "#e0e0e0", "statusbar_fg": "#333333",
        "btn_bg": "#d0d0d0", "btn_fg": "#222222",
        "btn_hover": "#b0b0b0",
        "highlight_line": "#e8f0fe",
        "output_error": "#cc0000", "output_warn": "#996600", "output_ok": "#008800",
    },
    "dark": {
        "name": "Dark",
        "text_bg": "#1e1e1e", "text_fg": "#d4d4d4",
        "canvas_bg": "#2d2d2d", "canvas_border": "#3e3e3e",
        "root_bg": "#252526", "frame_bg": "#252526",
        "editor_frame_bg": "#252526", "editor_frame_fg": "#d4d4d4",
        "input_bg": "#1e1e1e", "input_fg": "#d4d4d4",
        "statusbar_bg": "#007acc", "statusbar_fg": "#ffffff",
        "btn_bg": "#3e3e3e", "btn_fg": "#d4d4d4",
        "btn_hover": "#505050",
        "highlight_line": "#2a2d2e",
        "output_error": "#f44747", "output_warn": "#cca700", "output_ok": "#6a9955",
    },
    "classic": {
        "name": "Classic",
        "text_bg": "white", "text_fg": "black",
        "canvas_bg": "#fffef0", "canvas_border": "#cccccc",
        "root_bg": "#e0e0e0", "frame_bg": "#e0e0e0",
        "editor_frame_bg": "#e0e0e0", "editor_frame_fg": "black",
        "input_bg": "white", "input_fg": "black",
        "statusbar_bg": "#c0c0c0", "statusbar_fg": "#000000",
        "btn_bg": "#d0d0d0", "btn_fg": "#000000",
        "btn_hover": "#b0b0b0",
        "highlight_line": "#e8e8e0",
        "output_error": "#cc0000", "output_warn": "#996600", "output_ok": "#008800",
    },
    "solarized_dark": {
        "name": "Solarized Dark",
        "text_bg": "#002b36", "text_fg": "#839496",
        "canvas_bg": "#073642", "canvas_border": "#586e75",
        "root_bg": "#002b36", "frame_bg": "#002b36",
        "editor_frame_bg": "#002b36", "editor_frame_fg": "#839496",
        "input_bg": "#073642", "input_fg": "#839496",
        "statusbar_bg": "#073642", "statusbar_fg": "#93a1a1",
        "btn_bg": "#073642", "btn_fg": "#839496",
        "btn_hover": "#0a4a5a",
        "highlight_line": "#073642",
        "output_error": "#dc322f", "output_warn": "#b58900", "output_ok": "#859900",
    },
    "solarized_light": {
        "name": "Solarized Light",
        "text_bg": "#fdf6e3", "text_fg": "#657b83",
        "canvas_bg": "#eee8d5", "canvas_border": "#93a1a1",
        "root_bg": "#fdf6e3", "frame_bg": "#fdf6e3",
        "editor_frame_bg": "#fdf6e3", "editor_frame_fg": "#657b83",
        "input_bg": "#eee8d5", "input_fg": "#657b83",
        "statusbar_bg": "#eee8d5", "statusbar_fg": "#586e75",
        "btn_bg": "#eee8d5", "btn_fg": "#657b83",
        "btn_hover": "#ddd6c1",
        "highlight_line": "#eee8d5",
        "output_error": "#dc322f", "output_warn": "#b58900", "output_ok": "#859900",
    },
    "monokai": {
        "name": "Monokai",
        "text_bg": "#272822", "text_fg": "#f8f8f2",
        "canvas_bg": "#3e3d32", "canvas_border": "#75715e",
        "root_bg": "#272822", "frame_bg": "#272822",
        "editor_frame_bg": "#272822", "editor_frame_fg": "#f8f8f2",
        "input_bg": "#3e3d32", "input_fg": "#f8f8f2",
        "statusbar_bg": "#414339", "statusbar_fg": "#f8f8f2",
        "btn_bg": "#3e3d32", "btn_fg": "#f8f8f2",
        "btn_hover": "#555649",
        "highlight_line": "#3e3d32",
        "output_error": "#f92672", "output_warn": "#e6db74", "output_ok": "#a6e22e",
    },
    "dracula": {
        "name": "Dracula",
        "text_bg": "#282a36", "text_fg": "#f8f8f2",
        "canvas_bg": "#44475a", "canvas_border": "#6272a4",
        "root_bg": "#282a36", "frame_bg": "#282a36",
        "editor_frame_bg": "#282a36", "editor_frame_fg": "#f8f8f2",
        "input_bg": "#44475a", "input_fg": "#f8f8f2",
        "statusbar_bg": "#44475a", "statusbar_fg": "#f8f8f2",
        "btn_bg": "#44475a", "btn_fg": "#f8f8f2",
        "btn_hover": "#565978",
        "highlight_line": "#44475a",
        "output_error": "#ff5555", "output_warn": "#f1fa8c", "output_ok": "#50fa7b",
    },
    "nord": {
        "name": "Nord",
        "text_bg": "#2e3440", "text_fg": "#d8dee9",
        "canvas_bg": "#3b4252", "canvas_border": "#4c566a",
        "root_bg": "#2e3440", "frame_bg": "#2e3440",
        "editor_frame_bg": "#2e3440", "editor_frame_fg": "#d8dee9",
        "input_bg": "#3b4252", "input_fg": "#d8dee9",
        "statusbar_bg": "#3b4252", "statusbar_fg": "#d8dee9",
        "btn_bg": "#3b4252", "btn_fg": "#d8dee9",
        "btn_hover": "#4c566a",
        "highlight_line": "#3b4252",
        "output_error": "#bf616a", "output_warn": "#ebcb8b", "output_ok": "#a3be8c",
    },
    "high_contrast": {
        "name": "High Contrast",
        "text_bg": "black", "text_fg": "white",
        "canvas_bg": "#0a0a0a", "canvas_border": "white",
        "root_bg": "black", "frame_bg": "black",
        "editor_frame_bg": "black", "editor_frame_fg": "white",
        "input_bg": "#0a0a0a", "input_fg": "white",
        "statusbar_bg": "#1a1a1a", "statusbar_fg": "#ffff00",
        "btn_bg": "#1a1a1a", "btn_fg": "#ffffff",
        "btn_hover": "#333333",
        "highlight_line": "#1a1a1a",
        "output_error": "#ff4444", "output_warn": "#ffff00", "output_ok": "#44ff44",
    },
}

# Map theme keys to line-number background colours (for syntax highlighting)
LINE_NUMBER_BG = {
    "dark": "#1e1e1e", "light": "#f0f0f0", "monokai": "#272822",
    "classic": "#ffffff", "solarized_dark": "#002b36",
    "solarized_light": "#fdf6e3", "dracula": "#282a36",
    "nord": "#2e3440", "high_contrast": "#000000",
}


# ---------------------------------------------------------------------------
#  Font Sizes
# ---------------------------------------------------------------------------

FONT_SIZES = {
    "tiny":     {"name": "Tiny (8pt)",         "editor": 8,  "output": 8},
    "small":    {"name": "Small (10pt)",        "editor": 10, "output": 9},
    "medium":   {"name": "Medium (12pt)",       "editor": 12, "output": 11},
    "large":    {"name": "Large (14pt)",        "editor": 14, "output": 13},
    "xlarge":   {"name": "Extra Large (16pt)",  "editor": 16, "output": 15},
    "xxlarge":  {"name": "Huge (18pt)",         "editor": 18, "output": 17},
    "xxxlarge": {"name": "Giant (22pt)",        "editor": 22, "output": 20},
}

# Ordered list of font-size keys for Ctrl+scroll cycling
FONT_SIZE_ORDER = ["tiny", "small", "medium", "large", "xlarge", "xxlarge", "xxxlarge"]

# Monospace fonts to prioritise in the font-family picker
PRIORITY_FONTS = [
    "Courier", "Courier New", "Consolas", "Monaco", "Menlo",
    "DejaVu Sans Mono", "Liberation Mono", "Ubuntu Mono",
    "Fira Code", "Source Code Pro", "JetBrains Mono",
    "Cascadia Code", "SF Mono", "Inconsolata", "Roboto Mono",
    "Hack", "Anonymous Pro", "Droid Sans Mono", "PT Mono",
]


# ---------------------------------------------------------------------------
#  Auto-complete Keywords
# ---------------------------------------------------------------------------

KEYWORDS = [
    # BASIC
    "PRINT", "LET", "IF", "THEN", "ELSE", "ELSEIF", "ENDIF", "END",
    "FOR", "TO", "STEP", "NEXT",
    "WHILE", "WEND",
    "DO", "LOOP", "UNTIL",
    "GOTO", "GOSUB", "RETURN",
    "ON", "BEEP",
    "DIM", "DATA", "READ", "RESTORE",
    "INPUT", "REM", "STOP", "CLS",
    "SELECT", "CASE", "EXIT",
    "SWAP", "INCR", "DECR", "DELAY",
    "ABS", "INT", "SQR", "RND", "SIN", "COS", "TAN", "LOG", "EXP",
    "LEFT$", "RIGHT$", "MID$", "LEN", "VAL", "STR$", "CHR$", "ASC",
    "TAB", "SPC", "MOD",
    "TIMER", "DATE$", "TIME$", "TYPE",
    # PILOT
    "T:", "A:", "M:", "Y:", "N:", "J:", "C:", "E:", "R:",
    "U:", "L:", "S:", "G:", "P:", "D:",
    # Logo
    "FORWARD", "FD", "BACK", "BK", "LEFT", "LT", "RIGHT", "RT",
    "PENUP", "PU", "PENDOWN", "PD", "HOME", "CLEARSCREEN", "CS",
    "SETCOLOR", "SETPENSIZE", "SETFILLCOLOR", "SETBACKGROUND",
    "SETXY", "SETX", "SETY", "SETHEADING", "SETH",
    "SHOWTURTLE", "ST", "HIDETURTLE", "HT",
    "CIRCLE", "ARC", "DOT", "RECT", "SQUARE", "TRIANGLE",
    "POLYGON", "STAR", "FILL",
    "REPEAT", "MAKE", "TO",
    "TOWARDS", "HEADING", "POS",
    "LABEL", "STAMP", "PENCOLOR?", "PENSIZE?",
    "WRAP", "WINDOW", "FENCE",
]

# Keywords that should increase indentation on the next line
INDENT_OPENERS = {"FOR", "WHILE", "IF", "ELSEIF", "DO", "REPEAT", "SELECT", "THEN"}


# ---------------------------------------------------------------------------
#  Welcome Message
# ---------------------------------------------------------------------------

WELCOME_MESSAGE = """\
Welcome to Time Warp II! 🚀

TempleCode is a fusion of BASIC, PILOT, and Logo
— a single retro-inspired language from the early 1990s.

BASIC commands:
  PRINT, LET, IF/THEN/ELSEIF/ENDIF, FOR/NEXT, GOTO, GOSUB
  DIM, REM, ON GOTO/GOSUB, READ/DATA/RESTORE, TIMER, CLS

PILOT commands:
  T: (type)  A: (accept)  M: (match)  Y:/N: (conditional)
  J: (jump)  C: (compute) E: (end)    *label

Logo turtle graphics:
  FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN
  SETCOLOR, REPEAT [ ... ], TO procname ... END
  LABEL, STAMP, WRAP/WINDOW/FENCE

Enter your code in the left panel and click ▶ Run to execute!
Press F1 or Help → Quick Reference for the full command list.
"""
