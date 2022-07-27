from ..models import Students, Employees, Groups, Genders, Departments, Status_Employees
from .extra import Extra
import string
import random
from calendar import monthrange
from datetime import date




class Generate():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        LN_M = [
                    "Андреев", 
                    "Борисов", 
                    "Викторов", 
                    "Глебов", 
                    "Дмитриев", 
                    "Егоров", 
                    "Захаров", 
                    "Иванов", 
                    "Кириллов", 
                    "Леонидов", 
                    "Макаров", 
                    "Петров"]
        FN_M = [
                    "Андрей", 
                    "Борис", 
                    "Виктор", 
                    "Глеб", 
                    "Дмитрий", 
                    "Егор", 
                    "Захар", 
                    "Иван", 
                    "Кирилл", 
                    "Леонид", 
                    "Макар", 
                    "Петр"]
       
        PT_M = [
                    "Андреевич", 
                    "Борисович", 
                    "Викторович", 
                    "Глебович", 
                    "Дмитриевич", 
                    "Егорович", 
                    "Захарович", 
                    "Иванович", 
                    "Кириллович", 
                    "Леонидович", 
                    "Макарович", 
                    "Петрович"]
       
        FN_F = [
                    "Анна", 
                    "Виктория",
                    "Дарья",
                    "Елена",
                    "Зинаида",
                    "Ирина",
                    "Ксения",
                    "Мария",
                    "Надежда", 
                    "Ольга",
                    "Полина",
                    "Юлия"]
        
        self.__names = {
                        "M": {
                            "lastname": LN_M, 
                            "firstname": FN_M,
                            "patronymic": PT_M},
                        "F": {
                            "lastname": list(map(lambda s: s+"а", LN_M)), 
                            "firstname": FN_F,
                            "patronymic": list(map(lambda s: s[:-2]+"на", PT_M))}
                      }
        
        self.__gender = ["M", "F"]
        self.__year = [1970, 2000]
        self.__phone = {"EX": "+7", "COUNT": 10, "CHARS": list(map(str, range(10)))}
        self.__email = ["yandex.ru", "gmail.com", "mail.ru", "rambler.ru"]
        self.__login = {"COUNT": 32, "CHARS": string.ascii_letters + string.digits}
        
        self.__translit = {
                    "А": "a",
                    "Б": "b",
                    "В": "v",
                    "Г": "g",
                    "Д": "d",
                    "Е": "e",
                    "Ё": "yo",
                    "Ж": "zh",
                    "З": "z",
                    "И": "i",
                    "Й": "j",
                    "К": "k",
                    "Л": "l",
                    "М": "m",
                    "Н": "n",
                    "О": "o",
                    "П": "p",
                    "Р": "r",
                    "С": "s",
                    "Т": "t",
                    "У": "u",
                    "Ф": "f",
                    "Х": "h",
                    "Ц": "c",
                    "Ч": "ch",
                    "Ш": "sh",
                    "Щ": "shch",
                    "Ь": "`",
                    "Ы": "y",
                    "Ъ": "`",
                    "Э": "e",
                    "Ю": "yu",
                    "Я": "ya"} 

    def generatePersons(self):
        """Генерация работников и студентов"""
        prof = Employees.objects.all()
        stud = Students.objects.all()
        if(len(prof) + len(stud) > 0):
            return "Уже имеются {} {} и {} {}".format(
                len(prof), Extra().getStringAmountProfessors(len(prof)),
                len(stud), Extra().getStringAmountStudents(len(stud)))
        
        gr = list(Groups.objects.all())        
        for i in range(100):
            pers = self.__getPersonInfo()
            pers["group"] = random.choice(gr)           #TODO TEST
            try:
                Students.objects.create(**pers)
            except:
                pass 
        
        dp = list(Departments.objects.all())
        stL = Status_Employees.objects.get(index="leader")
        stE = Status_Employees.objects.get(index="employee")
        for i in dp:
            self.__createEmployee(i, "leader")
            for e in range(random.randint(3, 5)):
                self.__createEmployee(i, "employee")        
         
        return "Всё сделано. Проверьте."   
    
    def __createEmployee(self, dp, st):
        pers = self.__getPersonInfo()
        pers["department"] = dp
        pers["status"] = Status_Employees.objects.get(index=st)
        try:
            Employees.objects.create(**pers)
        except:
            pass
    
    def __getPersonInfo(self):
        gn = random.choice(self.__gender)
        nm = self.__names[gn]        
        res = {"gender": Genders.objects.get(index=gn)}        
        for k in nm:
            res[k] = random.choice(nm[k])        
        if(random.randint(0, 9) == 0):
            res["patronymic"] = ""
        ya = random.randint(*self.__year)
        mn = random.randint(1, 12)
        dy = random.randint(1, monthrange(ya, mn)[1])                     
        res["birthday"] = date(ya, mn, dy)        
        res["phone"] = self.__phone["EX"]
        for n in range(self.__phone["COUNT"]):
            res["phone"] += random.choice(self.__phone["CHARS"])
        em = list(map(lambda s: self.__translit[s.upper()], res["lastname"]))
        res["e_mail"] = "{}@{}".format("".join(em), random.choice(self.__email))
        res["login"] = ""
        for n in range(self.__login["COUNT"]):
            res["login"] += random.choice(self.__login["CHARS"])
        return res    
            
            
            
            
            
            
            
            
            
            
            
            
            