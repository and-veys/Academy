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
from .extra.applications import Applications
from .extra.bot import Bot
import json
from datetime import date


def render(*args):
    return Extra().render(*args)

def bot(request):                                   
    """Обработчик сообщений от телебота"""
    if("command" not in request.GET):
        return render(request, "error_access.html")
    resp = Bot().message(request.GET)
    return HttpResponse(resp)

def pageNotFound(request, exception):
    return render(request, "error_access.html", {"ERR": 404})


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

@Access().isAccess
@Access().convertData
def info(request, **kwargs):         
    """Страница с краткой информацией о работниках/студентах"""
    if("person" not in kwargs):
        back = ["/departments", "К структуре Академии"]
        per = "employees"
        id = kwargs["id"]
    elif("std" in kwargs):
        per = "students"
        id = kwargs["std"]
        temp = list(map(lambda s: (s if (type(s) == type("1")) else s.id), kwargs.values()))
        if("sch" in kwargs):
            temp = temp[:-1]
            back = "editmarks"
        else:
            if("sbj" in kwargs):
                back = "markssubjectstudent"
            else:
                back = "marksgroupstudent"
        back = [Extra().getPath(back, *temp), "Назад"] 
    elif("cwk" in kwargs):
        per = kwargs["person"]
        id = kwargs["cwk"]
        back = [Extra().getPath("coworkers", kwargs["person"], kwargs["id"].id), "Назад"]        
    else:
        return render(request, "error_access.html") 
        
    return personalInformation(request, per, id, False, back)

@Access().isAccess
@Access().convertData
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
    if(content["OK"]):
        back[0] = Extra().setAnchor(back[0], content["id"])
        content["back"] = back    
        content["full"] = full 
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
    return render(request, "registration.html")

@Access().isAccess
@Access().convertData
def changePersonal(request, person, id):            
    """Страница изменения личных данных"""
    res = {
        "caption": "Изменение персональных данных",
        "info": True}
    return changeInfo(request, person, id, res)

@Access().isAccess  
@Access().convertData
def changePassword(request, person, id):           
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


@Access().isAccess
@Access().convertData
def work(request, person, id):                      
    """Рабочая страница работников и студентов"""
    info = Persons().getWork(id, person)   
    info["today"] = date.today().strftime("%Y%m")
    return render(request, info["html"], info)

@Access().isAccess  
@Access().convertData
@Access().isEmployee
@Access().isLeader
def groups(request, person, id):
    """Страница составления-просмотра расписания группы"""
    info = Groups().createStructure(id)  
    content = {
        "data": info,
        "person": Extra().getPath(person, id.id) + "/",
        "back": Extra().getPath("work", person, id.id)}        
    return render(request, "groups.html",  content)

@Access().isAccess
@Access().convertData
@Access().isEmployee
@Access().isLeader
def setSchedule(request, person, id, grp, sbj):
    """Страница первичного составления расписания предмета"""
    back = Extra().getPath("groups", person, id.id)
    back = Extra().setAnchor(back, grp.id, sbj.id) 
    
    if(request.method.upper() == "POST"):
        data = json.load(request)
        res = Schedule().setSchedule(data, grp, sbj)
        if(res == ""):
            res = back
        return HttpResponse(res);
    info = Schedule().createSchedule(grp, sbj) 
    info["back"] = back
    return render(request, "set_schedule.html", info)

@Access().isAccess
@Access().convertData
@Access().isEmployee
@Access().isLeader
def getSchedule(request, person, id, grp, sbj):
    """Страница просмотра расписания предмета"""
    info = Schedule().createLessons(grp, sbj)
    back = Extra().getPath("groups", person, id.id)     
    info["back"] = Extra().setAnchor(back, grp.id, sbj.id) 
    info["person"] = Extra().getPath(person, id.id, grp.id, sbj.id) + "/"
    return render(request, "get_schedule.html", info)

@Access().isAccess
@Access().convertData
@Access().isEmployee
@Access().isLeader
def editSchedule(request, person, id, grp, sbj, sch):
    """Страница редактирования даты-время-преподаватель урока"""
    back = Extra().getPath("getschedule", person, id.id, grp.id, sbj.id)
    back = Extra().setAnchor(back, sch.id)
    if(request.method.upper() == "POST"):
        data = json.load(request)
        Schedule().setEditSchedule(data, sch)       
        return HttpResponse(back);
    
    info = Schedule().createLesson(sch) 
    info["back"] = back
    return render(request, "edit_schedule.html", info)

@Access().isAccess
@Access().convertData
def calendar(request, person, id, dt):        
    """Страница личного календаря"""                      
    return getCalendar(request, person, id, dt, "my")

@Access().isAccess
@Access().convertData
@Access().isEmployee
@Access().isLeader
def calendarDepartment(request, person, id, dt):           
    """Страница календаря отдела"""                      
    return getCalendar(request, person, id, dt, "dep")   

@Access().isAccess
@Access().convertData
@Access().isEmployee
@Access().isDIR
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
    content = Calendar().getContent(info)
    return render(request, "calendar.html", content)
    
    
@Access().isAccess    
@Access().convertData
@Access().isEmployee
@Access().isLeaderOrDIR
def progress(request, person, id):
    """Страница курс-предмет факультета""" 
    info = Groups().createStructure(id)  
    content = {
        "data": info,
        "person": Extra().getPath(person, id.id) + "/",
        "back": Extra().getPath("work", person, id.id)}        
    return render(request, "progress_groups.html", content)
    return getProgress(request, person, id, False)


@Access().isAccess 
@Access().convertData
@Access().isEmployee  
@Access().isLeaderOrDIR                              
def marksGroup(request, person, id, grp):
    """Страница средних оценок студентов группы"""
    info = Groups().getMarksGroup(grp)    
    back = Extra().getPath("progress", person, id.id)
    info["person"] = Extra().getPath("marksgroupstudent", person, id.id, grp.id) + "/"
    info["back"] = Extra().setAnchor(back, grp.id)
    return render(request, "get_marks.html", info)
    

@Access().isAccess
@Access().convertData
@Access().isEmployee
@Access().isLeaderOrDIR
def marksSubject(request, person, id, grp, sbj):   
    """Страница средних оценок по предмету студентов группы"""
    info = Groups().getMarksGroup(grp, sbj)
    back = Extra().getPath("progress", person, id.id)
    info["person"] = Extra().getPath("markssubjectstudent", person, id.id, grp.id, sbj.id) + "/"
    info["back"] = Extra().setAnchor(back, grp.id, sbj.id)
    return render(request, "get_marks.html", info) 

@Access().isAccess     
@Access().convertData 
@Access().isEmployee
@Access().isLeaderOrDIR
def marksGroupStudent(request, person, id, grp, std):               
    """Страница всех оценок студента группы"""
    info = Groups().getMarksStudent(std)
    back = Extra().getPath("marksgroup", person, id.id, grp.id)
    
    info["back"] = Extra().setAnchor(back, std.id)
    info["person"] = Extra().getPath("info", person, id.id, grp.id, std.id)
    return render(request, "get_student_marks.html", info)

@Access().isAccess 
@Access().convertData
@Access().isEmployee  
@Access().isLeaderOrDIR
def marksSubjectStudent(request, person, id, grp, sbj, std):                 
    """Страница всех оценок по предмету студента группы"""
    info = Groups().getMarksStudent(std, sbj)
    back = Extra().getPath("markssubject", person, id.id, grp.id, sbj.id)
    info["back"] = Extra().setAnchor(back, std.id)
    info["person"] = Extra().getPath("info", person, id.id, grp.id, sbj.id, std.id)
    return render(request, "get_student_marks.html",  info)

@Access().isAccess
@Access().convertData
@Access().isEmployee  
def marks(request, person, id):                                 
    """Страница предмет-группы для преподавателя"""
    info = Schedule().createProfessorSubjects(id)
    content = {
        "data": info,
        "back": Extra().getPath("work", person, id.id),
        "person": Extra().getPath(person, id.id) + "/"  }
    return render(request, "professor_groups.html", content) 

@Access().isAccess
@Access().convertData
@Access().isEmployee
def setMarks(request, person, id, grp, sbj):
    """Страница просмотра расписания предмета"""
    info = Schedule().createLessons(grp, sbj, False) 
    back = Extra().getPath("marks", person, id.id) 
    info["id"] = id.id
    info["back"] = Extra().setAnchor(back, grp.id, sbj.id)
    info["person"] = Extra().getPath(person, id.id, grp.id, sbj.id) + "/"
    return render(request, "set_marks.html", info)


@Access().isAccess
@Access().convertData
@Access().isEmployee
def editMarks(request, person, id, grp, sbj, sch):
    """Страница просмотра расписания предмета"""
    if(request.method.upper() == "POST"):           
        data = json.load(request)
        res = Schedule().setMarks(grp, sch, data)
        if(res == ""):
            res = Extra().getPath("editmarks", person, id.id, grp.id, sbj.id, sch.id)
        return HttpResponse(res);
    info = Schedule().createMarks(sch) 
    back = Extra().getPath("setmarks", person, id.id, grp.id, sbj.id)  
    info["back"] = Extra().setAnchor(back, sch.id) 
    info["person"] = Extra().getPath(person, id.id, grp.id, sbj.id, sch.id) + "/"
    return render(request, "edit_marks.html", info)


@Access().isAccess 
@Access().convertData
def coworkers(request, person, id):
    """Страница коллег по отделу/группе"""
    if(person == "employees"):
        content = Departments().createDepartment(id.department)  
        path = "coworkers.html"
    else:
        content = Groups().createGroup(id.group) 
        path = "classmate.html"
    content["person"] = Extra().getPath(person, id.id) + "/"
    content["back"] = Extra().getPath("work", person, id.id)
    return render(request, path, content)



@Access().isAccess 
@Access().convertData
@Access().isEmployee
@Access().isDIR
@Access().isLeader
def activ(request, person, id, per, abc):
    content = Generate().createStructure(per, abc, True)
    if(not content):
        return render(request, "error_access.html") 
    content["back"] = Extra().getPath("work", person, id.id)
    content["caption"] = "Заблокировать / Разблокировать"

        
    return render(request, "loginas.html", content)

@Access().isAccess 
@Access().convertData
@Access().isEmployee
@Access().isDIR
@Access().isLeader
def block(request, person, id, per, abc, bl): 
    info = Persons().getDataAll(bl, per)
    if(not info):
        return render(request, "error_access.html")
    back = [Extra().getPath("activ", person, id.id, per, abc), "Назад"] 
    back[0] = Extra().setAnchor(back[0], bl) 
    if(request.method.upper() == "POST"):  
        Persons().setBlock(info)
        return HttpResponse(back[0]) 
    content = info.getPersonalInfo()
    content["back"] = back 
    content["activ"] = content["OK"]
    return render(request, "block.html", content)
    

@Access().isAccess 
@Access().convertData
@Access().isEmployee
@Access().isDIR
@Access().isLeader
def applications(request, person, id, per):
    info = Applications().createCtructure(per)
    content = {
        "data": info,
        "back": Extra().getPath("work", person, id.id),
        "person": Extra().getPath(person, id.id, per) + "/",
        "caption": "Заявки на {}".format(("работу" if per=="employee" else "учебу"))
    }
    return render(request, "applications.html", content)

@Access().isAccess 
@Access().convertData
@Access().isEmployee
@Access().isDIR
@Access().isLeader   
def appFromBot(request, person, id, per, bl):
    info = Applications().getDataAll(bl, per)
    if(not info):
        return render(request, "error_access.html")
    back = [Extra().getPath("applications", person, id.id, per), "Назад"] 
    back[0] = Extra().setAnchor(back[0], bl) 
    if(request.method.upper() == "POST"):  
        data = json.load(request)
        if(Applications().setBlock(info, data)):
            return HttpResponse(back[0]) 
        return render(request, "error_access.html")        
    content = info.getInfo()
    content["back"] = back 
    content["caption"] = "Заявка на {}".format(("работу" if per=="employee" else "учебу"))
    content["dataApp"] = Applications().getDepartmentGroup(info)
    content["extraApp"] = Applications().getStatus(info)
    if(content["dataApp"]):
        return render(request, "app_from_bot.html", content)
    return render(request, "error_access.html") 
    
@Access().isAdministrator
def administrator(request):
    """Страница администратора"""
    return render(request, "administrator.html")

@Access().isAdministrator
def loginas(request, person, abc):
    """Страница выбора работника/студента администратором"""
    content = Generate().createStructure(person, abc)
    if(not content):
        return render(request, "error_access.html")  
    content["back"] = "/administrator"
    content["caption"] = "Войти как ..."
    return render(request, "loginas.html", content)


@Access().isAdministrator
def generate(request):                                  
    """Генерация студентов и преподавателей"""
    res = ""
    res += Generate().generateStudents()
    res += Generate().generateEmployees()
    res += Generate().generateMarks()
    res += "<a href='/administrator'>Назад</a>"
    return HttpResponse(res)

@Access().isAdministrator
def serialize(request):          
    """Сохранение данных БД""" 
    content = {
        "data": Generate().serialize().split("<br />"),
        "caption": "Результат сохранения данных"
    }
    return render(request, "save_load.html", content)


@Access().isAdministrator                                  
def loaddata(request):   
    """Загрузка данных БД""" 
    content = {
        "data": Generate().loaddata().split("<br />"),
        "caption": "Результат загрузки данных"
    }
    return render(request, "save_load.html", content)
    



  
    
    