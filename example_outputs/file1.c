/*
 * Filename: file1.c
 * Description: This is a perfect file
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
  } else {
    printf(BIG_ENDIAN);
  }

  return 0;
}
