from django.urls import path
from .views import start_page, add_experiment, experiments_list_all, experiment_detail

app_name = 'analyzer_results'

urlpatterns = [
    path('add_experiment/', add_experiment, name='add_experiment'),
    path('', start_page, name='start_page'),
    path('experiments_list/', experiments_list_all, name='experiments_list'),
    path('experiment_detail/<str:id>/', experiment_detail, name='experiment_detail'),
]
