from ..models import ApplicationBot as db, Groups, Departments
from .extra import Extra

class Applications():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 

    def getDataAll(self, id, per):     
        try:
            el = db.objects.get(id=id, person=per)
        except:
            return None
        return el 

    def createCtructure(self, per):
        rows = db.objects.filter(person=per, activ=True, action=0)
        if(len(rows)==0):
            return None
        return dict(map(lambda s: (str(s.id), s.getFullName()), rows))
                  
    def getDepartmentGroup(self, per):
        temp = {"employee": [Departments, "ОТДЕЛ"], "student": [Groups, "ГРУППА"]}
        try:
            temp = temp[per.person]
        except:
            return None
        rows = temp[0].objects.all()            
        return [dict(map(lambda s: (str(s.id), s.name), rows)), temp[1]]
 
    def setBlock(self, id, data):      
        act = data["action"] + 1
        id.action = act        
        if(act == 3):
            temp = {"employee": Departments, "student": Groups}
            try:
                temp = temp[id.person].objects.get(id=data["id"]) 
            except:
                return False
            Extra().paint("-------------------------------",temp)
            if(id.person == "employee"):
                id.department = temp               
            else:
                id.group = temp
        id.save()
        return True