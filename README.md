# Style Checker
## cstyle.py
A style checker/linter for C files.

What it can check:

- Excess white space
- Lines over 80 characters
- General indentation
- "Magic" Numbers
- Commented out code (most of them)
- Left in TODO comments
- Check for tabs (style guide uses spaces for C files)

### Usage

    - Usage: python cstyle.py [-h] -f <C filename> [-i <indent amount>] [-w]
                -h/--help: Show help message
                -f/--file: Filename to style check (required argument)
                -i/--indent: Indentation amount
                -w/--whitespace-check: Use excess white space check
                -p/--print-headers: If passed, program will print the file/function headers
    
## sstyle.py
A style checker/linter for ARM assembly files.

What it can check:

- Lines over 80 characters
- General indentation
- "Magic" Numbers
- Left in TODO comments
- Check for indenting using spaces (style guide uses tabs for assembly files)
    
Note: This should only be used as a general guide for styling. The program
will not always be able to catch every styling mistake nor will the
mistakes that it catches always be a styling error.
    
### Usage

    - Usage: python sstyle.py [-h] -f <C filename>
                -h/--help: Show help message
                -f/--file: Filename to style check (required argument)
                -p/--print-headers: If passed, program will print the file/function headers