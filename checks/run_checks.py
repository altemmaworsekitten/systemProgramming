"""Проверки репозитория по дисциплине «Системное программирование».

Запускается в GitHub Actions на трёх системах (Windows, macOS, Linux) после каждой
отправки кода и локально командой: python checks/run_checks.py

Что проверяется:
1. Лабораторные работы, у которых есть код: программа собирается и печатает
   ожидаемую строку. Код для другой системы пропускается (hello.c с windows.h
   собирается только в Windows, с unistd.h — только в macOS и Linux).
2. Проверки агента-сторожа. Каждая открывается на своей паре; до этого она
   отмечена как «ещё не открыта» и на результат не влияет.

Файл ведёт преподаватель: при обновлении материалов он заменяется новой версией.
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM = {"Windows": "win", "Darwin": "mac", "Linux": "linux"}[platform.system()]
SYSTEM_NAME = {"win": "Windows", "mac": "macOS", "linux": "Linux"}[SYSTEM]

# Проверки агента: номер, пара, на которой открывается, название.
AGENT_CHECKS = [
    (1, 4, "Список процессов совпадает с системным"),
    (2, 6, "Процесс загружает процессор больше 80%"),
    (3, 8, "Память процесса растёт без остановки"),
    (4, 10, "Изменён файл hosts"),
    (5, 11, "Новый файл в папке автозагрузки пользователя"),
    (6, 12, "Новая запись в системной автозагрузке"),
    (7, 13, "Пять неудачных входов подряд"),
    (8, 14, "Открыт новый порт"),
    (9, 15, "Модель ИИ занимает больше заданной памяти"),
    (10, 18, "В отправленных данных нет имени пользователя"),
    (11, 20, "Ядро работает в фоне и отвечает"),
    (12, 21, "Подключено новое устройство"),
    (13, 22, "Запущена программа без подписи или не из пакета"),
]
OPENED = 0  # сколько проверок агента уже открыто; растёт с каждой парой

PID_LINE = re.compile(r"agent v0(?: \(python\))?, pid= ?\d+")


def target_of_c(text):
    return "win" if "windows.h" in text else "posix"


def target_of_py(text):
    return "win" if "windll" in text else "posix"


def fits(target):
    return target == "win" if SYSTEM == "win" else target == "posix"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60, **kw)


def build_c(src, out_dir):
    exe = Path(out_dir) / ("hello.exe" if SYSTEM == "win" else "hello")
    if SYSTEM == "win":
        r = run(["cl", "/nologo", str(src), f"/Fe:{exe}", f"/Fo:{out_dir}\\"])
    else:
        cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
        r = run([cc, "-o", str(exe), str(src)])
    return exe, r


def check_lab01():
    rows = []
    lab = ROOT / "labs" / "01-process-inside"
    c, py = lab / "hello.c", lab / "hello.py"
    if not c.exists() and not py.exists():
        return [("ЛР 1", "hello.c, hello.py", "не сдано", "")], True
    ok = True
    if c.exists():
        text = c.read_text(encoding="utf-8", errors="replace")
        if not fits(target_of_c(text)):
            rows.append(("ЛР 1", "hello.c", "пропущено", f"код для другой системы, {SYSTEM_NAME} его не собирает"))
        else:
            with tempfile.TemporaryDirectory() as d:
                exe, r = build_c(c, d)
                if r.returncode != 0:
                    ok = False
                    rows.append(("ЛР 1", "hello.c", "ошибка", "не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150]))
                else:
                    out = run([str(exe)], input="\n").stdout
                    if PID_LINE.search(out):
                        rows.append(("ЛР 1", "hello.c", "пройдено", PID_LINE.search(out).group(0)))
                    else:
                        ok = False
                        rows.append(("ЛР 1", "hello.c", "ошибка", "нет строки «agent v0, pid=…» в выводе"))
    if py.exists():
        text = py.read_text(encoding="utf-8", errors="replace")
        if not fits(target_of_py(text)):
            rows.append(("ЛР 1", "hello.py", "пропущено", f"код для другой системы, в {SYSTEM_NAME} не запускается"))
        else:
            r = run([sys.executable, str(py)], input="\n")
            m = PID_LINE.search(r.stdout)
            if r.returncode == 0 and m:
                rows.append(("ЛР 1", "hello.py", "пройдено", m.group(0)))
            else:
                ok = False
                tail = (r.stderr.strip().splitlines() or ["нет строки «agent v0 (python), pid=…» в выводе"])[-1]
                rows.append(("ЛР 1", "hello.py", "ошибка", tail[:150]))
    return rows, ok


def main():
    # Консоль Windows по умолчанию в cp1252: русский текст выводится в UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    rows, ok = check_lab01()
    passed = 0  # проверки агента появятся с пары 4
    lines = [f"## Проверки · {SYSTEM_NAME}", "",
             "| Работа | Файл | Результат | Подробности |", "|---|---|---|---|"]
    lines += [f"| {a} | `{b}` | {c} | {d} |" for a, b, c, d in rows]
    lines += ["", f"### Агент-сторож: проверок пройдено {passed} / {len(AGENT_CHECKS)}", "",
              "| № | Пара | Проверка | Результат |", "|---|---|---|---|"]
    for n, pair, name in AGENT_CHECKS:
        state = "ещё не открыта" if n > OPENED else "не пройдена"
        lines.append(f"| {n} | {pair} | {name} | {state} |")
    report = "\n".join(lines)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
