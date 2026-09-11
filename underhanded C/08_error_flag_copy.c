/* Dunphy's 2015 local-error-flag mechanism; not the full numeric entry. */
#include "fixture.h"
#if USE_CORRECTED
static void validate_count(int count, int *invalid)
{
    *invalid = count < 0;
}
#else
static void validate_count(int count, int invalid)
{
    invalid = count < 0;
    /* The local write does not reach the caller. */
}
#endif

static int accept_count(int count)
{
    int invalid = 0;
#if USE_CORRECTED
    validate_count(count, &invalid);
#else
    validate_count(count, invalid);
#endif
    return !invalid;
}

int main(void)
{
    if (!accept_count(0) || !accept_count(12))
        return control_error();
    return property_result(!accept_count(-1), "08_error_flag_copy");
}
