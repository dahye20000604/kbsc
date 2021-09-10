from django.urls import path

from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('device/add/', views.device_add, name='device_add'),
    path('device/', views.device, name='device')
]