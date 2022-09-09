

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
    path("calendar_department/<str:person>/<int:id>/<int:dt>", views.calendar_department),
    path("calendar_all/<str:person>/<int:id>/<int:dt>", views.calendar_all),
    
    path("set_schedule/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.set_schedule),
    path("get_schedule/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.get_schedule),
    path("edit_schedule/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:sch>", views.edit_schedule),    
    
    path("progress/<str:person>/<int:id>", views.progress),

    path("marks_group/<str:person>/<int:id>/<int:grp>", views.marks_group),
    path("marks_group_student/<str:person>/<int:id>/<int:grp>/<int:std>", views.marks_group_student),
    path("info_student/<str:person>/<int:id>/<int:grp>/<int:std>", views.info_student),
      
    path("marks_subject/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.marks_subject),
    path("marks_subject_student/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:std>", views.marks_subject_student),
    path("info_student/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:std>", views.info_student2),

    path("marks/<str:person>/<int:id>", views.marks),
    
    path("serialize/", views.serialize),
    path("generate/", views.generate),
    path("loaddata/", views.loaddata),    
    path("bot/", views.bot),
    path("changeinfo/<str:person>/<int:id>", views.changePersonal),
    path("changepassword/<str:person>/<int:id>", views.changePassword)
]
