from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from .extra.generate import Generate
from .extra.departments import Departments
from .extra.courses import Courses
from .extra.persons import Persons
from .extra.calendar import Calendar
from .extra.groups import Groups
from .extra.bot import Bot
import json
from datetime import date

def isDIR(fun):
    def wrapper(request, **kwargs):
        if(kwargs["id"].department.status.index == "DIR"):            #TODO     
            return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper


def isStudent(fun):
    def wrapper(request, **kwargs):
        gr = kwargs["grp"]
        std = Groups().getStudent(kwargs["std"])       
        if(std):       
            if(gr.id == std.group.id):
                kwargs["std"] = std
                return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper


def isSchedule(fun):
    def wrapper(request, **kwargs):
        sch = Groups().getSchedule(kwargs["sch"])        
        if(sch):       
            if(sch.group.id == kwargs["grp"].id and sch.subject.id == kwargs["sbj"].id):
                kwargs["sch"] = sch
                return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper


def isSubject(fun):
    def wrapper(request, **kwargs):
        per = kwargs["id"]
        data = Groups().getGroupSubject(kwargs["grp"], kwargs["sbj"])  
        if(data):  
            if(kwargs["person"]=="employees"):
                res = (per.department == data["course"].department)
            else:
                res = (per.group.course == data["course"])     
            if(res):
                kwargs["sbj"]=data["subject"]                    
                return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper


def isGroup(fun):
    def wrapper(request, **kwargs):
        per = kwargs["id"]
        data = Groups().getGroup(kwargs["grp"])  
        if(data):              
            if(kwargs["person"]=="employees"):
                res = (per.department == data.course.department)
            else:
                res = (per.group == data)
            if(res):
                kwargs["grp"]=data                
                return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper

def isLeader(fun):
    def wrapper(request, **kwargs):        
        if(kwargs["person"]=="employees" and kwargs["id"].status.index == "leader"):
            return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper
  
  
def isAdministrator(fun): #Доступ только администратору
    def wrapper(request):
        session = Persons().getSession(request)
        if(session):
            if(session["id"] == -1):
                return fun(request)
        return render(request, "error_access.html") 
    return wrapper


def isAccess(fun):          #доступ по id, person или администратору
    def wrapper(request, **kwargs):
        person = kwargs["person"]
        id = kwargs["id"]
        session = Persons().getSession(request)
        if(session):
            if(session["id"] == -1 or (person == session["tp"] and id == session["id"])):
                per = Persons().getPersonFromId(kwargs["id"], kwargs["person"]) 
                if(per):
                    kwargs["id"] = per                
                    return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper


def bot(request):                                   #"bot/"
    """Обработчик сообщений от телебота"""
    if("command" not in request.GET):
        return render(request, "error_access.html")
    resp = Bot().message(request.GET)
    return HttpResponse(resp)

def main(request):                                  #"" 
    """Главная страница"""
    return render(request, "start.html")

def departments(request):                           #"departments/"
    """Страница структуры отделов"""        
    content = Departments().createStructure()    
    return render(request, "departments.html", {"data": content, "path": "/departments/employees/"})

def infoEmployeesShot(request, id):           #"departments/employees/<int:id>"
    """Страница с информацией (краткой) о работниках"""
    return personalInformation(request, "employees", id, False, ["/departments", "К структуре Академии"])



    
@isAccess
def infoPersons(request, person, id):          #"personal/<str:person>/<int:id>"
    """Страница с информацией (полной) о работниках и студентах"""
    return  personalInformation(request, person, id, True, ["/work/{}/{}".format(person, id.id), "Приступить к работе"]) #TODO


def personalInformation(request, person, id, full, back):  
    if(request.method.upper() == "POST"): 
        data = json.load(request)
        return HttpResponse(Persons().loadPhoto(data, id, person)) 
    content = Persons().createStructure(id, person)     
    content["back"] = back    
    content["full"] = full 
    if(content["OK"]):
        return render(request, "info_persons.html", content)
    else:
        return render(request, "error_access.html")

@isAccess
def changePersonal(request, person, id):            #"changeinfo/<str:person>/<int:id>"
    """Страница изменения личных данных"""
    res = {
        "caption": "Изменение персональных данных",
        "info": True
    }
    return changeInfo(request, person, id, res)

@isAccess
def changePassword(request, person, id):            #"changepassword/<str:person>/<int:id>"
    """Страница изменения пароля"""
    res = {
        "caption": "Изменение идентификации",
        "password": True
    }
    return changeInfo(request, person, id, res)

def changeInfo (request, person, id, add):          
    if(request.method.upper() == "POST"):
        data = json.load(request)
        return HttpResponse(Persons().loadInfo(data, id, person))
    content = Persons().createStructure(id, person) | add
    content["back"] =  ["/personal/{}/{}".format(person, id.id), "Назад"]       
    return render(request, "change_info.html", content)


def registration(request):                          #"registration/" 
    """Страница регистрации (доступна для всех)"""
    if(request.method.upper() == "POST"):
        data = json.load(request)        
        data = Persons().getRegistration(data)
        res = HttpResponse(data["path"])
        if(data["OK"]):
            request.session[data["login"]] = data["session"]
            res.set_cookie("login", data["login"], max_age = data["age"])  
        return res  
    return render(request, "registration.html", {"login": bool(Persons().getSession(request))})

def courses(request):                               #"courses/"
    """Страница курсов обучения (доступна для всех)"""    
    content = Courses().createStructure()      
    return render(request, "courses.html", {"data": content, "path": ""})

@isAccess
def work(request, person, id):                      #TODO           #"work/"
    """Рабочая страница работников и студентов"""
    info = Persons().getWork(id, person)   
    info["today"] = date.today().strftime("%Y%m")
    return render(request, info["html"], info)

@isAccess
def calendar(request, person, id, dt):            #TODO           #"calendar/"
    """Страница личного календаря"""                      
    return getCalendar(request, person, id, dt, "my")

@isAccess
@isLeader
def calendar_department(request, person, id, dt):            #TODO           #"calendar_department/"
    """Страница календаря отдела"""                      
    return getCalendar(request, person, id, dt, "dep")   


@isAccess
@isDIR
def calendar_all(request, person, id, dt):            #TODO           #"calendar_all/"
    """Страница календаря всех"""                      
    return getCalendar(request, person, id, dt, "all")   

def getCalendar(request, person, id, dt, ev):     
    info = Calendar().getMonthData(dt)
    if(not info):
        return render(request, "error_access.html") 
    info["events"] = Persons().getEvent(id, person, info["range"], ev)
    info["back"] = "/work/{}/{}".format(person, id.id)
    return render(request, "calendar.html", Calendar().getContent(info))
    






@isAccess
@isLeader
def groups(request, person, id):
    info = Groups().createStructure(id)
    if(not info):    
        return render(request, "error_access.html")           
    return render(request, "groups.html", {"data": info, "person": "{}/{}".format(person, id.id)})

@isAccess
@isLeader
@isGroup
@isSubject
def set_schedule(request, person, id, grp, sbj):
    if(request.method.upper() == "POST"):
        data = json.load(request)
        return HttpResponse(Groups().setSchedule(data, grp, sbj, "/groups/{}/{}".format(person, id.id)));
    info = Groups().createSchedule(grp, sbj)
    if(not info):    
        return render(request, "error_access.html") 
    info["person"] = "{}/{}".format(person, id.id)
    return render(request, "set_schedule.html", info)

@isAccess
@isLeader
@isGroup
@isSubject
def get_schedule(request, person, id, grp, sbj):
    info = Groups().createLessons(grp, sbj)
    if(not info):    
        return render(request, "error_access.html") 
    info["person"] = "{}/{}".format(person, id.id)
    info["edit"] = "/{}/{}/".format(grp.id, sbj.id)
    return render(request, "get_schedule.html", info)

@isAccess
@isLeader
@isGroup
@isSubject
@isSchedule
def edit_schedule(request, person, id, grp, sbj, sch):
    back = "/get_schedule/{}/{}/{}/{}#{}".format(person, id.id, grp.id, sbj.id, sch.id)
    if(request.method.upper() == "POST"):
        data = json.load(request)
        return HttpResponse(Groups().setEditSchedule(data, sch, back));
    
    info = Groups().createLesson(sch) 
    info["back"] = back
    return render(request, "edit_lesson.html", info) 

    
@isAccess
@isLeader
def progress(request, person, id):                  
    info = Groups().createStructure(id)
    if(not info):    
        return render(request, "error_access.html")           
    return render(request, "progress_groups.html", {"data": info, "person": "{}/{}".format(person, id.id)}) 



@isAccess   
@isLeader
@isGroup                                        
def marks_group(request, person, id, grp):
    info = Groups().getMarksGroup(grp)    
    info["person"] = "/marks_group_student/{}/{}/{}/".format(person, id.id, grp.id)
    info["back"] = "/progress/{}/{}".format(person, id.id)
    return render(request, "get_marks.html", info)   

@isAccess   
@isLeader
@isGroup
@isStudent
def marks_group_student(request, person, id, grp, std):                 #TODO
    info = Groups().getMarksStudent(std)
    info["back"] = "/marks_group/{}/{}/{}".format(person, id.id, grp.id)
    info["person"] = "/info_student/{}/{}/{}/{}".format(person, id.id, grp.id, std.id)
    return render(request, "get_student_marks.html", info)  


@isAccess   
@isLeader
@isGroup
@isStudent
def info_student(request, person, id, grp, std):
    back = "/marks_group_student/{}/{}/{}/{}".format(person, id.id, grp.id, std.id)
    return personalInformation(request, "students", std.id, False, [back, "Назад"])
        


@isAccess
@isLeader
@isGroup
@isSubject
def marks_subject(request, person, id, grp, sbj):   #TODO
    info = Groups().getMarksGroup(grp, sbj)
    info["person"] = "/marks_subject_student/{}/{}/{}/{}/".format(person, id.id, grp.id, sbj.id)
    info["back"] = "/progress/{}/{}".format(person, id.id)
    return render(request, "get_marks.html", info)  

@isAccess   
@isLeader
@isGroup
@isSubject
@isStudent
def marks_subject_student(request, person, id, grp, sbj, std):                 #TODO
    info = Groups().getMarksStudent(std, sbj)
    info["back"] = "/marks_subject/{}/{}/{}/{}".format(person, id.id, grp.id, sbj.id)
    info["person"] = "/info_student/{}/{}/{}/{}/{}".format(person, id.id, grp.id, sbj.id, std.id)
    return render(request, "get_student_marks.html", info)  

@isAccess   
@isLeader
@isGroup
@isSubject
@isStudent
def info_student2(request, person, id, grp, sbj, std):
    back = "/marks_subject_student/{}/{}/{}/{}/{}".format(person, id.id, grp.id, sbj.id, std.id)
    return personalInformation(request, "students", std.id, False, [back, "Назад"])



def marks(request, person, id):
    return render(request, "error_access.html") 





@isAdministrator
def generate(request):                                  #"generate/"
    """Генерация студентов и преподавателей"""
    res = ""
    res += Generate().generateStudents()
    res += Generate().generateEmployees()
    res += Generate().generateMarks()
    return HttpResponse(res)

@isAdministrator
def serialize(request):                                 #"serialize/"              
    return HttpResponse(Generate().serialize())

@isAdministrator                                  
def loaddata(request):                                  #loaddata/"
    return HttpResponse(Generate().loaddata())
    



  
    
    