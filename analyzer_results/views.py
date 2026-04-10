from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
import os
from image_analyzer.analyzer import analyze_image
from django.conf import settings
from .forms import ExperimentForm
from .models import Experiments

def add_experiment(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ExperimentForm(request.POST, request.FILES)
        if form.is_valid():

            # get experiment.drawing
            drawing_file = form.cleaned_data['drawing']

            # get experiment.id
            file_name = drawing_file.name

            if Experiments.objects.filter(id=file_name).exists():
                messages.error(request, f'Эксперимент с id "{file_name}" уже существует')
                return render(request, 'analyzer_results/add_experiment.html', {'form': form})

            # get experiment.analyzer_res_json
            image_path = "art/" + file_name
            analyzer_res = analyze_image(image_path)

            experiment = Experiments(
                id = file_name,
                drawing = drawing_file,
                analyzer_res_json = analyzer_res,
            )

            experiment.save()

            messages.success(request, f'Эксперимент "{experiment.id}" успешно добавлен.')
            return redirect(reverse('analyzer_results:experiments_list'))

        else:
            messages.error(request, 'Исправьте ошибки в форме.')

    else:
        form = ExperimentForm()

    return render(request, 'analyzer_results/add_experiment.html', {'form': form})

def start_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'analyzer_results/start_page.html')

def experiments_list_all(request: HttpRequest) -> HttpResponse:
    context = {
        "experiments": Experiments.objects.all(),
    }
    return render(request, 'analyzer_results/experiments_list.html', context=context)