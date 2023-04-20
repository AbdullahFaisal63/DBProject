from django.db import connection
from django.http import HttpRequest

def searchRec(request):
    data=[]
    cursor = connection.cursor()
    #print(f"SELECT * FROM products WHERE productname LIKE '%{request.GET.get('name')}%'"))
    if request.GET.get('query'):
      if request.GET.get('query').isdigit():
        cursor.execute(f"SELECT * FROM products WHERE productid = '{request.GET.get('query')}'")
      else:
        cursor.execute(f"SELECT * FROM products WHERE productname LIKE '%{request.GET.get('query')}%' OR category = '{request.GET.get('query')}'")
    else:
      if request.GET.get('id') and request.GET.get('name') and request.GET.get('category'):
        cursor.execute(f"SELECT * FROM products WHERE productid = '{request.GET.get('id')}' AND productname LIKE '%{request.GET.get('name')}%' AND category = '{request.GET.get('category')}'")
      else:
        if request.GET.get('name'):
          if request.GET.get('id'):
            cursor.execute(f"SELECT * FROM products WHERE productname LIKE '%{request.GET.get('name')}%' AND productid = '{request.GET.get('id')}'")
          elif request.GET.get('category'):
            cursor.execute(f"SELECT * FROM products WHERE productname LIKE '%{request.GET.get('name')}%' AND category = '{request.GET.get('category')}'")
          else:
            cursor.execute(f"SELECT * FROM products WHERE productname LIKE '%{request.GET.get('name')}%'")
        elif request.GET.get('id'):
          if request.GET.get('category'):
            cursor.execute(f"SELECT * FROM products WHERE productid = '{request.GET.get('id')}' AND category = '{request.GET.get('category')}'")
          else:
            cursor.execute(f"SELECT * FROM products WHERE productid = '{request.GET.get('id')}'")
        elif request.GET.get('category'):
          cursor.execute(f"SELECT * FROM products WHERE category = '{request.GET.get('category')}'")

    
    rows=cursor.fetchall()
    columns=[]
    for col in cursor.description:
      columns.append(col[0])

    for row in rows:
      row_dict = {}
      for i in range(len(columns)):
        row_dict[columns[i]] = row[i]
      data.append(row_dict)

    #print(data)
    cursor.close()
    return data