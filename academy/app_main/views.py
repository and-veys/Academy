from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .extra.registration import Registration
from .extra.generate import Generate
from .extra.departments import Departments
from .extra.courses import Courses
from .extra.persons import Persons
from .extra.bot import Bot
import json


def isAccessAdministrator(fun):
    def wrapper(request):
        session = Persons().getSession(request)
        if(session):
            if(session["id"] == -1):
                return fun(request)
            return render(request, "error_access.html") 
    return wrapper


def isAccess(fun):          #доступ по id, person или администратору
    def wrapper(request, person, id):
        session = Persons().getSession(request)
        if(session):
            if(session["id"] == -1 or (person == session["tp"] and id == session["id"])):
                return fun(request, person, id)
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
    print("*"*88)
    print(Persons().getSession(request))
    """Страница с информацией (полной) о работниках и студентах"""
    return  personalInformation(request, person, id, True, ["/work/{}/{}".format(person, id), "Приступить к работе"]) #TODO


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
    content["back"] =  ["/personal/{}/{}".format(person, id), "Назад"]       
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

def courses(request):                           #"courses/"
    """Страница курсов обучения (доступна для всех)"""    
    content = Courses().createStructure()      
    return render(request, "courses.html", {"data": content, "path": ""})

@isAccess
def work(request, person, id):
    info = Persons().getWork(id, person)
    return render(request, info["html"], info)


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
    
    
    
    