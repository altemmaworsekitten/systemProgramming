# Мозг агента (Python)

`brain.py` загружает ядро через `ctypes`, по расписанию вызывает его функции и решает, что считать нарушением.
Первая версия появляется на паре 3.

| Файл | Что в нём |
|---|---|
| `brain.py` | `CoreInfo` (зеркало `struct core_info`), `CoreProc`, `get_info()`, `list_procs()`, `parents()`, `send()` в n8n; печатает сообщение `agent_started` в JSON |

Запуск: `python3 brain.py` — только JSON; `python3 brain.py http://127.0.0.1:5678/webhook/agent` — ещё и отправка в n8n.
