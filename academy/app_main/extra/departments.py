from ..models import Departments as dp, Employees as em, Status_Employees as st


class Departments():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 
    
    def createStructure(self):
        res = {}
        rows = dp.objects.all().order_by("status__sort_weight", "name")
        stat = st.objects.all().order_by("sort_weight")   
        for el in rows:
            temp = em.objects.filter(department=el.id)
            pl = {}
            for q in stat:
                pers = temp.filter(status=q.id)
                if(len(pers)):                
                    pl[pers[0].getStatusAlias(True)] = dict(
                                map(lambda s: [str(s.id), s.getShotName()], pers)) 
            res[el.name] = pl
        return res
        