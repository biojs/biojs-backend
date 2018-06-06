from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Component)
admin.site.register(Tag)
admin.site.register(Contributor)
admin.site.register(Contribution)