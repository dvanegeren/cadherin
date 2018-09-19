from django.urls import path

from . import views

app_name = 'cadherin'

urlpatterns = [
    path('', views.index, name='index'),
    path('add_person/', views.add_person, name='add_person'),
    path('person_list/', views.PersonListView.as_view(), name='person_list'),
    path('add_publication/', views.add_pub, name='add_pub'),
    path('people/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('get_person_nodes/', views.get_person_nodes_csv, name='person_nodes'),
    path('get_person_collabs/', views.get_person_collaborators_csv, name='person_collabs'),
    path('get_person_graph/', views.get_person_json_graph, name='person_graph')
]