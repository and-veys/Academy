
from .persons import Extra
from .persons import Persons
from .groups import Groups
from .subjects import Subjects
from .students import Students
from .schedule import Schedule


class Access():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 


    def convertData(self, fun):
        """Конвертирование и проверка параметров"""
        def wrapper(request, **kwargs):
            if("person" in kwargs):
                arr = {"id": Persons(), "grp": Groups(), "sbj": Subjects(), "std": Students(), "sch": Schedule()}
            else:
                arr = {}
            res = True
            for el in arr:
                if(el in kwargs):   
                    temp = arr[el].getData(kwargs[el], kwargs["person"])
                    if(temp):
                        kwargs[el] = temp
                    else:
                        res = False
                        break
            if(res):
                for el in kwargs:
                    if((el in arr) and (not arr[el].control(kwargs))):
                        res = False          
                        break
            if(res):   
                return fun(request, **kwargs)
            return Extra().render(request, "error_access.html") 
        return wrapper
        
    def isAccess(self, fun):
        """Доступ по id, person или администратору"""
        def wrapper(request, **kwargs):
            if(len(kwargs) == 1):
                return fun(request, **kwargs)
            session = Extra().getSession(request)
            if(session):
                if(session["id"] == -1 or (kwargs["person"] == session["tp"] and kwargs["id"].id == session["id"])):
                    return fun(request, **kwargs)
            return Extra().render(request, "error_access.html") 
        return wrapper

    def isAdministrator(self, fun):
        """Доступ только администратору"""
        def wrapper(request):
            session = Extra().getSession(request)
            if(session):
                if(session["id"] == -1):
                    return fun(request)
            return Extra().render(request, "error_access.html") 
        return wrapper

    def isEmployee(self, fun):
        """Доступ только работникам"""
        def wrapper(request, **kwargs):
            if(kwargs["person"] == "employees"):
                return fun(request, **kwargs)
            return Extra().render(request, "error_access.html") 
        return wrapper


    def isLeader(self, fun):
        """Доступ только начальникам"""
        def wrapper(request, **kwargs):
            if(kwargs["id"].status.index == "leader"):
                return fun(request, **kwargs)
            return Extra().render(request, "error_access.html") 
        return wrapper

    def isDIR(self, fun):
        """Доступ только руководству"""
        def wrapper(request, **kwargs):
            if(kwargs["id"].department.status.index == "DIR"):            #TODO     
                return fun(request, **kwargs)
            return Extra().render(request, "error_access.html") 
        return wrapper

    def isLeaderOrDIR(self, fun):
        """Доступ только начальникам или руководству"""
        def wrapper(request, **kwargs):
            if(kwargs["id"].status.index == "leader" or kwargs["id"].department.status.index == "DIR"):
                return fun(request, **kwargs)
            return Extra().render(request, "error_access.html") 
        return wrapper