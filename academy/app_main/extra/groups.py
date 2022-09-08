from ..models import Groups as gr, Course_Subject, Schedule, Subjects, Employees, NamesWeekDays, LessonTimes
from ..models import Marks, Students
from .extra import Extra
from datetime import date


from django.db.models import Count, Sum, Avg, Min, Max
from django.db import connection, reset_queries
import time
import functools




class Groups():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 
    
    def getGroup(self, grp):  
        try:
            g = gr.objects.get(id=grp)               
        except:
            None    
        return g
    
    def getStudent(self, std):  
        try:
            s = Students.objects.get(id=std)               
        except:
            None    
        return s
    
    
    def getGroupSubject(self, grp, sbj):  
        try:
            g = grp
            s = Subjects.objects.get(id=sbj)
            cs = Course_Subject.objects.get(course__id=g.course.id, subject__id=sbj)                   
        except:
            return {}     
        return {"group": g, "subject": s, "course": cs.course}
    
    
    def createStructure(self, per): #TODO протестить не активного профессора
        rows = gr.objects.filter(course__department=per.department)
        res = {}
        for r in rows:
            temp = self.__getSchedule(r)
            for el in temp: 
                temp[el] = [
                    temp[el][0], 
                    temp[el][1][0]["date"] == None,
                    len(list(filter(lambda s: s["professor"] == None, temp[el][1]))) != 0]
            res[str(r.id)] = [r.name, r.course.name, temp]            
        return res
    
    def __getSchedule(self, gr):        #TODO протестить не активного профессора
        sch = Schedule.objects.filter(group=gr)
        cs = Course_Subject.objects.filter(course=gr.course)
        res = {}
        for el in cs:
            temp = sch.filter(subject=el.subject)             
            res[str(el.subject.id)] = [
                    el.subject.name, 
                    list(map(lambda s: {"date": s.lesson_date, "professor": s.isActivProfessor()}, temp))]
        return res            
    
    def createSchedule(self, g, s):
        emp = Employees.objects.filter(department=s.department, activ=True)    
        return {
            "group": g.name,
            "subject": s.name,
            "course": g.course.name,
            "begin": Extra().getStringData(g.started),
            "end": Extra().getStringData(g.endStudy()),
            "amount": s.amount_lessons,
            "professors": dict(map(lambda s: (str(s.id), s.getShotName()), emp)),
            "daysofweek": list(map(lambda s: [s.shortName, str(s.index)], NamesWeekDays.objects.all())),
            "lessontimes": dict(map(lambda s: (str(s.id), Extra().getStringTimeShort(s.time)), LessonTimes.objects.all()))
            }
    
    
    def getSchedule(self, sch):
        try:
            sch = Schedule.objects.get(id=sch)
        except:
            return {}
        return sch
        
    
    def setSchedule(self, data, gr, sb, back):
        sch = Schedule.objects.filter(group=gr.id, subject=sb.id)
        if(len(sch) != len(data["lessons"])):
            return "\nОшибка совместимости. Обратитесь к администратору"
        pr = Employees.objects.get(id=data["professor"])       
        i=0
        for el in sch:
            el.setLesson(data["lessons"][i], pr)
            i+=1
        return back
    
    def setEditSchedule(self, data, sch, back):
        pr = Employees.objects.get(id=data["professor"])            
        sch.setLesson(data["lesson"], pr);    
        return back
    
    def createLessons(self, grp, sbj):
        rows = Schedule.objects.filter(group=grp.id, subject=sbj.id).order_by('lesson_date', 'lesson_time')
        res = {}
        an = ""
        for el in rows:
            but = "was"
            if(date.today() <= el.lesson_date):
                but = ("" if el.isActivProfessor() else "bg_red")
                if(an == ""):
                    an = str(el.id)               
            temp = [but, [
                Extra().getStringData(el.lesson_date),
                Extra().getStringTimeShort(el.lesson_time.time),
                el.getActivProfessor()]]
            res[str(el.id)] = temp
        return {
                "group_subject": '{}, "{}"'.format(grp.name, sbj.name),
                "caption": ["Урок", "Дата", "Время", "Преподаватель"],
                "lessons": res,
                "anchor": str(an)}
    
    def createLesson(self, sch):
        pr = sch.isActivProfessor()
        res = self.createSchedule(sch.group, sch.subject)
        res["group_subject"] = '{}, "{}"'.format(res["group"], res["subject"])
        res["currentdate"] =  Extra().getStringData(sch.lesson_date)
        res["currenttime"] = str(sch.lesson_time.id)
        res["currentprofessor"] = str(pr.id if pr else -1)
        return res


    def query_debugger(func):               #TODO  удалить и импорты
        @functools.wraps(func)
        def inner_func(*args, **kwargs):
            reset_queries()            
            start_queries = len(connection.queries)
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            end_queries = len(connection.queries)
            print(f"Function : {func.__name__}")
            print(f"Number of Queries : {end_queries - start_queries}")
            print(f"Finished in : {(end - start):.2f}s")
            return result
        return inner_func

    def getMarksGroup(self, grp, sbj=None):             #TODO            
        data = dict(map(lambda s: (str(s.id), [s.getShotName(), 0]), Students.objects.filter(group=grp))) 
        if(sbj):
            marks = Marks.objects.filter(lesson__group=grp, lesson__subject=sbj) 
        else:
            marks = Marks.objects.filter(lesson__group=grp) 
        mm = marks.values("student").annotate(avg=Avg('mark__index'))    
        for el in mm:                                     
            data[str(el["student"])][1] = el["avg"]
        try:
            mm = marks.aggregate(avg=Avg('mark__index'))["avg"]
        except:
            mm = 0
        data = list(map(lambda s: ([s[0]] + s[1]), data.items()))
        data.sort(reverse=True, key = (lambda s: s[2])) 
        
        for el in data:
            el[2] = Extra().getRoundString(el[2], 2)
        
        return {    
            "group": grp.name, 
            "course": grp.course.name,
            "total": Extra().getRoundString(mm, 2),
            "data": data,
            "subject": (sbj.name if sbj else "")}
            
    #@query_debugger
    def getMarksStudent(self, std, sbj=None):        
        if(sbj):
            marks = Marks.objects.select_related('lesson', 'mark').filter(student=std, lesson__subject=sbj).order_by('-lesson__lesson_date') 
        else:
            marks = Marks.objects.select_related('lesson', 'mark').filter(student=std).order_by('-lesson__lesson_date') 
        data = list(map(lambda s: [Extra().getStringData(s.lesson.lesson_date), s.lesson.subject.name, s.mark.name], marks))
        try:
            mm = marks.aggregate(avg=Avg('mark__index'))["avg"]
        except:
            mm = 0
        return {
                "lastname": std.lastname,
                "firstname": std.firstname,
                "patronymic": std.patronymic,
                "total": Extra().getRoundString(mm, 2),
                "data": data,
                "subject": (sbj.name if sbj else "")}
        