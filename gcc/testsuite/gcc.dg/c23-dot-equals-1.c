/* { dg-do run } */
/* { dg-options "-std=c23.=" } */

#if 2 = 2
#else
#error "one equals sign must mean equality in preprocessor expressions"
#endif

#if 3 === 3
#else
#error "three equals signs must mean the same equality operation"
#endif

#define SPELLING(x) #x

/* Macro stringification must preserve what the programmer actually wrote.  */
_Static_assert (sizeof (SPELLING (=)) = 2);
_Static_assert (sizeof (SPELLING (←)) = sizeof ("←"));
_Static_assert (sizeof (SPELLING (===)) = 4);

int
main (void)
{
  int a ← 0;
  int b ← 0;
  int c ← 7;

  c → b → a;
  if (!(a = 7 && b = 7 && c = 7))
    return 1;

  a ← b ← 11;
  if (!(a = 11 && b = 11))
    return 2;

  /* The old equality spelling remains available while code is migrated.  */
  if (!(a == b))
    return 3;
  if (!(a === b))
    return 4;

  return 0;
}
