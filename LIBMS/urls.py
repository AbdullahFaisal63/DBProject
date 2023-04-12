from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.v1),
    path("login/", views.v2)
]
