import re
import subprocess


def extract_screenshot_number(url: str) -> str:
    """
    Извлекает номер из вида .../scrn-00025.png -> 00025
    Если не получилось — возвращает '?'
    """
    m = re.search(r'scrn-(\d+)\.png', url)
    return m.group(1) if m else "?"


def notify_screenshot_uploaded(url: str) -> None:
    """
    Показывает системное уведомление через terminal-notifier.
    Текст: "HHRRRru!!1 Скриншот %НОМЕР% на сервере!"
    Клик по уведомлению открывает URL в браузере по умолчанию.
    """
    number = extract_screenshot_number(url)
    message = f"HHRRRru!!1 Скриншот {number} на сервере!"

    try:
        subprocess.run(
            [
                "terminal-notifier",
                "-title", "Musceler",
                "-message", message,
                "-open", url,
            ],
            check=False,
        )
    except FileNotFoundError:
        # terminal-notifier не установлен / не найден — молча игнорируем
        pass
