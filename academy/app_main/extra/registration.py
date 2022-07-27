from ..models import Students, Employees

class Registration:
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        self.__href = {}
        self.__href["dean"] = {
                    "class": Deans,
                    "href": []}     #TODO допустимые пути
        self.__href["professor"] = {
                    "class": Professors,
                    "href": []}     #TODO допустимые пути
        self.__href["student"] = {
                    "class": Students,
                    "href": []}     #TODO допустимые пути
                    
    def getSession(self, request):
        
        pass
        
 