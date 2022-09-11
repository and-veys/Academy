from ..models import Schedule as db, Employees, NamesWeekDays, LessonTimes
from .extra import Extra
from datetime import date

class Schedule():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst
    
    def getData(self, id, person):  
        return Extra().getDataObject(db, id)    
    
    def control(self, kwargs):
        return (kwargs["sch"].group == kwargs["grp"] and kwargs["sch"].subject == kwargs["sbj"])
        
        
        
    def setSchedule(self, data, gr, sb):
        sch = db.objects.filter(group=gr.id, subject=sb.id)
        if(len(sch) != len(data["lessons"])):
            return "\nОшибка совместимости. Обратитесь к администратору"
        pr = Employees.objects.get(id=data["professor"])       
        i=0
        for el in sch:
            el.setLesson(data["lessons"][i], pr)
            i+=1
        return ""
        
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
            
            
            
    def createLessons(self, grp, sbj):
        rows = db.objects.filter(group=grp.id, subject=sbj.id).order_by('lesson_date', 'lesson_time')
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
                
            
                
        
    
    def setEditSchedule(self, data, sch):
        pr = Employees.objects.get(id=data["professor"])            
        sch.setLesson(data["lesson"], pr);    
                
                
                
                