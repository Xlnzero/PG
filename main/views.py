import logging

# Настройка логгера (можно поместить это в settings.py или в начале файла views.py)
logging.basicConfig(level=logging.INFO)  # Уровень логирования INFO
logger = logging.getLogger(__name__)    # Имя текущего модуля

from django.shortcuts import render, redirect
import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import ContactForm
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.mail import send_mail

import re  # Добавляем импорт модуля регулярных выражений



menu = [
    {'name': 'Главная', 'route_name': 'home'},
    {'name': 'О компании', 'route_name': 'about'},
    {'name': 'Памятники', 'route_name': 'pam'},
    {'name': 'Аксессуары', 'route_name': 'aks'},  # Указываем только категорию, без '_gal'
    {'name': 'Наши работы', 'route_name': 'obj'},
    {'name': 'Виды гранита', 'route_name': 'vid'},
]




def contact_view(request):
    title = 'Заявка на звонок'
    success_message = None
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data["full_name"]
            phone = form.cleaned_data["phone"]

            try:
                send_mail(
                    "Новая заявка с сайта",
                    f"ФИО: {full_name}\nТелефон: {phone}",
                    "xlnzeroeva@gmail.com",
                    ["xlnzeroeva@gmail.com"],
                    fail_silently=False,
                )
                success_message = "Ваше сообщение отправлено!"
            except Exception as e:
                print(f"Ошибка при отправке письма: {e}")

            form = ContactForm()
    else:
        form = ContactForm()
    return render(request, "main/contact.html", context={'menu': menu, 'title': title, "form": form, "success_message": success_message})






def get_title_from_menu(menu, current_route_name):
    for item in menu:
        if item['route_name'] == current_route_name:
            return item['name']
    return 'Без названия'  # Значение по умолчанию


def index(request):
    title = get_title_from_menu(menu, 'home')
    return render(request, 'main/index.html', context={'menu': menu, 'title': title})


def about(request):
    title = get_title_from_menu(menu, 'about')
    return render(request, 'main/about.html',  context={'menu': menu, 'title': title})

def pam(request):
    title = get_title_from_menu(menu, 'pam')
    return render(request, 'main/pam.html', context={'menu': menu, 'title': title})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))





















def aks(request):
    return dynamic_gallery(request, 'aks')




def obj(request):
    return dynamic_gallery(request, 'obj')


def vid(request):
    return dynamic_gallery(request, 'vid')

def cat(request):
    title = 'Каталог ПАНГРАН'
    return render(request, 'main/cat.html',  context={'menu': menu, 'title': title})


import os
import re
from django.shortcuts import render


# Функция для естественной сортировки (на случай, если имена файлов содержат числа)
def natural_key(filename):
    name = os.path.splitext(filename)[0]
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', name)]


def model(request):
    # Путь к папке с 360-моделью
    base_folder_360 = os.path.join(BASE_DIR, 'main', 'static', 'main', 'img', '360')

    # Получаем список папок внутри base_folder_360
    folders = sorted(
        [f for f in os.listdir(base_folder_360) if os.path.isdir(os.path.join(base_folder_360, f))],
        key=lambda x: x  # либо natural_key(x) если в названиях папок есть числа
    )

    # Для каждой папки из 360 выбираем превью – например, 17-е фото (при условии, что нумерация начинается с 0 -> индекс 16)
    preview_index = 16
    preview_images = {}
    for folder in folders:
        folder_path = os.path.join(base_folder_360, folder)
        # Получаем список файлов в папке, которые являются изображениями
        images = sorted(
            [f for f in os.listdir(folder_path) if
             os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))],
            key=natural_key
        )
        if images:
            if len(images) > preview_index:
                preview_images[folder] = images[preview_index]
            else:
                preview_images[folder] = images[-1]  # если в папке меньше кадров – берем последний
        else:
            preview_images[folder] = None

    title = '3D модели'
    context = {
        'folders': folders,
        'preview_images': preview_images,
        'title': title,
        'menu': menu  # убедитесь, что переменная menu доступна
    }
    return render(request, 'main/model2.html', context)


def about_mo(request):
    title = 'Мобильный офис Пангран'
    return render(request, 'main/about_mo.html', context={'menu': menu, 'title': title})





def page_not_found(request, exception):
    return HttpResponseNotFound("Не существует")



import os
import re



def update_od_model(request):
    folder = request.GET.get('folder', '1')
    base_path = request.GET.get('base_path', 'OD')  # Используем базовый путь для получения папки
    image_folder_od_model = os.path.join(BASE_DIR, 'main', 'static', 'main', 'img', base_path, folder)
    images_od_model = [f for f in os.listdir(image_folder_od_model) if os.path.isfile(os.path.join(image_folder_od_model, f))]
    # Сортируем изображения по числовому значению
    images_od_model.sort(key=lambda x: int(os.path.splitext(x)[0]))
    return JsonResponse({'images': images_od_model})


def dynamic_model(request, category):
    import os
    import re

    # Словарь для маппинга категорий
    title_map = {
        'zv': 'Цветники',
        'od': 'Одиночные памятники',
        'pol': 'Полуторные памятники',
        'dv': 'Двойные памятники',
        'vip': 'Эксклюзивные памятники',
    }

    # Получаем заголовок категории
    title = title_map.get(category, 'Категория не найдена')

    # Путь к базовой папке
    folder_base_path = os.path.join(BASE_DIR, 'main', 'static', 'main', 'img', 'PAM', category)

    # Получаем список папок и сортируем их по числовому значению
    all_folders = [f for f in os.listdir(folder_base_path) if os.path.isdir(os.path.join(folder_base_path, f))]
    sorted_folders = sorted(all_folders, key=lambda x: int(re.match(r'\d+', x).group()))

    # Формируем отображаемые названия папок (без номера)
    display_folders = [re.sub(r'^\d+\s', '', folder) for folder in sorted_folders]

    # Выбираем папку (по умолчанию первую) или указанную в запросе
    folder = request.GET.get('folder', sorted_folders[0])
    image_folder = os.path.join(folder_base_path, folder)

    # Список изображений в выбранной папке
    images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

    # Сортируем изображения
    images.sort(key=lambda x: int(re.sub(r'\D', '', os.path.splitext(x)[0])))

    # Передаём данные в шаблон
    context = {
        'menu': menu,
        'title': title,
        'images': images,
        'category': category,
        'folders': zip(sorted_folders, display_folders),  # Передаем пару (реальное имя, отображаемое имя)
        'current_folder': folder
    }
    return render(request, 'main/dynamic_model.html', context)





import os
from django.shortcuts import render

def natural_key(filename):
    # Извлекаем имя файла без расширения
    name = os.path.splitext(filename)[0]
    # Разбиваем строку на части, где числа находятся между текстовыми фрагментами
    parts = re.split(r'(\d+)', name)
    # Преобразуем числовые части в int, а текстовые – к нижнему регистру
    return [int(part) if part.isdigit() else part.lower() for part in parts]

def dynamic_gallery(request, category):
    # Маппинг заголовка и основной папки
    title_map = {
        'aks': 'Аксессуары',
        'obj': 'Наши работы',
        'vid': 'Виды гранита',
    }
    base_path_map = {
        'aks': '1 Аксессуары',
        'obj': '2 Наши работы',
        'vid': '3 Виды гранита',
    }

    title = title_map.get(category, 'Категория не найдена')
    base_folder = base_path_map.get(category)
    if not base_folder:
        return render(request, 'main/dynamic_gallery.html', {'title': title, 'gallery': []})

    base_path = os.path.join(BASE_DIR, 'main', 'static', 'main', 'img', 'DRUG', base_folder)

    # Получаем список подпапок (например, "1 Гравировка", "2 ...")
    subfolders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    # Создаем список объектов галереи
    gallery = []
    for sub in subfolders:
        subfolder_path = os.path.join(base_path, sub)
        # Собираем файлы с нужными расширениями и сортируем с помощью natural_key
        images = sorted(
            [img for img in os.listdir(subfolder_path)
             if img.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))],
            key=natural_key
        )

        # Если в имени есть пробел, отбрасываем всё до первого пробела для отображения
        display_name = sub.split(" ", 1)[1] if " " in sub else sub
        gallery.append({
            'folder': sub,             # оригинальное имя папки (для формирования путей)
            'display_name': display_name,  # очищенное имя для отображения
            'images': images,
        })

    context = {
        'menu': menu,  # убедитесь, что переменная menu определена
        'title': title,
        'gallery': gallery,
        'base_folder': base_folder,  # используется при формировании полного пути к файлам
    }

    return render(request, 'main/dynamic_gallery.html', context)


