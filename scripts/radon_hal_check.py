# scripts/radon_hal_check.py

import subprocess
import sys

def main():
    print("Running radon Halstead Complexity check...")
    cmd = ["radon", "hal", "../election_app/"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    # По умолчанию не завершаемся ошибкой,
    # но если нужно «завалить» при высоких метриках,
    # можно парсить результат и сделать sys.exit(1) при необходимости.

if __name__ == "__main__":
    main()
