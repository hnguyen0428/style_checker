/*
 * Filename: file2.c
 * Description: This file has many errors. Including
 *              - Commented out code
 *              - Magic Number
 *              - TODO comments
 *              - Indentation errors
 *              - Used Tab (Line 29)
 *              - Line over 80
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
  //int y = 5;
   char* ptr = (char*) &x;

  if (ptr[0]) {
    printf(LITTLE_ENDIAN);
  } else {
     printf(BIG_ENDIAN);
  }

	// This line was indented using TAB

  char magic_array[5] = {0};
  // TODO: Do something with this array

  // This a very very very very very very very very  long comment that is over 80 characters.

  return 0;
}
