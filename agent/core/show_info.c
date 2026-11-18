#include <inttypes.h>
#include <stdio.h>

#include "core.h"

int main(void) {
    struct core_info info;
    int err = core_get_info(&info);
    if (err != 0) {
        printf("core_get_info: error %d\n", err);
        return 1;
    }
    printf("pid:       %" PRId64 "\n", info.pid);
    printf("cpus:      %" PRId32 "\n", info.cpus);
    printf("page_size: %" PRId32 "\n", info.page_size);
    printf("host:      %s\n", info.host);
    printf("uptime_s:  %" PRId64 "\n", info.uptime_s);
    printf("sizeof(struct core_info) = %zu\n", sizeof(info));
    printf("address of info = %p\n", (void *)&info);
    return 0;
}
