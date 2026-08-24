from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('languages/', views.language_list, name='language_list'),
    path('languages/<int:pk>/', views.language_detail, name='language_detail'),
    path('languages/<int:pk>/lessons/<int:lesson_order>/', views.lesson_detail, name='lesson_detail'),
    path('languages/<int:pk>/lessons/<int:lesson_order>/complete/', views.lesson_complete, name='lesson_complete'),
    path('run/', views.run_code, name='run_code'),
    path('try-it/', views.try_it, name='try_it'),
    path('hardware/', views.hardware_list, name='hardware_list'),
    path('hardware/<slug:slug>/', views.hardware_detail, name='hardware_detail'),
    path('hardware/<slug:slug>/<int:challenge_pk>/', views.hardware_challenge, name='hardware_challenge'),
    path('hardware/<slug:slug>/<int:challenge_pk>/complete/', views.hardware_complete, name='hardware_complete'),
]
