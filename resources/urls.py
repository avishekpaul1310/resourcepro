from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('<int:pk>/', views.resource_detail, name='resource_detail'),
    path('create/', views.resource_create, name='resource_create'),
    path('<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('skills/create/', views.create_skill, name='create_skill'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),
]