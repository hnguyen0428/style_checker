/*
 * Filename: file4.c
 * Description: This file demonstrates that it could parse code many
 *              layers in, such as if statements inside if statements
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

  if (ptr[0]) {
    printf(LITTLE_ENDIAN);
    // The following if statement has indentation error
     if (x) {
      // Magic String
      printf("Hello World\n");
     } else {
      printf("Hello World Again\n");  // printf("Commented out code");
   }
  } else {
    printf(BIG_ENDIAN);
  }

  return 0;
}
