from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboards/", views.dashboards, name="dashboards"),
    path("dashboards/<slug:slug>/", views.dashboard_view, name="dashboard_view"),
]