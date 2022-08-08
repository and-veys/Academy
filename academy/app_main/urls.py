

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
    path("generate/", views.generate),
    path("serialize/", views.serialize),
    path("generate/", views.generate),
    path("loaddata/", views.loaddata),    
    path("bot/", views.bot),
    path("changeinfo/<str:person>/<int:id>", views.changePersonal),
    path("changepassword/<str:person>/<int:id>", views.changePassword)
    
    
    
    
    
    # path('application/<str:person>', views.application),
    # path('administrator', views.administrator, name="administrator"),
    # path('employee/HR/EMP', views.department_hr_empoyee, name="department_hr_empoyee"),
    # path('employee/HR/BOS', views.department_hr_boss, name="department_hr_boss"),
    
    
    
    # path('calendar/', views.calendar),  
    # path('test/', views.test, name="test"),
]
