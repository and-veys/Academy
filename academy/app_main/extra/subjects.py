from ..models import Subjects as db, Course_Subject
from .extra import Extra

class Subjects():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst
        
    def getData(self, id, person):  
        return Extra().getDataObject(db, id) 
    
    def control(self, kwargs):
        try:
            cs = Course_Subject.objects.filter(course=kwargs["grp"].course, subject=kwargs["sbj"])
        except:
            return False
        return True