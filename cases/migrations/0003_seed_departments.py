from django.db import migrations


def seed_departments(apps, schema_editor):
    alias = schema_editor.connection.alias
    Organization = apps.get_model("cases", "Organization")
    Department = apps.get_model("cases", "Department")
    organization, _ = Organization.objects.using(alias).get_or_create(name="Civic Desk")
    for name in ("IT Department", "Rent Complaint", "CA Department"):
        departments = Department.objects.using(alias).filter(organization=organization, name=name)
        if not departments.exists():
            Department.objects.using(alias).create(organization=organization, name=name)


class Migration(migrations.Migration):
    dependencies = [("cases", "0002_citizenprofile")]
    operations = [migrations.RunPython(seed_departments, migrations.RunPython.noop)]
