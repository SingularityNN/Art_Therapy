from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from image_analyzer.analyzer import analyze_image
from .forms import ExperimentForm, NoteForm
from .models import Experiments

def add_experiment(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ExperimentForm(request.POST, request.FILES)
        if form.is_valid():

            # get experiment.drawing_first
            drawing_first_file = form.cleaned_data['drawing_first']

            # get experiment.drawing_second
            drawing_second_file = form.cleaned_data['drawing_second']

            # get experiment.id
            file_name_first = drawing_first_file.name
            file_name_second = drawing_second_file.name
            file_name_shortened = file_name_first[4:-7]

            if Experiments.objects.filter(id=file_name_shortened).exists():
                messages.error(request, f'Эксперимент с id "{file_name_shortened}" уже существует')
                return render(request, 'analyzer_results/add_experiment.html', {'form': form})

            # get experiment.analyzer_res_first_json
            image_path_first = "art/" + file_name_first
            analyzer_res_first = analyze_image(image_path_first)

            # get experiment.analyzer_res_second_json
            image_path_second = "art/" + file_name_second
            analyzer_res_second = analyze_image(image_path_second)

            experiment = Experiments(
                id = file_name_shortened,
                drawing_first = drawing_first_file,
                analyzer_res_first_json = analyzer_res_first,
                drawing_second = drawing_second_file,
                analyzer_res_second_json = analyzer_res_second,
            )

            experiment.save()

            messages.success(request, f'Эксперимент "{experiment.id}" успешно добавлен.')
            return redirect(reverse('analyzer_results:experiments_list'))

        else:
            messages.error(request, 'Исправьте ошибки в форме.')

    else:
        form = ExperimentForm()

    return render(request, 'analyzer_results/add_experiment.html', {'form': form})

def experiment_detail(request: HttpRequest, id) -> HttpResponse:
    exp = get_object_or_404(Experiments, id=id)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            return redirect(reverse('analyzer_results:experiments_list'))

        else:
            messages.error(request, 'Исправьте ошибки в форме.')

    else:
        form = NoteForm(instance=exp)
    return render(request, 'analyzer_results/experiment_detail.html', {'form': form, 'exp': exp,})

def delete_experiment (request: HttpRequest, id) -> HttpResponse:
    obj = Experiments.objects.get(id=id)
    obj.delete()
    return redirect(reverse('analyzer_results:experiments_list'))

def start_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'analyzer_results/start_page.html')

def experiments_list_all(request: HttpRequest) -> HttpResponse:
    context = {
        "experiments": Experiments.objects.all(),
    }
    return render(request, 'analyzer_results/experiments_list.html', context=context)
