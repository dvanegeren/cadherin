from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('people/<str:person_name>/', views.person_detail, name='person_detail')
]