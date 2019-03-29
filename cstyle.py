'''
    Filename: cstyle.py
    Author: Daniel Nguyen
    Date Created: March 23, 2019
    Last Modified: March 29, 2019
    Python Version: 2.7
'''


import re
import sys
import getopt

LEFT_CURLY = '{'
RIGHT_CURLY = '}'
LEFT_PAREN = '('
RIGHT_PAREN = ')'
SEMICOLON = ';'
COLON = ':'
BACKSLASH = '\\'
FORWARD_SLASH = '/'
DOUBLE_QUOTE = '\"'
SINGLE_QUOTE = '\''
TAB_CHAR = '\t'
SPACE_CHAR = ' '
START_BLOCK_COMMENT = '/*'
END_BLOCK_COMMENT = '*/'
ASTERISK = '*'
START_COMMENT = '//'
SPACE_REPLACEMENT_CHAR = '^'
POUND = '#'

VARS_ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

# Characters that can be used in a type or a function name
STD_CHARS_REGEXP = "[a-zA-Z_][a-zA-Z0-9_]*"
NUMBER_REGEXP = "(-|)(0x|0|)[0-9]+"


BLCK_COMMENT_REGEXP = " *(\/\*)"
COMMENT_REGEXP = " *\/\/.*"
STMT_REGEXP = ".*;"
WHITE_SPACE_REGEXP = "(|( |\t)+)\Z"
MAGIC_NUMBER_REGEXP = "[^a-zA-Z0-9_]+(-|)((0x|0|)[0-9]+)"
# The group index that is the number inside the magic number pattern
NUM_GROUP_IND = 2

STRING_REGEXP = "(\".*\")"
CHAR_REGEXP = "(\'.*\')"
SEP_BY_SPACE_REGEXP = "\A. .\Z"

# Covers most cases of return types for functions
FUNC_KEYWORDS = [
    'static *', 'const *', 'struct *', 'static struct *', 'const struct *', 'enum *',
    'static enum *', 'const enum *', 'unsigned *', 'static unsigned *', 'const unsigned *',
    'long *', 'static long *', 'const long *', 'signed *', 'static signed *', 'const signed *',
    'unsigned short *', 'static unsigned short *', 'const unsigned short *',
    'short *', 'static short *', 'const short *', 'unsigned long *', 'static unsigned long *',
    'const unsigned long *', 'long long *', 'static long long *', 'const long long *',
    'unsigned long long *', 'static unsigned long long *', 'const unsigned long long *'
]

# Code detections regular expressions
C_DIRS_REGEXP = " *\#(define|include|undef|ifdef|ifndef|if|else|elif|endif|error|pragma)"
FUNC_REGEXP = (" *(%s|)" % "|".join(FUNC_KEYWORDS)) +\
    "([a-zA-Z_][a-zA-Z0-9_]*)(\** +| +\**| +\** +)([a-zA-Z_][a-zA-Z0-9_]*)( )*(\(.*\))"
FUNC_HDR_REGEXP = (" *(%s|)" % "|".join(FUNC_KEYWORDS)) +\
    "[a-zA-Z_][a-zA-Z0-9_]*(\** +| +\**| +\** +)[a-zA-Z_][a-zA-Z0-9_]*( )*\(.*\) *; *\Z"
ASSIGNMENT_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *=.* *;"
DEC_ASSIGNMENT_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *\** *[a-zA-Z_][a-zA-Z0-9_]* *=.* *;"
FUNC_CALL_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *\(.*\) *;"
DECLARATIONS_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *\** *[a-zA-Z_][a-zA-Z0-9_]* *;"
KEYWORDS_REGEXP = "( *(if|else if|while|for|switch) *\(.*\))|((continue|break);)"

# Misc
TODO_COMMENT_REGEXP = " *// *TODO"

SWITCH_CASE_REGEXP = " *((case .+ *:)|(default *:))"


blck_cmmt_ptrn = re.compile(BLCK_COMMENT_REGEXP)
cmmt_ptrn = re.compile(COMMENT_REGEXP)
stmt_ptrn = re.compile(STMT_REGEXP)
white_space_ptrn = re.compile(WHITE_SPACE_REGEXP)
magic_num_ptrn = re.compile(MAGIC_NUMBER_REGEXP)
string_ptrn = re.compile(STRING_REGEXP)
char_ptrn = re.compile(CHAR_REGEXP)
switch_case_regexp = re.compile(SWITCH_CASE_REGEXP)

c_dirs_ptrn = re.compile(C_DIRS_REGEXP)
func_ptrn = re.compile(FUNC_REGEXP)
func_hdr_ptrn = re.compile(FUNC_HDR_REGEXP)
asg_ptrn = re.compile(ASSIGNMENT_REGEXP)
dec_asg_ptrn = re.compile(DEC_ASSIGNMENT_REGEXP)
func_call_ptrn = re.compile(FUNC_CALL_REGEXP)
dec_ptrn = re.compile(DECLARATIONS_REGEXP)
keywords_ptrn = re.compile(KEYWORDS_REGEXP)

todo_cmmt_ptrn = re.compile(TODO_COMMENT_REGEXP)
sep_space_ptrn = re.compile(SEP_BY_SPACE_REGEXP)

code_regexp = [c_dirs_ptrn, func_ptrn, func_hdr_ptrn, asg_ptrn,
dec_asg_ptrn, func_call_ptrn, dec_ptrn, keywords_ptrn]

# Types
_BLOCK_CMMT = 0
_CMMT = 1
_DIRECTIVE = 2
_CONDITIONAL = 3
_UNCONDITIONAL = 4
_FUNC = 5
_STATEMENT = 6
_STRUCTURE = 7      # Anything within curly braces that is not a function defn
_EMPTY_LINE = 8
_SWITCH_CASE = 9


CONDITIONALS = ["while", "for", "switch", "if", "else if"]
UNCONDITIONALS = ["else", "do"]
SWITCH_CASE = ["case", "default"]
OTHERS = ["break"]

# DECLARATIONS_REGEXP = " *(union | struct | enum |)[a-zA-Z_][a-zA-Z0-9_]* [a-zA-Z_][a-zA-Z0-9_]*;"

LINE_LIMIT = 80
TAB_LENGTH = 2
NEWLINES_LIMIT = 2
NON_MAGIC_NUMBERS = [
    '0', '-1', '1', '\"\\n\"', '\'\\n\'', '\'\\0\'',
    '\"r\"', '\"w\"', '\"a\"', '\"r+\"', '\"w+\"', '\"a+\"', 
    '\"rb\"', '\"wb\"', '\"ab\"', '\"r+b\"', '\"w+b\"', '\"a+b\"', 
    '\"rb+\"', '\"wb+\"', '\"ab+\"'
    # Note there are more but these are the ones for now
]

matchers = {
    '{': '}',
    '(': ')',
    '/*': '*/'
}


class CodeBlock(object):
    def __init__(self, lines, t):
        self.lines = lines
        self._type = t

        # Used to store the keyword (aka switch/if/else/etc...)
        self.keyword = None

        # Location represented as tuple of (line number, index in line)
        # Note that end location is INCLUSIVE
        self.start = None
        self.end = None
        self.term_loc = None

        # If the code block has a condition include that too
        # End location is INCLUSIVE
        self.start_cond = None
        self.end_cond = None

        # Block location is stored as a tuple of (location, location)
        # where each location is a tuple of (line number, index in line)
        # This field is available if the block uses curly braces surrounded code
        self.block_loc = None

        # Flag set to indicate that the block uses curly brace. Some blocks
        # do not need curly brace like (if/else) so we need this
        self.uses_curly = False

        # Used only to store location of while in do while loop
        self.do_while_loc = None

        # Used for else if and else to record the location of the }
        # from the previous if/else if
        self.prev_rcurly = None

        # Used for functions only
        self.start_params = None
        self.end_params = None

        # For switch case
        self.colon_loc = None

    def get_type(self):
        return self._type

class CStyleChecker(object):
    def __init__(self, filename, check_whitespace=True,
                 print_headers=False, strict=False):
        self.check_ws = check_whitespace
        self.print_headers = print_headers
        self.strict = strict
        self.og_lines = []
        self.lines = []
        self.indent_amt = TAB_LENGTH
        self.block_cmmts = []

        try:
            f = open(filename, "r")
        except IOError:
            print('Could not open file')
            sys.exit(1)

        l = f.readline()
        while l:
            if l[-1] == '\n':
                l = l[:-1]
            self.og_lines.append(l)
            self.lines.append(l.replace(TAB_CHAR, SPACE_CHAR * TAB_LENGTH))
            l = f.readline()

        f.close()

        # Preprocessing Stuff
        self.get_block_comments()

        # Find the first indented line to figure out the indent amount
        i = 0
        while i < len(self.lines):
            block = self.parse_line(i)
            t = block.get_type()
            if t == _FUNC:
                term_line, term_ind = block.term_loc[0], block.term_loc[1]
                # Use the first non empty line as the basis for indent amount
                j = term_line + 1
                while j < len(self.lines) and len(self.lines[j].lstrip()) == 0:
                    j += 1

                if j < len(self.lines):
                    next_line = self.lines[j]
                    self.indent_amt = len(next_line) - len(next_line.lstrip())
                else:
                    self.indent_amt = TAB_LENGTH
                break

            i = block.lines[-1] + 1

        # Loop through to see which switch indentation convention
        # they use
        for i, line in enumerate(self.lines):
            keyword, switch_ind = self.match_keywords(line, i)
            if keyword == "switch":
                # Find a case
                term_line, term_ind = self.find_statement_terminator(i, switch_ind, 
                                        term=COLON)
                j = term_line + 1
                while j < len(self.lines):
                    keyword, case_ind = self.match_keywords(self.lines[j], j)
                    if keyword in SWITCH_CASE:
                        if case_ind - switch_ind == 0:
                            # Case where they do not indent switch case
                            self.case_indent = 0
                        else:
                            # Case where they do indent switch case
                            self.case_indent = self.indent_amt
                    j += 1

    def override_indent_amt(self, indent_amt):
        self.indent_amt = indent_amt
        if self.case_indent != 0:
            self.case_indent = self.indent_amt

    def get_block_comments(self):
        start = None

        for i in range(len(self.lines)):
            line = self.lines[i]
            for j in range(len(line)-1):
                if line[j:j+2] == START_BLOCK_COMMENT:
                    if self.valid_string(line, i, j, j+2):
                        start = (i, j)
                elif line[j:j+2] == END_BLOCK_COMMENT:
                    end = (i, j+2)
                    self.block_cmmts.append((start, end))

    def get_indent_amt(self, n):
        stripped = self.lines[n].lstrip()
        return len(self.lines[n]) - len(stripped)

    def is_code(self, s):
        for ptrn in code_regexp:
            match = ptrn.match(s)
            if match:
                return match
        return None

    # A string is considered valid if they are not within quotes and not
    # within comments
    def valid_string(self, s, n, lo, hi):
        return not self.within_quotes(s, lo, hi) and not self.within_comment(s, n, lo, hi)

    def contains_magic(self, line, n):
        # Hack: Add a space at the beginning so the regexp works
        line = ' ' + line
        matches = magic_num_ptrn.finditer(line)
        for match in matches:
            number = match.group(NUM_GROUP_IND)
            if number not in NON_MAGIC_NUMBERS:
                lo, hi = match.start(NUM_GROUP_IND), match.end(NUM_GROUP_IND)
                in_comment = self.within_comment(line, n, lo, hi)
                if not in_comment:
                    return True

        in_quote = False
        index = line.find(DOUBLE_QUOTE)
        if index != -1:
            prev_quote = index
            # Check for strings on this line
            for i in range(index, len(line)):
                if line[i] == DOUBLE_QUOTE and (i == 0 or line[i-1] != BACKSLASH):
                    if in_quote:
                        in_quote = False
                        # Check if the string found is non magic string
                        if line[prev_quote:i+1] not in NON_MAGIC_NUMBERS:
                            index = line.find(line[prev_quote:i+1])
                            lo, hi = index, index + len(line[prev_quote:i+1])
                            in_comment = self.within_comment(line, n, lo, hi)
                            if not in_comment:
                                return True
                    else:
                        in_quote = True
                        prev_quote = i
        
        index = line.find(SINGLE_QUOTE)
        if index != -1:
            prev_quote = index
            # Check for strings on this line
            for i in range(index, len(line)):
                if line[i] == SINGLE_QUOTE and (i == 0 or line[i-1] != BACKSLASH):
                    if in_quote:
                        in_quote = False
                        # Check if the char found is non magic char
                        if line[prev_quote:i+1] not in NON_MAGIC_NUMBERS:
                            index = line.find(line[prev_quote:i+1])
                            lo, hi = index, index + len(line[prev_quote:i+1])
                            in_comment = self.within_comment(line, n, lo, hi)
                            if not in_comment:
                                return True
                    else:
                        in_quote = True
                        prev_quote = i

        return False

    # Check if the comment contains TODO or code in it
    def check_comment(self, s, n):
        strip = s.lstrip()
        strip = strip.lstrip(FORWARD_SLASH)
        if self.is_code(strip):
            print('Line %d: Commented out code' % (n+1))
            print(self.lines[n])

        if todo_cmmt_ptrn.match(s):
            print('Line %d: Left in TODO comment' % (n+1))
            print(self.lines[n])

    def within_quotes(self, s, lo, hi):
        # Capture ranges that are within a string
        ranges = []
        index = s.find(DOUBLE_QUOTE)
        if index == -1:
            return False

        # Look for matching double quotes that are not escaped
        in_quote = False
        prev_quote = index
        for i in range(index, len(s)):
            # Check if char at index i is a double quotes that is not escaped
            if s[i] == DOUBLE_QUOTE and (i == 0 or s[i-1] != BACKSLASH):
                if in_quote:
                    in_quote = False
                    ranges.append((prev_quote, i+1))
                else:
                    in_quote = True
                    prev_quote = i

        # If the range is within the quotes
        return any([lo >= left and hi < right for (left, right) in ranges])

    # s is the line, n is the line number
    def within_comment(self, s, n, lo, hi):
        # Look left from lo to check for //
        in_quote = False
        for i in reversed(range(1, lo)):
            if not in_quote and (s[i-1] + s[i]) == START_COMMENT:
                return True
            if s[i] == DOUBLE_QUOTE and (i == 0 or s[i-1] != BACKSLASH):
                if in_quote:
                    in_quote = False
                else:
                    in_quote = True

        # Check if the string is within a block comment
        for (start, end) in self.block_cmmts:
            start_line, start_ind = start[0], start[1]
            end_line, end_ind = end[0], end[1]
            # If line is within range
            if n >= start_line and n <= end_line:
                if n == start_line and start_line == end_line:
                    if lo >= start_ind and hi < end_ind:
                        return True
                elif n == start_line:
                    if lo >= start_ind:
                        return True
                elif n == end_line:
                    if hi < end_ind:
                        return True
                else:
                    return True

        return False

    # Given two locations, figure out if they are only separated by a space
    def within_one_space(self, loc1, loc2):
        if loc1[0] != loc2[0]:
            return False

        if loc1[1] < loc2[1]:
            return sep_space_ptrn.match(self.lines[loc1[0]][loc1[1]:loc2[1]+1])
        else:
            return sep_space_ptrn.match(self.lines[loc1[0]][loc2[1]:loc1[1]+1])

    def match_keywords(self, line, n):
        for j in range(len(line)):
            for keyword in CONDITIONALS + UNCONDITIONALS + SWITCH_CASE + OTHERS:
                if len(line) <= len(keyword):
                    if line.startswith(keyword):
                        return keyword, 0
                else:
                    if line[j:j+len(keyword)] == keyword:
                        # Look to the left and right to see if it is part of a variable
                        # name
                        left = True
                        right = True
                        if j != 0:
                            left = line[j-1] not in VARS_ALLOWED_CHARS
                        if j + len(keyword) < len(line):
                            right = line[j+len(keyword)] not in VARS_ALLOWED_CHARS

                        if left and right:
                            # Check if it's part of a comment
                            if self.valid_string(line, n, j, j+len(keyword)):
                                return keyword, j

        return None, -1

    # Look for matching pair of {} () etc...
    # l1 j1 l2 j2 indicate start and end locations
    def match_terms(self, l1, j1, l2, j2, term):
        assert term in matchers
        match = matchers[term]
        # Use this value to account for when match is longer than 1 char
        lookahead = len(match) - 1
        start = 0
        prev = None
        for line_n in range(l1, l2+1):
            line = self.lines[line_n]
            lo = j1 if line_n == l1 else 0
            hi = j2-lookahead if line_n == l2 else len(line) - lookahead
            for j in range(lo, hi):
                if line[j:j+len(term)] == term and\
                        self.valid_string(line, line_n, j, j+len(term)):
                    start += 1
                    if prev is None:
                        prev = (line_n, j)
                elif line[j:j+len(match)] == match and\
                        self.valid_string(line, line_n, j, j+len(match)):
                    start -= 1
                    if start == 0:
                        return prev, (line_n, j)

        return None, None

    # Look for either the ; or {.
    # If include_keywords, will also look for the keywords on the following lines
    def find_statement_terminator(self, n, start, term=None, include_keywords=False):
        keywords = CONDITIONALS + UNCONDITIONALS + SWITCH_CASE + OTHERS
        for line_n in range(n, len(self.lines)):
            lo = start if line_n == n else 0
            line = self.lines[line_n]
            for j in range(lo, len(line)):
                if term is None:
                    if line[j] in (LEFT_CURLY, SEMICOLON):
                        if self.valid_string(line, line_n, j, j+1):
                            return line_n, j
                else:
                    if line[j] in term:
                        if self.valid_string(line, line_n, j, j+1):
                            return line_n, j

                if include_keywords:
                    for keyword in keywords:
                        if line[j:j+len(keyword)] == keyword and\
                                self.valid_string(line, line_n, j, j+len(keyword)):
                            return line_n, j

        return -1, -1

    # Look from right to left for the term
    def rfind_statement_terminator(self, n, start, term):
        for line_n in reversed(range(n+1)):
            line = self.lines[line_n]
            hi = start+1 if line_n == n else len(line)
            for j in range(hi):
                if line[j] in term and self.valid_string(line, line_n, j, j+1):
                    return line_n, j
        return -1, -1

    # Look for the beginning ( and end ) of a condition
    # Return two tuples, of location of ( and location of )
    def find_condition(self, n, start):
        return self.match_terms(n, start,
                                len(self.lines)-1, len(self.lines[-1]),
                                LEFT_PAREN)

    # Find all lines of code within curly braces
    # Argument n, start specifies the first curly brace
    def find_code_block(self, n, start):
        assert self.lines[n][start] == LEFT_CURLY
        return self.match_terms(n, start,
                                len(self.lines)-1, len(self.lines[-1]),
                                LEFT_CURLY)

    # Generate a string parallel to the passed in string with ^ at passed in indices
    def generate_guide(self, s, indices):
        return "".join(['^' if i in indices else ' ' for i in range(len(s))])

    # Check what kind of statement starting from this line
    # Return group of lines that belong to that statement and the type
    def parse_line(self, n):
        og_line = self.lines[n]
        line = og_line.lstrip()    # Strip white space to the left
        group = []

        if len(line) == 0:
            group.append(n)
            # If lines below are empty, add them to the group
            for line_n in range(n+1, len(self.lines)):
                if len(self.lines[line_n].lstrip()) == 0:
                    group.append(line_n)
                else:
                    break
            block = CodeBlock(group, _EMPTY_LINE)
            return block

        match = cmmt_ptrn.match(line)
        if match:
            block = CodeBlock([n], _CMMT)
            # Find where the / starts
            block.start = (n, og_line.find(FORWARD_SLASH))
            block.end = (n, len(og_line)-1)
            return block

        match = blck_cmmt_ptrn.match(line)
        if match:
            # Find the end of the comment block
            start = og_line.find(START_BLOCK_COMMENT)
            for line_n in range(n, len(self.lines)):
                lo = start+2 if line_n == n else 0
                for j in range(lo, len(self.lines[line_n])-1):
                    pair = self.lines[line_n][j:j+2]
                    if pair == END_BLOCK_COMMENT:
                        # Found the end of the comment block
                        group.append(line_n)
                        block = CodeBlock(group, _BLOCK_CMMT)
                        block.start = (n, start)
                        block.end = (line_n, j+1)
                        return block

                group.append(line_n)

        keyword, index = self.match_keywords(og_line, n)
        if keyword:
            if keyword in CONDITIONALS:
                block = CodeBlock(group, _CONDITIONAL)
                block.keyword = keyword
                # Start of the keyword
                block.start = (n, index)

                start, end = self.find_condition(n, index)
                block.start_cond = start
                block.end_cond = end
                # All line numbers from start of condition keyword to end of condition
                line_nums = [_ for _ in range(n, end[0]+1)]
                group.extend(line_nums)

                l, j = self.find_statement_terminator(end[0], end[1])
                block.term_loc = (l, j)
                if self.lines[l][j] == LEFT_CURLY:
                    block.uses_curly = True

                    # Get start and end of code block
                    code_start, code_end = self.find_code_block(l, j)
                    block.block_loc = (code_start, code_end)
                    block.end = code_end
                    # Add all lines up to the matching right curly brace (inclusive)
                    group.extend([_ for _ in range(end[0]+1, code_end[0]+1)])
                else:   # Terminator is semicolon
                    # Add all lines from one past the condition right paren up to
                    # the semicolon
                    group.extend([_ for _ in range(end[0]+1, l+1)])
                    block.end = (l, j)

                if block.keyword == "else if":
                    # Look for }
                    l, j = self.rfind_statement_terminator(block.start[0],
                                                           block.start[1],
                                                           term=[RIGHT_CURLY, SEMICOLON])
                    # Check if it's } since the previous block could possibly not use
                    # curly braces
                    if self.lines[l][j] == RIGHT_CURLY:
                        block.prev_rcurly = (l, j)

                return block
            elif keyword in UNCONDITIONALS:
                block = CodeBlock(group, _UNCONDITIONAL)
                block.keyword = keyword
                block.start = (n, index)

                # Find left curly brace or semicolon
                l, j = self.find_statement_terminator(n, 0)
                block.term_loc = (l, j)

                # If do while loop, look for the semicolon after while
                if keyword == "do":
                    block.uses_curly = True

                    # Get start and end of code block
                    code_start, code_end = self.find_code_block(l, j)
                    block.block_loc = (code_start, code_end)

                    # Look for while
                    while_l, while_j = self.find_statement_terminator(code_end[0],
                                                                      code_end[1],
                                                                      include_keywords=True)
                    # Make sure that it is while
                    assert self.lines[while_l][while_j:while_j+len("while")] == "while"

                    block.do_while_loc = (while_l, while_j)
                    start_cond, end_cond = self.find_condition(while_l, while_j)
                    block.start_cond = start_cond
                    block.end_cond = end_cond
                    # Look for semi colon after condition
                    l, j = self.find_statement_terminator(end_cond[0], end_cond[1], term=SEMICOLON)
                    end = (l, j)
                    block.end = end
                    group.extend([_ for _ in range(n, end[0]+1)])
                    return block
                else:
                    if self.lines[l][j] == LEFT_CURLY:
                        block.uses_curly = True
                        # Get start and end of code block
                        code_start, code_end = self.find_code_block(l, j)
                        block.block_loc = (code_start, code_end)
                        block.end = code_end

                        # Add all lines up to the matching right curly brace (inclusive)
                        group.extend([_ for _ in range(n, code_end[0]+1)])
                    else:   # Terminator is semicolon
                        # Add all lines from one past the condition right paren up to
                        # the semicolon
                        block.end = (l, j)
                        group.extend([_ for _ in range(n, l+1)])

                    if block.keyword == "else":
                        # Look for }
                        l, j = self.rfind_statement_terminator(block.start[0],
                                                               block.start[1],
                                                               term=[RIGHT_CURLY, SEMICOLON])
                        # Check if it's } since the previous block could possibly not use
                        # curly braces
                        if self.lines[l][j] == RIGHT_CURLY:
                            block.prev_rcurly = (l, j)
                    return block
            elif keyword in SWITCH_CASE:    # Keyword is case or default
                block = CodeBlock(group, _SWITCH_CASE)
                block.keyword = keyword
                block.start = (n, index)

                # Must get all the statements that belong to this case
                # that means look for the next case or look for the end of switch (})

                # Look for colon
                term_line, term_ind = self.find_statement_terminator(n, index, term=COLON)
                block.term_loc = (term_line, term_ind)
                block.colon_loc = block.term_loc

                # Look for curly brace if the case uses curly brace. This includes
                # keywords so we will know if we run into another block that uses curly
                # brace, not to confuse with the curly brace of the case. If it runs
                # into a curly brace first, then the case uses curly brace
                term_line, term_ind = self.find_statement_terminator(term_line, 
                    term_ind+1, term=[LEFT_CURLY, SEMICOLON], include_keywords=True)
                uses_curly = self.lines[term_line][term_ind] == LEFT_CURLY
                block.uses_curly = uses_curly
                if uses_curly:
                    # Update block terminator location to the curly
                    block.term_loc = (term_line, term_ind)

                count = 1   # Curly brace count starts at 1 because we are within switch
                lo = block.term_loc[0]
                for line_n in range(lo, len(self.lines)):
                    line = self.lines[line_n]
                    # If we don't use curly then if we run into another case, then
                    # we are at the next case
                    if not uses_curly:
                        # We only match from the terminator location on if it's the first
                        # line. Or else it would match the first line
                        start = block.term_loc[1]+1 if line_n == lo else 0
                        match = switch_case_regexp.match(self.lines[line_n][start:])
                        if match:   # If there is a match, we are at the next case
                            break

                    # Start at +1 since we don't want to match the { since count
                    # starts at 1
                    start = block.term_loc[1] + 1 if line_n == lo else 0
                    # Look for matching right curly brace for the switch statement.
                    # If there is one, then this is the last case in the switch
                    for j in range(start, len(line)):
                        if line[j] == LEFT_CURLY:
                            # Check if the curly is in a comment or in string
                            if self.valid_string(line, line_n, j, j+1):
                                count += 1
                        elif line[j] == RIGHT_CURLY:
                            # Check if the curly is in a comment or in string
                            if self.valid_string(line, line_n, j, j+1):
                                count -= 1
                                if count == 0:
                                    if not uses_curly:
                                        # Include the line with the right brace only if
                                        # it contains statements from the current case
                                        match = white_space_ptrn.match(line[:j])
                                        if match is None:
                                            group.append(line_n)
                                    else:
                                        block.end = (line_n, j)
                                        block.block_loc = (block.term_loc, block.end)
                                        group.append(line_n)

                                    return block

                    group.append(line_n)

                return block

        match = c_dirs_ptrn.match(line)
        if match:
            block = CodeBlock(group, _DIRECTIVE)
            block.start = (n, og_line.find(POUND))
            # C Directive
            for line_n in range(n, len(self.lines)):
                line = self.lines[line_n]
                group.append(line_n)
                # Check if this directive was escaped and break if it is not
                # since the next line won't be part of the directive
                l = line.rstrip()
                if not l.endswith(BACKSLASH):
                    block.end = (line_n, len(line))
                    break

            return block

        # Either regular statements or function definition
        l, j = self.find_statement_terminator(n, 0)
        code = "".join([self.lines[_] for _ in range(n, l+1)])
        if func_ptrn.match(code) and not func_hdr_ptrn.match(code):
            block = CodeBlock(group, _FUNC)
            index = len(og_line) - len(og_line.lstrip())
            block.start = (n, index)

            # Function definition
            # It is possible that the function was declared in this way
            # In which case, terminator is ;. Solve this by force finding {
            # int foo(c) int c; {}

            l, j = self.find_statement_terminator(l, j, term=LEFT_CURLY)
            block.term_loc = (l, j)
            if l == -1:
                print(self.lines[n])
                print('Program ran into an error')
                sys.exit(1)

            # Find parameters start and end
            start_params, end_params = self.match_terms(block.start[0], block.start[1],
                                                        l, j, term=LEFT_PAREN)
            block.start_params, block.end_params = start_params, end_params

            start, end = self.find_code_block(l, j)
            block.block_loc = (start, end)
            block.end = end
            block.uses_curly = True
            group.extend([_ for _ in range(n, end[0]+1)])
            return block
        else:   # Either structure or regular statement
            index = len(og_line) - len(og_line.lstrip())
            if self.lines[l][j] == LEFT_CURLY:
                block = CodeBlock(group, _STRUCTURE)
                block.start = (n, index)

                # Structure
                start, end = self.find_code_block(l, j)
                block.block_loc = (start, end)
                block.end = end
                group.extend([_ for _ in range(n, end[0]+1)])
                block.uses_curly = True
                return block
            else:   # Semicolon
                block = CodeBlock(group, _STATEMENT)
                block.start = (n, index)
                block.end = (l, j)

                group.extend([_ for _ in range(n, l+1)])
                return block

    def print_lines(self, lines, print_n=False):
        for line_n in lines:
            if print_n:
                print('%d\t\t%s' % (line_n+1, self.lines[line_n]))
            else:
                print(self.lines[line_n])

    # General case indentation
    # all_exact parameter will make the function do a strict check
    # with exact indentation match
    # relax parameter will only check if the actual indent amount is at least 
    # up to the indent_amt
    def check_indentation(self, lines, indent_amt, all_exact=False, relax=False):
        indent_error = False
        for line_n in lines:
            # Replace tabs with spaces
            line = self.lines[line_n]
            # Ignore if the line is whitespace only
            if white_space_ptrn.match(line):
                block = CodeBlock([line_n], _EMPTY_LINE)
                self.handle_whitespace(block)
                continue

            stripped_line = line.lstrip()
            actual_indent_amt = len(line) - len(stripped_line)
            if all_exact:
                if actual_indent_amt != indent_amt:
                    indent_error = True
            elif relax:
                if actual_indent_amt < indent_amt:
                    indent_error = True
            else:
                if line_n == lines[0]:
                    # For the first line, the statement start exactly at indent_amt
                    if actual_indent_amt != indent_amt:
                        indent_error = True
                else:
                    # For any other line, the statement must be indented
                    # at least indent_amt in
                    if actual_indent_amt < indent_amt:
                        indent_error = True

        if indent_error:
            if len(lines) > 1:
                print('Line %d to %d: Inconsistent Indentation' % (lines[0]+1, lines[-1]+1))
            else:
                print('Line %d: Inconsistent Indentation' % (lines[0]+1))
            self.print_lines(lines)

    def check_magic(self, lines):
        for line_n in lines:
            has_magic = self.contains_magic(self.lines[line_n], line_n)
            if has_magic:
                print('Line %d: Contains magic number/word' % (line_n+1))
                print(self.lines[line_n])

    # General case: Handling group of lines with t being the type that
    # the lines belong to
    def handle_block(self, block, indent_amt, check_magic=True, in_switch=False):
        t = block.get_type()
        if t == _BLOCK_CMMT:
            return self.handle_block_comment(block, indent_amt)
        elif t == _CMMT:
            return self.handle_comment(block, indent_amt, in_switch)
        elif t == _DIRECTIVE:
            return self.handle_directive(block, indent_amt)
        elif t == _CONDITIONAL:
            return self.handle_cond(block, indent_amt)
        elif t == _UNCONDITIONAL:
            return self.handle_uncond(block, indent_amt)
        elif t == _FUNC:
            return self.handle_func(block, indent_amt)
        elif t == _STATEMENT:
            return self.handle_statement(block, indent_amt, check_magic)
        elif t == _STRUCTURE:
            return self.handle_structure(block, indent_amt, check_magic)
        elif t == _EMPTY_LINE:
            return self.handle_whitespace(block)
        elif t == _SWITCH_CASE:
            return self.handle_switch_case(block, indent_amt)

        return None

    def handle_trailing_string(self, trail, n, terminator):
        if len(trail) != 0:
            # Trailing white space is more than 1 space char
            if white_space_ptrn.match(trail):
                if len(trail) > 1 and self.check_ws:
                    print('Line %d: Extra white space behind %s' % (n+1, terminator))
                    print(self.lines[n])
            else:
                # Check if the trailing string is a comment. If it is then it's fine
                if not cmmt_ptrn.match(trail):
                    print('Line %d: Statements behind %s should be '\
                        'on the next line' % (n+1, terminator))
                    print(self.lines[n])
                else:
                    # Check if the comment is a todo comment or commented out code
                    self.check_comment(trail, n)

    def handle_leading_string(self, leading, n, terminator, indent_amt):
        if len(leading) != 0:
            if white_space_ptrn.match(leading):
                self.check_indentation([n], indent_amt)
            else:
                print('Line %d: %s should be on the next line' % (n+1, terminator))

    # Handle style checking around the terminator { or ;
    # If {, then it will check the curly brace indentation. Returns None
    # If ;, then it will simply handle the statement that follows up to that ;
    # Returns the line number to follow if ;
    def handle_terminator(self, lines, term_line, term_ind, indent_amt):
        # Check indentation up to the terminator
        # Two cases: { is on the same line as the conditional statement
        # or { is on the next line
        if self.lines[term_line][term_ind] == LEFT_CURLY:
            # Check indentation up to the terminator
            # Two cases: { is on the same line as the conditional statement
            # or { is on the next line
            line = self.lines[term_line]
            if white_space_ptrn.match(line[:term_ind]):
                # Case 1: { on next line. Need to specifically check
                # if the indent amount == indent_amt
                check_lines = [_ for _ in range(lines[0], term_line)]
                self.check_indentation(check_lines, indent_amt)
                self.check_indentation([term_line], indent_amt)
            else:
                # Case 2: { on the same line as condition.
                check_lines = [_ for _ in range(lines[0], term_line+1)]
                self.check_indentation(check_lines, indent_amt)

            after = self.lines[term_line][term_ind+1:]
            self.handle_trailing_string(after, term_line, LEFT_CURLY)
            return None
        else:   # Semicolon or keywords
            # If the terminator is a keyword, then we have to check indentation
            # If not, then handle group will do the indentation check
            if self.lines[term_line][term_ind] != SEMICOLON:
                self.check_indentation([term_line], indent_amt+self.indent_amt)

            # Condition statement and the following statement is on the same
            # line. For example: if (condition) print(something);
            if term_line == lines[0]:
                return term_line + 1
            
            # Must handle case where we have
            # if (condition1)
            #   if (condition2)
            #     statement;
            block = self.parse_line(term_line)
            return self.handle_block(block, indent_amt+self.indent_amt)

    def handle_end_block(self, block, indent_amt):
        curly_start, curly_end = block.block_loc[0], block.block_loc[1]
        last_line = self.lines[curly_end[0]]
        before = last_line[:curly_end[1]]
        # First check the part before the } for code
        self.handle_leading_string(before, curly_end[0], RIGHT_CURLY, indent_amt)

        # Skip trailing check for do while since while is behind the curly
        if block.keyword == "do":
            return None

        # Check the part behind } for keywords
        after = last_line[curly_end[1]+1:]
        if len(after) != 0:
            # If the after part is not a comment
            if not cmmt_ptrn.match(after) and not blck_cmmt_ptrn.match(after):
                keyword, index = self.match_keywords(after, curly_end[0])
                # If there is a keyword, return this line so that
                # that could be parsed later
                if keyword:
                    return keyword
                elif block.get_type() != _STRUCTURE:
                    self.handle_trailing_string(after, curly_end[0], RIGHT_CURLY)
        return None

    def handle_if_else_spacing(self, block):
        loc1 = block.prev_rcurly
        loc2 = (block.start[0], block.start[1])
        if not self.within_one_space(loc1, loc2):
            line = self.lines[block.start[0]]
            if loc1[0] != loc2[0]:
                print('Line %d to %d: %s block must start on the same line as the '
                      'curly brace of the previous if/else if block'\
                      % (loc1[0]+1, loc2[0]+1, block.keyword))
                self.print_lines([_ for _ in range(block.prev_rcurly[0],
                                                   block.start[0]+1)])
            else:
                print('Line %d: %s block must start within one space of }'\
                      % (block.start[0]+1, block.keyword))
                print(line)
                print(self.generate_guide(line, [loc1[1], loc2[1]]))

    def handle_curly_brace_spacing(self, block):
        if block.get_type() == _CONDITIONAL:
            loc1 = block.end_cond
        elif block.get_type() == _SWITCH_CASE:
            loc1 = block.colon_loc
        else:
            end = block.start[1] + len(block.keyword) - 1
            loc1 = (block.start[0], end)

        loc2 = block.block_loc[0]
        if not self.within_one_space(loc1, loc2):
            line = self.lines[loc1[0]]
            if loc1[0] != loc2[0]:
                print('Line %d to %d: { must be on the same line after the '
                      'end of %s condition'
                      % (loc1[0]+1, loc2[0]+1, block.keyword))
                self.print_lines([_ for _ in range(loc1[0], loc2[0]+1)])
            else:
                print('Line %d: ) and { must be separated with a space'
                      % (loc1[0]+1))
                print(line)
                print(self.generate_guide(line, [loc1[1], loc2[1]]))

    def handle_block_comment(self, block, indent_amt):
        lines = block.lines
        indent_error = False
        for line_n in lines:
            # Replace tabs with spaces
            line = self.lines[line_n]
            stripped_line = line.lstrip()

            # Ignore if the line is empty
            if len(stripped_line) == 0:
                continue

            actual_indent_amt = len(line) - len(stripped_line)
            if line_n == lines[0]:
                # For the first line, the / should be == indent_amt
                if actual_indent_amt != indent_amt:
                    indent_error = True
            else:
                # For any other line, the * should line up, so indent
                # amount should be == indent_amt + 1
                # Only check this if they start the comment block with *
                if stripped_line[0] == ASTERISK:
                    if actual_indent_amt != indent_amt + 1:
                        indent_error = True

        if indent_error:
            if len(lines) > 1:
                print('Line %d to %d: Inconsistent Indentation' % (lines[0]+1, lines[-1]+1))
            else:
                print('Line %d: Inconsistent Indentation' % (lines[0]+1))
            self.print_lines(lines)

        last_line = self.lines[lines[-1]]
        index = last_line.find(END_BLOCK_COMMENT)
        if index != -1:
            after = last_line[index+2:]
            self.handle_trailing_string(after, lines[-1], END_BLOCK_COMMENT)

            # Return the next line number
            return lines[-1] + 1

        # This should not happen given the code compiles
        return None

    def handle_comment(self, block, indent_amt, in_switch=False):
        lines = block.lines
        if in_switch:
            indent_amt = indent_amt + self.case_indent
            # Relax the indentation check if inside switch
            self.check_indentation(lines, indent_amt, relax=True)
        else:
            self.check_indentation(lines, indent_amt)

        # Check for TODO and commented out code
        self.check_comment(self.lines[lines[0]], lines[0])

        return lines[0] + 1

    def handle_directive(self, block, indent_amt):
        lines = block.lines
        self.check_indentation(lines, indent_amt)
        return lines[-1] + 1

    def handle_switch_case(self, block, indent_amt):
        lines = block.lines
        switch_indent = indent_amt
        indent_amt = indent_amt + self.case_indent

        if block.uses_curly and self.strict:
            self.handle_curly_brace_spacing(block)

        # Look for colon
        term_line, term_ind = block.term_loc[0], block.term_loc[1]
        self.check_magic([_ for _ in range(lines[0], term_line+1)])

        # Check behind colon or curly brace for anything
        line = self.lines[term_line]
        after = line[term_ind+1:]
        self.handle_trailing_string(after, term_line, line[term_ind])

        # Parse the statements for this case
        i = term_line + 1
        # If uses curly, we only go up to the second to last line
        k = lines[-1]-1 if block.uses_curly else lines[-1]
        while i < len(self.lines) and i <= k:
            n_block = self.parse_line(i)
            if n_block.get_type() == _CMMT:
                i = self.handle_block(n_block, switch_indent, in_switch=True)
            else:
                i = self.handle_block(n_block, indent_amt+self.indent_amt, in_switch=True)

        keyword = None
        if block.uses_curly:
            keyword = self.handle_end_block(block, indent_amt)
            if keyword:
                print('Line %d: Next case statement should be on the next line'\
                            % (lines[-1]+1))
                print(self.lines[lines[-1]])

        return lines[-1] if keyword else lines[-1] + 1

    # Anything with conditions (while, for, if, else if, switch)
    # indent_amt passed in is the indent amount of the code within
    # the condition statements, not the first line itself
    def handle_cond(self, block, indent_amt):
        lines = block.lines
        is_switch = block.keyword == "switch"

        # Check if condition contains magic number
        self.check_magic([_ for _ in range(lines[0], block.end_cond[0]+1)])

        if self.strict:
            self.handle_cond_strict(block, indent_amt)

        ret = self.handle_terminator(lines, block.term_loc[0],
                                     block.term_loc[1], indent_amt)
        if ret:
            return ret

        i = block.term_loc[0] + 1
        while i < len(self.lines) and i < lines[-1]:
            n_block = self.parse_line(i)
            n_indent_amt = indent_amt if is_switch else indent_amt+self.indent_amt
            i = self.handle_block(n_block, n_indent_amt, in_switch=is_switch)

        keyword = self.handle_end_block(block, indent_amt)
        return lines[-1] if keyword else lines[-1] + 1

    def handle_cond_strict(self, block, indent_amt):
        # 1: Condition must start 1 space in from the keyword
        loc1 = (block.start[0], block.start[1]+len(block.keyword)-1)
        loc2 = block.start_cond
        if not self.within_one_space(loc1, loc2):
            line = self.lines[loc1[0]]
            print('Line %d: %s and (condition) must be separated with a space'
                  % (block.start_cond[0]+1, block.keyword))
            print(line)
            print(self.generate_guide(line, [loc1[1], loc2[1]]))

        if block.uses_curly:
            self.handle_curly_brace_spacing(block)
        else:
            # 2: Should use curly braces for if/else/etc...
            print('Line %d: %s should use curly braces'
                  % (block.start[0]+1, block.keyword))
            print(self.lines[block.start[0]])

        # 3: Check for else if that the right curly brace of the previous
        #    if/else if is on the same line and within one space
        if block.keyword == "else if" and block.prev_rcurly is not None:
            self.handle_if_else_spacing(block)

    def handle_uncond(self, block, indent_amt):
        lines = block.lines

        if self.strict:
            self.handle_uncond_strict(block, indent_amt)

        ret = self.handle_terminator(lines, block.term_loc[0],
                                     block.term_loc[1], indent_amt)
        if ret:     # Will only be true if terminator != {
            return ret

        i = block.term_loc[0] + 1
        while i < len(self.lines) and i < lines[-1]:
            n_block = self.parse_line(i)
            i = self.handle_block(n_block, indent_amt+self.indent_amt)

        keyword = self.handle_end_block(block, indent_amt)
        if keyword == "do":
            # If it is do while, check the while condition for magic
            # number
            self.check_magic([block.do_while_loc[0]])

        return lines[-1] if keyword else lines[-1] + 1

    def handle_uncond_strict(self, block, indent_amt):
        if block.uses_curly:
            self.handle_curly_brace_spacing(block)
        elif block.keyword == "else":
            print('Line %d: %s should use curly braces'
                  % (block.start[0]+1, block.keyword))
            print(self.lines[block.start[0]])

        if block.keyword == "else" and block.prev_rcurly is not None:
            self.handle_if_else_spacing(block)

    def handle_func(self, block, indent_amt):
        lines = block.lines
        term_line, term_ind = block.term_loc[0], block.term_loc[1]
        self.check_magic([_ for _ in range(lines[0], term_line+1)])

        line = self.lines[term_line]
        if white_space_ptrn.match(line[:term_ind]):
            # { is by itself on a line
            check_lines = [_ for _ in range(lines[0], term_line)]
            self.check_indentation(check_lines, indent_amt)
            self.check_indentation([term_line], indent_amt)
        else:
            # { is on the same line as function header
            check_lines = [_ for _ in range(lines[0], term_line+1)]
            self.check_indentation(check_lines, indent_amt)

        i = term_line + 1
        while i < len(self.lines) and i < lines[-1]:
            n_block = self.parse_line(i)
            i = self.handle_block(n_block, indent_amt+self.indent_amt)

        self.check_indentation([lines[-1]], indent_amt)
        return lines[-1] + 1

    def handle_statement(self, block, indent_amt, check_magic=True):
        lines = block.lines
        self.check_indentation(lines, indent_amt)
        # Check for magic number
        if check_magic:
            self.check_magic(lines)

        after = self.lines[block.end[0]][block.end[1]+1:]
        term = self.lines[block.end[0]][block.end[1]]
        self.handle_trailing_string(after, block.end[0], term)
        return lines[-1] + 1

    def handle_structure(self, block, indent_amt, check_magic):
        lines = block.lines
        self.check_indentation([lines[0]], indent_amt)

        # If there is only 1 line, we're done checking
        if len(lines) == 1:
            if check_magic:
                self.check_magic(lines)
            return lines[-1] + 1

        term_line, term_ind = self.find_statement_terminator(lines[0], 0)
        # Check trailing after left curly brace
        after = self.lines[term_line][term_ind+1:]
        self.handle_trailing_string(after, lines[0], LEFT_CURLY)

        i = term_line + 1
        while i < len(self.lines) and i < lines[-1]:
            n_block = self.parse_line(i)
            i = self.handle_block(n_block, indent_amt+self.indent_amt,
                                  check_magic=check_magic)

        self.handle_end_block(block, indent_amt)
        return lines[-1] + 1

    def handle_whitespace(self, block):
        lines = block.lines
        # If check whitespace is enabled, then check for excess
        # whitespace
        if self.check_ws:
            indent_error = False
            for line_n in lines:
                line = self.lines[line_n]
                if len(line) > 1:
                    indent_error = True

            if indent_error:
                if len(lines) == 1:
                    print('Line %d: Extra whitespace on empty line' % (lines[0]+1))
                    print('Note: White space replaced with ^')
                    print(self.lines[lines[0]].replace(
                        SPACE_CHAR, SPACE_REPLACEMENT_CHAR)
                    )
                else:
                    print('Line %d to %d: Extra whitespace on empty lines' % (lines[0]+1, lines[-1]+1))
                    # Replace white space with caret so user could see the spaces
                    ls = [self.lines[l].replace(SPACE_CHAR, 
                        SPACE_REPLACEMENT_CHAR) for l in lines]
                    print('Note: White space replaced with ^')
                    for l in ls:
                        print(l)

        if len(lines) > NEWLINES_LIMIT:
            beg, end = lines[0]+1, lines[-1]+1
            print('Line %d to %d: Excess newlines. More than the newline limit (%d)'\
                % (beg, end, NEWLINES_LIMIT))

        return lines[-1] + 1

    def check_line_limit(self):
        for i, l in enumerate(self.lines):
            if len(l) > LINE_LIMIT:
                print('Line %d: Over %d characters' % (i+1, LINE_LIMIT))
                print(l)

    def check_tabs(self):
        for l in self.og_lines:
            if l.find(TAB_CHAR) != -1:
                print('File contains <TAB> characters')
                break

    def run(self):
        print('')
        self.check_tabs()
        self.check_line_limit()

        # Collect function headers
        func_headers = []

        i = 0
        # The way to keep track of function header is to check the type
        # If the type is a block comment, record that. Then when a function
        # type follows, it is most likely the function header
        prev_type = None
        prev_group = None
        while i < len(self.lines):
            block = self.parse_line(i)
            group, t = block.lines, block.get_type()
            i = self.handle_block(block, 0, check_magic=False)

            # Collect headers
            if t == _BLOCK_CMMT:
                prev_type = _BLOCK_CMMT
                prev_group = group
            elif t == _FUNC and prev_type == _BLOCK_CMMT:
                # Is a function header
                term_line, term_ind = self.find_statement_terminator(group[0], 0, term=LEFT_CURLY)
                # Join the function header lines with the function declaration
                new_group = prev_group + [_ for _ in range(group[0], term_line+1)]
                func_headers.append(new_group)
            elif t != _EMPTY_LINE:
                # If the type is not the empty line then we clear memory
                # of seeing a block comment
                prev_type = None

        if self.print_headers:
            # Print the file header first, which is the first block of comment
            if len(self.block_cmmts) != 0:
                (start, end) = self.block_cmmts[0]
                print('\nFile header:')
                lines = [_ for _ in range(start[0], end[0]+1)]
                self.print_lines(lines, print_n=True)

                # Print function headers
                if len(func_headers) != 0:
                    print('\nFunction headers:')
                    for lines in func_headers:
                        self.print_lines(lines, print_n=True)
                        print('')
                else:
                    print('\nThere are no function headers')
            else:
                print('\nNo file/function headers')

        print('')

def usage():
    print(
        ("Usage: python %s [-h] -f <C filename> [-i <indent amount>] [-w] [-p] [-s]\n" % sys.argv[0]) +
        "\t-h/--help: Show help message\n" +
        "\t-f/--file: Filename to style check (required argument)\n" +
        "\t-i/--indent: Indentation amount\n" +
        "\t-w/--whitespace-check: Use excess white space check\n" +
        "\t-p/--print-headers: If passed, program will print the file/function headers\n" +
        "\t-s/--strict-check: If passed, programm will check style in strict mode\n"
    )

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hf:i:wps", ["help", "file=",
        "indent=", "whitespace-check", "print-headers", "strict-check"])
    file = None
    indent = None
    check_whitespace = False
    print_headers = False
    strict = False
    for o, a in opts:
        if o in ("--help", "-h"):
            usage()
            sys.exit(0)
        elif o in ("--file", "-f"):
            file = a
        elif o in ("--indent", "-i"):
            indent = a
        elif o in ("--whitespace-check", "-w"):
            check_whitespace = True
        elif o in ("--print-headers", "-p"):
            print_headers = True
        elif o in ("--strict-check", "-s"):
            strict = True
        else:
            usage()
            sys.exit(1)

    if file is None:
        usage()
        sys.exit(1)

    stl = CStyleChecker(file, check_whitespace=check_whitespace,
        print_headers=print_headers, strict=strict)
    if indent is not None:
        # Override the checker's indent amount
        try:
            stl.override_indent_amt(int(indent))
        except ValueError:
            print('Indent must be able to convert to an integer')
            sys.exit(1)

    stl.run()
