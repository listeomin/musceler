import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOUND_PATH = BASE_DIR.parent / "assets" / "notification-success.mp3"

# AppleScript одной строкой: ждём 7 секунд и жмём кнопку у первого баннера
CLOSE_NOTIFICATION_SCRIPT = '''
delay 7
tell application "System Events"
    tell process "NotificationCenter"
        try
            click button 1 of window 1
        end try
    end tell
end tell
'''.strip()


def extract_screenshot_number(url: str) -> str:
    m = re.search(r'scrn-(\d+)\.png', url)
    return m.group(1) if m else "?"


def notify_screenshot_uploaded(url: str) -> None:
    number = extract_screenshot_number(url)
    message = f"HHRRRru!!1 Скриншот {number} на сервере!"

    # звук
    try:
        subprocess.Popen(
            ["afplay", str(SOUND_PATH)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass

    # уведомление
    try:
        subprocess.run(
            [
                "/usr/local/bin/terminal-notifier",
                "-title", "Musceler",
                "-message", message,
                "-open", url,
                # "-appIcon", ...
            ],
            check=False,
        )
    except FileNotFoundError:
        pass

    # автозакрытие через 7 секунд
    try:
        subprocess.Popen(
            ["osascript", "-e", CLOSE_NOTIFICATION_SCRIPT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        # нет osascript — просто не закрываем
        pass
