from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Question)
admin.site.register(Person)
admin.site.register(Project)
