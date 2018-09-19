from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.urls import reverse
from .models import *
from django.views import generic
import csv

# Create your views here.


class PersonDetailView(generic.DetailView):
    model = Person


class PersonListView(generic.ListView):
    model = Person
    context_object_name = 'latest_person_list'

    def get_queryset(self):
        return Person.objects.order_by('last_name')


def index(request):
    return render(request, 'cadherin/index.html')


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


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def get_person_nodes_csv(request):
    rows = [["name", "phd_advisor", "postdoc_advisor", "role", "id"]]
    rows.extend([person.first_name + " " + person.last_name, person.phd_advisor_id,
                 person.postdoc_advisor_id, person.role, person.id]
                for person in Person.objects.all())
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="people.csv"'
    return response


def get_person_collaborators_csv(request):
    rows = [["source", "target"]]
    for person in Person.objects.all():
        rows.extend([person.id, collab.id] for collab in person.collaborators.all())
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="collaborators.csv"'
    return response


def get_person_json_graph(request):
    nodes = []
    edges = []
    for person in Person.objects.all():
        nodes.append({"name": person.first_name + " " + person.last_name,
                            "phd_advisor": person.phd_advisor_id,
                            "postdoc_advisor": person.postdoc_advisor_id,
                            "role": person.role.name, "id": person.id})
        for collab in person.collaborators.all():
            edges.append({"source": person.id, "target": collab.id})
    return JsonResponse({"nodes": nodes, "links": edges})

