/* 2013 Szymaniak reduction: nonzero comparison results are not Boolean bits. */
#include "fixture.h"

static int both_differ(int contents_difference, int location_difference)
{
#if USE_CORRECTED
    return contents_difference != 0 && location_difference != 0;
#else
    return contents_difference & location_difference;
#endif
}

int main(void)
{
    if (!both_differ(1, 1) || both_differ(0, 4) || both_differ(2, 0))
        return control_error();
    /* Each input reports a difference; disjoint bits must not cancel it. */
    return property_result(both_differ(2, 4) != 0, "04_bitwise_truth");
}
