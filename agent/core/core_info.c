#include "core.h"

#include <errno.h>
#include <string.h>
#include <sys/sysinfo.h>
#include <unistd.h>

int core_get_info(struct core_info *out) {
    if (out == NULL)
        return EINVAL;
    memset(out, 0, sizeof(*out));

    out->pid = getpid();

    long cpus = sysconf(_SC_NPROCESSORS_ONLN);
    if (cpus < 0)
        return errno;
    out->cpus = (int32_t)cpus;

    long page = sysconf(_SC_PAGESIZE);
    if (page < 0)
        return errno;
    out->page_size = (int32_t)page;

    if (gethostname(out->host, sizeof(out->host)) != 0)
        return errno;
    out->host[sizeof(out->host) - 1] = '\0';

    struct sysinfo si;
    if (sysinfo(&si) != 0)
        return errno;
    out->uptime_s = si.uptime;

    return 0;
}
