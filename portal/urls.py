from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('applications/create/', views.create_application_view, name='create_application'),
    path('applications/<int:pk>/delete/', views.delete_application_view, name='delete_application'),

    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/applications/<int:pk>/in-progress/', views.set_status_in_progress_view, name='set_status_in_progress'),
    path('admin-panel/applications/<int:pk>/completed/', views.set_status_completed_view, name='set_status_completed'),
    path('admin-panel/categories/add/', views.add_category_view, name='add_category'),
    path('admin-panel/categories/<int:pk>/delete/', views.delete_category_view, name='delete_category'),
]