from ..models import Groups as db, Course_Subject, Schedule, Subjects, Employees, NamesWeekDays, LessonTimes
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
    
    def getData(self, id, person):  
        return Extra().getDataObject(db, id)
    
    def control(self, kwargs):
        if(kwargs["person"] == "employees"):
            return (kwargs["grp"].course.department.id == kwargs["id"].department.id)        
        return (kwargs["grp"].id == kwargs["id"].group.id)
        
    def createStructure(self, per):
        rows = db.objects.filter(course__department=per.department)
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
    
    def __getSchedule(self, gr):      
        sch = Schedule.objects.filter(group=gr)
        cs = Course_Subject.objects.filter(course=gr.course)
        res = {}
        for el in cs:
            temp = sch.filter(subject=el.subject)             
            res[str(el.subject.id)] = [
                    el.subject.name, 
                    list(map(lambda s: {"date": s.lesson_date, "professor": s.isActivProfessor()}, temp))]
        return res            
    
   

    
    



    # def query_debugger(func):               #TODO  удалить и импорты
        # @functools.wraps(func)
        # def inner_func(*args, **kwargs):
            # reset_queries()            
            # start_queries = len(connection.queries)
            # start = time.perf_counter()
            # result = func(*args, **kwargs)
            # end = time.perf_counter()
            # end_queries = len(connection.queries)
            # print(f"Function : {func.__name__}")
            # print(f"Number of Queries : {end_queries - start_queries}")
            # print(f"Finished in : {(end - start):.2f}s")
            # return result
        # return inner_func

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
        