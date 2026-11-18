#ifndef CORE_H
#define CORE_H

#include <stdint.h>

#ifdef _WIN32
#define CORE_API __declspec(dllexport)
#else
#define CORE_API
#endif

#define CORE_HOST_LEN 256

/* Факты о системе, которые ядро отдаёт мозгу. Порядок полей совпадает с CoreInfo в brain.py. */
struct core_info {
    int64_t pid;                 /* смещение 0   */
    int32_t cpus;                /* смещение 8   */
    int32_t page_size;           /* смещение 12  */
    char host[CORE_HOST_LEN];    /* смещение 16  */
    int64_t uptime_s;            /* смещение 272, итог 280 байт */
};

/* Заполняет *out. Возвращает 0 при успехе или код ошибки системы (errno / GetLastError). */
CORE_API int core_get_info(struct core_info *out);

#define CORE_NAME_MAX 64

/* Одна строка списка процессов: номер, номер родителя, имя. 80 байт, порядок как в CoreProc (brain.py). */
struct core_proc {
    int64_t pid;                 /* смещение 0  */
    int64_t ppid;                /* смещение 8  */
    char name[CORE_NAME_MAX];    /* смещение 16, итог 80 байт */
};

/* Пишет в out не больше max строк, в *count — сколько процессов найдено всего.
   0 — все поместились; ERANGE (Linux, macOS) / ERROR_INSUFFICIENT_BUFFER (Windows) — мест мало;
   EINVAL — неверные аргументы; иначе код ошибки системы. */
CORE_API int core_list_procs(struct core_proc *out, int32_t max, int32_t *count);

#endif
