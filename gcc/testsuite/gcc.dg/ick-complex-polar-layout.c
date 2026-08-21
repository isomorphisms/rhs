/* { dg-do run } */
/* { dg-options "-O2" } */

extern void abort (void);

_Static_assert (sizeof (float _Complex) == 2 * sizeof (float),
		"float complex must occupy two scalar slots");
_Static_assert (sizeof (double _Complex) == 2 * sizeof (double),
		"double complex must occupy two scalar slots");

static double _Complex static_z = 3.0 + 4.0i;
static double _Complex static_negative_axis = -2.0 + 0.0i;
static double _Complex static_zero = 0.0 + 0.0i;
static float _Complex static_float_negative_axis = -2.0f + 0.0fi;

/* Keep byte inspection across an optimization boundary so it observes the
   physical representation after complex lowering.  */
__attribute__ ((noinline, noipa))
static void
copy_bytes (void *destination, const void *source, unsigned long size)
{
  unsigned char *to = (unsigned char *) destination;
  const unsigned char *from = (const unsigned char *) source;

  for (unsigned long index = 0; index < size; ++index)
    to[index] = from[index];
}

static int
close_enough (double actual, double expected)
{
  double difference = actual - expected;
  return difference < 1e-12 && difference > -1e-12;
}

static int
close_enough_float (float actual, float expected)
{
  float difference = actual - expected;
  return difference < 2e-6f && difference > -2e-6f;
}

__attribute__ ((noinline, noipa))
static double _Complex
bounce (double _Complex value)
{
  return value;
}

int
main (void)
{
  double raw[2];
  copy_bytes (raw, &static_z, sizeof raw);
  if (!close_enough (raw[0], 5.0)
      || !close_enough (raw[1], __builtin_atan2 (4.0, 3.0)))
    abort ();

  /* Language-level Cartesian access is reconstructed from polar storage.  */
  if (!close_enough (__real__ static_z, 3.0)
      || !close_enough (__imag__ static_z, 4.0))
    abort ();

  double negative_raw[2];
  copy_bytes (negative_raw, &static_negative_axis, sizeof negative_raw);
  if (!close_enough (negative_raw[0], 2.0)
      || !close_enough (negative_raw[1],
			__builtin_atan2 (0.0, -2.0))
      || !close_enough (__real__ static_negative_axis, -2.0)
      || !close_enough (__imag__ static_negative_axis, 0.0))
    abort ();

  double zero_raw[2];
  copy_bytes (zero_raw, &static_zero, sizeof zero_raw);
  if (zero_raw[0] != 0.0 || zero_raw[1] != 0.0)
    abort ();

  /* Exercise runtime Cartesian-to-polar construction, not only constants.  */
  volatile double runtime_real = 3.0;
  volatile double runtime_imag = 4.0;
  double _Complex automatic_z
    = __builtin_complex (runtime_real, runtime_imag);
  double automatic_raw[2];
  copy_bytes (automatic_raw, &automatic_z, sizeof automatic_raw);
  if (!close_enough (automatic_raw[0], 5.0)
      || !close_enough (automatic_raw[1], raw[1]))
    abort ();

  /* ICK-to-ICK function arguments and returns carry the same polar pair.  */
  double _Complex returned_z = bounce (automatic_z);
  double returned_raw[2];
  copy_bytes (returned_raw, &returned_z, sizeof returned_raw);
  if (returned_raw[0] != automatic_raw[0]
      || returned_raw[1] != automatic_raw[1])
    abort ();

  double _Complex constant_returned = bounce (3.0 + 4.0i);
  double constant_returned_raw[2];
  copy_bytes (constant_returned_raw, &constant_returned,
	      sizeof constant_returned_raw);
  if (!close_enough (constant_returned_raw[0], 5.0)
      || !close_enough (constant_returned_raw[1], raw[1]))
    abort ();

  /* Multiplication operates natively on the polar pair.  */
  double _Complex unit_diagonal = bounce (1.0 + 1.0i);
  double _Complex product = unit_diagonal * unit_diagonal;
  double product_raw[2];
  copy_bytes (product_raw, &product, sizeof product_raw);
  if (!close_enough (product_raw[0], 2.0)
      || !close_enough (__real__ product, 0.0)
      || !close_enough (__imag__ product, 2.0)
      || !close_enough (__builtin_cabs (product), 2.0)
      || !close_enough (__builtin_carg (product),
			__builtin_atan2 (2.0, 0.0)))
    abort ();

  /* A principal +pi phase must not flip to -pi through sinf(pi).  */
  float float_negative_raw[2];
  copy_bytes (float_negative_raw, &static_float_negative_axis,
	      sizeof float_negative_raw);
  if (!close_enough_float (float_negative_raw[0], 2.0f)
      || __builtin_cargf (static_float_negative_axis)
	 != float_negative_raw[1])
    abort ();

  /* Multiplication may move the stored phase outside the principal range;
     carg must normalize that result rather than returning the raw slot.  */
  double phase_two_raw[2] = { 1.0, 2.0 };
  double _Complex phase_two;
  copy_bytes (&phase_two, phase_two_raw, sizeof phase_two);
  double _Complex phase_four = phase_two * phase_two;
  double phase_four_raw[2];
  copy_bytes (phase_four_raw, &phase_four, sizeof phase_four_raw);
  if (phase_four_raw[0] != 1.0 || phase_four_raw[1] != 4.0
      || !close_enough (__builtin_carg (phase_four),
			__builtin_atan2 (__builtin_sin (4.0),
					 __builtin_cos (4.0))))
    abort ();

  return 0;
}
