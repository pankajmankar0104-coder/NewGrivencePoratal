from django import forms
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import CitizenRegistrationForm, DepartmentLoginForm
from .models import Case, Event

class SubmitForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ["department", "subject", "description"]
        labels = {"department": "Organization / department"}

class UpdateForm(forms.Form):
    status = forms.ChoiceField()
    message = forms.CharField(max_length=4000, widget=forms.Textarea)
    version = forms.IntegerField(widget=forms.HiddenInput)

def page(request, title, **data):
    return render(request, "portal.html", {"title": title, **data})

def entrance(request, role):
    form_class = DepartmentLoginForm if role == "Officer" else AuthenticationForm
    form = form_class(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if hasattr(user, "officer") == (role == "Officer"):
            login(request, user)
            return redirect("dashboard")
        form.add_error(None, "Use the login for your account type.")
    return page(request, role + " login", form=form, action="Sign in")

def register(request):
    form = CitizenRegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.register())
        return redirect("dashboard")
    return page(request, "Citizen registration", form=form, action="Create account", registration=True)

@require_POST
def signout(request):
    logout(request)
    return redirect("/")

def accessible(user):
    if hasattr(user, "officer"):
        return Case.objects.filter(department=user.officer.department)
    return Case.objects.filter(citizen=user)

@login_required
def dashboard(request):
    officer = getattr(request.user, "officer", None)
    title = f"{officer.department.name} grievances" if officer else "My grievances"
    return page(request, title, queue=True, citizen=officer is None,
                cases=accessible(request.user).order_by("-opened"))

@login_required
def submit(request):
    if hasattr(request.user, "officer"):
        return HttpResponse(status=403)
    form = SubmitForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            case = form.save(commit=False)
            case.citizen = request.user
            case.save()
            Event.objects.create(case=case, author=request.user, status=case.status, message="Grievance registered.")
        return redirect("detail", tracking=case.tracking)
    return page(request, "Submit a grievance", form=form, action="Submit grievance")

@login_required
def detail(request, tracking):
    case = get_object_or_404(accessible(request.user), tracking=tracking)
    if hasattr(request.user, "officer"):
        transitions = {"Submitted": ["In Progress"], "In Progress": ["Awaiting Citizen", "Resolved"]}
    else:
        transitions = {"Awaiting Citizen": ["In Progress"], "Resolved": ["Closed", "In Progress"]}
    options = transitions.get(case.status, [])
    form = UpdateForm(request.POST if request.method == "POST" else None, initial={"version": case.version})
    form.fields["status"].choices = [(s, s) for s in options]
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        with transaction.atomic():
            updated = accessible(request.user).filter(pk=case.pk, version=data["version"], status=case.status).update(status=data["status"], version=case.version+1)
            if not updated:
                return HttpResponse("This case changed. Reload before submitting.", status=409)
            Event.objects.create(case=case, author=request.user, status=data["status"], message=data["message"])
        return redirect("detail", tracking=tracking)
    return page(request, case.subject, case=case, form=form if options else None, action="Save update")
