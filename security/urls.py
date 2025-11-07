from django.urls import path
from . import views

urlpatterns = [
    path('', views.fnct_security, name="url_security"),
    path('sobre/', views.fnct_scrty_sobre, name="url_scrty_sobre"),
    path('acessos/', views.fnct_scrty_acessos, name="url_scrty_acessos"),
    path('grafico_dados/', views.grafico_dados, name='grafico_dados'),
]
