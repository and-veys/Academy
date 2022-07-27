

from django.urls import path        

from . import views                    
    
urlpatterns = [
    path("", views.main, name="main"), 
    path("departments/", views.departments, name="departments"),
    path("courses/", views.courses, name="courses"),
    path("registration/", views.registration, name="registration"),
    path("info/<str:person>/<int:id>", views.infoPersonsShot),
    path("personal/<str:person>/<int:id>", views.infoPersons),
    path("generatePersons/", views.generatePersons, name = "generatePersons"),
    path("bot/", views.bot, name = "bot"),
    path("changeinfo/<str:person>/<int:id>", views.changePersonal),
    path("changepassword/<str:person>/<int:id>", views.changePassword)
    
    
    
    
    
    # path('registration', views.registration, name="registration"),
    # path('application/<str:person>', views.application),
    # path('administrator', views.administrator, name="administrator"),
    # path('employee/HR/EMP', views.department_hr_empoyee, name="department_hr_empoyee"),
    # path('employee/HR/BOS', views.department_hr_boss, name="department_hr_boss"),
    
    
    
    # path('calendar/', views.calendar),  
    # path('test/', views.test, name="test"),
]
