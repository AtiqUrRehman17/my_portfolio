from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('contact/', views.contact, name='contact'),
    path('resume/', views.resume, name='resume'),
]
