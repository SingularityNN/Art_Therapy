from django.urls import path
from .views import show_res, input_path

app_name = 'analyzer_results'

urlpatterns = [
    path('result/', show_res, name='show_res'),
    path('input_path/', input_path, name='input_path'),
]
