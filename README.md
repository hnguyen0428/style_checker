# Style Checker
## cstyle.py
A style checker/linter for C files.

### What it can check:

- Excess white space
- Lines over 80 characters
- General indentation
- "Magic" Numbers
- Commented out code (most of them)
- Left in TODO comments
- Check for tabs (style guide uses spaces for C files)
- Will not automatically check for file/function headers but can
print them out for manual checking.
- Spacings for if/else/etc...

### Usage

    - Usage: python cstyle.py [-h] -f <C filename> [-i <indent amount>] [-w] [-p] [-s]
                -h/--help: Show help message
                -f/--file: Filename to style check (required argument)
                -i/--indent: Indentation amount
                -w/--whitespace-check: Use excess white space check
                -p/--print-headers: If passed, program will print the file/function headers
                -s/--strict-check: If passed, programm will check style in strict mode
                
### Whitespace Check
With this enabled, the program will check if there are any white spaces
on lines that are empty or when a statement finishes and there are extra
spaces at the end.

### Strict Mode
With this enabled, the program will do spacing checks. For instance:

    if (condition) {
      // Do something
    }
    
There must be a space between "if" and the condition. There must also be a
space between the condition and the left curly brace.
Note that the curly brace is required to be on the same line as the end of
the condition. 

These rules go for other constructs that have conditions.

For if/else if/else/for/while, it is required that there is an accompanying
curly brace even if they only contain one line.

For else if/else, the blocks must start on the same line as the previous
if/else if block. For example:

    if (condition) {
      // If
    } else {  // Note that else is on this line
      // Else
    }

In strict mode, number of spaces used for indenting is enforced to be 2
spaces.

For inline comments, the comment should always start with // followed by
a space.

For more information, refer to the Google Style Guide.
    
## sstyle.py
A style checker/linter for ARM assembly files.

### What it can check:

- Lines over 80 characters
- General indentation
- "Magic" Numbers
- Left in TODO comments
- Check for indenting using spaces (style guide uses tabs for assembly files)
- Will not automatically check for file/function headers but can
print them out for manual checking.
    
### Usage

    - Usage: python sstyle.py [-h] -f <C filename>
                -h/--help: Show help message
                -f/--file: Filename to style check (required argument)
                -p/--print-headers: If passed, program will print the file/function headers
                
                
 
Note: This should only be used as a general guide for styling. The program
will not always be able to catch every styling mistake nor will the
mistakes that it catches always be a styling error.