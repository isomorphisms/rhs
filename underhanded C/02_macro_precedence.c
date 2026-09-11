/* 2008 Akesson mechanism reduction; no out-of-bounds access is performed. */
#include "fixture.h"
#if USE_CORRECTED
#define PIXEL_BYTES(small) (3U << (!(small)))
#else
#define PIXEL_BYTES(small) (3U << (!small))
#endif

int main(void)
{
    unsigned maximum = 255;
    if (PIXEL_BYTES(1) != 3U || PIXEL_BYTES(0) != 6U)
        return control_error();
    /* Equivalent comparisons must select the same storage width. */
    return property_result(PIXEL_BYTES(256U > maximum) ==
                           PIXEL_BYTES(maximum < 256U),
                           "02_macro_precedence");
}
