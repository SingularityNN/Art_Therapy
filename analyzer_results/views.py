from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from image_analyzer.analyzer import analyze_image
from .forms import ExperimentForm, NoteForm
from .models import Experiments

def export_to_xlsx(request: HttpRequest) -> HttpResponse:
    queryset = Experiments.objects.all()
    keys = ['ignored_white_pixels',
            'avg_hue',
            'avg_saturation',
            'avg_brightness',
            'red_percent',
            'green_percent',
            'blue_percent']

    wb = Workbook()
    ws = wb.active
    ws.title = "drawings_data"
    headers = ['ID',
            'ignored_white_pixels (%)',
            'avg_hue (0-179)',
            'avg_saturation (0-100)',
            'avg_brightness (0-100)',
            'red_percent (%)',
            'green_percent (%)',
            'blue_percent (%)']
    ws.append(headers)

    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 22
    ws.column_dimensions['E'].width = 22
    ws.column_dimensions['F'].width = 18
    ws.column_dimensions['G'].width = 18
    ws.column_dimensions['H'].width = 18

    header_fill = PatternFill(start_color="D3D3D3",
                              end_color="D3D3D3",
                              fill_type="solid")

    for cell in ws[1]:  # ws[1] — это первая строка
        cell.fill = header_fill


    for obj in queryset:
        row = [obj.id + '_1']
        for key in keys:
            value = obj.analyzer_res_first_json.get(key, '')
            row.append(value)
        ws.append(row)

        row = [obj.id + '_2']
        for key in keys:
            value = obj.analyzer_res_second_json.get(key, '')
            row.append(value)
        ws.append(row)

        columns_format = {
            'B': '0.00',
            'F': '0.00',
            'G': '0.00',
            'H': '0.00',
        }

        for row in range(2, ws.max_row + 1):
            for col_letter, fmt in columns_format.items():
                cell = ws[f"{col_letter}{row}"]
                # Если значение в ячейке - число (int или float), применяем формат
                if isinstance(cell.value, (int, float)):
                    cell.number_format = fmt


    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="export_drawings_data.xlsx"'
    wb.save(response)
    return response

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
