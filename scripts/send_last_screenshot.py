from pathlib import Path
import subprocess
import sys

# Базовая директория проекта: /Users/ufoanima/Dev/personal/musceler
BASE_DIR = Path(__file__).resolve().parent.parent

# Папка со скриптами: /Users/ufoanima/Dev/personal/musceler/scripts
SCRIPTS_DIR = BASE_DIR / "scripts"

# Папка со скриншотами: /Users/ufoanima/Dev/personal/musceler/scrn
SCREENSHOTS_DIR = BASE_DIR / "scrn"

# Путь к musceler.py
MUSCELER_SCRIPT = SCRIPTS_DIR / "musceler.py"

# Импортируем уведомления из отдельного файла notification.py
from notification import notify_screenshot_uploaded


def get_last_screenshot() -> Path:
    if not SCREENSHOTS_DIR.exists():
        print(f"Папка со скриншотами не найдена: {SCREENSHOTS_DIR}")
        sys.exit(1)

    # Берём файлы PNG в папке
    files = sorted(
        [p for p in SCREENSHOTS_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".png"],
        key=lambda p: p.stat().st_mtime,
    )

    if not files:
        print(f"В папке {SCREENSHOTS_DIR} нет PNG-файлов")
        sys.exit(1)

    return files[-1]  # самый свежий по времени изменения


def run_musceler(local_path: Path) -> str:
    # Запускаем musceler.py как отдельный процесс и читаем его вывод
    cmd = ["python3", str(MUSCELER_SCRIPT), str(local_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("musceler.py завершился с ошибкой:")
        print(result.stderr or result.stdout)
        sys.exit(result.returncode)

    # Ищем строку "Готово. URL: ..."
    url = None
    for line in (result.stdout or "").splitlines():
        if "Готово. URL:" in line:
            url = line.split("Готово. URL:")[-1].strip()
            break

    if not url:
        print("Не удалось извлечь URL из вывода musceler.py")
        print("Вывод был:")
        print(result.stdout)
        sys.exit(1)

    return url


def copy_to_clipboard(text: str):
    # macOS: утилита pbcopy
    proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
    proc.communicate(input=text)


def main():
    last = get_last_screenshot()
    print(f"Последний скриншот: {last}")

    url = run_musceler(last)
    print(f"URL: {url}")

    copy_to_clipboard(url)
    print("Ссылка скопирована в буфер обмена.")

    notify_screenshot_uploaded(url)


if __name__ == "__main__":
    main()
