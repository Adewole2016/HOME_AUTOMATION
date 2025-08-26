
from django.contrib import admin
from django.urls import path
from automation import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('api/device/<str:device_id>/desired/', views.api_desired_state, name='api_desired_state'),
    path('api/device/<str:device_id>/report/', views.api_report_state, name='api_report_state'),
    path('device/<str:device_id>/toggle/<int:channel>/', views.toggle_channel, name='toggle_channel'),
    path('device/<str:device_id>/all/<str:action>/', views.all_channels, name='all_channels'),
]
