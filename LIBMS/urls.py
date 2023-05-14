from django.urls import path


from . import views



urlpatterns = [
    path("", views.home, name="home"),
    path("adminDashboard/", views.dashboard),
    path("purchaseStock/", views.purchaseStock),
    path("insert/", views.insert),
    path("adminView/", views.adminView, name='adminView'),
    path("delete/",views.delete),
    path("venSearch/",views.venSearch, name='venSearch'),
    path("adminSearch/",views.adminSearch, name='adminSearch'),
    path("racks/",views.racks),
    path("cusLogin/",views.cusLogin),
    path("adminLogin/",views.adminLogin),
    path("venLogin/",views.venLogin),
    path("logout/",views.logout),
    path("cusReg/",views.cusReg),
    path("venReg/",views.venReg),
    path("cusCart/",views.cusCart),
    path("adminCart/",views.adminCart),
    path("addCusCart/",views.addCusCart, name="addCusCart"),
    path("remCusCart/",views.remCusCart, name="remCusCart"),
    path("addAdminCart/",views.addAdminCart, name="addAdminCart"),
    path("remAdminCart/",views.remAdminCart, name="remAdminCart"),
    path("manageAdmins/",views.manageAdmins),
    path("manageAdmins/addAdmin/",views.addAdmin),
    path("manageAdmins/remAdmin/",views.remAdmin),
    path("venHome/",views.venHome, name="venHome"),
    path("addItems/",views.addItems),
    path("remItems/",views.remItems),
    path("listItem/",views.listItem, name="listItem"),
    path("generateReport/",views.generateReport, name="generateReport"),
    path("sendNotifications/",views.sendNotifications),
    path("notifications/",views.notifications)
]


