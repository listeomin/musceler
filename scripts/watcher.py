# scripts/watcher.py
import subprocess
import time
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "scrn"
SCRIPTS_DIR = BASE_DIR / "scripts"
SEND_LAST_SCRIPT = SCRIPTS_DIR / "send_last_screenshot.py"

# как часто опрашивать папку, сек
INTERVAL = 1.0


def list_png_files() -> set[Path]:
    return {
        p for p in SCREENSHOTS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".png"
    }


def handle_new_screenshot():
    """
    Просто вызываем твой send_last_screenshot.py как есть.
    Вся логика уже внутри него.
    """
    cmd = ["python3", str(SEND_LAST_SCRIPT)]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        print("[watcher] Ошибка при запуске send_last_screenshot.py:")
        print(result.stderr or result.stdout)
    else:
        print("[watcher] send_last_screenshot.py отработал:")
        print(result.stdout.strip())


def main():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[watcher] Старт. Наблюдаю за {SCREENSHOTS_DIR}")

    known = list_png_files()

    while True:
        current = list_png_files()
        new_files = current - known
        if new_files:
            # обрабатываем по порядку появления
            for _ in sorted(new_files, key=lambda p: p.stat().st_mtime):
                handle_new_screenshot()
        known = current
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
