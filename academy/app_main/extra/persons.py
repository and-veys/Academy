from ..models import Employees, Students, Schedule
from .extra import Extra
from django.conf import settings
from django.db.models import Q

class Persons():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        self.__person = {"employees": Employees, "students": Students}
        self.__event = {
            "my_employees":None,
            "my_students":None
            }
        
    def createStructure(self, id, tp): 
        if(type(id) == type(1)):
            id = self.getPersonFromId(id, tp)        
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
        if("login" in data):            #TODO
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
        for k, cl in self.__person.items():       
            try:
                row = cl.objects.get(login=login)
                return {"row": row, "tp": k}
            except:
                pass
        return {}    
    
    
    def getPersonFromId(self, id, tp):
        try:
            return self.__person[tp].objects.get(id=id)
        except:
            pass
        return {}
       
    def getRegistration(self, data):        
        row = self.getPersonFromLogin(data["login"])
        print("+"*88)
        print(data["login"])
        print(row)
        if(row):
            return {
                "login": data["login"], 
                "session": {"id": row["row"].id, "tp": row["tp"]},
                "age": Extra().getRestDay(),
                "path": "/personal/{}/{}".format(row["tp"], row["row"].id),
                "OK": True
            } 
        if(self.isAdministrator(data["login"])):
            return {
                "login": data["login"], 
                "session": {"id": -1, "tp": "root"},
                "age": Extra().getRestDay(),
                "path": "\nВы вошли как Администратор.",
                "OK": True
            }   
        return {"path": "\nОшибочные логин и пароль.", "OK": False}
            
    def isAdministrator(self, login): 
        return (login == settings.ROOT_USER)
        
    def getSession(self, request):
        try:
            return request.session[request.COOKIES["login"]] 
        except:
            return {}
            
    def getWork(self, id, tp):
        return id.getPersonalInfo()

    def getEvent(self, id, tp, rg, ev):             #TODO
        dtMin, dtMax = rg   
        print("*"*88)
        a = 1
        print(type("")==type(a))
        
        
        #rows = WeekEnds.objects.filter(~Q(delay=None) & Q(delay__gte=dtMin) & Q(delay__lte=dtMax))
        
    
    
    
    
    
        return {"1": ["One", "Two", "Three"], "13": ["Five"]}
        
        
        
        
        
        
        
        
        
        
        
        
        
    