from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .forms import myForm
from django.db import connection
from .helper import searchRec

# Create your views here.

def home(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    columns=[]
    for col in cursor.description:
      columns.append(col[0])

    data=[]
    for row in rows:
      row_dict = {}
      for i in range(len(columns)):
        row_dict[columns[i]] = row[i]
      data.append(row_dict)

    #print(data)
    context = {'data': data}
    return render(request, 'home.html', context)

def insert(request):
  if request.method=='POST':
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO products(productName, category) VALUES(\'{request.POST.get('name')}\', \'{request.POST.get('category')}\');")
    #print(f"Name: {request.POST.get('name')}\nCategory: {request.POST.get('category')}\nInsert successful!")
    cursor.close()
    context={'flag':1}
  else:
    context={'flag':0}
  return render(request, "insert.html", context)

def view(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    columns=[]
    for col in cursor.description:
      columns.append(col[0])

    data=[]
    for row in rows:
      row_dict = {}
      for i in range(len(columns)):
        row_dict[columns[i]] = row[i]
      data.append(row_dict)

    #print(data)
    context = {'data': data}
    return render(request, 'view.html', context)

def delete(request):
  flag=0
  if request.method=="POST":
    print(request.POST)
    cursor = connection.cursor()
    if 'delbtn' in request.POST:
      selected_row_ids = request.POST.getlist('selected_rows')
      for i in selected_row_ids:
        cursor.execute(f"DELETE FROM products WHERE productid = {i}")
      flag=1
    elif 'delallbtn' in request.POST:
      cursor.execute("DELETE FROM products")
      cursor.execute("commit")
      flag=2
    cursor.close()
    
  if request.GET.get('id') or request.GET.get('name') or request.GET.get('category') or request.GET.get('query'):
    context={'data': searchRec(request), 'flag': 1, 'btn': flag}
  else:
      context={'data': [], 'flag': 0, 'btn': flag}
  return render(request, "delete.html", context)

def search(request):
    if request.GET.get('id') or request.GET.get('name') or request.GET.get('category') or request.GET.get('query'):
      context={'data': searchRec(request), 'flag': 1}
    else:
      context={'data': [], 'flag': 0}
  
    return render(request, "search.html", context)