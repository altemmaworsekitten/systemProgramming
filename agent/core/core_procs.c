#include "core.h"

#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

/* Linux: список процессов по папкам /proc/<номер> и файлам /proc/<номер>/stat. */
int core_list_procs(struct core_proc *out, int32_t max, int32_t *count) {
    if (count == NULL || max < 0 || (out == NULL && max > 0))
        return EINVAL;
    *count = 0;

    DIR *dir = opendir("/proc");
    if (dir == NULL)
        return errno;

    struct dirent *ent;
    while ((ent = readdir(dir)) != NULL) {
        if (!isdigit((unsigned char)ent->d_name[0]))
            continue;                       /* cpuinfo, self, ... — не процессы */

        char path[300];                 /* d_name до 255 байт */
        snprintf(path, sizeof(path), "/proc/%s/stat", ent->d_name);
        FILE *f = fopen(path, "r");
        if (f == NULL)
            continue;                       /* процесс успел завершиться */

        char line[512];
        int ok = fgets(line, sizeof(line), f) != NULL;
        fclose(f);
        if (!ok)
            continue;

        /* Формат: pid (name) state ppid ... — имя может содержать пробелы и скобки. */
        char *open = strchr(line, '(');
        char *close = strrchr(line, ')');
        if (open == NULL || close == NULL || close < open)
            continue;

        long long pid, ppid;
        if (sscanf(line, "%lld", &pid) != 1)
            continue;
        if (sscanf(close + 1, " %*c %lld", &ppid) != 1)
            continue;

        if (*count < max) {
            struct core_proc *p = &out[*count];
            p->pid = pid;
            p->ppid = ppid;
            size_t len = (size_t)(close - open - 1);
            if (len >= CORE_NAME_MAX)
                len = CORE_NAME_MAX - 1;
            memcpy(p->name, open + 1, len);
            p->name[len] = '\0';
        }
        (*count)++;                         /* считаем и то, что не поместилось */
    }
    closedir(dir);

    return *count > max ? ERANGE : 0;
}
