/* 2013 Nicolussi reduction: equality of IDs is not identity of storage. */
#include "fixture.h"
struct record { unsigned user_id, distance; };

static void copy_result(struct record *destination, const struct record *source)
{
#if USE_CORRECTED
    if (destination != source)
#else
    if (destination->user_id != source->user_id)
#endif
        *destination = *source;
}

int main(void)
{
    struct record destination = {1, 0}, source = {2, 6};
    copy_result(&destination, &source);
    if (destination.user_id != 2 || destination.distance != 6)
        return control_error();
    copy_result(&destination, &destination);
    if (destination.user_id != 2 || destination.distance != 6)
        return control_error();
    destination = (struct record){7, 0};
    source = (struct record){7, 6};
    copy_result(&destination, &source);
    return property_result(destination.user_id == 7 && destination.distance == 6,
                           "05_equality_identity");
}
