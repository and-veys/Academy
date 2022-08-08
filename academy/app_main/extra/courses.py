from ..models import Departments as dp, Courses as cs, Course_Subject as cs_sc


class Courses():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 
    
    def createStructure(self):
        res = {}
        rows = dp.objects.all().order_by("status__sort_weight", "name") 
        for el in rows:
            cour = cs.objects.filter(department=el.id)
            pl = {}
            for c in cour:
                sub = cs_sc.objects.filter(course=c.id)
                if(len(sub)):
                    pl[sub[0].course.name] = dict(map(lambda s: [s.id, s.subject.name], sub))
            if(pl):
                res[el.name] = pl               
        return res
        