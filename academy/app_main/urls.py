

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
    path("calendar/<str:person>/<int:id>/<int:dt>", views.calendar),
    path("serialize/", views.serialize),
    path("generate/", views.generate),
    path("loaddata/", views.loaddata),    
    path("bot/", views.bot),
    path("changeinfo/<str:person>/<int:id>", views.changePersonal),
    path("changepassword/<str:person>/<int:id>", views.changePassword)
]
