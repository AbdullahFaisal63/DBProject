from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("insert/", views.insert),
    path("view/", views.view),
    path("delete/",views.delete),
    path("search/",views.search, name='search')
]
