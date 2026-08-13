/* { dg-do compile } */
/* { dg-options "-std=c23.= -Wall" } */

int
equal_after_assignment (int left, int right)
{
  right → left;
  return left = right;
}
