import uuid
from django.contrib.auth.models import User
from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=160, unique=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    name = models.CharField(max_length=160)

    def __str__(self):
        return f"{self.organization} / {self.name}"

class Officer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

class CitizenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="citizen_profile")
    mobile_number = models.CharField(max_length=16)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField("state or region", max_length=100)
    postal_code = models.CharField(max_length=20)

class Case(models.Model):
    tracking = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    citizen = models.ForeignKey(User, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    subject = models.CharField(max_length=180)
    description = models.TextField()
    status = models.CharField(max_length=30, default="Submitted")
    opened = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=0)

class Event(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="events")
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(max_length=30)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
