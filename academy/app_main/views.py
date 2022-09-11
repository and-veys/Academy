from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .extra.extra import Extra
from .extra.generate import Generate
from .extra.departments import Departments
from .extra.courses import Courses
from .extra.persons import Persons
from .extra.calendar import Calendar
from .extra.groups import Groups
from .extra.subjects import Subjects
from .extra.students import Students
from .extra.schedule import Schedule

from .extra.bot import Bot
import json
from datetime import date

def convertData(fun):
    """Конвертирование и проверка параметров"""
    def wrapper(request, **kwargs):
        if("person" in kwargs):
            arr = {"id": Persons(), "grp": Groups(), "sbj": Subjects(), "std": Students(), "sch": Schedule()}
        else:
            arr = {}
        res = True
        for el in arr:
            if(el in kwargs):   
                temp = arr[el].getData(kwargs[el], kwargs["person"])
                if(temp):
                    kwargs[el] = temp
                else:
                    res = False
                    break
        if(res):
            for el in kwargs:
                if((el in arr) and (not arr[el].control(kwargs))):
                    res = False          
                    break
        if(res):   
            return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper
    
def isAccess(fun):
    """Доступ по id, person или администратору"""
    def wrapper(request, **kwargs):
        if(len(kwargs) == 1):
            return fun(request, **kwargs)
        session = Persons().getSession(request)
        if(session):
            if(session["id"] == -1 or (kwargs["person"] == session["tp"] and kwargs["id"].id == session["id"])):
                return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper

def isAdministrator(fun):
    """Доступ только администратору"""
    def wrapper(request):
        session = Persons().getSession(request)
        if(session):
            if(session["id"] == -1):
                return fun(request)
        return render(request, "error_access.html") 
    return wrapper

def isEmployee(fun):
    """Доступ только работникам"""
    def wrapper(request, **kwargs):
        if(kwargs["person"] == "employees"):
            return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper


def isLeader(fun):
    """Доступ только начальникам"""
    def wrapper(request, **kwargs):
        if(kwargs["id"].status.index == "leader"):
            return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper

def isDIR(fun):
    def wrapper(request, **kwargs):
        if(kwargs["id"].department.status.index == "DIR"):            #TODO     
            return fun(request, **kwargs)
        return render(request, "error_access.html") 
    return wrapper

def bot(request):                                   
    """Обработчик сообщений от телебота"""
    if("command" not in request.GET):
        return render(request, "error_access.html")
    resp = Bot().message(request.GET)
    return HttpResponse(resp)

def main(request):                                  
    """Главная страница"""
    return render(request, "start.html")

def departments(request):                           
    """Страница структуры отделов"""        
    content = Departments().createStructure()    
    return render(request, "departments.html", {"data": content})

def courses(request):                             
    """Страница курсов обучения"""    
    content = Courses().createStructure()      
    return render(request, "courses.html", {"data": content})


@convertData
@isAccess
def info(request, **kwargs):         
    """Страница с краткой информацией о работниках/студентах"""
    if("person" not in kwargs):
        back = ["/departments", "К структуре Академии"]
        per = "employees"
        id = kwargs["id"]
    elif("grp" in kwargs and "std" in kwargs):
        per = "students"
        id = kwargs["std"]
        temp = map(lambda s: (s if (type(s) == type("1")) else s.id), kwargs.values())
        if("sbj" in kwargs):
            back = [Extra().getPath("markssubjectstudent", *temp), "Назад"]
        else:
            back = [Extra().getPath("marksgroupstudent", *temp), "Назад"]
    else:
        return render(request, "error_access.html")
    return personalInformation(request, per, id, False, back)

@convertData
@isAccess
def personalInfo(request, person, id):          
    """Страница с информацией (полной) о работниках и студентах"""
    return  personalInformation(request, person, id, True, [Extra().getPath("work", person, id.id), "Приступить к работе"]) 

def personalInformation(request, person, id, full, back):  
    """Функция вывода персональной информации"""
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


def registration(request):                         
    """Страница регистрации"""
    if(request.method.upper() == "POST"):
        data = json.load(request)        
        data = Persons().getRegistration(data)
        res = HttpResponse(data["path"])
        if(data["OK"]):
            request.session[data["login"]] = data["session"]
            res.set_cookie("login", data["login"], max_age = data["age"])  
        return res  
    return render(request, "registration.html", {"login": bool(Persons().getSession(request))})


@convertData
@isAccess
def changePersonal(request, person, id):            #"changeinfo/<str:person>/<int:id>"
    """Страница изменения личных данных"""
    res = {
        "caption": "Изменение персональных данных",
        "info": True}
    return changeInfo(request, person, id, res)
    
@convertData
@isAccess
def changePassword(request, person, id):            #"changepassword/<str:person>/<int:id>"
    """Страница изменения пароля"""
    res = {
        "caption": "Изменение идентификации",
        "password": True}
    return changeInfo(request, person, id, res)

def changeInfo (request, person, id, add):    
    """Функция вывода изменения персональной информации"""
    if(request.method.upper() == "POST"):
        data = json.load(request)
        return HttpResponse(Persons().loadInfo(data, id, person))
    content = Persons().createStructure(id, person) | add
    content["back"] = Extra().getPath("personal", person, id.id)     
    return render(request, "change_info.html", content)



@convertData
@isAccess
def work(request, person, id):                      #TODO           #"work/"
    """Рабочая страница работников и студентов"""
    info = Persons().getWork(id, person)   
    info["today"] = date.today().strftime("%Y%m")
    return render(request, info["html"], info)

@convertData
@isAccess
@isEmployee
@isLeader
def groups(request, person, id):
    """Страница составления-просмотра расписания группы"""
    info = Groups().createStructure(id)
    if(not info):    
        return render(request, "error_access.html")    
    content = {
        "data": info,
        "person": Extra().getPath(person, id.id) + "/",
        "back": Extra().getPath("work", person, id.id)}        
    return render(request, "groups.html", content)




@convertData
@isAccess
@isLeader
def setSchedule(request, person, id, grp, sbj):
    """Страница первичного составления расписания предмета"""
    back = Extra().getPath("groups", person, id.id)
    if(request.method.upper() == "POST"):
        data = json.load(request)
        res = Schedule().setSchedule(data, grp, sbj)
        if(res == ""):
            res = back
        return HttpResponse(res);
    info = Schedule().createSchedule(grp, sbj)
    if(not info):    
        return render(request, "error_access.html") 
    info["back"] = back
    return render(request, "set_schedule.html", info)

@convertData
@isAccess
@isLeader
def getSchedule(request, person, id, grp, sbj):
    """Страница просмотра расписания предмета"""
    info = Schedule().createLessons(grp, sbj)
    if(not info):    
        return render(request, "error_access.html") 
    info["back"] = Extra().getPath("groups", person, id.id)   
    info["person"] = Extra().getPath(person, id.id, grp.id, sbj.id) + "/"
    return render(request, "get_schedule.html", info)

@convertData
@isAccess
@isLeader
def editSchedule(request, person, id, grp, sbj, sch):
    """Страница редактирования даты-время-преподаватель урока"""
    back = Extra().getPath("getschedule", person, id.id, grp.id, sbj.id)
    if(request.method.upper() == "POST"):
        data = json.load(request)
        Schedule().setEditSchedule(data, sch)       
        return HttpResponse(back);
    
    info = Schedule().createLesson(sch) 
    info["back"] = back
    return render(request, "edit_schedule.html", info) 

@convertData
@isAccess
def calendar(request, person, id, dt):        
    """Страница личного календаря"""                      
    return getCalendar(request, person, id, dt, "my")

@convertData
@isAccess
@isLeader
def calendarDepartment(request, person, id, dt):           
    """Страница календаря отдела"""                      
    return getCalendar(request, person, id, dt, "dep")   


@convertData
@isAccess
@isDIR
def calendarAll(request, person, id, dt):            
    """Страница календаря всех"""                      
    return getCalendar(request, person, id, dt, "all")   



def getCalendar(request, person, id, dt, ev): 
    """Функция отображения календаря"""
    info = Calendar().getMonthData(dt)
    if(not info):
        return render(request, "error_access.html") 
    info["events"] = Persons().getEvent(id, person, info["range"], ev)
    info["back"] = Extra().getPath("work", person, id.id)
    return render(request, "calendar.html", Calendar().getContent(info))
    


@convertData
@isAccess
@isLeader
def progress(request, person, id):                  
    info = Groups().createStructure(id)
    if(not info):    
        return render(request, "error_access.html")   
    content = {
        "data": info,
        "person": Extra().getPath(person, id.id) + "/",
        "back": Extra().getPath("work", person, id.id)}        
    return render(request, "progress_groups.html", content) 

@convertData
@isAccess   
@isLeader                                    
def marksGroup(request, person, id, grp):
    info = Groups().getMarksGroup(grp)    
    info["person"] = Extra().getPath("marksgroupstudent", person, id.id, grp.id) + "/"
    info["back"] = Extra().getPath("progress", person, id.id)
    return render(request, "get_marks.html", info)   

@convertData
@isAccess
@isLeader
def marksSubject(request, person, id, grp, sbj):   #TODO
    info = Groups().getMarksGroup(grp, sbj)
    info["person"] = Extra().getPath("markssubjectstudent", person, id.id, grp.id, sbj.id) + "/"
    info["back"] = Extra().getPath("progress", person, id.id)
    return render(request, "get_marks.html", info)  
    
@convertData
@isAccess   
@isLeader
def marksGroupStudent(request, person, id, grp, std):                 #TODO
    info = Groups().getMarksStudent(std)
    info["back"] = Extra().getPath("marksgroup", person, id.id, grp.id)
    
    
    info["person"] = Extra().getPath("info", person, id.id, grp.id, std.id)
    
    
    return render(request, "get_student_marks.html", info)  

@convertData
@isAccess   
@isLeader
def marksSubjectStudent(request, person, id, grp, sbj, std):                 #TODO
    info = Groups().getMarksStudent(std, sbj)
    info["back"] = Extra().getPath("markssubject", person, id.id, grp.id, sbj.id)
    info["person"] = Extra().getPath("info", person, id.id, grp.id, sbj.id, std.id)
    return render(request, "get_student_marks.html", info)  




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
    



  
    
    