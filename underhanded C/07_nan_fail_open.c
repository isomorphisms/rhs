/* 2015 NaN family reduction: comparison gate only, not NaN generation. */
#include <math.h>
#include "fixture.h"

static int acceptable_score(double score)
{
#if USE_CORRECTED
    return isfinite(score) && score >= 0.5;
#else
    return !(score < 0.5);
#endif
}

int main(void)
{
    if (acceptable_score(0.0) || !acceptable_score(1.0))
        return control_error();
#ifdef NAN
    if (!isnan(NAN)) {
        puts("UNSUPPORTED: NaN semantics unavailable");
        return 77;
    }
    /* Invalid numerical evidence must not become acceptance. */
    return property_result(!acceptable_score(NAN), "07_nan_fail_open");
#else
    puts("UNSUPPORTED: NAN unavailable");
    return 77;
#endif
}
