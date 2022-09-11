from ..models import Employees, Students, Schedule
from .extra import Extra
from django.conf import settings
from django.db.models import Q
from datetime import timedelta

class Persons():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        self.__person = {"employees": Employees, "students": Students}
    
    def getData(self, id, person):  
        return Extra().getDataObject(self.__person[person], id)

    def control(self, kwargs):
        return (kwargs["id"].getType() == kwargs["person"])     
    
    
    
    
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
    
    

       
    def getRegistration(self, data):        
        row = self.getPersonFromLogin(data["login"])
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

    def getEvent(self, id, tp, rg, ev):             #TODO Test         
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
        

        
        
        
        
        
        
        
        
        
        
        
        
    