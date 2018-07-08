from django.db import models

# Create your models here.


class Person(models.Model):
    name = models.CharField(max_length=100)
    phd_advisor = models.ForeignKey('self', on_delete=models.CASCADE, related_name='students', blank=True, null=True)
    postdoc_advisor = models.ForeignKey('self', on_delete=models.CASCADE, related_name='postdoc', blank=True, null=True)
    collaborators = models.ManyToManyField('self', blank=True, null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_text = models.CharField(max_length=300)

    def __str__(self):
        return self.question_text


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=3000)
    people = models.ManyToManyField(Person, blank=True, null=True)

    def __str__(self):
        return self.name
