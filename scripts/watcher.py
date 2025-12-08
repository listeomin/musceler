# scripts/watcher.py
import os
import sys
import subprocess
import time
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "scrn"
SCRIPTS_DIR = BASE_DIR / "scripts"
SEND_LAST_SCRIPT = SCRIPTS_DIR / "send_last_screenshot.py"

# как часто опрашивать папку, сек
INTERVAL = 1.0

# путь к основному лог-файлу
LOG_FILE = BASE_DIR / "logs" / "musceler.log"


def setup_logging():
    """
    Настраиваем логирование в musceler.log.
    Используем отдельный файл, не stdout, чтобы не зависеть от launchd.
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [watcher] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )


def log_startup():
    """
    Логируем базовую информацию о запуске.
    """
    logging.info("===== watcher startup =====")
    logging.info("sys.argv: %s", sys.argv)
    logging.info("__file__: %s", __file__)
    logging.info("cwd: %s", os.getcwd())
    logging.info("HOME: %s", os.environ.get("HOME"))
    logging.info("USER: %s", os.environ.get("USER"))
    logging.info("PATH: %s", os.environ.get("PATH"))
    logging.info("SCREENSHOTS_DIR: %s", SCREENSHOTS_DIR)
    logging.info("===== end startup =====")


def list_png_files() -> set[Path]:
    return {
        p for p in SCREENSHOTS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".png"
    }


def handle_new_screenshot():
    """
    Запускаем send_last_screenshot.py тем же интерпретатором, что и watcher.
    """
    cmd = [sys.executable, str(SEND_LAST_SCRIPT)]
    logging.info("Запуск send_last_screenshot: %s", cmd)
    try:
        result = subprocess.run(cmd, text=True, capture_output=True)
    except Exception as e:
        logging.error("Ошибка при запуске send_last_screenshot.py: %s", e)
        return

    logging.info("send_last_screenshot returncode=%s", result.returncode)
    if result.returncode != 0:
        logging.error(
            "send_last_screenshot stderr/stdout: %s",
            (result.stderr or result.stdout).strip(),
        )
    else:
        logging.info(
            "send_last_screenshot output: %s",
            (result.stdout or "").strip(),
        )


def main():
    setup_logging()
    log_startup()

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("Старт. Наблюдаю за %s", SCREENSHOTS_DIR)

    known = list_png_files()

    while True:
        try:
            current = list_png_files()
        except Exception as e:
            logging.error("Ошибка при чтении директории скриншотов: %s", e)
            time.sleep(INTERVAL)
            continue

        new_files = current - known
        if new_files:
            names = ", ".join(p.name for p in new_files)
            logging.info("Найдены новые файлы: %s", names)
            for p in sorted(new_files, key=lambda f: f.stat().st_mtime):
                logging.info("Обработка файла: %s", p)
                handle_new_screenshot()
        else:
            logging.debug("Нет новых файлов")

        known = current
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
