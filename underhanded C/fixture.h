#ifndef UNDERHANDED_C_FIXTURE_H
#define UNDERHANDED_C_FIXTURE_H
#include <stdio.h>
#ifndef USE_CORRECTED
#define USE_CORRECTED 0
#endif
#if USE_CORRECTED != 0 && USE_CORRECTED != 1
#error USE_CORRECTED must be 0 or 1
#endif
static int control_error(void)
{
    fputs("CONTROL_FAIL\n", stderr);
    return 2;
}
static int property_result(int holds, const char *name)
{
    puts("CONTROL_OK");
    printf("%s %s\n", holds ? "CONTRACT_PASS" : "CONTRACT_FAIL", name);
    return holds ? 0 : 1;
}
#endif
