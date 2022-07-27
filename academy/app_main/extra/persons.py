from ..models import Employees, Students
from django.conf import settings

class Persons():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        self.person = {"employees": Employees, "students": Students}
        
        
    def createStructure(self, id, tp): 
        try:
            row = self.person[tp].objects.get(id=id)
        except:
            return {"OK": False}
        return row.getPersonalInfo()      
    
    def loadPhoto(self, data, id, tp):
        try:
            row = self.person[tp].objects.get(id=id)
        except:
            return "/nОшибка чтения записи на сервере."
        path = "{}/persons/{}.{}".format(settings.MEDIA_ROOT, row.login, data["type"])
        try:
            file = open(path, "wb")
        except:
            return "/nОшибка записи файла на сервере."
        file.write(bytes(data["pic"]))
        file.flush()
        file.close()        
        row.picture = path
        try:
            row.save()
        except:
            return "/nОшибка записи базы данных на сервере."
        return "/personal/{}/{}".format(tp, id)
            
    def loadInfo(self, data, id, tp):
        try:
            row = self.person[tp].objects.get(id=id)
        except:
            return "/nОшибка чтения записи на сервере."        
        if("login" in data):
            try:
                self.person[tp].objects.get(login=data["login"]) 
                return "/nСовпадение логина и пароля в базе данных."
            except:
                row.login = data["login"]
        if("phone" in data):
            row.phone = data["phone"]   
        if("e_mail" in data):
            row.e_mail = data["e_mail"]
        try:
            row.save()
        except:
            return "/nОшибка записи базы данных на сервере."
        return "/personal/{}/{}".format(tp, id)