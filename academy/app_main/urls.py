

from django.urls import path        

from . import views                    
    
urlpatterns = [
    path("bot/", views.bot),
    
    path("", views.main), 
    path("departments/", views.departments),
    path("info/<int:id>", views.info),
    path("info/<str:person>/<int:id>/<int:grp>/<int:std>", views.info),
    path("info/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:std>", views.info),
    path("info/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:sch>/<int:std>", views.info),
    path("info/<str:person>/<int:id>/<int:cwk>", views.info),



    
    path("courses/", views.courses),
    path("registration/", views.registration),
    
    path("personal/<str:person>/<int:id>", views.personalInfo),
    path("changeinfo/<str:person>/<int:id>", views.changePersonal),
    path("changepassword/<str:person>/<int:id>", views.changePassword),
    
    path("work/<str:person>/<int:id>", views.work),    
    path("groups/<str:person>/<int:id>", views.groups),
    
    path("setschedule/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.setSchedule),
    path("getschedule/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.getSchedule),
    path("editschedule/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:sch>", views.editSchedule),    
        
    path("calendar/<str:person>/<int:id>/<int:dt>", views.calendar),
    path("calendardepartment/<str:person>/<int:id>/<int:dt>", views.calendarDepartment),
    path("calendarall/<str:person>/<int:id>/<int:dt>", views.calendarAll),
    
    path("progress/<str:person>/<int:id>", views.progress),
        
    path("marksgroup/<str:person>/<int:id>/<int:grp>", views.marksGroup),    
    path("markssubject/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.marksSubject),
    
    
    path("marksgroupstudent/<str:person>/<int:id>/<int:grp>/<int:std>", views.marksGroupStudent),
    path("markssubjectstudent/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:std>", views.marksSubjectStudent),

    path("marks/<str:person>/<int:id>", views.marks),
    path("setmarks/<str:person>/<int:id>/<int:grp>/<int:sbj>", views.setMarks),
    path("editmarks/<str:person>/<int:id>/<int:grp>/<int:sbj>/<int:sch>", views.editMarks),
    
    path("coworkers/<str:person>/<int:id>", views.coworkers),
    
    
    path("administrator/", views.administrator),
    path("serialize/", views.serialize),
    path("generate/", views.generate),
    path("loaddata/", views.loaddata), 
    path("loginas/<str:person>/<int:abc>", views.loginas)
    

]
