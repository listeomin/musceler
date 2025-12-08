import re
import sys
import subprocess
from pathlib import Path

# Настройки
SERVER = "root@92.255.76.109"
REMOTE_DIR = "/var/www/hhrrr.ru/musceler"
BASE_URL = "http://hhrrr.ru/musceler"
SSH_KEY = "/Users/ufoanima/.ssh/id_rsa"

# Имена вида scrn-00001.png, scrn-12345.jpg и т.п.
SCRN_PATTERN = re.compile(r"^scrn-(\d{5})\.(png|jpg|jpeg)$", re.IGNORECASE)


def get_next_scrn_name() -> str:
    """
    Подключается к серверу, смотрит файлы в musceler,
    находит максимальный scrn-xxxxx.* и возвращает следующее имя (xxxxx + 1).
    """
    cmd = ["ssh", "-i", SSH_KEY, SERVER, "ls", "-1", REMOTE_DIR]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Предупреждение: не удалось получить список файлов, начинаю с scrn-00001.png")
        return "scrn-00001.png"

    max_num = 0
    for line in result.stdout.splitlines():
        name = line.strip()
        m = SCRN_PATTERN.match(name)
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num

    next_num = max_num + 1
    return f"scrn-{next_num:05d}.png"


def upload_file_as_scrn(local_path: Path):
    if not local_path.exists():
        print(f"Файл не найден: {local_path}")
        sys.exit(1)

    remote_name = get_next_scrn_name()
    remote_path = f"{SERVER}:{REMOTE_DIR}/{remote_name}"

    cmd = ["scp", "-i", SSH_KEY, str(local_path), remote_path]
    print("Выполняю:", " ".join(cmd))

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Ошибка при выполнении scp")
        sys.exit(result.returncode)

    url = f"{BASE_URL}/{remote_name}"
    print("Готово. URL:", url)
    return url


def main():
    if len(sys.argv) != 2:
        print("Использование: python3 musceler.py /путь/к/файлу")
        sys.exit(1)

    local_path = Path(sys.argv[1]).expanduser()
    upload_file_as_scrn(local_path)


if __name__ == "__main__":
    main()
