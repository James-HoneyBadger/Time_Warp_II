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
                "Functions & Subs": {
                    "Simple Function": 'FUNCTION DOUBLE(X)\n  RETURN X * 2\nEND FUNCTION\n\nLET RESULT = DOUBLE(21)\nPRINT "Double of 21 = "; RESULT\nEND',
                    "Recursive Factorial": 'FUNCTION FACTORIAL(N)\n  IF N <= 1 THEN RETURN 1\n  RETURN N * FACTORIAL(N - 1)\nEND FUNCTION\n\nPRINT "5! = "; FACTORIAL(5)\nPRINT "10! = "; FACTORIAL(10)\nEND',
                    "Subroutine": 'SUB GREET(NAME)\n  PRINT "Hello, "; NAME; "!"\n  PRINT "Welcome to TempleCode."\nEND SUB\n\nCALL GREET("Alice")\nCALL GREET("Bob")\nEND',
                    "Multiple Functions": 'FUNCTION MAX(A, B)\n  IF A > B THEN RETURN A\n  RETURN B\nEND FUNCTION\n\nFUNCTION MIN(A, B)\n  IF A < B THEN RETURN A\n  RETURN B\nEND FUNCTION\n\nLET X = 42\nLET Y = 17\nPRINT "Max: "; MAX(X, Y)\nPRINT "Min: "; MIN(X, Y)\nEND',
                },
                "Lists & Dicts": {
                    "List Operations": 'LIST FRUITS = "apple", "banana", "cherry"\nPUSH FRUITS, "date"\nPRINT "Length: "; FRUITS_LENGTH\n\nFOREACH ITEM IN FRUITS\n  PRINT "Fruit: "; ITEM\nNEXT ITEM\n\nSORT FRUITS\nPRINT "Sorted:"\nFOREACH ITEM IN FRUITS\n  PRINT "  "; ITEM\nNEXT ITEM\nEND',
                    "Dictionary": 'DICT PERSON = "name":"Alice", "age":"30", "city":"London"\nGET PERSON.name INTO N\nGET PERSON.age INTO A\nPRINT N; " is "; A; " years old"\n\nSET PERSON.email = "alice@example.com"\nGET PERSON.email INTO E\nPRINT "Email: "; E\nEND',
                    "Nested Iteration": 'LIST SCORES = 85, 92, 78, 95, 88\nLET TOTAL = 0\nLET COUNT = 0\nFOREACH S IN SCORES\n  LET TOTAL = TOTAL + S\n  LET COUNT = COUNT + 1\nNEXT S\nPRINT "Average: "; TOTAL / COUNT\nEND',
                    "Stack (LIFO)": 'LIST STACK\nPUSH STACK, "first"\nPUSH STACK, "second"\nPUSH STACK, "third"\n\nPOP STACK, VAL\nPRINT "Popped: "; VAL\nPOP STACK, VAL\nPRINT "Popped: "; VAL\nEND',
                },
                "File I/O": {
                    "Write & Read": 'REM Write data to a file\nOPEN "output.txt" FOR OUTPUT AS #1\nWRITELINE #1, "Hello from TempleCode!"\nWRITELINE #1, "Line 2 of the file"\nCLOSE #1\n\nREM Read it back\nOPEN "output.txt" FOR INPUT AS #1\nREADLINE #1, A$\nPRINT "Read: "; A$\nREADLINE #1, B$\nPRINT "Read: "; B$\nCLOSE #1\nEND',
                    "Quick File Ops": 'WRITEFILE "data.txt", "This is file content"\nREADFILE "data.txt", CONTENT\nPRINT "File says: "; CONTENT\nEND',
                    "CSV Writer": 'OPEN "scores.csv" FOR OUTPUT AS #1\nWRITELINE #1, "Name,Score"\nDATA Alice,95,Bob,82,Charlie,91\nFOR I = 1 TO 3\n  READ N$\n  READ S\n  WRITELINE #1, N$ + "," + STR$(S)\nNEXT I\nCLOSE #1\nPRINT "CSV written!"\nEND',
                },
                "Error Handling": {
                    "Try/Catch": 'TRY\n  LET X = 10 / 0\n  PRINT "This won\'t print"\nCATCH ERR\n  PRINT "Caught error: "; ERR\nEND TRY\nPRINT "Program continues!"\nEND',
                    "Custom Errors": 'FUNCTION DIVIDE(A, B)\n  IF B = 0 THEN THROW "Division by zero!"\n  RETURN A / B\nEND FUNCTION\n\nTRY\n  PRINT DIVIDE(10, 3)\n  PRINT DIVIDE(10, 0)\nCATCH E\n  PRINT "Error: "; E\nEND TRY\nEND',
                    "Assert": 'LET X = 42\nASSERT X > 0, "X must be positive"\nASSERT X = 42, "X must be 42"\nPRINT "All assertions passed!"\nEND',
                },
                "Functional": {
                    "Lambda & Map": 'LAMBDA DOUBLE(X) = X * 2\nLIST NUMS = 1, 2, 3, 4, 5\nMAP DOUBLE ON NUMS INTO DOUBLED\n\nFOREACH N IN DOUBLED\n  PRINT N;\n  PRINT " ";\nNEXT N\nPRINT\nEND',
                    "Filter": 'LAMBDA ISEVEN(X) = X - INT(X / 2) * 2 = 0\nLIST DATA = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10\nFILTER ISEVEN ON DATA INTO EVENS\n\nPRINT "Even numbers:"\nFOREACH N IN EVENS\n  PRINT N; " ";\nNEXT N\nPRINT\nEND',
                    "Reduce": 'LAMBDA ADD(A, B) = A + B\nLIST VALUES = 10, 20, 30, 40, 50\nREDUCE ADD ON VALUES INTO TOTAL FROM 0\nPRINT "Sum: "; TOTAL\nEND',
                },
                "JSON & Regex": {
                    "JSON Parse": 'LET DATA$ = \'{"name":"Alice","score":95}\'\nJSON PARSE DATA$ INTO RECORD\nGET RECORD.name INTO NAME\nGET RECORD.score INTO SCORE\nPRINT NAME; " scored "; SCORE\nEND',
                    "Regex Match": 'LET TEXT$ = "My phone is 555-1234"\nREGEX MATCH "\\d{3}-\\d{4}" IN TEXT$ INTO PHONE\nPRINT "Found phone: "; PHONE\nEND',
                    "Regex Replace": 'LET HTML$ = "<b>Hello</b> <i>World</i>"\nREGEX REPLACE "<[^>]+>" WITH "" IN HTML$ INTO PLAIN\nPRINT "Plain text: "; PLAIN\nEND',
                    "Regex Split": 'LET CSV$ = "one,two,three,four"\nREGEX SPLIT "," IN CSV$ INTO PARTS\nFOREACH P IN PARTS\n  PRINT "Part: "; P\nNEXT P\nEND',
                },
                "Structs & Enums": {
                    "Struct": 'STRUCT POINT = X, Y\nNEW POINT AS P1\nSET P1.X = 10\nSET P1.Y = 20\nGET P1.X INTO PX\nGET P1.Y INTO PY\nPRINT "Point: ("; PX; ", "; PY; ")"\nEND',
                    "Enum": 'ENUM COLOR = RED, GREEN, BLUE, YELLOW\nLET MYCOLOR = COLOR_GREEN\nIF MYCOLOR = COLOR_GREEN THEN PRINT "Green!"\nPRINT "Total colors: "; COLOR_COUNT\nEND',
                    "Constants": 'CONST MAX_SIZE = 100\nCONST APP_NAME = "MyApp"\nPRINT APP_NAME; " max size: "; MAX_SIZE\nREM This would cause an error:\nREM LET MAX_SIZE = 200\nEND',
                },
                "Formatted Output": {
                    "Printf": 'LET NAME = "Alice"\nLET SCORE = 95.5\nPRINTF "Hello {NAME}, your score is {1}!", SCORE\nPRINTF "Pi to 4 places: {0}", 3.14159265\nEND',
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
