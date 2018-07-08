from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Question)
admin.site.register(Person)
admin.site.register(Project)
admin.site.register(Role)
admin.site.register(Category)
admin.site.register(Publication)
