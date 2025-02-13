# scripts/vulture_check.py

import subprocess
import sys

def main():
    print("Running Vulture dead code check...")
    cmd = ["vulture", "../election_app/"]
    # По умолчанию vulture при нахождении dead code не возвращает ошибку => code=0
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    output = result.stdout
    # Выводим, что нашла Vulture
    print(output)

    # Если хотим «падать», когда есть dead code:
    # Ищем "unused" или "unreachable" (по желанию).
    # (в older versions vulture писала "unused function", "unused class", etc.)
    if "unused" in output.lower() or "unreachable" in output.lower():
        print("Vulture found dead code/unreachable code.")
        sys.exit(1)
    else:
        print("No dead code found by Vulture")

if __name__ == "__main__":
    main()
