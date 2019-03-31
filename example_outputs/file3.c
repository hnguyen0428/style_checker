/*
 * Filename: file3.c
 * Description: This file demonstrates style checked in strict mode.
 */

#include <stdio.h>

#define LITTLE_ENDIAN "Little Endian\n"
#define BIG_ENDIAN "Big Endian\n"

/*
 * Function: int main()
 * Description: Find out if the system is little or big endian
 */
int main() {
  int x = 1;
  char* ptr = (char*) &x;

  // This if statement was should have a space between if and the condition
  if(ptr[0])
  {  // This curly brace should be on the line above
    printf(LITTLE_ENDIAN);
  }
  else {  // This should be on the line above
    printf(BIG_ENDIAN);
	}

  if (x == 1)
    // This if statement does not use curly braces
    printf("This if statement should have curly braces. This string is also"\
           "considered magic number\n");
    printf("This statement is not part of the previous if statement");

  return 0;
}
