/* One component of Pease's 2014 winner, NOT its full overwrite chain. */
#include "fixture.h"
#define LEAP_YEAR(year) ((year) % 4U != 0U ? 0 : \
                        (year) % 100U != 0U ? 1 : (year) % 400U == 0U)
static unsigned audit_count;

static unsigned audit_year(unsigned year)
{
    ++audit_count;
    return year;
}

static int audited_leap_year(unsigned year)
{
#if USE_CORRECTED
    unsigned saved_year = audit_year(year);
    return LEAP_YEAR(saved_year);
#else
    return LEAP_YEAR(audit_year(year));
#endif
}

int main(void)
{
    audit_count = 0;
    if (audited_leap_year(2023) || audit_count != 1)
        return control_error();
    audit_count = 0;
    if (!audited_leap_year(2000))
        return control_error();
    /* Logging one year must produce one audit record, not three. */
    return property_result(audit_count == 1, "06_macro_repeated_effect");
}
