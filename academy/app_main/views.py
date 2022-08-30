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



def isAccessSchedule(fun):
    def wrapper(request, **kwargs):
        sch = Groups().getSchedule(kwargs["sch"])        
        if(sch):       
            if(sch.group.id == kwargs["grp"].id and sch.subject.id == kwargs["sbj"].id):
                kwargs["sch"] = sch
                return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper



def isAccessGroup(fun):
    def wrapper(request, **kwargs):
        data = Groups().getGroup(kwargs["grp"], kwargs["sbj"])          
        per = kwargs["id"]
        if(data):       
            if(per.department == data["group"].course.department):
                kwargs["grp"]=data["group"]
                kwargs["sbj"]=data["subject"]
                return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper

def isLeader(fun):
    def wrapper(request, **kwargs):
        kwargs["id"] = per
        if(kwargs["id"].status.index == "leader"):
            return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper
  
  
def isAccessAdministrator(fun): #Доступ только администратору
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
    """Страница календаря"""                        
    info = Calendar().getMonthData(dt)
    return getCalendar(info, request, person, id, "my")
    


def getCalendar(info, request, person, id, ev):       
    if(info):
        temp = Persons().getEvent(id, person, info["range"], ev)
    if((not info) or (not temp)):
        return render(request, "error_access.html") 
    info["events"] = temp
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
@isAccessGroup
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
@isAccessGroup
def get_schedule(request, person, id, grp, sbj):
    info = Groups().createLessons(grp, sbj)
    info["person"] = "{}/{}".format(person, id.id)
    info["edit"] = "/{}/{}/".format(grp.id, sbj.id)
    return render(request, "get_schedule.html", info)

@isAccess
@isLeader
@isAccessGroup
@isAccessSchedule
def edit_schedule(request, person, id, grp, sbj, sch):
    back = "/get_schedule/{}/{}/{}/{}#{}".format(person, id.id, grp.id, sbj.id, sch.id)
    if(request.method.upper() == "POST"):
        data = json.load(request)
        return HttpResponse(Groups().setEditSchedule(data, sch, back));

    info = Groups().createLesson(sch) 
    info["back"] = back
    return render(request, "edit_lesson.html", info) 
    


@isAccessAdministrator
def generate(request):                                  #"generate/"
    """Генерация студентов и преподавателей"""
    res = ""
    res += Generate().generateStudents()
    res += Generate().generateEmployees()
    return HttpResponse(res)

@isAccessAdministrator
def serialize(request):                                 #"serialize/"              
    return HttpResponse(Generate().serialize())

@isAccessAdministrator                                  
def loaddata(request):                                  #loaddata/"
    return HttpResponse(Generate().loaddata())
    
  
    
    