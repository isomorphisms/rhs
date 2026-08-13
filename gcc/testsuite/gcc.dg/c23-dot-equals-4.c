/* { dg-do compile } */
/* { dg-options "-std=c23.=" } */

int
ordinary_assignment_is_not_c23_dot_equals (void)
{
  int value = 1; /* { dg-error "expected .* before .*==.* token" } */
  /* { dg-error "expected expression before .*==.* token" "" { target *-*-* } .-1 } */
  return value;
}
