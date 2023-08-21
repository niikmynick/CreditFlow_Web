from django.urls import path
from .views import get_info, get_creditors_info, show_results, about

urlpatterns = [
    path('', get_info, name='index'),
    path('about', about, name='about'),
    path('creditors_info', get_creditors_info, name='creditors_info'),
    path('results', show_results, name='results'),
]
