from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
import os
from image_analyzer.analyzer import analyze_image
from django.conf import settings




def show_res(request: HttpRequest) -> HttpResponse:
    """
    Обрабатывает POST-запрос с полем image_path, содержащим путь к файлу изображения.
    Возвращает результат анализа.
    """
    if request.method == 'POST':
        image_rel_path = request.POST.get('image_path', '').strip()
        if not image_rel_path:
            return render(request, 'analyzer_results/upload_form.html', {'error': 'Путь к изображению не указан'})

        # Преобразуем относительный путь в абсолютный относительно корня проекта
        image_abs_path = os.path.join(settings.BASE_DIR, image_rel_path)

        if not os.path.isfile(image_abs_path):
            return render(request, 'analyzer_results/upload_form.html', {'error': f'Файл не найден: {image_abs_path}'})

        result = analyze_image(image_abs_path)
        if result['error']:
            return render(request, 'analyzer_results/analysis_result.html', {'error': result['error']})

        context = {
            'plot': result['plot_base64'],
        }
        return render(request, 'analyzer_results/results.html', context)

    return render(request, 'analyzer_results/upload_form.html')


def input_path(request: HttpRequest) -> HttpResponse:
    return render(request, 'analyzer_results/upload_form.html')