'''
    Filename: sstyle.py
    Author: Daniel Nguyen
    Date Created: March 27, 2019
    Last Modified: March 27, 2019
    Python Version: 2.7
'''

import re
import sys
import getopt

COLON = ':'
START_BLOCK_COMMENT = '/*'
END_BLOCK_COMMENT = '*/'
START_COMMENT_SLASH = '//'
BACKSLASH = '\\'
TAB_CHAR = '\t'
SPACE_CHAR = ' '
DOUBLE_QUOTE = '\"'
SINGLE_QUOTE = '\''
START_COMMENT_CHARS = ['@', '#']

LABEL_REGEXP = " *[a-zA-Z_\.][a-zA-Z0-9_\.]*\:"
DIRECTIVES = " *\.[a-zA-Z0-9_\.]+"
BLCK_COMMENT_REGEXP = " *(\/\*)"
COMMENT_REGEXP = " *(\/\/|\@|\#).*"

MAGIC_NUMBER_REGEXP = "[^a-zA-Z0-9_]+(-|)((0x|0|)[0-9]+)"
# The group index that is the number inside the magic number pattern
NUM_GROUP_IND = 2
WHITE_SPACE_REGEXP = "( |\t)+\Z"
TODO_COMMENT_REGEXP = " *(//|@|#) *TODO"


label_ptrn = re.compile(LABEL_REGEXP)
dir_ptrn = re.compile(DIRECTIVES)
blck_cmmt_ptrn = re.compile(BLCK_COMMENT_REGEXP)
cmmt_ptrn = re.compile(COMMENT_REGEXP)
magic_num_ptrn = re.compile(MAGIC_NUMBER_REGEXP)
white_space_ptrn = re.compile(WHITE_SPACE_REGEXP)

todo_cmmt_ptrn = re.compile(TODO_COMMENT_REGEXP)


#Types
_BLOCK_CMMT = 0
_CMMT = 1
_LABEL = 2
_DIRECTIVE = 3
_INSTRUCTION = 4
_EMPTY_LINE = 5


LINE_LIMIT = 80
TAB_LENGTH = 4
NEWLINES_LIMIT = 2
NON_MAGIC_NUMBERS = [
    '0', '-1', '1'
]

class SStyleChecker(object):
    def __init__(self, filename, print_headers=False):
        self.lines = []
        self.og_lines = []
        self.indent_amt = TAB_LENGTH
        self.used_space_lines = []
        self.block_cmmts = []
        self.print_headers = print_headers

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

        self.get_block_comments()

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
        return any([lo > left and hi < right for (left, right) in ranges])

    def within_comment(self, s, n, lo, hi):
        # Look left from lo to check for //, @, #
        in_quote = False
        for i in reversed(range(1, lo)):
            if not in_quote and (s[i-1] + s[i]) == START_COMMENT_SLASH:
                return True

            if not in_quote and s[i] in START_COMMENT_CHARS:
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
                if n == start_line:
                    if lo >= start_ind:
                        return True
                elif n == end_line:
                    if lo <= end_ind:
                        return True
                else:
                    return True

        return False

    def print_lines(self, lines, print_n=False):
        for line_n in lines:
            if print_n:
                print('%d\t\t%s' % (line_n+1, self.lines[line_n]))
            else:
                print(self.lines[line_n])

    def get_block_comments(self):
        in_block = False
        start = None

        for i in range(len(self.lines)):
            line = self.lines[i]
            for j in range(len(line)-1):
                if line[j:j+2] == START_BLOCK_COMMENT and not self.within_quotes(line, j, j+2)\
                    and not self.within_comment(line, i, j, j+2):
                    in_block = True
                    start = (i, j)
                elif line[j:j+2] == END_BLOCK_COMMENT:
                    in_block = False
                    end = (i, j+2)
                    self.block_cmmts.append((start, end))

    def parse_line(self, n):
        line = self.lines[n]
        group = []

        if len(line.strip()) == 0:
            # Empty line
            group.append(n)
            # If lines below are empty, add them to the group
            for line_n in range(n+1, len(self.lines)):
                if len(self.lines[line_n].lstrip()) == 0:
                    group.append(line_n)
                else:
                    break

            return group, _EMPTY_LINE

        match = cmmt_ptrn.match(line)
        if match:
            return [n], _CMMT

        match = blck_cmmt_ptrn.match(line)
        if match:
            # Find the end of the comment block
            start = self.lines[n].find(START_BLOCK_COMMENT)
            for line_n in range(n, len(self.lines)):
                lo = start+2 if line_n == n else 0
                for j in range(lo, len(self.lines[line_n])-1):
                    pair = self.lines[line_n][j] + self.lines[line_n][j+1]
                    if pair == END_BLOCK_COMMENT:
                        # Found the end of the comment block
                        group.append(line_n)
                        return group, _BLOCK_CMMT

                group.append(line_n)

        if label_ptrn.match(line):
            # Is a label
            return [n], _LABEL
        elif dir_ptrn.match(line):
            # Is a directive
            return [n], _DIRECTIVE
        else:
            # Is instruction
            return [n], _INSTRUCTION

    def check_indentation(self, n, t):
        line = self.lines[n]
        if t == _LABEL:
            stripped = line.lstrip()
            if len(line) != len(stripped):
                # Label was indented
                print('Line %d: Assembly label should not be indented' % (n+1))
                print(line)
        elif t == _INSTRUCTION or t == _DIRECTIVE:
            stripped = line.lstrip()
            actual_indent_amt = len(line) - len(stripped)
            if actual_indent_amt == 0:
                print('Line %d: Assembly instruction or directive should be '\
                    'indented with 1 tab' % (n+1))
                print(line)
            elif actual_indent_amt != self.indent_amt:
                print('Line %d: Inconsistent Indentation' % (n+1))
                print(line)

            # Check for Tab usage
            og_line = self.og_lines[n]
            stripped = og_line.lstrip()
            whitespace = og_line[:len(og_line) - len(stripped)]
            if whitespace.find(SPACE_CHAR) != -1:
                # Indented using space
                self.used_space_lines.append(n)

    def handle_trailing_string(self, trail, n, terminator):
        if len(trail) != 0:
            # Check if the trailing string is a comment. If it is then it's fine
            if not cmmt_ptrn.match(trail) and len(trail.lstrip()) != 0:
                print('Line %d: Statements behind %s should be '\
                    'on the next line' % (n+1, terminator))
                print(self.lines[n])

    def handle_group(self, group, t):
        if t == _BLOCK_CMMT:
            return self.handle_block_comment(group)
        elif t == _CMMT:
            return self.handle_comment(group)
        elif t == _LABEL:
            return self.handle_label(group)
        elif t == _DIRECTIVE:
            return self.handle_directive(group)
        elif t == _INSTRUCTION:
            return self.handle_instruction(group)
        elif t == _EMPTY_LINE:
            return self.handle_whitespace(group)

        return None

    def handle_block_comment(self, lines):
        last_line = self.lines[lines[-1]]
        index = last_line.find(END_BLOCK_COMMENT)
        if index != -1:
            after = last_line[index+2:]
            self.handle_trailing_string(after, lines[-1], END_BLOCK_COMMENT)

            # Return the next line number
            return lines[-1] + 1

        # This should not happen given the code compiles
        return None

    def handle_comment(self, lines):
        if todo_cmmt_ptrn.match(self.lines[lines[0]]):
            print('Line %d: Left in TODO comment' % (lines[0]+1))
            print(self.lines[lines[0]])

        return lines[-1] + 1

    def handle_instruction(self, lines):
        self.check_indentation(lines[0], _INSTRUCTION)
        magic = self.contains_magic(self.lines[lines[0]], lines[0])
        if magic:
            print('Line %d: Contains magic number' % (lines[0]+1))
            print(self.lines[lines[0]])
        return lines[-1] + 1

    def handle_directive(self, lines):
        self.check_indentation(lines[0], _DIRECTIVE)
        return lines[-1] + 1

    def handle_label(self, lines):
        self.check_indentation(lines[0], _LABEL)
        index = self.lines[lines[0]].find(COLON)
        after = self.lines[lines[0]][index+1:]
        if len(after) != 0:
            if not white_space_ptrn.match(after) and not\
                cmmt_ptrn.match(after) and not blck_cmmt_ptrn.match(after):
                print('Line %d: Statements behind label should be on'\
                    ' the next line' % (lines[0]+1))
                print(self.lines[lines[0]])

        return lines[-1] + 1

    def handle_whitespace(self, lines):
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

    def check_space_indentation(self):
        if len(self.used_space_lines) != 0:
            lines = [str(n+1) for n in self.used_space_lines]
            lines = ", ".join(lines)
            print('Indented using spaces on lines %s' % lines)

    def run(self):
        print('')
        self.check_line_limit()

        # Collect function headers
        func_headers = []

        i = 0
        prev_type = None
        prev_group = None
        while i < len(self.lines):
            group, t = self.parse_line(i)
            i = self.handle_group(group, t)

            # Collect headers
            if t == _BLOCK_CMMT:
                prev_type = _BLOCK_CMMT
                prev_group = group
            elif t == _LABEL and prev_type == _BLOCK_CMMT:
                # Join the function header lines with the function declaration
                new_group = prev_group + group
                func_headers.append(new_group)
            elif t != _EMPTY_LINE:
                # If the type is not the empty line then we clear memory
                # of seeing a block comment
                prev_type = None

        self.check_space_indentation()

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
        ("Usage: python %s [-h] -f <C filename>\n" % sys.argv[0]) +
        "\t-h/--help: Show help message\n" +
        "\t-f/--file: Filename to style check (required argument)\n" +
        "\t-p/--print-headers: If passed, program will print the file/function headers\n"
    )

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hf:p", ["help", "file=", "print-headers"])
    file = None
    print_headers = False
    for o, a in opts:
        if o in ("--help", "-h"):
            usage()
            sys.exit(0)
        elif o in ("--file", "-f"):
            file = a
        elif o in ("--print-headers", "-p"):
            print_headers = True
        else:
            usage()
            sys.exit(1)

    if file is None:
        usage()
        sys.exit(1)

    stl = SStyleChecker(file, print_headers=print_headers)
    stl.run()
