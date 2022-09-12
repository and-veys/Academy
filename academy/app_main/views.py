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
from .extra.access import Access
from .extra.bot import Bot
import json
from datetime import date


def bot(request):                                   
    """Обработчик сообщений от телебота"""
    if("command" not in request.GET):
        return Extra().render(request, "error_access.html")
    resp = Bot().message(request.GET)
    return HttpResponse(resp)

def main(request):                                  
    """Главная страница"""
    return Extra().render(request, "start.html")

def departments(request):                           
    """Страница структуры отделов"""        
    content = Departments().createStructure()    
    return Extra().render(request, "departments.html", {"data": content})

def courses(request):                             
    """Страница курсов обучения"""    
    content = Courses().createStructure()      
    return Extra().render(request, "courses.html", {"data": content})


@Access().convertData
@Access().isAccess
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
        return Extra().render(request, "error_access.html")
    return personalInformation(request, per, id, False, back)

@Access().convertData
@Access().isAccess
def personalInfo(request, person, id):          
    """Страница с информацией (полной) о работниках и студентах"""
    back = [Extra().getPath("work", person, id.id), "Приступить к работе"]
    return  personalInformation(request, person, id, True, back) 

def personalInformation(request, person, id, full, back):  
    """Функция вывода персональной информации"""
    if(request.method.upper() == "POST"): 
        data = json.load(request)
        return HttpResponse(Persons().loadPhoto(data, id, person)) 
    content = Persons().createStructure(id, person)     
    content["back"] = back    
    content["full"] = full 
    if(content["OK"]):
        return Extra().render(request, "info_persons.html", content)
    else:
        return Extra().render(request, "error_access.html")


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
    return Extra().render(request, "registration.html")


@Access().convertData
@Access().isAccess
def changePersonal(request, person, id):            #"changeinfo/<str:person>/<int:id>"
    """Страница изменения личных данных"""
    res = {
        "caption": "Изменение персональных данных",
        "info": True}
    return changeInfo(request, person, id, res)
    
@Access().convertData
@Access().isAccess
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
    return Extra().render(request, "change_info.html", content)



@Access().convertData
@Access().isAccess
def work(request, person, id):                      #TODO           #"work/"
    """Рабочая страница работников и студентов"""
    info = Persons().getWork(id, person)   
    info["today"] = date.today().strftime("%Y%m")
    return Extra().render(request, info["html"], info)
    
@Access().convertData
@Access().isAccess
@Access().isEmployee
@Access().isLeader
def groups(request, person, id):
    """Страница составления-просмотра расписания группы"""
    info = Groups().createStructure(id)
    if(not info):    
        return Extra().render(request, "error_access.html")    
    content = {
        "data": info,
        "person": Extra().getPath(person, id.id) + "/",
        "back": Extra().getPath("work", person, id.id)}        
    return Extra().render(request, "groups.html",  content)

@Access().convertData
@Access().isAccess
@Access().isLeader
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
        return Extra().render(request, "error_access.html") 
    info["back"] = back
    return Extra().render(request, "set_schedule.html", info)

@Access().convertData
@Access().isAccess
@Access().isLeader
def getSchedule(request, person, id, grp, sbj):
    """Страница просмотра расписания предмета"""
    info = Schedule().createLessons(grp, sbj)
    if(not info):    
        return Extra().render(request, "error_access.html") 
    info["back"] = Extra().getPath("groups", person, id.id)   
    info["person"] = Extra().getPath(person, id.id, grp.id, sbj.id) + "/"
    return Extra().render(request, "get_schedule.html", info)

@Access().convertData
@Access().isAccess
@Access().isLeader
def editSchedule(request, person, id, grp, sbj, sch):
    """Страница редактирования даты-время-преподаватель урока"""
    back = Extra().getPath("getschedule", person, id.id, grp.id, sbj.id)
    if(request.method.upper() == "POST"):
        data = json.load(request)
        Schedule().setEditSchedule(data, sch)       
        return HttpResponse(back);
    
    info = Schedule().createLesson(sch) 
    info["back"] = back
    return Extra().render(request, "edit_schedule.html", info)

@Access().convertData
@Access().isAccess
def calendar(request, person, id, dt):        
    """Страница личного календаря"""                      
    return getCalendar(request, person, id, dt, "my")

@Access().convertData
@Access().isAccess
@Access().isLeader
def calendarDepartment(request, person, id, dt):           
    """Страница календаря отдела"""                      
    return getCalendar(request, person, id, dt, "dep")   


@Access().convertData
@Access().isAccess
@Access().isDIR
def calendarAll(request, person, id, dt):            
    """Страница календаря всех"""                      
    return getCalendar(request, person, id, dt, "all")   


def getCalendar(request, person, id, dt, ev): 
    """Функция отображения календаря"""
    info = Calendar().getMonthData(dt)
    if(not info):
        return Extra().render(request, "error_access.html") 
    info["events"] = Persons().getEvent(id, person, info["range"], ev)
    info["back"] = Extra().getPath("work", person, id.id)
    content = Calendar().getContent(info)
    return Extra().render(request, "calendar.html", content)
    
    
    
@Access().convertData
@Access().isAccess
@Access().isLeaderOrDIR
def progress(request, person, id):
    """Страница курс-предмет факультета""" 
    info = Groups().createStructure(id)
    if(not info):    
        return Extra().render(request, "error_access.html")   
    content = {
        "data": info,
        "person": Extra().getPath(person, id.id) + "/",
        "back": Extra().getPath("work", person, id.id)}        
    return Extra().render(request, "progress_groups.html", content)
    return getProgress(request, person, id, False)



@Access().convertData
@Access().isAccess   
@Access().isLeaderOrDIR                              
def marksGroup(request, person, id, grp):
    """Страница средних оценок студентов группы"""
    info = Groups().getMarksGroup(grp)    
    info["person"] = Extra().getPath("marksgroupstudent", person, id.id, grp.id) + "/"
    info["back"] = Extra().getPath("progress", person, id.id)
    return Extra().render(request, "get_marks.html", info)
    


@Access().convertData
@Access().isAccess
@Access().isLeaderOrDIR
def marksSubject(request, person, id, grp, sbj):   
    """Страница средних оценок по предмету студентов группы"""
    info = Groups().getMarksGroup(grp, sbj)
    info["person"] = Extra().getPath("markssubjectstudent", person, id.id, grp.id, sbj.id) + "/"
    info["back"] = Extra().getPath("progress", person, id.id)
    return Extra().render(request, "get_marks.html", info) 
    
@Access().convertData
@Access().isAccess   
@Access().isLeaderOrDIR
def marksGroupStudent(request, person, id, grp, std):               
    """Страница всех оценок студента группы"""
    info = Groups().getMarksStudent(std)
    info["back"] = Extra().getPath("marksgroup", person, id.id, grp.id)
    info["person"] = Extra().getPath("info", person, id.id, grp.id, std.id)
    return Extra().render(request, "get_student_marks.html", info)

@Access().convertData
@Access().isAccess   
@Access().isLeaderOrDIR
def marksSubjectStudent(request, person, id, grp, sbj, std):                 
    """Страница всех оценок по предмету студента группы"""
    info = Groups().getMarksStudent(std, sbj)
    info["back"] = Extra().getPath("markssubject", person, id.id, grp.id, sbj.id)
    info["person"] = Extra().getPath("info", person, id.id, grp.id, sbj.id, std.id)
    return Extra().render(request, "get_student_marks.html",  info)














def marks(request, person, id):                                 #TODO
    """Страница предмет-группы для преподавателя"""
    return Extra().render(request, "error_access.html") 





@Access().isAdministrator
def generate(request):                                  
    """Генерация студентов и преподавателей"""
    res = ""
    res += Generate().generateStudents()
    res += Generate().generateEmployees()
    res += Generate().generateMarks()
    return HttpResponse(res)

@Access().isAdministrator
def serialize(request):          
    """Сохранение данных БД"""                                   
    return HttpResponse(Generate().serialize())

@Access().isAdministrator                                  
def loaddata(request):   
    """Загрузка данных БД"""                       
    return HttpResponse(Generate().loaddata())
    



  
    
    