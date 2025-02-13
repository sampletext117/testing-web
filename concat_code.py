#!/usr/bin/env python3
import os


def main():
    # Текущая директория, где запущен скрипт, считается корневой
    root_dir = os.getcwd()
    output_filename = "merged_code.txt"

    # Список разрешенных расширений файлов
    allowed_extensions = ['.py', '.sql', '.txt', '.feature', '.env', '.yml', '', '.yaml']
    # Список директорий, которые нужно исключить из обхода (указывайте имена директорий относительно корня)
    skip_dirs = ['slave', 'my_project.egg-info', '.git', 'nginx', 'venv']

    # Открываем результирующий файл для записи (перезаписываем, если уже существует)
    with open(output_filename, "w", encoding="utf-8") as out_file:
        # Рекурсивно проходим по всем поддиректориям и файлам
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Исключаем заданные директории из обхода, чтобы os.walk не заходил в них
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]

            for filename in filenames:
                # Пропускаем результирующий файл, чтобы не включить его в объединение
                if filename == output_filename:
                    continue

                # Получаем расширение файла в нижнем регистре
                ext = os.path.splitext(filename)[1].lower()
                # Если расширение файла не входит в список разрешенных, пропускаем его
                if ext not in allowed_extensions:
                    continue

                # Полный путь к файлу
                file_path = os.path.join(dirpath, filename)
                # Относительный путь к файлу от корневой директории
                rel_path = os.path.relpath(file_path, root_dir)

                # Записываем заголовок с именем файла, выделенным символом '#'
                out_file.write(f"## {rel_path}\n")

                try:
                    # Читаем содержимое файла
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    out_file.write(content)
                except Exception as e:
                    # В случае ошибки чтения записываем информацию об ошибке
                    out_file.write(f"Ошибка при чтении файла: {e}")

                # Добавляем две пустые строки для разделения файлов
                out_file.write("\n\n")


if __name__ == "__main__":
    main()
