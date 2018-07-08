from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import *

# Create your views here.


def index(request):
    latest_person_list = Person.objects.order_by('name')[:5]
    context = {'latest_person_list': latest_person_list}
    return render(request, 'cadherin/index.html', context)


def person_detail(request, person_name):
    try:
        person = Person.objects.get(name=person_name)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")
    return render(request, 'cadherin/person_detail.html', {'person': person})
