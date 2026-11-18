from django.contrib import admin
from django.urls import path
from cases import views

urlpatterns = [
    path("", lambda request: views.page(request, "Grievance portal", home=True)),
    path("citizen/login/", views.entrance, {"role": "Citizen"}),
    path("officer/login/", views.entrance, {"role": "Officer"}),
    path("register/", views.register), path("logout/", views.signout),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("new/", views.submit), path("case/<uuid:tracking>/", views.detail, name="detail"),
    path("admin/", admin.site.urls),
]
