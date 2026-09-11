/* 2008 Meacham winner mechanism, reduced to one decimal pixel token. */
#include <string.h>
#include "fixture.h"

static int erase_pixel(unsigned sample, char output[16])
{
    if (sample > 255)
        return 0;
#if USE_CORRECTED
    return snprintf(output, 16, "0") == 1;
#else
    int length = snprintf(output, 16, "%u", sample);
    if (length < 1 || length >= 16)
        return 0;
    for (int position = 0; position < length; ++position)
        output[position] = '0';
    return 1;
#endif
}

int main(void)
{
    char first[16], second[16];
    if (!erase_pixel(0, first) || strcmp(first, "0") != 0)
        return control_error();
    if (!erase_pixel(7, first) || !erase_pixel(255, second))
        return control_error();
    /* Both represent black; the serialized redaction must also be identical. */
    return property_result(strcmp(first, second) == 0, "03_redaction_width");
}
