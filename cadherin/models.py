from django.db import models
import requests
import xml.etree.ElementTree as ET

# Create your models here.


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
    first_author = models.CharField(max_length=100, blank=True, null=True)
    last_author = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    journal = models.CharField(max_length=100, blank=True, null=True)
    abstract = models.CharField(max_length=1000, blank=True, null=True)
    pm_id = models.CharField(max_length=50, blank=True, null=True)
    pub_year = models.IntegerField(blank=True, null=True)
    authors = models.ManyToManyField(Person, blank=True, null=True)
    related_to_pubs = models.ManyToManyField('self', blank=True, null=True, through='PubRelation',
        through_fields=('from_pub', 'to_pub'), related_name='related_from_pubs', symmetrical=False)
    notes = models.ManyToManyField(Note, blank=True, null=True)

    def populate_fields_pm(self, pm_id):
        payload = {'db': 'pubmed', 'id': pm_id, 'retmode': 'xml'}
        url_str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        url_data = requests.get(url_str, params=payload)
        root = ET.fromstring(url_data.text)
        data = root.find('PubmedArticle/MedlineCitation/Article')
        first = True
        for author in data.findall('AuthorList/Author'):
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
        self.pub_year = int(data.find('Journal/JournalIssue/PubDate/Year').text)
        self.journal = data.find('Journal/ISOAbbreviation').text
        self.abstract = data.find('Abstract/AbstractText').text
        self.pm_id = root.find('PubmedArticle/MedlineCitation/PMID').text
        self.link = "www.ncbi.nlm.nih.gov/pubmed/" + self.pm_id
        self.save()

    def __str__(self):
        return str(self.first_author) + '...' + str(self.last_author) + '. ' + str(self.journal) + ' (' + str(self.pub_year) + ').'


class PubRelation(models.Model):
    to_pub = models.ForeignKey(Publication, on_delete=models.PROTECT, related_name='in_relations')
    from_pub = models.ForeignKey(Publication, on_delete=models.PROTECT, related_name='out_relations')
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.description
