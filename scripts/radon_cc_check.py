# scripts/radon_cc_check.py

import subprocess
import sys


def main():
    print("Running radon Cyclomatic Complexity check...")
    # Для Radon < 5: --total-average --fail "C" говорит:
    # "если какая-либо функция имеет CC >= 11 (класс C), заверши с кодом 1"
    # cmd = ["radon", "cc", "--total-average", "--fail", "C", "../election_app/"]

    # Если у вас Radon 5+, возможно:
    cmd = ["radon", "cc", "--min C", "--max 2", "--fail-on C", "../election_app/"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        # Если check=True, при ненулевом коде возврата будет вызван CalledProcessError
        print(result.stdout)
        print("Radon CC check passed.")
    except subprocess.CalledProcessError as e:
        # Выводим stdout и stderr для отладки
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
