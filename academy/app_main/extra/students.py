from ..models import Students as db
from .extra import Extra

class Students():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst
        
    def getData(self, id, person): 
        el = Extra().getDataObject(db, id)
        if(el and el.activ):
            return el
        return None  
        
    def control(self, kwargs):
        return (kwargs["std"].group == kwargs["grp"])