from django.urls import path
from . import views

app_name = 'screener'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:name>-<int:tf>', views.test_view, name='test_view'),
    path('<str:name>', views.single_currency, name='single_currency')
]