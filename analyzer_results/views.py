from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
import os
from image_analyzer.analyzer import analyze_image
from django.conf import settings




def show_res(request: HttpRequest) -> HttpResponse:
    """
    Обрабатывает POST-запрос с полем image_path, содержащим путь к файлу изображения.
    Возвращает результат анализа.
    """
    image_path = request.session.get('image_path')
    if not image_path:
        messages.error(request, 'Не указан путь к изображению. Пожалуйста, заполните форму.')
        return redirect(reverse('analyzer_results:input_path'))

    result = analyze_image(image_path)
    if result['error']:
        messages.error(request, result['error'])
        return redirect(reverse('analyzer_results:input_path'))

    context = {
        'plot': result['plot_base64'],
    }
    return render(request, 'analyzer_results/results.html', context=context)


def input_path(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        image_path = request.POST.get('image_path', '').strip()
        if not image_path:
            messages.error(request, 'Путь к изображению не указан')
            return render(request, 'analyzer_results/upload_form.html')

        # Проверяем существование файла
        if not os.path.isfile(image_path):
            # пробуем как относительный от BASE_DIR
            abs_path = os.path.join(settings.BASE_DIR, image_path)
            if not os.path.isfile(abs_path):
                messages.error(request, f'Файл не найден: {image_path}')
                return render(request, 'analyzer_results/upload_form.html')
            else:
                image_path = abs_path

        # Сохраняем путь в сессии и редиректим
        request.session['image_path'] = image_path
        return redirect(reverse('analyzer_results:show_res'))

    return render(request, 'analyzer_results/upload_form.html')

def start_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'analyzer_results/start_page.html')