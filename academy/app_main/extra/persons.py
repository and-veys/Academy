from ..models import Employees, Students, Schedule, Genders
from .extra import Extra
from django.conf import settings
from django.db.models import Q
from datetime import timedelta, date
import re

class Persons():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 

    
    
    
    
    def getDataAll(self, id, person): 
        temp = {"employees": Employees, "students": Students}
        try:
            el = Extra().getDataObject(temp[person], id)
        except:
            return None
        return el
        
     
    
    
    def getData(self, id, person):  
        temp = {"employees": Employees, "students": Students}
        try:
            el = Extra().getDataObject(temp[person], id)
            if(el and el.activ):
                return el
            return None
        except:
            return None

    def control(self, kwargs):
        return ((kwargs["id"].getType() == kwargs["person"]) and kwargs["id"].activ)     
    
    

    
    def createStructure(self, id, tp):         
        if(type(id) == type(1)):
            id = self.getData(id, tp)
            if(not id):
                return {"OK": False}
        return id.getPersonalInfo()  






        
    
    def loadPhoto(self, data, id, tp):
        row = id
        path = "{}/persons/{}.{}".format(settings.MEDIA_ROOT, row.login, data["type"])
        try:
            file = open(path, "wb")
        except:
            return "\nОшибка записи файла на сервере."
        file.write(bytes(data["pic"]))
        file.flush()
        file.close()        
        row.picture = path
        try:
            row.save()
        except:
            return "\nОшибка записи базы данных на сервере."
        return "/personal/{}/{}".format(tp, id.id)
            
    def loadInfo(self, data, id, tp): 
        row = id
        if("login" in data):            
            if(self.isAdministrator(data["login"]) or self.getPersonFromLogin(data["login"])):
                return "\nСовпадение логина и пароля в базе данных."            
            row.login = data["login"]        
        if("phone" in data):
            row.phone = data["phone"]   
        if("e_mail" in data):
            row.e_mail = data["e_mail"]
        try:
            row.save()
        except:
            return "\nОшибка записи базы данных на сервере."
        return "/personal/{}/{}".format(tp, id.id)  
    
    def getPersonFromLogin(self, login):
        temp = {"employees": Employees, "students": Students}
        for k, cl in temp.items():       
            try:
                row = cl.objects.get(login=login)
                return {"row": row, "tp": k}
            except:
                pass
        return {}    
    
    

       
    def getRegistration(self, data):        
        row = self.getPersonFromLogin(data["login"])
        if(row):
            return {
                "login": data["login"], 
                "session": {"id": row["row"].id, "tp": row["tp"], "name": row["row"].getShortName()},
                "age": Extra().getRestDay(),
                "path": "/personal/{}/{}".format(row["tp"], row["row"].id),
                "OK": True
            } 
        if(self.isAdministrator(data["login"])):
            return {
                "login": data["login"], 
                "session": {"id": -1, "tp": "root", "name": "Администратор"},
                "age": Extra().getRestDay(),
                "path": Extra().getPath("administrator"),
                "OK": True
            }   
        return {"path": "\nОшибочные логин и пароль.", "OK": False}
            
    def isAdministrator(self, login): 
        return (login == settings.ROOT_USER)
        

            
    def getWork(self, id, tp):
        return id.getPersonalInfo()

    def getEvent(self, id, tp, rg, ev):                  
        dtMin, dtMax = rg
        temp = "{}_{}".format(ev, tp)  
        if(temp == "my_employees"):
            rows = Schedule.objects.filter(Q(lesson_date__gte=dtMin) & Q(lesson_date__lte=dtMax) & Q(professor__id=id.id))
        elif(temp=="my_students"):
            rows = Schedule.objects.filter(Q(lesson_date__gte=dtMin) & Q(lesson_date__lte=dtMax) & Q(group__id=id.group.id))
        elif(temp=="dep_employees"): 
            rows = Schedule.objects.filter(Q(lesson_date__gte=dtMin) & Q(lesson_date__lte=dtMax) & Q(subject__department=id.department)).order_by('lesson_date')
        elif(temp=="all_employees"):
            rows = Schedule.objects.filter(Q(lesson_date__gte=dtMin) & Q(lesson_date__lte=dtMax))
        else:
            return {} 
        dt = timedelta(days=1)
        res = {}
        while(dtMin <= dtMax):
            q = rows.filter(lesson_date=dtMin).order_by('lesson_time')
            if(len(q)):                
                temp = []
                for el in q:
                    temp.append(el.getStringInfo())
                res[str(dtMin.day)] = temp
            dtMin += dt
        return res  
    
    def __getName(self, nm):
        if(re.match("^[А-ЯЁа-яё-]+$", nm)):        
            temp = list(map(lambda s: s[0].upper() + s[1:].lower(), nm.split("-")))
            temp = "-".join(temp)
            return temp           
        return ""
    
    def controlData(self, dt):
        ln = len(dt)
        if(ln != 7 and ln != 6):
            return None
        data = {}
        temp = self.__getName(dt[0])
        if(temp == ""):
            return None        
        data["lastname"] = temp
        temp = self.__getName(dt[1])
        if(temp == ""):
            return None
        data["firstname"] = temp       
        if(ln == 7):
            ln = 0
            temp = self.__getName(dt[2])
            if(temp == ""):
                return None            
            data["patronymic"] = temp
        else:
            ln = 1
        try:
            temp = Extra().getDate(dt[3-ln])                
        except:
            return None
        if(temp.year < 1950 or temp > date.today()):
            return None        
        data["birthday"] = temp
        if(not re.match("^[MЖМ]$", dt[4-ln])):
            return None
        if(dt[4-ln] == "Ж"):
            data["gender"] = Genders.objects.get(index="F")
        else:
            data["gender"] = Genders.objects.get(index="M")
        temp = dt[5-ln].split("-")  
        temp = "".join(temp)
        if(not re.match("^\+[0-9]{11}$", temp)):
            return None
        data["phone"] = temp
        if(not re.match("^[0-9A-Za-z\._\-]+@[0-9A-Za-z\._\-]+\.[0-9A-Za-z\._\-]+$", dt[6-ln])):
            return None       
        data["e_mail"] = dt[6-ln]
        return data
          
    def setBlock(self, id):
        id.activ = (not id.activ)
        id.save()
        

        
        
        
        
        
        
        
        
    