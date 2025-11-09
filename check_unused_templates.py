import os
import re

# === НАСТРОЙКИ ===
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))  # корень проекта (где manage.py)
TEMPLATES_DIR = os.path.join(PROJECT_DIR, 'main', 'templates')  # путь к шаблонам

# === ПОИСК ===
used_templates = set()
html_files = []

# 1️⃣ Собираем все html-файлы
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, TEMPLATES_DIR).replace('\\', '/')
            html_files.append(rel_path)

# 2️⃣ Ищем упоминания шаблонов во всем проекте
pattern = re.compile(r"['\"]([\w\/\-\_]+\.html)['\"]")

for root, _, files in os.walk(PROJECT_DIR):
    for f in files:
        if f.endswith(('.py', '.html')):
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    matches = pattern.findall(content)
                    used_templates.update(matches)
            except Exception:
                pass  # если какой-то файл не читается, просто пропускаем

# 3️⃣ Проверяем, какие шаблоны не используются
unused = []
for html in html_files:
    # Django иногда ищет 'main/osn_gallery.html', поэтому проверяем оба варианта
    possible_names = {html, f"main/{html}"}
    if not possible_names & used_templates:
        unused.append(html)

# === РЕЗУЛЬТАТ ===
print("\nНеиспользуемые шаблоны:\n")
if unused:
    for f in sorted(unused):
        print(f" - {f}")
else:
    print("Все шаблоны используются!")
