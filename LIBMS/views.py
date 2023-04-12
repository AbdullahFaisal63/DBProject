from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


# Create your views here.

def v1(Request):
    context = {"name":"Abdullah"}
    return render(Request, "new.html", context)

def v2(Request):
    return HttpResponse("hello2")

def v3(Request):
    return HttpResponse("hello3 has")

