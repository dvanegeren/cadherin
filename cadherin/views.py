from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from .models import *
from django.views import generic

# Create your views here.


class PersonDetailView(generic.DetailView):
    model = Person


class PersonListView(generic.ListView):
    model = Person
    context_object_name = 'latest_person_list'

    def get_queryset(self):
        return Person.objects.order_by('last_name')


def index(request):
    latest_person_list = Person.objects.order_by('last_name')[:5]
    context = {'latest_person_list': latest_person_list}
    return render(request, 'cadherin/index.html', context)


def add_person(request):
    try:
        new_person = Person(last_name=request.POST['last_name'], first_name=request.POST['first_name'], role=Role.objects.get(pk=request.POST['role']))
        new_person.save()
    except (KeyError):
        context = {'latest_roles': Role.objects.all(),
                   'latest_categories': Category.objects.all(),
                   'error_message': "You suck at forms."}
        return render(request, 'cadherin/add_person.html', context)
    else:
        return HttpResponseRedirect(reverse('cadherin:index'))


def add_pub(request):
    try:
        response_keys = request.POST.keys()
        if 'pm_id' in response_keys and request.POST['pm_id']:
            pm_response = request.POST['pm_id']
            new_pub = Publication()
            new_pub.save()
            new_pub.populate_fields_pm(pm_response)
            return HttpResponseRedirect(reverse('cadherin:index'))
        elif 'pmc_id' in response_keys and request.POST['pmc_id']:
            pmc_response = request.POST['pmc_id']
            new_pub = Publication()
            new_pub.save()
            new_pub.populate_fields_pmc(pmc_response)
            return HttpResponseRedirect(reverse('cadherin:index'))
        elif 'doi' in response_keys and request.POST['doi']:
            doi_response = request.POST['doi']
            new_pub = Publication()
            new_pub.save()
            new_pub.populate_fields_doi(doi_response)
            return HttpResponseRedirect(reverse('cadherin:index'))
    except (KeyError, DataRetrievalException):
        new_pub.delete()
        context = {'error_message': "You suck at forms."}
        return render(request, 'cadherin/add_publication.html', context)
    return render(request, 'cadherin/add_publication.html')

