/* { dg-do run } */
/* { dg-options "-O2" } */

#include <math.h>
#include <string.h>

extern void abort (void);

int
main (void)
{
  double _Complex z = 1.0 + 1.0i;
  double _Complex down = floor (z);
  double _Complex up = ceil (z);
  double zr[2], dr[2], ur[2];

  memcpy (zr, &z, sizeof zr);
  memcpy (dr, &down, sizeof dr);
  memcpy (ur, &up, sizeof ur);

  if (dr[0] != 1.0 || ur[0] != 2.0)
    abort ();
  if (dr[1] != zr[1] || ur[1] != zr[1])
    abort ();

  /* Even when radial floor collapses to zero, its stored argument is kept.  */
  double _Complex small = 0.3 + 0.4i;
  double _Complex small_down = floor (small);
  double sr[2], sdr[2];
  memcpy (sr, &small, sizeof sr);
  memcpy (sdr, &small_down, sizeof sdr);
  if (sdr[0] != 0.0 || sdr[1] != sr[1])
    abort ();

  return 0;
}
