/* { dg-do run } */
/* { dg-options "-O2" } */

#include <complex.h>
#include <math.h>
#include <string.h>

extern void abort (void);

static double _Complex static_z = 3.0 + 4.0i;

static int
close_enough (double a, double b)
{
  double d = a - b;
  return d < 1e-12 && d > -1e-12;
}

__attribute__ ((noinline))
static double _Complex
bounce (double _Complex z)
{
  return z;
}

int
main (void)
{
  double raw[2];
  memcpy (raw, &static_z, sizeof raw);
  if (!close_enough (raw[0], 5.0)
      || !close_enough (raw[1], atan2 (4.0, 3.0)))
    abort ();

  /* Language-level Cartesian access is reconstructed from polar storage.  */
  if (!close_enough (__real__ static_z, 3.0)
      || !close_enough (__imag__ static_z, 4.0))
    abort ();

  double _Complex automatic_z = 3.0 + 4.0i;
  double automatic_raw[2];
  memcpy (automatic_raw, &automatic_z, sizeof automatic_raw);
  if (!close_enough (automatic_raw[0], 5.0)
      || !close_enough (automatic_raw[1], raw[1]))
    abort ();

  /* ICK-to-ICK function arguments and returns carry the same polar pair.  */
  double _Complex returned_z = bounce (automatic_z);
  double returned_raw[2];
  memcpy (returned_raw, &returned_z, sizeof returned_raw);
  if (returned_raw[0] != automatic_raw[0]
      || returned_raw[1] != automatic_raw[1])
    abort ();

  double _Complex constant_returned = bounce (3.0 + 4.0i);
  double constant_returned_raw[2];
  memcpy (constant_returned_raw, &constant_returned,
          sizeof constant_returned_raw);
  if (!close_enough (constant_returned_raw[0], 5.0)
      || !close_enough (constant_returned_raw[1], raw[1]))
    abort ();

  /* Multiplication operates natively on the polar pair.  */
  double _Complex product = (1.0 + 1.0i) * (1.0 + 1.0i);
  double product_raw[2];
  memcpy (product_raw, &product, sizeof product_raw);
  if (!close_enough (product_raw[0], 2.0)
      || !close_enough (__real__ product, 0.0)
      || !close_enough (__imag__ product, 2.0)
      || !close_enough (cabs (product), 2.0)
      || !close_enough (carg (product), atan2 (2.0, 0.0)))
    abort ();

  return 0;
}
