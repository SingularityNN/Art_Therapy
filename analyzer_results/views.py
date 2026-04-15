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

            # get experiment.drawing
            drawing_file = form.cleaned_data['drawing']

            # get experiment.id
            file_name = drawing_file.name
            file_name_shortened = file_name[4:-5]

            if Experiments.objects.filter(id=file_name_shortened).exists():
                messages.error(request, f'Эксперимент с id "{file_name_shortened}" уже существует')
                return render(request, 'analyzer_results/add_experiment.html', {'form': form})

            # get experiment.analyzer_res_json
            image_path = "art/" + file_name
            analyzer_res = analyze_image(image_path)

            experiment = Experiments(
                id = file_name_shortened,
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
