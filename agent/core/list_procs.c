#include <stdio.h>
#include <stdlib.h>

#include "core.h"

#define ROOM 4096

static struct core_proc procs[ROOM];   /* ~320 КБ — не на стек */

int main(int argc, char *argv[]) {
    int32_t room = ROOM;
    if (argc > 1) {
        long v = strtol(argv[1], NULL, 10);
        if (v >= 0 && v <= ROOM)
            room = (int32_t)v;
    }

    int32_t count = 0;
    int err = core_list_procs(procs, room, &count);
    if (err != 0) {
        printf("core_list_procs: error %d, need %d places, have %d\n", err, count, room);
        return 1;
    }
    for (int32_t i = 0; i < count; i++)
        printf("%7lld %7lld %s\n", (long long)procs[i].pid, (long long)procs[i].ppid, procs[i].name);
    printf("processes %d, sizeof %zu\n", count, sizeof(struct core_proc));
    return 0;
}
