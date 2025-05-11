from django.urls import path
from . import views

urlpatterns = [
    path('', views.automation_list, name='automation_list'),
    path('create/', views.automation_create, name='automation_create'),
    path('<int:pk>/', views.automation_detail, name='automation_detail'),
    path('<int:pk>/execute/', views.automation_execute, name='automation_execute'),
]