from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .forms import myForm
from django.db import connection
from .helper import searchRec
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch


# Create your views here.


def cus_login_required(view_func):
  def wrapper(request, *args, **kwargs):
      if request.session.get('user_id', None) and request.session.get('user_type', None)=='customer':
          return view_func(request, *args, **kwargs)
      else:
          return redirect('/cusLogin')
  return wrapper


def admin_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_id', None) and request.session.get('user_type', None)=='admin':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/adminLogin')
    return wrapper

def ven_login_required(view_func):
  def wrapper(request, *args, **kwargs):
      if request.session.get('user_id', None) and request.session.get('user_type', None)=='vendor':
          return view_func(request, *args, **kwargs)
      else:
          return redirect('/venLogin')
  return wrapper

def any_login_required(view_func):
  def wrapper(request, *args, **kwargs):
      if request.session.get('user_id', None):
          return view_func(request, *args, **kwargs)
      else:
          return redirect('/cusLogin')
  return wrapper

@admin_login_required
def dashboard(request):
    cursor = connection.cursor()
    cursor.execute("SELECT p.*, p1.quantity FROM products p, admin_products p1 WHERE p.id=p1.pid")
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

    cursor.execute("SELECT * FROM purchase_his")
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
    context['phis'] = data
    cursor.execute("SELECT * FROM sales_his")
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
    context['shis'] = data
    return render(request, 'adminDashboard.html', context)


@admin_login_required
def insert(request):
  cursor = connection.cursor()
  if request.method=='POST':
    cursor.execute(f"INSERT INTO products(name, price, category, description, img) VALUES(\'{request.POST.get('name')}\', {request.POST.get('price')}, \'{request.POST.get('category')}\', \'{request.POST.get('description')}\', \'{request.POST.get('img')}\');")
    #cursor.execute(f"UPDATE racks SET occupied = occupied + 1 WHERE id=\'{request.POST.get('id')}\'")
    #print(f"Name: {request.POST.get('name')}\nCategory: {request.POST.get('category')}\nInsert successful!")
    context={'flag':1}
  else:
    cursor.execute(f"SELECT COUNT(id) FROM racks")
    #print(cursor.fetchall())
    context={'flag':0, 'num_rows':range(cursor.fetchall()[0][0]), 'num_cols':range(12)}
  cursor.close()
  return render(request, "insert.html", context)


@cus_login_required
def home(request):
  cursor=connection.cursor()

  if request.GET.get('sort'):
    if request.GET.get('sort')=='phl':
      cursor.execute("SELECT p.*, p1.price as uprice, p1.quantity FROM products p,admin_products p1 where p.id=p1.pid ORDER BY p.price DESC;")
    else:
      cursor.execute("SELECT p.*, p1.price as uprice, p1.quantity FROM products p,admin_products p1 where p.id=p1.pid ORDER BY p.price ASC;")
    context = {'selected':'All Products'}
  elif request.GET.get('search') and request.GET.get('category'):
    cursor.execute(f"SELECT p.*, vp.price as uprice,vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%' AND category='{request.GET.get('category')}'")
    context = {'selected':request.GET.get('category')}
  elif request.GET.get('search'):
    #search on name in products table
    #print(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('search')}%'")
    cursor.execute(f"SELECT p.*, vp.price as uprice,vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%'")
    context = {'selected':'All Products'}
  elif request.GET.get('query'):
    #print(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('query')}%'")
    cursor.execute(f"SELECT p.*, vp.price as uprice,vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('query')}%'")
    context = {'selected':'All Products'}
  elif request.GET.get('category'):
    #search on name and category on products table
    cursor.execute(f"SELECT p.*, vp.price as uprice,vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id and category='{request.GET.get('category')}'")
    context = {'selected':request.GET.get('category')}
  else:
    cursor=connection.cursor()
    cursor.execute("SELECT p.*, vp.price as uprice,vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id")
    context = {'selected':'All Products'}

  rows = cursor.fetchall()
  print(rows)
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  # print(data)
  context['data'] = data
  return render(request, 'home.html', context)


@admin_login_required
def delete(request):
  flag=0
  if request.method=="POST":
    #print(request.POST)
    cursor = connection.cursor()
    if 'delbtn' in request.POST:
      selected_row_ids = request.POST.getlist('selected_rows')
      # print('yay::',selected_row_ids)
      for i in selected_row_ids:
        # print(f"DELETE FROM admin_products WHERE pid = {i} AND vid={request.session.get('user_id')}")
        cursor.execute(f"DELETE FROM admin_products WHERE pid = {i}")
      flag=1
    elif 'delallbtn' in request.POST:
      # print("yayy")
      cursor.execute(f"DELETE FROM admin_products")
      cursor.execute("commit")
      flag=2
    cursor.close()

  cursor=connection.cursor()
  if request.GET.get('search') and request.GET.get('category'):
    cursor.execute(f"SELECT p.*, vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%' AND category='{request.GET.get('category')}'")
  elif request.GET.get('search'):
    #search on name in products table
    print(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('search')}%'")
    cursor.execute(f"SELECT p.*, vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%'")
  elif request.GET.get('category'):
    #search on name and category on products table
    cursor.execute(f"SELECT p.*, vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id and category='{request.GET.get('category')}'")

  else:
    cursor=connection.cursor()
    cursor.execute("SELECT p.*, vp.quantity FROM products p,admin_products vp WHERE vp.pid=p.id")

  rows = cursor.fetchall()
  print(rows)
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  # print(data)
  context = {'data': data, 'btn':flag, 'flag':1}
  return render(request, "delete.html", context)


@ven_login_required
def venSearch(request):
    cursor=connection.cursor()
    #search in vendor products with join
    cursor.execute()
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
    # print(data)
    context = {'data': data}
    cursor.close()
    return render(request, "venSearch.html", context)


@admin_login_required
def adminSearch(request):
    cursor=connection.cursor()
    #search in admin products with join
    cursor.execute()
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
    # print(data)
    context = {'data': data}
    cursor.close()
    return render(request, "search.html", context)

@admin_login_required
def adminView(request):
  cursor=connection.cursor()
  if request.GET.get('search') and request.GET.get('category'):
    cursor.execute(f"SELECT p.*,vp.quantity, vp.price AS uprice FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%' AND category='{request.GET.get('category')}'")
  elif request.GET.get('search'):
    #search on name in products table
    #print(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('search')}%'")
    cursor.execute(f"SELECT p.*,vp.quantity, vp.price AS uprice FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%'")
  elif request.GET.get('query'):
    #print(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('query')}%'")
    cursor.execute(f"SELECT p.*,vp.quantity, vp.price AS uprice FROM products p,admin_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('query')}%'")
  elif request.GET.get('category'):
    #search on name and category on products table
    cursor.execute(f"SELECT p.*,vp.quantity, vp.price AS uprice FROM products p,admin_products vp WHERE vp.pid=p.id and category='{request.GET.get('category')}'")
  else:
    cursor=connection.cursor()
    cursor.execute("SELECT p.*,vp.quantity, vp.price AS uprice FROM products p,admin_products vp WHERE vp.pid=p.id")

  rows = cursor.fetchall()
  print(rows)
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  # print(data)
  context = {'data': data}
  return render(request, 'adminView.html',context)


@admin_login_required
def racks(request):
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM rackview")
  rows=cursor.fetchall()
  data=[]
  columns=[]
  for col in cursor.description:
    columns.append(col[0])

  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  ta=data
  #print(f"Name: {request.POST.get('name')}\nCategory: {request.POST.get('category')}\nInsert successful!")
  cursor.execute("SELECT * FROM rackview1")
  rows=cursor.fetchall()
  data=[]
  columns=[]
  for col in cursor.description:
    columns.append(col[0])

  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  tb=data
  print(tb)
  cursor.close()
  context={'ta':ta,'tb':tb}
  return render(request, "racks.html", context)


def cusLogin(request):
  if request.method=='POST':
    cursor = connection.cursor()
    # print(request.POST.get('email'))
    # print(request.POST.get('password'))
    # print(f"SELECT * FROM customer WHERE email='{request.POST.get('email')}' AND pass='{request.POST.get('password')}'")
    cursor.execute("SELECT * FROM customer WHERE EMAIL=%s AND PASS=%s;",[request.POST.get('email'),request.POST.get('password')])
    user_data = cursor.fetchall()
    cursor.close()
    if user_data:
      request.session['user_type'] = 'customer' # Store user type in session
      request.session['user_id'] = user_data[0][0] # Store user ID in session
      #print(request.session['user_id'])
      return redirect('/') # Redirect to homepage
    else:
      messages.error(request, 'Invalid username or password')
      return redirect('/cusLogin')
  else:
    return render(request, 'customerLogin.html')


def adminLogin(request):
  if request.method=='POST':
    cursor = connection.cursor()
    # print(request.POST.get('email'))
    # print(request.POST.get('password'))
    # print(f"SELECT * FROM customer WHERE email='{request.POST.get('email')}' AND pass='{request.POST.get('password')}'")
    cursor.execute("SELECT * FROM admin WHERE EMAIL=%s AND PASS=%s;",[request.POST.get('email'),request.POST.get('password')])
    user_data = cursor.fetchall()
    if user_data:
      request.session['user_type'] = 'admin' # Store user type in session
      request.session['user_id'] = user_data[0][2] # Store user ID in session
      p1="""
      begin
      p1;
      end;
      """
      cursor.execute(p1)
      cursor.close()
      return redirect('/adminDashboard') # Redirect to homepage
    else:
      messages.error(request, 'Invalid username or password')
      cursor.close()
      return redirect('/adminLogin')
  else:
    return render(request, 'adminLogin.html')


def venLogin(request):
  if request.method=="POST":
    cursor = connection.cursor()
    # print(request.POST.get('email'))
    # print(request.POST.get('password'))
    # print(f"SELECT * FROM customer WHERE email='{request.POST.get('email')}' AND pass='{request.POST.get('password')}'")
    cursor.execute("SELECT * FROM vendor WHERE EMAIL=%s AND PASS=%s;",[request.POST.get('email'),request.POST.get('password')])
    user_data = cursor.fetchall()
    # print(user_data)
    cursor.close()
    if user_data:
      request.session['user_type'] = 'vendor' # Store user type in session
      request.session['user_id'] = user_data[0][2] # Store user ID in session
      return redirect('/venHome') # Redirect to homepage
    else:
      messages.error(request, 'Invalid username or password')
      return redirect('/venLogin')
  else:
    return render(request, 'vendorLogin.html')


def cusReg(request):
  if request.method=='POST':
    cursor=connection.cursor()
    #print(f"insert into customer(fname, lname, address, email, pass, wallet) values({request.POST.get('firstname')},{request.POST.get('lastname')},{request.POST.get('houseNumber')+request.POST.get('streetNumber')+request.POST.get('city')},{request.POST.get('email')},{request.POST.get('password')},0)")
    #print(request.POST.get('firstName'))
    cursor.execute("insert into customer(fname, lname, address, email, pass, wallet) values(%s,%s,%s,%s,%s,0)", (request.POST.get('firstName'), request.POST.get('lastName'), request.POST.get('houseNumber') + ' ' + request.POST.get('streetNumber') + ' ' + request.POST.get('city'), request.POST.get('email'), request.POST.get('password')))
    #cursor.execute("commit")
    cursor.close()
    return redirect('/cusLogin')
  return render(request, 'registration.html')


def venReg(request):
  if request.method=='POST':
    cursor=connection.cursor()
    #print(f"insert into customer(fname, lname, address, email, pass, wallet) values({request.POST.get('firstname')},{request.POST.get('lastname')},{request.POST.get('houseNumber')+request.POST.get('streetNumber')+request.POST.get('city')},{request.POST.get('email')},{request.POST.get('password')},0)")
    #print(request.POST.get('firstName'))
    cursor.execute("insert into vendor(fname, lname, address, email, pass) values(%s,%s,%s,%s,%s)", (request.POST.get('firstName'), request.POST.get('lastName'), request.POST.get('houseNumber') + ' ' + request.POST.get('streetNumber') + ' ' + request.POST.get('city'), request.POST.get('email'), request.POST.get('password')))
    #cursor.execute("commit")
    cursor.close()
    return redirect('/venLogin')
  return render(request, 'registration.html')

def logout(request):
    del request.session['user_type']
    del request.session['user_id']
    return redirect('/cusLogin')

@cus_login_required
def cusCart(request):
  if request.method=="POST":
    cursor=connection.cursor()
    checkout = """
    begin
    cuscheckout;
    end;
    """
    cursor.execute(checkout)
    cursor.close()
    context={}
  else:
    cursor=connection.cursor()
    cursor.execute(f"SELECT p.id, p.name, c.price, c.quantity, c.cart_id FROM products p, cuscart c WHERE c.product_id=p.id AND c.id={request.session.get('user_id')}")
    rows=cursor.fetchall()
    columns=[]
    # print(rows)
    for col in cursor.description:
      columns.append(col[0])
    columns.append('TOTAL')
    # print(columns)
    data=[]
    for row in rows:
      row_dict = {}
      for i in range(len(columns)-1):
        row_dict[columns[i]] = row[i]
      row_dict['TOTAL']=row_dict['PRICE']*row_dict['QUANTITY']
      data.append(row_dict)
    print(data)
    #cursor.execute(f"SELECT SUM(p.price) FROM products p, cuscart c WHERE p.id=c.product_id AND c.id={request.session.get('user_id')}")
    subtotal=0
    for i in data:
      subtotal+=i['TOTAL']
    tax=subtotal*0.18
    total=subtotal+tax
    context={'data':data, 'subtotal':subtotal, 'tax':tax, 'total':total}
    cursor.close()
  return render(request,'cusCart.html',context)

@cus_login_required
def addCusCart(request):
  if request.method=='POST':
    cursor=connection.cursor()
    #print(f"INSERT INTO cart(customer_id, product_id) VALUES({request.session.get('user_id')},{list(request.POST)[1]})")
    insertcuscart = f"""
    begin
    addcuscart({list(request.POST)[1]},{request.session.get('user_id')},{request.POST[list(request.POST)[1]]});
    end;
    """
    cursor.execute(insertcuscart)
    cursor.close()
    # list(request.POST)[1]
  return redirect('/')

@cus_login_required
def remCusCart(request):
  if request.method=='POST':
    cursor=connection.cursor()
    remcart = f"""
    begin
    remcuscart({list(request.POST)[1]});
    end;
    """
    print(remcart)
    cursor.execute(remcart)
    cursor.close()
    # list(request.POST)[1]
  return redirect('/cusCart')

@admin_login_required
def addAdminCart(request):
  if request.method=='POST':
    cursor=connection.cursor()
    #print(f"INSERT INTO cart(customer_id, product_id) VALUES({request.session.get('user_id')},{list(request.POST)[1]})")
    cursor.execute(f"SELECT vid FROM vendor_products WHERE pid={list(request.POST)[1]}")
    vid=cursor.fetchone()[0]
    addcart = f"""
    begin
    addadmincart({list(request.POST)[1]},{list(request.POST)[2]},{request.POST[list(request.POST)[1]]},{request.session.get('user_id')});
    end;
    """
    #print(list(request.POST)[1])
    #print(f"INSERT INTO admincart(vid, product_id, aid, quantity) VALUES({list(request.POST)[2]},{list(request.POST)[1]},{request.session.get('user_id')},{request.POST[list(request.POST)[1]]})")
    # cursor.execute(f"INSERT INTO admincart(vid, product_id, aid, quantity) VALUES({list(request.POST)[2]},{list(request.POST)[1]},{request.session.get('user_id')},{request.POST[list(request.POST)[1]]})")
    cursor.execute(addcart)
    cursor.close()
    # list(request.POST)[1]
  return redirect('/purchaseStock')

@admin_login_required
def remAdminCart(request):
  if request.method=='POST':
    cursor=connection.cursor()
    remadmin = f"""
    begin
    remadmincart({list(request.POST)[1]});
    end;
    """
    cursor.execute(remadmin)
    cursor.close()
    # list(request.POST)[1]
  return redirect('/adminCart')

@admin_login_required
def purchaseStock(request):
  cursor=connection.cursor()
  data=[]
  columns=[]
  if request.GET.get('category') != 'ALL' and request.GET.get('category'):
    cursor.execute("SELECT p.*, vp.quantity, vp.vid FROM products p, vendor_products vp WHERE p.category=%s AND p.id=vp.pid",[request.GET.get('category')])
    rows = cursor.fetchall()
    for col in cursor.description:
      columns.append(col[0])    
    for row in rows:
      row_dict = {}
      for i in range(len(columns)):
        row_dict[columns[i]] = row[i]
      data.append(row_dict)
    context = {'data': data, 'selected':request.GET.get('category')}
  else:
    cursor.execute("SELECT p.*, vp.quantity, vp.vid FROM products p, vendor_products vp WHERE p.id=vp.pid")
    rows = cursor.fetchall()
    for col in cursor.description:
      columns.append(col[0])
    for row in rows:
      row_dict = {}
      for i in range(len(columns)):
        row_dict[columns[i]] = row[i]
      data.append(row_dict)
      # print(data)
    context = {'data': data, 'selected':'All Products'}

  cursor.close()
  return render(request, 'purchaseStock.html', context)

@admin_login_required
def adminCart(request):
    if request.method=="POST":
      reciept=generateReport(request)
      cursor=connection.cursor()
      checkout = """
      begin
      checkout;
      end;
      """
      cursor.execute(checkout)
      cursor.close()
      return reciept
      context={}
    else:
      cursor=connection.cursor()
      cursor.execute(f"SELECT p.id, p.name, p.price, c.quantity, c.cart_id FROM products p, admincart c WHERE c.product_id=p.id AND c.aid={request.session.get('user_id')}")
      rows=cursor.fetchall()
      columns=[]
      # print(rows)
      for col in cursor.description:
        columns.append(col[0])
      columns.append('TOTAL')
      # print(columns)
      data=[]
      for row in rows:
        row_dict = {}
        for i in range(len(columns)-1):
          row_dict[columns[i]] = row[i]
        row_dict['TOTAL']=row_dict['PRICE']*row_dict['QUANTITY']
        data.append(row_dict)
      print(data)
      #cursor.execute(f"SELECT SUM(p.price) FROM products p, cuscart c WHERE p.id=c.product_id AND c.id={request.session.get('user_id')}")
      subtotal=0
      for i in data:
        subtotal+=i['TOTAL']
      tax=subtotal*0.18
      total=subtotal+tax
      context={'data':data, 'subtotal':subtotal, 'tax':tax, 'total':total}
      cursor.close()
    return render(request,'adminCart.html',context)


@admin_login_required
def manageAdmins(request):
  cursor=connection.cursor()
  cursor.execute("select id, fname||' '||lname AS name, email, pass FROM admin")
  rows=cursor.fetchall()
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  
  context={'data':data}

  return render(request, 'manageAdmins.html', context)

@admin_login_required
def addAdmin(request):
  if request.method=='POST':
    cursor=connection.cursor()
    cursor.execute(f"INSERT INTO admin(fname, lname, email, pass) VALUES(\'{request.POST.get('firstname')}\',\'{request.POST.get('lastname')}\',\'{request.POST.get('email')}\',\'{request.POST.get('password')}\')")
    cursor.close()
  return render(request, 'addAdmin.html')


@admin_login_required
def remAdmin(request):
  cursor=connection.cursor()
  if request.method=='POST':
    selected_row_ids = request.POST.getlist('selected_ids')
    for i in selected_row_ids:
      # print(request.session.get('user_id'))
      # print(i)
      if request.session.get('user_id') != int(i):
        cursor.execute(f"DELETE FROM admin WHERE id = {i}")
    
  cursor.execute("select id, fname||' '||lname AS name, email, pass FROM admin")
  rows=cursor.fetchall()
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  
  context={'data':data}
  cursor.close()
  return render(request, 'remAdmin.html', context)

@ven_login_required
def venHome(request):
  if request.GET.get('query'):
    cursor=connection.cursor()
    cursor.execute(f"SELECT p.*, v.quantity FROM products p, vendor_products v WHERE v.pid=p.id AND v.vid={request.session.get('user_id')} AND p.name LIKE '%{request.GET.get('query')}%'")
  else:
    cursor=connection.cursor()
    cursor.execute(f"SELECT p.*, v.quantity FROM products p, vendor_products v WHERE v.pid=p.id AND v.vid={request.session.get('user_id')}")
  rows=cursor.fetchall()
  #print(cursor.description)
  columns=[]
  for col in cursor.description:
    #print(col)
    columns.append(col[0])
  data=[]
  for row in rows:
    print(row)
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  
  context={'data':data}
  return render(request, 'venHome.html', context)

@ven_login_required
def addItems(request):
  cursor=connection.cursor()
  if request.GET.get('search') and request.GET.get('category'):
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('search')}%' AND category='{request.GET.get('category')}'")
  elif request.GET.get('search'):
    #search on name in products table
    # print(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('search')}%'")
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('search')}%'")
  elif request.GET.get('category'):
    #search on name and category on products table
    cursor.execute(f"SELECT * FROM products WHERE category='{request.GET.get('category')}'")

  else:
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM products")

  rows = cursor.fetchall()
  # print(rows)
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  # print(data)
  context = {'data': data}
  return render(request, 'addItems.html', context)

@ven_login_required
def remItems(request):
  #print(request.POST)
  flag=0
  if request.method=="POST":
    #print(request.POST)
    cursor = connection.cursor()
    if 'delbtn' in request.POST:
      selected_row_ids = request.POST.getlist('selected_rows')
      # print('yay::',selected_row_ids)
      for i in selected_row_ids:
        # print(f"DELETE FROM vendor_products WHERE pid = {i} AND vid={request.session.get('user_id')}")
        cursor.execute(f"DELETE FROM vendor_products WHERE pid = {i} AND vid={request.session.get('user_id')}")
      flag=1
    elif 'delallbtn' in request.POST:
      # print("yayy")
      cursor.execute(f"DELETE FROM vendor_products WHERE vid={request.session.get('user_id')}")
      cursor.execute("commit")
      flag=2
    cursor.close()

  cursor=connection.cursor()
  if request.GET.get('search') and request.GET.get('category'):
    cursor.execute(f"SELECT p.* FROM products p,vendor_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%' AND category='{request.GET.get('category')}'")
  elif request.GET.get('search'):
    #search on name in products table
    print(f"SELECT * FROM products WHERE name LIKE '%{request.GET.get('search')}%'")
    cursor.execute(f"SELECT p.* FROM products p,vendor_products vp WHERE vp.pid=p.id and name LIKE '%{request.GET.get('search')}%'")
  elif request.GET.get('category'):
    #search on name and category on products table
    cursor.execute(f"SELECT p.* FROM products p,vendor_products vp WHERE vp.pid=p.id and category='{request.GET.get('category')}'")

  else:
    cursor=connection.cursor()
    cursor.execute("SELECT p.* FROM products p,vendor_products vp WHERE vp.pid=p.id")

  rows = cursor.fetchall()
  print(rows)
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  # print(data)
  context = {'data': data, 'btn':flag, 'flag':1}
  return render(request, "remItems.html", context)


@ven_login_required
def listItem(request):
  cursor=connection.cursor()
  # print(list(request.POST)[1])  --product ID
  # print(request.POST[list(request.POST)[1]])  --qty

  insertvp = f"""
  begin
  vendorqty({request.session.get('user_id')},{list(request.POST)[1]},{request.POST[list(request.POST)[1]]});
  end; 
  """
  cursor.execute(insertvp)
  #cursor.execute(f"INSERT INTO vendor_products VALUES({list(request.POST)[1]},1,{request.session.get('user_id')})")
  cursor.close()
  return redirect('/addItems')

@admin_login_required
def generateReport(request):
  if request.POST.get('reportType')=='inv':
    filename='inventory_report'
    data=[]
    cursor = connection.cursor()
    cursor.execute("SELECT p.id,p.name,p.category, p1.quantity as qty, p.price as cp, p1.price as rp FROM products p, admin_products p1 WHERE p.id=p1.pid")
    rows = cursor.fetchall()
    columns=[]
    for col in cursor.description:
      columns.append(col[0])
    data.append(columns)
    for row in rows:
      row_dict = []
      for i in range(len(columns)):
        row_dict.append(row[i])
      data.append(row_dict)
    cursor.close()
    colWidths=[0.5*inch, 1.5*inch, 2.5*inch, 0.75*inch, 0.875*inch, 0.875*inch]
  elif request.POST.get('reportType')=='pHis':
    filename='purchase_report'
    data=[]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM purchase_his")
    rows = cursor.fetchall()
    columns=[]
    for col in cursor.description:
      columns.append(col[0])
    data.append(columns)
    for row in rows:
      row_dict = []
      for i in range(len(columns)):
        row_dict.append(row[i])
      data.append(row_dict)
    cursor.close()
    colWidths=[1*inch, 1*inch, 2*inch, 3*inch]
  elif request.POST.get('reportType')=='sHis':
    filename='sales_report'
    data=[]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sales_his")
    rows = cursor.fetchall()
    columns=[]
    for col in cursor.description:
      columns.append(col[0])
    data.append(columns)
    for row in rows:
      row_dict = []
      for i in range(len(columns)):
        row_dict.append(row[i])
      data.append(row_dict)
    cursor.close()
    colWidths=[1.25*inch, 1.5*inch, 1*inch, 1.25*inch, 2*inch]
  elif request.POST.get('adminCheckout'):
    filename='reciept'
    data=[]
    cursor = connection.cursor()
    cursor.execute("SELECT a.product_id AS PID, p.name, a.quantity AS qty, p.price, a.quantity*p.price total FROM admincart a, products p WHERE a.product_id=p.id")
    rows = cursor.fetchall()
    columns=[]
    for col in cursor.description:
      columns.append(col[0])
    data.append(columns)
    for row in rows:
      row_dict = []
      for i in range(len(columns)):
        row_dict.append(row[i])
      data.append(row_dict)
    cursor.close()
    colWidths=[0.75*inch, 2.5*inch, 0.75*inch, 1.25*inch, 1.75*inch]


  # Set up the PDF document
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
  doc = SimpleDocTemplate(response, pagesize=letter)

  # Create the table and style
  table = Table(data, colWidths)
  table.setStyle(TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
      ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 14),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
      ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
      ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
      ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
      ('FONTSIZE', (0, 1), (-1, -1), 12),
      ('GRID', (0, 0), (-1, -1), 1, colors.black),
  ]))

  # Add the table to the document
  elements = []
  elements.append(table)
  doc.build(elements)

  return response

@admin_login_required
def sendNotifications(request):
  if request.method=="POST":
    cursor=connection.cursor()
    print(f"insert into notifications values(\'{request.POST.get('notification')}\',{request.POST.get('email')},{int(request.session.get('user_id'))};")

    cursor.execute(f"SELECT email FROM admin WHERE id={request.session.get('user_id')}")
    aemail=cursor.fetchone()[0]
    cursor.execute(f"insert into notifications(message,cusid,aid) values(\'{request.POST.get('notification')}\',\'{request.POST.get('email')}\',\'{aemail}\');")
    cursor.close()
  return render(request,'sendNotifications.html')

@cus_login_required
def notifications(request):
  if request.method=="POST":
    cursor=connection.cursor()
    cursor.execute(f"DELETE FROM notifications WHERE notno={request.POST.get('notno')}")
    cursor.close()
  cursor=connection.cursor()
  
  cursor.execute(f"SELECT email from customer WHERE id={request.session.get('user_id')}")
  aemail=cursor.fetchone()[0]
  cursor.execute(f"SELECT n.notno, n.message, n.aid, a.fname FROM notifications n, admin a WHERE n.cusid=\'{aemail}\' AND n.aid=a.email")
  
  rows=cursor.fetchall()
  columns=[]
  for col in cursor.description:
    columns.append(col[0])
  data=[]
  for row in rows:
    row_dict = {}
    for i in range(len(columns)):
      row_dict[columns[i]] = row[i]
    data.append(row_dict)
  context={'data':data}
  cursor.close()
  return render(request,'notifications.html',context)