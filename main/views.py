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
    {'name': 'ПАМЯТНИКИ', 'route_name': 'pam'},
    {'name': 'Аксессуары', 'route_name': 'aks'},
    {'name': 'Наши работы', 'route_name': 'pam_got'},
    {'name': 'Виды гранита', 'route_name': 'vid'},
]





def contact_view(request):
    title = 'Заявка на звонок'
    success_message = None
    error_message = None
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data["full_name"]
            phone = form.cleaned_data["phone"]

            try:
                send_mail(
                    "Новая заявка с сайта",
                    f"ФИО: {full_name}\nТелефон: {phone}",
                    "pangran@bk.ru",
                    ["pangran@bk.ru"],
                    fail_silently=False,
                )
                success_message = "Ваше сообщение отправлено!"
                form = ContactForm()  # Очищаем форму после успешной отправки
            except Exception as e:
                logger.error(f"Ошибка при отправке письма: {e}")
                error_message = "Сообщение не отправлено. Проверьте не включен ли у вас VPN. Или позвоните нам на прямую +375 29 2222 759"
    else:
        form = ContactForm()
    return render(request, "main/contact.html", context={'menu': menu, 'title': title, "form": form, "success_message": success_message, "error_message": error_message})






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

def pam_got(request):
    title = get_title_from_menu(menu, 'pam_got')
    return render(request, 'main/pam_got.html', context={'menu': menu, 'title': title})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


import os
import re
from django.conf import settings
from django.shortcuts import render

def pam_got_gallery(request, category):
    # Маппинг для заголовков

    title_map = {
        'zv': 'Цветники',
        'od': 'Одиночные памятники',
        'pol': 'Полуторные памятники',
        'dv': 'Двойные памятники',
        'vip': 'Эксклюзивные памятники',
    }

    title = title_map.get(category, 'Категория не найдена')

    # Путь к базовой папке
    folder_base_path = os.path.join(
        settings.BASE_DIR, 'main', 'static', 'main', 'img', 'PAM_got', category
    )

    if not os.path.exists(folder_base_path):
        return render(request, 'main/pam_got_gallery.html', {
            'title': title,
            'gallery': [],
            'base_folder': category,
        })

    # Список подпапок
    all_folders = [
        f for f in os.listdir(folder_base_path)
        if os.path.isdir(os.path.join(folder_base_path, f))
    ]

    # Сортировка по числу в начале
    def folder_key(name):
        m = re.match(r'(\d+)', name)
        return int(m.group(1)) if m else 9999

    sorted_folders = sorted(all_folders, key=folder_key)

    gallery = []
    for folder in sorted_folders:
        folder_path = os.path.join(folder_base_path, folder)
        images = [
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]
        # сортировка картинок по числу в имени
        images.sort(key=lambda x: int(re.sub(r'\D', '', os.path.splitext(x)[0]) or 0))

        display_name = re.sub(r'^\d+\s*', '', folder)

        gallery.append({
            'folder': folder,
            'display_name': display_name,
            'images': images,
            'route_name': category,  # если нужно для условия в шаблоне
        })

    context = {
        'title': title,
        'gallery': gallery,
        'base_folder': category,
        'menu': menu,
    }
    return render(request, 'main/pam_got_gallery.html', context)



def aks(request):
    return osn_gallery(request, 'aks')




def obj(request):
    return osn_gallery(request, 'obj')


def vid(request):
    return osn_gallery(request, 'vid')

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
        'hide_names': True,  # на этой странице убираем блок
        'menu': menu  # убедитесь, что переменная menu доступна
    }
    return render(request, 'main/model_360.html', context)


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




def pam_render_gallery(request, category):
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
    return render(request, 'main/pam_render_gallery.html', context)





import os
from django.shortcuts import render

def natural_key(filename):
    # Извлекаем имя файла без расширения
    name = os.path.splitext(filename)[0]
    # Разбиваем строку на части, где числа находятся между текстовыми фрагментами
    parts = re.split(r'(\d+)', name)
    # Преобразуем числовые части в int, а текстовые – к нижнему регистру
    return [int(part) if part.isdigit() else part.lower() for part in parts]

def osn_gallery(request, category):
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
        return render(request, 'main/osn_gallery.html', {'title': title, 'gallery': []})

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
            'route_name': category,  # ← вот это добавляем
        })

    context = {
        'menu': menu,  # убедитесь, что переменная menu определена
        'title': title,
        'gallery': gallery,
        'base_folder': base_folder,  # используется при формировании полного пути к файлам
    }

    return render(request, 'main/osn_gallery.html', context)


