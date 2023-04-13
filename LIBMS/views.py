from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


# Create your views here.

def v1(Request):
    context = {"name":"Abdullah"}
    print('hello how are you')
    if Request.method=='POST':
      print('hello how are you mus1')
      fname = Request.POST.get("fname")
      lname = Request.POST.get("lname")
      print(fname,lname)
      return HttpResponse('data received')
    else:
        print('ui')
        return render(Request, "new.html")

def v2(Request):
    return HttpResponse("hello2")

def v3(Request):
    return HttpResponse("hello3 has")

