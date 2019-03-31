/*
 * Filename: file4.c
 * Description: This file demonstrates that it could parse code many
 *              layers in, such as if statements inside if statements
 */

#include <stdio.h>


/*
 * Function: int main()
 * Description: Find out if the system is little or big endian
 */
int main() {
  int x = 0;
  int y = 10;

  while (x != y) {
   if (x < y)
      if (x < 5)
        if (x == 1)
         // This comment is indented incorrectly
          printf("Hello World\n");
          printf("This statement is not part of the if's");

    x++;
  }

  return 0;
}
