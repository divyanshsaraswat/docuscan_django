from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/txt/', views.download_txt, name='download_txt'),
    path('download/pdf/', views.download_pdf, name='download_pdf'),
]
