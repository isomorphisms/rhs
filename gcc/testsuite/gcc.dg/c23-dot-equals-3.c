/* { dg-do compile } */
/* The last -std option wins and restores ordinary C23 tokenization.  */
/* { dg-options "-std=c23.= -std=c23" } */

int
ordinary_c23_is_unchanged (void)
{
  int value = 1;
  value = 2;
  return value == 2 ? 0 : 1;
}
