

from django.urls import path        

from . import views                    
    
urlpatterns = [
    path("", views.main, name="main"), 
    path("departments/", views.departments),
    path("courses/", views.courses),
    path("registration/", views.registration),
    path("departments/employees/<int:id>", views.infoEmployeesShot),
    path("personal/<str:person>/<int:id>", views.infoPersons),
    path("work/<str:person>/<int:id>", views.work),
    path("groups/<str:person>/<int:id>", views.groups),
    path("calendar/<str:person>/<int:id>/<int:dt>", views.calendar),
    
    path("set_schedule/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.set_schedule),
    path("get_schedule/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.get_schedule),
    path("edit_schedule/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:sch>", views.edit_schedule),    
    
    path("serialize/", views.serialize),
    path("generate/", views.generate),
    path("loaddata/", views.loaddata),    
    path("bot/", views.bot),
    path("changeinfo/<str:person>/<int:id>", views.changePersonal),
    path("changepassword/<str:person>/<int:id>", views.changePassword)
]
