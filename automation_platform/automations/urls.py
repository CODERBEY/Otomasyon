from django.urls import path
from . import views

urlpatterns = [
    path('', views.automation_list, name='automation_list'),
    path('guide/', views.automation_guide, name='automation_guide'),
    path('create/', views.automation_create, name='automation_create'),
    path('<int:pk>/', views.automation_detail, name='automation_detail'),
    path('<int:pk>/execute/', views.automation_execute, name='automation_execute'),
    path('<int:pk>/guide/', views.automation_usage_guide, name='automation_usage_guide'),  # YENİ
    path('result/<int:execution_id>/', views.automation_result, name='automation_result'),
    path('execution-result/<int:execution_id>/', views.automation_execution_result, name='automation_execution_result'),  # YENİ
]