#!/usr/bin/env python3
"""
Code Templates System for Time Warp II
Provides organized code templates for the TempleCode language
"""


class CodeTemplates:
    """Manages code templates organized by category"""

    def __init__(self):
        """Initialize the code templates system"""
        self.templates = self._load_templates()

    def _load_templates(self):
        """Load all code templates"""
        return {
            "TempleCode": {
                "BASIC Basics": {
                    "Hello World": '10 PRINT "Hello, World!"\n20 PRINT "Welcome to TempleCode!"\n30 END',
                    "User Input": '10 PRINT "What\'s your name?"\n20 INPUT NAME$\n30 PRINT "Hello, "; NAME$; "!"\n40 END',
                    "Simple Math": "10 LET A = 5\n20 LET B = 3\n30 PRINT \"Sum: \"; A + B\n40 PRINT \"Product: \"; A * B\n50 END",
                    "FOR Loop": "10 FOR I = 1 TO 10\n20 PRINT \"Count: \"; I\n30 NEXT I\n40 END",
                    "Factorial": "10 PRINT \"Enter a number:\"\n20 INPUT N\n30 LET FACT = 1\n40 FOR I = 1 TO N\n50 LET FACT = FACT * I\n60 NEXT I\n70 PRINT \"Factorial: \"; FACT\n80 END",
                    "Guess Number": "10 RANDOMIZE TIMER\n20 LET SECRET = INT(RND * 100) + 1\n30 PRINT \"Guess my number (1-100):\"\n40 INPUT GUESS\n50 IF GUESS = SECRET THEN PRINT \"Correct!\": END\n60 IF GUESS < SECRET THEN PRINT \"Too low!\"\n70 IF GUESS > SECRET THEN PRINT \"Too high!\"\n80 GOTO 30",
                },
                "PILOT Interaction": {
                    "Hello World": "T:Hello, World!\nT:Welcome to TempleCode!\nE:",
                    "User Input": "T:What's your name?\nA:\nT:Hello, $INPUT!\nE:",
                    "Simple Quiz": "T:What is the capital of France?\nA:\nM:Paris\nY:T:Correct! Well done!\nN:T:Sorry, it's Paris.\nE:",
                    "Menu System": "*MENU\nT:Choose: 1) Start 2) Help 3) Exit\nA:\nM:1\nY:J:START\nM:2\nY:J:HELP\nM:3\nY:J:EXIT\nJ:MENU\n*START\nT:Let's begin!\nE:\n*HELP\nT:This is a menu demo.\nJ:MENU\n*EXIT\nT:Goodbye!\nE:",
                    "Counting Loop": "C:COUNT = 1\n*LOOP\nT:Count: #COUNT\nC:COUNT = COUNT + 1\nJ(COUNT < 10):LOOP\nT:Done counting!\nE:",
                },
                "Logo Graphics": {
                    "Square": "FORWARD 100\nRIGHT 90\nFORWARD 100\nRIGHT 90\nFORWARD 100\nRIGHT 90\nFORWARD 100",
                    "Triangle": "FORWARD 100\nRIGHT 120\nFORWARD 100\nRIGHT 120\nFORWARD 100",
                    "Repeat Square": "REPEAT 4 [FORWARD 100 RIGHT 90]",
                    "Star": "REPEAT 5 [FORWARD 100 RIGHT 144]",
                    "Colorful Spiral": "SETCOLOR red\nREPEAT 36 [FORWARD 100 RIGHT 170]",
                    "Flower": "REPEAT 6 [REPEAT 4 [FORWARD 50 RIGHT 90] RIGHT 60]",
                    "Procedure": "TO SQUARE :SIZE\n  REPEAT 4 [FORWARD :SIZE RIGHT 90]\nEND\n\nSQUARE 50\nPENUP\nFORWARD 70\nPENDOWN\nSQUARE 100",
                },
                "Mixed (BASIC + Logo)": {
                    "BASIC with Turtle": '10 REM Draw a colorful pattern\n20 PRINT "Drawing pattern..."\n30 FOR I = 1 TO 36\n40 FORWARD I * 3\n50 RIGHT 91\n60 NEXT I\n70 PRINT "Done!"\n80 END',
                    "BASIC with PILOT I/O": "10 REM Combine BASIC logic with PILOT I/O\nT:Welcome to the number game!\n20 LET SECRET = INT(RND * 10) + 1\nT:I'm thinking of a number 1-10.\nA:\n30 IF INPUT = SECRET THEN GOTO 60\nT:Nope, try again!\nA:\n40 GOTO 30\n60 T:You got it!\n70 END",
                },
            },
        }

    def get_languages(self):
        """Get all available languages"""
        return list(self.templates.keys())

    def get_categories(self, language):
        """Get categories for a language"""
        if language in self.templates:
            return list(self.templates[language].keys())
        return []

    def get_templates(self, language, category):
        """Get templates for a language and category"""
        if language in self.templates and category in self.templates[language]:
            return list(self.templates[language][category].keys())
        return []

    def get_template_code(self, language, category, template_name):
        """Get the code for a specific template"""
        if (
            language in self.templates
            and category in self.templates[language]
            and template_name in self.templates[language][category]
        ):
            return self.templates[language][category][template_name]
        return ""

    def get_template_info(self, language, category, template_name):
        """Get template information including code and metadata"""
        code = self.get_template_code(language, category, template_name)
        if code:
            return {
                "name": template_name,
                "language": language,
                "category": category,
                "code": code,
                "lines": len(code.split("\n")),
            }
        return None
