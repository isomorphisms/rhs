/* 2007 Wagner/Biondi mechanism reduction; source and scope in README.md. */
#include "fixture.h"

static void exchange(unsigned *left, unsigned *right)
{
#if USE_CORRECTED
    unsigned previous = *left;
    *left = *right;
    *right = previous;
#else
    *left ^= *right;
    *right ^= *left;
    *left ^= *right;
#endif
}

int main(void)
{
    unsigned left = 13, right = 71, shared = 71;
    exchange(&left, &right);
    if (left != 71 || right != 13)
        return control_error();
    exchange(&shared, &shared);
    /* Exchanging a location with itself must preserve its contents. */
    return property_result(shared == 71, "01_xor_swap_alias");
}
