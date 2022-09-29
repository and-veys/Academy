from .extra import Extra
import string
import random
from calendar import monthrange
from datetime import date
from django.conf import settings
import pickle
from django.db.models import Q

from ..models import    Genders, \
                        Status_Departments, \
                        Status_Employees, \
                        Status_Aliases, \
                        Departments, \
                        Courses, \
                        Subjects, \
                        Course_Subject, \
                        Groups, \
                        Students, \
                        Employees, \
                        Schedule, \
                        LessonTimes, \
                        NamesWeekDays, \
                        NamesMonths, \
                        WeekEnds, \
                        NamesMarks, \
                        Marks, \
                        ApplicationBot


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
        self.__login = {"COUNT": 16, "CHARS": string.ascii_letters + string.digits}
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
        self.__classes = [
            Genders,
            Status_Departments,
            Status_Employees,
            Status_Aliases,
            Departments,
            Courses,
            Subjects,
            Course_Subject,
            Groups,
            Students,
            Employees,
            LessonTimes,
            Schedule, 
            NamesWeekDays, 
            NamesMonths, 
            WeekEnds, 
            NamesMarks,
            Marks,
            ApplicationBot

        ]
        self.__ABC = list(self.__translit.keys())


    def generateStudents(self):
        """Генерация студентов"""
        stud = Students.objects.all()
        if(len(stud)):
            return "Студенты: уже есть {} {} <br />".format(len(stud), Extra().getStringAmountStudents(len(stud)))
        gr = list(Groups.objects.all())  
        count = 0
        for i in range(100):
            pers = self.__getPersonInfo()
            pers["group"] = random.choice(gr)           #TODO TEST
            try:
                Students.objects.create(**pers)
                count += 1
            except:
                pass    
        return "Студенты: создано {} {} <br />".format(count, Extra().getStringAmountStudents(count))

    def generateEmployees(self):
        """Генерация работников"""
        emp = Employees.objects.all()
        if(len(emp)):
            return "Сотрудники: уже есть {} {} <br />".format(len(emp), Extra().getStringAmountProfessors(len(emp)))
        dp = list(Departments.objects.all())
        count = 0
        for i in dp:
            while(self.__createEmployee(i, "leader") == 0):
                pass
            count += 1
            for e in range(random.randint(3, 6)):
                count += self.__createEmployee(i, "employee") 
        return "Сотрудники: создано {} {} <br />".format(count, Extra().getStringAmountProfessors(count))
    
    def __createEmployee(self, dp, st):
        pers = self.__getPersonInfo()
        pers["department"] = dp
        pers["status"] = Status_Employees.objects.get(index=st)
        try:
            Employees.objects.create(**pers)
            return 1
        except:
            return 0
        
    
    
    def encodeInfo(self, lg, pw):
        a = [lg[:5], lg[5:], pw[:3], pw[3:]]
        return a[0]+a[3]+a[2]+a[1]
    
    def generatePassword(self, kol):
        res = ["", ""]
        for q in range(len(res)):
            for n in range(kol):
                res[q] += random.choice(self.__login["CHARS"])
        return res   
    
    
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
        
        temp = self.generatePassword(self.__login["COUNT"])       
        res["login"] = self.encodeInfo(*temp)
        return res   
    

                
    def serialize(self):
        res = ""
        for el in self.__classes:
            res += self.__save(el)
        return res   
            
    def __save(self, cl):
        try:
            file = open("{}/{}.dat".format(settings.DATA_URL, cl.__name__), "wb")
        except:
            return "{}: ошибка записи в файл <br />".format(cl.__name__)
        rows = cl.objects.all().values()
        for el in rows:
            pickle.dump(el, file)
        return "{}: сохранено {} {} <br />".format(cl.__name__, len(rows), Extra().getStringAmountNotes(len(rows)))
            
    def loaddata(self):
        res = ""
        for el in self.__classes:
            res += self.__load(el)
        return res
            
    def __load(self, cl):
        rows = cl.objects.all()
        if(len(rows)):
            return "{}: уже есть {} {} <br />".format(cl.__name__, len(rows), Extra().getStringAmountNotes(len(rows))) 
        try:
            file = open("{}/{}.dat".format(settings.DATA_URL, cl.__name__), "rb")
        except:
            return "{}: ошибка чтения файла <br />".format(cl.__name__)
        count = 0
        while(True):
            try:
                data = pickle.load(file)
            except:
                break;
            q = cl(**data)
            q.save(True)
            count += 1
        return "{}: создано {} {} <br />".format(cl.__name__, count, Extra().getStringAmountNotes(count))     
            
    def generateMarks(self):
        kol = 0
        les = 0
        dt = date.today()
        rows = Schedule.objects.filter(~Q(lesson_date=None) & Q(lesson_date__lte=dt))
        for el in rows:
            if(len(Marks.objects.filter(lesson=el))):
                continue
            st = Students.objects.filter(group=el.group, activ=True)
            les += 1
            for w in st:                
                if(random.randint(0, 1)==0):
                    kol += 1
                    data = {"lesson": el, "student":w, "mark": NamesMarks.objects.get(index=random.randint(2, 5))}
                    Marks.objects.create(**data)                   
        return "Оценки: добавлено {} {} в {} {} <br />".format(
                            kol, Extra().getStringAmountMarks(kol),
                            les, Extra().getStringAmount(les, ["уроке", "уроках", "уроках"]))              
   
    def createStructure(self, person, abc, full=False):
        ar = list(map(lambda s: [s, self.__ABC.index(s)], self.__ABC))
        
        db = {"employees": Employees, "students": Students}
        try:
            ch = ar[abc]
            db = db[person]
        except:
            return None
        res = []
        k=11;
        while(ar):
            res.append(ar[0:k])
            ar = ar[k:]
        
        if(full):
            data = db.objects.filter(Q(lastname__startswith=ch[0])).order_by('lastname', 'firstname', "patronymic")
        else:
            data = db.objects.filter(Q(lastname__startswith=ch[0]) & Q(activ=True)).order_by('lastname', 'firstname', "patronymic")
        
        data = dict(map(lambda s: (s.id, s.getPersonalInfo()), data))
        return {
            "abc": res,
            "current": person,
            "currentABC": ch[1],
            "type": {"employees": "Сотрудники", "students": "Студенты"},
            "data": data
        }        
            
            