'''
	Filename: cstyle.py
	Author: Daniel Nguyen
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
START_COMMENT = '//'
SPACE_REPLACEMENT_CHAR = '^'

VARS_ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

# Characters that can be used in a type or a function name
STD_CHARS_REGEXP = "[a-zA-Z_][a-zA-Z0-9_]*"
NUMBER_REGEXP = "(-|)(0x|0|)[0-9]+"


BLCK_COMMENT_REGEXP = " *(\/\*)"
COMMENT_REGEXP = " *\/\/.*"
STMT_REGEXP = ".*;"
WHITE_SPACE_REGEXP = "( |\t)+\Z"
MAGIC_NUMBER_REGEXP = "[^a-zA-Z0-9_]+(-|)((0x|0|)[0-9]+)"
STRING_REGEXP = "(\".*\")"
CHAR_REGEXP = "(\'.*\')"

# Code detections regular expressions
C_DIRS_REGEXP = " *\#(define|include|undef|ifdef|ifndef|if|else|elif|endif|error|pragma)"
FUNC_REGEXP = " *([a-zA-Z_][a-zA-Z0-9_]*) *\** *([a-zA-Z_][a-zA-Z0-9_]*)( )*(\(.*\))"
FUNC_HDR_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *\** *[a-zA-Z_][a-zA-Z0-9_]*( )*\(.*\) *; *\Z"
ASSIGNMENT_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *=.* *;"
DEC_ASSIGNMENT_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *\** *[a-zA-Z_][a-zA-Z0-9_]* *=.* *;"
FUNC_CALL_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *\(.*\) *;"
DECLARATIONS_REGEXP = " *[a-zA-Z_][a-zA-Z0-9_]* *\** *[a-zA-Z_][a-zA-Z0-9_]* *;"
KEYWORDS_REGEXP = "( *(if|else if|while|for|switch) *\(.*\))|((continue|break);)"

# Misc
TODO_COMMENT_REGEXP = " *// *TODO"

# The group index that is the number inside the magic number pattern
NUM_GROUP_IND = 1
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
_STRUCTURE = 7		# Anything within curly braces that is not a function defn
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

class CStyleChecker(object):
	def __init__(self, filename, check_whitespace=True):
		self.check_ws = check_whitespace
		self.og_lines = []
		self.lines = []
		self.indent_amt = TAB_LENGTH

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

		# Find the first indented line to figure out the indent amount
		i = 0
		while i < len(self.lines):
			group, t = self.parse_line(i)
			if t == _FUNC:
				term_line, term_ind = self.find_statement_terminator(group[0], 0)
				# Use the first non empty line as the basis for indent amount
				j = term_line + 1
				while j < len(self.lines) and len(self.lines[j].lstrip()) == 0:
					j += 1

				next_line = self.lines[j]
				self.indent_amt = len(next_line) - len(next_line.lstrip())
				break

			i = group[-1] + 1

		# Loop through to see which switch indentation convention
		# they use
		for i, line in enumerate(self.lines):
			keyword, switch_ind = self.match_keywords(line)
			if keyword == "switch":
				# Find a case
				term_line, term_ind = self.find_statement_terminator(i, switch_ind, 
					term=COLON)
				j = term_line + 1
				while j < len(self.lines):
					keyword, case_ind = self.match_keywords(self.lines[j])
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

	def is_code(self, s):
		for ptrn in code_regexp:
			match = ptrn.match(s)
			if match:
				return match
		return None		

	def contains_magic(self, line):
		# Hack: Add a space at the beginning so the regexp works
		line = ' ' + line
		matches = magic_num_ptrn.findall(line)
		for match in matches:
			number = match[NUM_GROUP_IND]
			if number not in NON_MAGIC_NUMBERS:
				index = line.find(number)
				lo, hi = index, index + len(number)
				in_comment = self.within_comment(line, lo, hi)
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
							in_comment = self.within_comment(line, lo, hi)
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
							in_comment = self.within_comment(line, lo, hi)
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

	def within_comment(self, s, lo, hi):
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

		in_block_comment = False
		index = s.find(START_BLOCK_COMMENT)
		ranges = []
		if index == -1:
			return False

		prev = index
		for i in range(index, len(s)-1):
			if s[i:i+2] == START_BLOCK_COMMENT:
				in_block_comment = True
				prev = i
			elif s[i:i+2] == END_BLOCK_COMMENT:
				in_block_comment = False
				ranges.append((prev, i+2))

		return any([lo > left and hi < right for (left, right) in ranges])


	def match_keywords(self, line):
		for s in CONDITIONALS + UNCONDITIONALS + SWITCH_CASE + OTHERS:
			if len(line) <= len(s):
				if line.startswith(s):
					return s, 0
			else:
				# Find the substring inside line
				index = line.find(s)
				if index != -1:
					# Look to the left and right to see if it is part of a variable
					# name
					left = True
					right = True
					if index != 0:
						left = line[index-1] not in VARS_ALLOWED_CHARS
					if index + len(s) < len(line):
						right = line[index+len(s)] not in VARS_ALLOWED_CHARS
					
					if left and right and not self.within_quotes(line, index, index+len(s)):
						# Check if it's part of a comment
						if not self.within_comment(line, index, index+len(s)):
							return s, index

		return None, -1

	# Look for either the ; or {.
	# If include_keywords, will also look for the keywords on the following lines
	def find_statement_terminator(self, n, start, term=None, include_keywords=False):
		for line_n in range(n, len(self.lines)):
			lo = start if line_n == n else 0
			for j in range(lo, len(self.lines[line_n])):
				if term is None:
					if self.lines[line_n][j] in (LEFT_CURLY, SEMICOLON):
						return line_n, j
				else:
					if self.lines[line_n][j] == term:
						return line_n, j

			if line_n != n and include_keywords:
				keyword, ind = self.match_keywords(self.lines[line_n])
				if keyword:
					return line_n, ind

	# Look for the beginning ( and end ) of a condition
	# Return two tuples, of location of ( and location of )
	def find_condition(self, n, start):
		num_paren = 0
		start_paren_loc = None
		for line_n in range(n, len(self.lines)):
			lo = start if line_n == n else 0
			for j in range(lo, len(self.lines[line_n])):
				if self.lines[line_n][j] == LEFT_PAREN:
					num_paren += 1
					if start_paren_loc is None:
						start_paren_loc = (line_n, j)
				elif self.lines[line_n][j] == RIGHT_PAREN:
					num_paren -= 1
					if num_paren == 0:
						return start_paren_loc, (line_n, j)

	# Find all lines of code within curly braces
	# Argument n, start specifies the first curly brace
	def find_code_block(self, n, start):
		assert self.lines[n][start] == LEFT_CURLY

		num_brace = 0
		for line_n in range(n, len(self.lines)):
			lo = start if line_n == n else 0
			for j in range(lo, len(self.lines[line_n])):
				if self.lines[line_n][j] == LEFT_CURLY:
					num_brace += 1
				elif self.lines[line_n][j] == RIGHT_CURLY:
					num_brace -= 1
					if num_brace == 0:
						return (n, start), (line_n, j)


	# Check what kind of statement starting from this line
	# Return group of lines that belong to that statement and the type
	def parse_line(self, n):
		line = self.lines[n]
		line = line.lstrip()	# Strip white space to the left
		group = []

		if len(line) == 0:
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

		keyword, index = self.match_keywords(self.lines[n])
		if keyword:
			if keyword in CONDITIONALS:
				start, end = self.find_condition(n, index)
				# All line numbers from start of condition keyword to end of condition
				line_nums = [_ for _ in range(n, end[0]+1)]
				group.extend(line_nums)

				l, j = self.find_statement_terminator(end[0], end[1])
				if self.lines[l][j] == LEFT_CURLY:
					# Get start and end of code block
					code_start, code_end = self.find_code_block(l, j)
					# Add all lines up to the matching right curly brace (inclusive)
					group.extend([_ for _ in range(end[0]+1, code_end[0]+1)])
					return group, _CONDITIONAL
				else:	# Terminator is semicolon
					# Add all lines from one past the condition right paren up to
					# the semicolon
					group.extend([_ for _ in range(end[0]+1, l+1)])
					return group, _CONDITIONAL
			elif keyword in UNCONDITIONALS:
				# Find left curly brace or semicolon
				l, j = self.find_statement_terminator(n, 0)

				# If do while loop, look for the semicolon after while
				if keyword == "do":
					# Get start and end of code block
					code_start, code_end = self.find_code_block(l, j)
					l, j = self.find_statement_terminator(code_end[0], code_end[1])
					end = (l, j)
					group.extend([_ for _ in range(n, end[0]+1)])
					return group, _UNCONDITIONAL
				else:
					if self.lines[l][j] == LEFT_CURLY:
						# Get start and end of code block
						code_start, code_end = self.find_code_block(l, j)
						# Add all lines up to the matching right curly brace (inclusive)
						group.extend([_ for _ in range(n, code_end[0]+1)])
						return group, _UNCONDITIONAL
					else:	# Terminator is semicolon
						# Add all lines from one past the condition right paren up to
						# the semicolon
						group.extend([_ for _ in range(n, l+1)])
						return group, _UNCONDITIONAL
			elif keyword in SWITCH_CASE:	# Keyword is case or default
				# Must get all the statements that belong to this case
				# that means look for the next case or look for the end of switch (})
				count = 1	# Curly brace count starts at 1 because we are within switch
				group.append(n)
				for line_n in range(n+1, len(self.lines)):
					match = switch_case_regexp.match(self.lines[line_n])
					if match:	# If there is a match, we are at the next case
						break

					# Look for matching right curly brace for the switch statement.
					# If there is one, then this is the last case in the switch
					for j in range(len(self.lines[line_n])):
						if self.lines[line_n][j] == LEFT_CURLY:
							count += 1
						elif self.lines[line_n][j] == RIGHT_CURLY:
							count -= 1
							if count == 0:
								# Include the line with the right brace only if
								# it contains statements from the current case
								match = white_space_ptrn.match(self.lines[line_n][:j])
								if match is None:
									group.append(line_n)

								return group, _SWITCH_CASE

					group.append(line_n)

				return group, _SWITCH_CASE

		match = c_dirs_ptrn.match(line)
		if match:
			# C Directive
			for line_n in range(n, len(self.lines)):
				group.append(line_n)
				# Check if this directive was escaped and break if it is not
				# since the next line won't be part of the directive
				l = self.lines[line_n].rstrip()
				if not l.endswith(BACKSLASH):
					break

			return group, _DIRECTIVE

		# Either regular statements or function definition
		l, j = self.find_statement_terminator(n, 0)
		code = "".join([self.lines[_] for _ in range(n, l+1)])
		if func_ptrn.match(code) and not func_hdr_ptrn.match(code):
			# Function definition
			# It is possible that the function was declared in this way
			# In which case, terminator is ;. Solve this by force finding {
			# int foo(c) int c; {}
			l, j = self.find_statement_terminator(l, j, term=LEFT_CURLY)
			start, end = self.find_code_block(l, j)
			group.extend([_ for _ in range(n, end[0]+1)])
			return group, _FUNC
		else:	# Either structure or regular statement
			if self.lines[l][j] == LEFT_CURLY:
				# Structure
				start, end = self.find_code_block(l, j)
				group.extend([_ for _ in range(n, end[0]+1)])
				return group, _STRUCTURE
			else:	# Semicolon
				group.extend([_ for _ in range(n, l+1)])
				return group, _STATEMENT

	def print_lines(self, lines):
		for line_n in lines:
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
				self.handle_whitespace([line_n])
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
			has_magic = self.contains_magic(self.lines[line_n])
			if has_magic:
				print('Line %d: Contains magic number/word' % (line_n+1))
				print(self.lines[line_n])

	# General case: Handling group of lines with t being the type that
	# the lines belong to
	def handle_group(self, group, t, indent_amt, check_magic=True, in_switch=False):
		if t == _BLOCK_CMMT:
			return self.handle_block_comment(group, indent_amt)
		elif t == _CMMT:
			return self.handle_comment(group, indent_amt, in_switch)
		elif t == _DIRECTIVE:
			return self.handle_directive(group, indent_amt)
		elif t == _CONDITIONAL:
			return self.handle_cond(group, indent_amt)
		elif t == _UNCONDITIONAL:
			return self.handle_uncond(group, indent_amt)
		elif t == _FUNC:
			return self.handle_func(group, indent_amt)
		elif t == _STATEMENT:
			return self.handle_statement(group, indent_amt, check_magic)
		elif t == _STRUCTURE:
			return self.handle_structure(group, indent_amt, check_magic)
		elif t == _EMPTY_LINE:
			return self.handle_whitespace(group)
		elif t == _SWITCH_CASE:
			return self.handle_switch_case(group, indent_amt)

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

	def handle_leading_string(self, leading, n, terminator, indent_amt):
		if len(leading) != 0:
			if white_space_ptrn.match(leading):
				self.check_indentation([n], indent_amt)
			else:
				print('Line %d: %s should be on the next line' % (n+1, terminator))
				self.check_indentation([n], indent_amt+self.indent_amt)

	# Handle style checking around the terminator { or ;
	# If {, then it will check the curly brace indentation. Returns None
	# If ;, then it will simply handle the statement that follows up to that ;
	# Returns the line number to follow if ;
	def handle_terminator(self, lines, term_line, term_ind, indent_amt):
		# Check indentation up to the terminator
		# Two cases: { is on the same line as the conditional statement
		# or { is on the next line
		line = self.lines[term_line]
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
		else:	# Semicolon or keywords
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
			group, t = self.parse_line(term_line)
			return self.handle_group(group, t, indent_amt+self.indent_amt)

	def handle_block_comment(self, lines, indent_amt):
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

	def handle_comment(self, lines, indent_amt, in_switch=False):
		if in_switch:
			indent_amt = indent_amt + self.case_indent
			# Relax the indentation check if inside switch
			self.check_indentation(lines, indent_amt, relax=True)
		else:
			self.check_indentation(lines, indent_amt)

		strip = self.lines[lines[0]].lstrip()
		strip = strip.lstrip(FORWARD_SLASH)
		if self.is_code(strip):
			print('Line %d: Commented out code' % (lines[0]+1))
			print(self.lines[lines[0]])

		if todo_cmmt_ptrn.match(self.lines[lines[0]]):
			print('Line %d: Left in TODO comment' % (lines[0]+1))
			print(self.lines[lines[0]])

		return lines[0] + 1

	def handle_directive(self, lines, indent_amt):
		self.check_indentation(lines, indent_amt)
		return lines[-1] + 1

	def handle_switch_case(self, lines, indent_amt):
		switch_indent = indent_amt
		indent_amt = indent_amt + self.case_indent

		# Look for colon
		term_line, term_ind = self.find_statement_terminator(lines[0], 0, 
			term=COLON)

		# Check behind colon for anything
		line = self.lines[term_line]
		after = line[term_ind+1:]
		self.handle_trailing_string(after, term_line, COLON)

		# Parse the statements for this case
		i = term_line + 1
		while i < len(self.lines) and i <= lines[-1]:
			group, t = self.parse_line(i)
			if t == _CMMT:
				i = self.handle_group(group, t, switch_indent, in_switch=True)
			else:
				i = self.handle_group(group, t, indent_amt+self.indent_amt, in_switch=True)

		return lines[-1] + 1


	# Anything with conditions (while, for, if, else if, switch)
	# indent_amt passed in is the indent amount of the code within
	# the condition statements, not the first line itself
	def handle_cond(self, lines, indent_amt):
		first_line = self.lines[lines[0]]
		# print(first_line)
		keyword, index = self.match_keywords(first_line)
		is_switch = keyword == "switch"

		# Parse the condition first
		paren_start, paren_end = self.find_condition(lines[0], index)
		self.check_magic([_ for _ in range(lines[0], paren_end[0]+1)])

		term_line, term_ind = self.find_statement_terminator(
			paren_end[0], paren_end[1], include_keywords=True
		)
		ret = self.handle_terminator(lines, term_line, term_ind, indent_amt)
		if ret:
			return ret

		# for, while, if, else if
		# Note: i is the global line index.
		# This loops checks all the way up to the last line not including the last line
		i = term_line + 1
		while i < len(self.lines) and i < lines[-1]:
			group, t = self.parse_line(i)
			if is_switch:
				i = self.handle_group(group, t, indent_amt, in_switch=True)
			else:
				i = self.handle_group(group, t, indent_amt+self.indent_amt)

		# Check the last line for indentation error and if it has keywords.
		# For example:
		# if (condition) {
		# } else {}
		curly_start, curly_end = self.find_code_block(term_line, term_ind)
		last_line = self.lines[curly_end[0]]
		before = last_line[:curly_end[1]]
		# First check the part before the } for code
		self.handle_leading_string(before, curly_end[0], RIGHT_CURLY, indent_amt)

		# Check the part behind } for keywords
		after = last_line[curly_end[1]+1:]
		if len(after) != 0:
			# If the after part is not a comment
			if not cmmt_ptrn.match(after) and not blck_cmmt_ptrn.match(after):
				keyword, index = self.match_keywords(after)
				# If there is a keyword, return this line so that
				# that could be parsed later
				if keyword:
					return lines[-1]
			else:
				self.handle_trailing_string(after, curly_end[0], RIGHT_CURLY)
		
		return lines[-1] + 1

	def handle_uncond(self, lines, indent_amt):
		term_line, term_ind = self.find_statement_terminator(lines[0], 0, include_keywords=True)
		ret = self.handle_terminator(lines, term_line, term_ind, indent_amt)
		if ret:	# Will only be true if terminator != {
			return ret

		i = term_line + 1
		while i < len(self.lines) and i < lines[-1]:
			group, t = self.parse_line(i)
			i = self.handle_group(group, t, indent_amt+self.indent_amt)

		# Handle the closing curly brace
		curly_start, curly_end = self.find_code_block(term_line, term_ind)
		last_line = self.lines[curly_end[0]]
		before = last_line[:curly_end[1]]
		# First check the part before the } for code
		self.handle_leading_string(before, curly_end[0], RIGHT_CURLY, indent_amt)

		keyword, index = self.match_keywords(self.lines[lines[0]])
		after = last_line[curly_end[1]+1:]
		# Skip the trailing check if it's a do while loop because the while
		# is behind the }
		if keyword != "do":
			if not cmmt_ptrn.match(after) and not blck_cmmt_ptrn.match(after):
				keyword, index = self.match_keywords(after)
				if keyword is not None:
					# If there is a keyword, return this line so that
					# that could be parsed later
					return lines[-1]
			else:
				self.handle_trailing_string(after, curly_end[0], RIGHT_CURLY)
		else:
			# If it is do while, check the while condition for magic
			# number
			self.check_magic([curly_end[0]])

		return lines[-1] + 1

	def handle_func(self, lines, indent_amt):
		term_line, term_ind = self.find_statement_terminator(lines[0], 0, term=LEFT_CURLY)
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
			group, t = self.parse_line(i)
			i = self.handle_group(group, t, indent_amt+self.indent_amt)

		self.check_indentation([lines[-1]], indent_amt)
		return lines[-1] + 1

	def handle_statement(self, lines, indent_amt, check_magic=True):
		self.check_indentation(lines, indent_amt)
		# Check for magic number
		if check_magic:
			self.check_magic(lines)

		return lines[-1] + 1

	def handle_structure(self, lines, indent_amt, check_magic):
		self.check_indentation([lines[0]], indent_amt)

		# If there is only 1 line, we're done checking
		if len(lines) == 1:
			return lines[-1] + 1

		term_line, term_ind = self.find_statement_terminator(lines[0], 0)
		# Check trailing after left curly brace
		after = self.lines[term_line][term_ind+1:]
		self.handle_trailing_string(after, lines[0], LEFT_CURLY)

		i = term_line + 1
		while i < len(self.lines) and i < lines[-1]:
			group, t = self.parse_line(i)
			i = self.handle_group(group, t, indent_amt+self.indent_amt, 
				check_magic=check_magic)

		curly_start, curly_end = self.find_code_block(term_line, term_ind)
		last_line = self.lines[curly_end[0]]
		before = last_line[:curly_end[1]]
		# Check the part before the } for code
		self.handle_leading_string(before, curly_end[0], RIGHT_CURLY, indent_amt)
		return lines[-1] + 1


	def handle_whitespace(self, lines):
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
				print('Line %d is over %d characters' % (i+1, LINE_LIMIT))
				print(l)

	def run(self):
		self.check_line_limit()

		i = 0
		while i < len(self.lines):
			group, t = self.parse_line(i)
			i = self.handle_group(group, t, 0, check_magic=False)

	def test_parse(self):
		names = {
			_BLOCK_CMMT: 'Block Comment',
			_CMMT: 'Comment',
			_DIRECTIVE: 'C Directive',
			_CONDITIONAL: 'Conditional',
			_UNCONDITIONAL: 'Unconditional',
			_FUNC: 'Function',
			_STATEMENT: 'Statement',
			_STRUCTURE: 'Structures',
			_EMPTY_LINE: 'Empty Line',
			_SWITCH_CASE: 'Switch Case'
		}
		i = 0
		while i < len(self.lines):
			group, t = self.parse_line(i)
			print('Found a/an %s' % names[t])

			for l in group:
				print(self.lines[l])

			if t == _FUNC:
				j = group[1]
				while j < group[-1]:
					g, t2 = self.parse_line(j)
					print('Found a/an %s' % names[t2])

					for l in g:
						print(self.lines[l])

					if t2 == _CONDITIONAL:
						k = g[1]
						while k < group[-1]:
							g3, t3 = self.parse_line(k)
							print('Found a/an %s' % names[t3])
							for l in g3:
								print(self.lines[l])

							k = g3[-1] + 1

					j = g[-1] + 1

			i = group[-1] + 1

	def test_magic(self):
		for i in range(len(self.lines)):
			line = self.lines[i]
			magic = self.contains_magic(line)
			if magic:
				print('Line %d: Contains magic number' % (i+1))
				print(line)

def usage():
	print(
		("Usage: python %s [-h] -f <C filename> [-i <indent amount>] [-w]\n" % sys.argv[0]) +
		"\t-h/--help: Show help message\n" +
		"\t-f/--file: Filename to style check (required argument)\n" +
		"\t-i/--indent: Indentation amount\n" +
		"\t-w/--whitespace-check: Use excess white space check\n"
	)

if __name__ == '__main__':
	opts, args = getopt.getopt(sys.argv[1:], "hf:i:w", ["help", "file=", "indent=", "whitespace-check"])
	file = None
	indent = None
	check_whitespace = False
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
		else:
			usage()
			sys.exit(1)

	if file is None:
		usage()
		sys.exit(1)

	stl = CStyleChecker(file, check_whitespace=check_whitespace)
	if indent is not None:
		# Override the checker's indent amount
		try:
			stl.override_indent_amt(int(indent))
		except ValueError:
			print('Indent must be able to convert to an integer')
			sys.exit(1)

	stl.run()
