from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction
from django.forms import fields_for_model

from .models import CitizenProfile, Department


class DepartmentLoginForm(AuthenticationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.select_related("organization").order_by("organization__name", "name"),
        empty_label="Select your department",
    )
    field_order = ("department", "username", "password")

    def clean(self):
        credentials = super().clean()
        department = credentials.get("department")
        officer = getattr(self.get_user(), "officer", None)
        if department is not None and (officer is None or officer.department_id != department.pk):
            raise forms.ValidationError("The account cannot sign in to this department.")
        return credentials


class CitizenRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "given-name"}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "family-name"}))
    mobile_number = forms.RegexField(
        regex=r"\A\+?[0-9]{7,15}\Z",
        max_length=16,
        help_text="Enter 7 to 15 digits. You can include a leading + for the country code.",
        error_messages={"invalid": "Enter a mobile number with 7 to 15 digits and an optional leading +."},
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("first_name", "last_name", "username")

    profile_fields = ("mobile_number", "street_address", "city", "state", "postal_code")
    field_order = ("first_name", "last_name", *profile_fields, "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.update(fields_for_model(CitizenProfile, fields=self.profile_fields[1:]))
        self.order_fields(self.field_order)

    @transaction.atomic
    def register(self):
        user = self.save()
        CitizenProfile.objects.create(
            user=user,
            **{field: self.cleaned_data[field] for field in self.profile_fields},
        )
        return user
