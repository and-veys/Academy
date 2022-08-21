from ..models import Employees, Students
from .extra import Extra
from django.conf import settings

class Persons():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        self.__person = {"employees": Employees, "students": Students}
        
    def createStructure(self, id, tp): 
        try:
            row = self.__getPerson(id, tp)
        except:
            return {"OK": False} 
        return row.getPersonalInfo()      
    
    def loadPhoto(self, data, id, tp):
        try:
            row = self.__getPerson(id, tp)
        except:
            return "\nОшибка чтения записи на сервере."
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
        return "/personal/{}/{}".format(tp, id)
            
    def loadInfo(self, data, id, tp):
        try:
            row = self.__getPerson(id, tp)
        except:
            return "\nОшибка чтения записи на сервере."        
        if("login" in data):            #TODO
            if(self.isAdministrator(data["login"]) or self.getPerson(data["login"])):
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
        return "/personal/{}/{}".format(tp, id)
    
    def __getPerson(self, id, tp):
        return self.__person[tp].objects.get(id=id)
    
    def getPerson(self, login):
        for k, cl in self.__person.items():       
            try:
                row = cl.objects.get(login=login)
                return {"row": row, "tp": k}
            except:
                pass
        return {}    
        
    def getRegistration(self, data):        
        row = self.getPerson(data["login"])
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
        return self.__getPerson(id, tp).getPersonalInfo()

    def getEvent(self, id, tp, rg):             #TODO
        return {"1": ["One", "Two", "Three"], "13": ["Five"]}
        
        
        
        
        
        
        
        
        
        
        
        
        
    