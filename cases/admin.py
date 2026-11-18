from django.contrib import admin
from .models import Organization, Department, Officer
admin.site.register([Organization, Department, Officer])
