from django.db import models
from datetime import date
import requests, calendar
import xml.etree.ElementTree as ET

# Create your models here.


class DataRetrievalException(Exception):
    pass


class Note(models.Model):
    note_text = models.CharField(max_length=2000)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Affiliation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phd_advisor = models.ForeignKey('self', on_delete=models.PROTECT, related_name='students', blank=True, null=True)
    postdoc_advisor = models.ForeignKey('self', on_delete=models.PROTECT, related_name='postdocs', blank=True, null=True)
    collaborators = models.ManyToManyField('self', blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    affiliations = models.ManyToManyField(Affiliation, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=True, null=True)
    notes = models.ManyToManyField(Note, blank=True, null=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Question(models.Model):
    question_text = models.CharField(max_length=300)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    notes = models.ManyToManyField(Note, blank=True, null=True)

    def __str__(self):
        return self.question_text


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=3000)
    people = models.ManyToManyField(Person, blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    related_to_projects = models.ManyToManyField('self', blank=True, null=True, through='ProjectRelation',
        through_fields=('from_project', 'to_project'), related_name='related_from_projects', symmetrical=False)
    notes = models.ManyToManyField(Note, blank=True, null=True)

    def __str__(self):
        return self.name


class ProjectRelation(models.Model):
    to_project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='in_relations')
    from_project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='out_relations')
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.description


def look_up_person(first_initial, last_name):
    try:
        return Person.objects.get(last_name=last_name, first_name__startswith=first_initial)
    except Person.MultipleObjectsReturned:
        return Person.objects.filter(last_name=last_name, first_name__startswith=first_initial)[0]


class Publication(models.Model):
    num_authors = models.IntegerField(blank=True, null=True)
    first_author = models.CharField(max_length=100, blank=True, null=True)
    last_author = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    journal = models.CharField(max_length=100, blank=True, null=True)
    abstract = models.CharField(max_length=1000, blank=True, null=True)
    pm_id = models.CharField(max_length=50, blank=True, null=True)
    pub_date = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Person, blank=True, null=True)
    related_to_pubs = models.ManyToManyField('self', blank=True, null=True, through='PubRelation',
        through_fields=('from_pub', 'to_pub'), related_name='related_from_pubs', symmetrical=False)
    notes = models.ManyToManyField(Note, blank=True, null=True)

    def populate_fields_pm(self, pm_id):
        pm_id = pm_id.strip()
        payload = {'db': 'pubmed', 'id': pm_id, 'retmode': 'xml'}
        url_str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        url_data = requests.get(url_str, params=payload)
        if url_data.status_code == 404:
            raise DataRetrievalException
        root = ET.fromstring(url_data.text)
        data = root.find('PubmedArticle/MedlineCitation/Article')
        if not data:
            raise DataRetrievalException
        first = True
        author_list = data.findall('AuthorList/Author')
        self.num_authors = len(author_list)
        for author in author_list:
            last_name = author.find('LastName').text
            first_init = author.find('ForeName').text[:1]
            if first:
                self.first_author = last_name + ', ' + first_init
                first = False
            try:
                new_author = look_up_person(first_init, last_name)
                self.authors.add(new_author)
            except Person.DoesNotExist:
                continue
        self.last_author = last_name + ', ' + first_init
        self.title = data.find('ArticleTitle').text

        monthstr_to_int = {v: k for k, v in enumerate(calendar.month_abbr)}
        pub_year = int(data.find('Journal/JournalIssue/PubDate/Year').text)
        pub_month = monthstr_to_int[data.find('Journal/JournalIssue/PubDate/Month').text]
        pub_day = int(data.find('Journal/JournalIssue/PubDate/Day').text)

        self.pub_date = date(pub_year, pub_month, pub_day)
        self.journal = data.find('Journal/ISOAbbreviation').text
        self.abstract = data.find('Abstract/AbstractText').text
        self.pm_id = root.find('PubmedArticle/MedlineCitation/PMID').text
        self.link = "http://www.ncbi.nlm.nih.gov/pubmed/" + self.pm_id
        self.save()

    def populate_fields_pmc(self, pmc_id):
        pmc_id = pmc_id.strip()
        payload = {'format': 'json', 'ids': pmc_id}
        url_str = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        url_data = requests.get(url_str, params=payload)
        url_data = url_data.json()
        self.pm_id = url_data['records'][0]['pmid']
        self.populate_fields_pm(self.pm_id)
        self.link = "https://www.ncbi.nlm.nih.gov/pmc/articles/" + url_data['records'][0]['pmcid']
        self.save()

    def populate_fields_doi(self, doi):
        doi = doi.strip()
        if len(doi) > 4 and doi[:4] == "doi:":
            doi = doi[4:]
        payload = {'format': 'json', 'ids': doi}
        url_str = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        url_data = requests.get(url_str, params=payload)
        url_data = url_data.json()
        if not url_data['records'][0]['status'] == "error":
            self.pm_id = url_data['records'][0]['pmid']
            self.populate_fields_pm(self.pm_id)
        else:
            url_str = "https://api.crossref.org/works/"
            url_data = requests.get(url_str+doi).json()
            if not url_data['status'] == 'ok':
                raise DataRetrievalException
            url_data = url_data['message']
            self.title = url_data['title'][0]
            self.link = url_data['URL']
            try:
                date_pub = url_data['published-online']
            except KeyError:
                date_pub = url_data['published-print']
            date_pub = date_pub['date-parts'][0]
            self.pub_date = date(date_pub[0], date_pub[1], date_pub[2])
            self.journal = url_data['container-title'][0]
            first = True
            author_list = url_data['author']
            self.num_authors = len(author_list)
            for author in author_list:
                last_name = author['family']
                first_init = author['given'][:1]
                if first:
                    self.first_author = last_name + ', ' + first_init
                    first = False
                try:
                    new_author = look_up_person(first_init, last_name)
                    self.authors.add(new_author)
                except Person.DoesNotExist:
                    continue
            self.last_author = last_name + ', ' + first_init
        self.save()

    def __str__(self):
        if not self.num_authors:
            return 'Empty publication'
        elif self.num_authors == 1:
            return '{}. {} ({}).'.format(str(self.first_author), str(self.journal), str(self.pub_date.year))
        elif self.num_authors == 2:
            return '{} and {}. {} ({}).'.format(str(self.first_author), str(self.last_author), str(self.journal),
                                               str(self.pub_date.year))
        return '{},...{}. {} ({}).'.format(str(self.first_author), str(self.last_author), str(self.journal), str(self.pub_date.year))


class PubRelation(models.Model):
    to_pub = models.ForeignKey(Publication, on_delete=models.PROTECT, related_name='in_relations')
    from_pub = models.ForeignKey(Publication, on_delete=models.PROTECT, related_name='out_relations')
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.description
