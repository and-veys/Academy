from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .extra.registration import Registration
from .extra.generate import Generate
from .extra.departments import Departments
from .extra.persons import Persons
from .extra.bot import Bot
import json

def bot(request):
    """Обработчик сообщений от телебота"""
    if("command" not in request.GET):
        content = {"back": ["main", "На главную страницу"]}
        return render(request, "error_access.html", content) 
    resp = Bot().message(request.GET)
    return HttpResponse(resp)

def main(request):   
    """Главная страница (доступна для всех)"""
    return render(request, "start.html")

def departments(request):          
    """Страница структуры отделов (доступна для всех)"""        
    if(request.method.upper() == "POST"):         
        data = json.load(request)
        return HttpResponse("/employees/{}".format(data["id"]))
    content = Departments().createStructure()    
    return render(request, "departments.html", {"data": content})


def infoPersonsShot(request, person, id):
    """Страница с информацией (краткой) о работниках (доступна для всех)"""     #TODO delete true
    return personalInformation(request, person, id, True, ["/departments", "К структуре Академии"])
    

def infoPersons(request, person, id):
    """Страница с информацией (полной) о работниках и студентах"""
    return personalInformation(request, person, id, True, ["/registration", "Приступить к работе"]) #TODO

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
        return render(request, "error_access.html", content)


def changePersonal(request, person, id):
    """Страница изменения личных данных"""
    res = {
        "caption": "Изменение персональных данных",
        "info": True
    }
    return changeInfo(request, person, id, res)

def changePassword(request, person, id):
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




















def courses(request):               #TODO
    """Страница курсов обучения (доступна для всех)"""
    return render(request, "registration.html")    
    
def registration(request):          #TODO  
    """Страница регистрации (доступна для всех)""" 
    if(request.method.upper() == "POST"):
        session = Registration().getSession(request)
        if(session):
            request.session[session["login"]] = session["access"]
            res = HttpResponse(session["href"])
            res.set_cookie("login", session["login"], max_age = session["age"])
        else:
            res = HttpResponse("")        
        return res        
    return render(request, "registration.html")


def generatePersons(request):               #TODO ограничение доступа
    """Генерация студентов и преподавателей"""
    #Только Администратор
    return HttpResponse(Generate().generatePersons())
