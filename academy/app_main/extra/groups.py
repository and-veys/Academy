from ..models import Groups as gr, Course_Subject, Schedule, Subjects, Employees, NamesWeekDays, LessonTimes
from .extra import Extra
from datetime import date

class Groups():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 
    
    def getGroup(self, grp, sbj):      
        try:
            g = gr.objects.get(id=grp)
            s = Subjects.objects.get(id=sbj)
            cs = Course_Subject.objects.get(course__id=g.course.id, subject__id=sbj)            
        except:
            return {}           
        return {"group": g, "subject": s}
    
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





    