from django.urls import path
from .views import show_res, input_path, start_page, add_experiment

app_name = 'analyzer_results'

urlpatterns = [
    path('add_experiment/', add_experiment, name='add_experiment'),
    path('result/', show_res, name='show_res'),
    path('input_path/', input_path, name='input_path'),
    path('', start_page, name='start_page'),

]
