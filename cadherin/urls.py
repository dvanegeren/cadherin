from django.urls import path

from . import views

app_name = 'cadherin'

urlpatterns = [
    path('', views.PersonListView.as_view(), name='index'),
    path('add_person/', views.add_person, name='add_person'),
    path('add_publication/', views.add_pub, name='add_pub'),
    path('people/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail')
]