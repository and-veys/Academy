from ..models import Departments as db, Employees, Status_Employees, Students
from .extra import Extra


class Departments():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 
    def getData(self, id, person):        
        if(person == "employees"):
            el = Extra().getDataObject(Employees, id)
        else:
            el = Extra().getDataObject(Students, id)
        if(el and el.activ):
            return el
        return  None 
    
    def control(self, kwargs):
        if(kwargs["person"] == "employees"):
            return (kwargs["id"].department.id == kwargs["cwk"].department.id)
        return (kwargs["id"].group.id == kwargs["cwk"].group.id)


    def createStructure(self, dep=None):
        res = {}
        if(dep):
            rows=db.objects.filter(id=dep.id)        
        else:
            rows = db.objects.all().order_by("status__sort_weight", "name")
        stat = Status_Employees.objects.all().order_by("sort_weight")   
        for el in rows:
            temp = Employees.objects.filter(department=el, activ=True)
            pl = {}
            for q in stat:
                pers = temp.filter(status=q.id)
                if(len(pers)):                
                    pl[pers[0].getStatusAlias(True)] = dict(
                                map(lambda s: [str(s.id), s.getShortName()], pers)) 
            res[el.name] = pl
        return res
    
    def createDepartment(self, dep):
        data = self.createStructure(dep)
        k = list(data.keys())[0]
        return {
            "caption": k,
            "data": data[k]
        }