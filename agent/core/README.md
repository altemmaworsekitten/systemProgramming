# Ядро агента (C)

Ядро собирается в динамическую библиотеку: `sentry_core.dll` в Windows, `libsentry_core.dylib` в macOS,
`libsentry_core.so` в Linux. Первая функция появляется на паре 2.

| Файл | Что в нём |
|---|---|
| `core.h` | структуры `core_info` (280 байт) и `core_proc` (80 байт), макрос `CORE_API`, объявления `core_get_info` и `core_list_procs` |
| `core_info.c` | `core_get_info` для macOS/Linux: getpid, sysconf, gethostname, sysinfo; при ошибке возвращает errno |
| `core_procs.c` | `core_list_procs` для Linux: папки `/proc` и файлы `/proc/N/stat`; при нехватке мест — ERANGE и полное число в `count` |
| `list_procs.c` | проверочная программа: печатает `pid ppid name` по строке на процесс; аргумент — число мест |
| `show_info.c` | проверочная программа: вызывает `core_get_info` и печатает поля, размер и адрес структуры |

Сборка в Linux (из `agent/core`):

```
gcc -Wall -Wextra -o show_info show_info.c core_info.c && ./show_info
gcc -Wall -Wextra -o list_procs list_procs.c core_procs.c && ./list_procs | tail -1
gcc -Wall -Wextra -shared -fPIC -o libsentry_core.so core_info.c core_procs.c
```
