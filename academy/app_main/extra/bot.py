from ..models import SunBot, ApplicationBot, Employees, Students, Status_Employees
from .extra import Extra
from .persons import Persons
from .generate import Generate
from datetime import date, timedelta
import json



class Bot():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    
    def __init(self):
        self.__activity = {                
                "start": [self.__start, "Приветствие"],
                "registration": [self.__registration, "Регистрация"],
                "delete": [self.__delete, "Выход из регистрации"],                
                "now": [self.__now, "Дата и время"],               #TODO сделать
                "today": [self.__today, "Расписание на сегодня"],
                "tomorrow": [self.__tomorrow, "Расписание на завтра"],
                "date": [self.__date, "Расписание на дату"],
                "employee": [self.__application, "Заявка на работу"],
                "student": [self.__application, "Заявка на учебу"],
                "help": [self.__help, "Справка"],
                "check": [self.__check, ""]
        }     
    def message(self, dt):         
        data = self.__split(dt) 
        data = self.__activity[data["command"]][0](data)
        if(data):
            return data
        return "{}\n{}\n{}".format(
                    "Зарегистрируйтесь, пожалуйста, -\nкоманда /registration.",
                    "Или подайте заявку на учебу - \nкоманда /student.",
                    "Или работу - \nкоманда /employee;",
                    )
        
    def __getRow(self, data):
        try:
            return SunBot.objects.get(bot_id=data["id"])
        except:
            return None
        
    def __split(self, dt):        
        temp = list(map(lambda s: s.strip(), dt["command"].split("\n")))
        temp = " ".join(temp)
        temp = list(map(lambda s: s.strip(), temp.split(" ")))    
        return {
            "command": temp[0][1:],
            "args": temp[1:],
            "id": dt["id"]
        }   
    
    def __start(self, data):
        row = self.__getRow(data)
        if(row):
            return "Здравствуйте,\n{}.\nПомощь по боту - команда /help.".format(row.getPerson()[1].getFullName())
        return ""
        
    def __getPromp(self, *args):
        res = []
        
        for el in args:
            if(type(el).__name__ == 'str'):
                res.append("<b>{}</b>".format(el))
            else:
                res.append("<b>{}</b> <i>({})</i>".format(*el))
    
    
        return "Аргументы команды через пробел или enter:\n" + "\n".join(res)
        
    def __registration(self, data):       #/registration Andrey 123456
        if(len(data["args"]) != 2):
            return self.__getPromp("Логин", "Пароль")
        login = Generate().encodeInfo(*data["args"])
        res = {"bot_id": data["id"], "employees": None, "students": None}
        row = Persons().getPersonFromLogin(login)        
        if(row["row"].activ == False):
            return "Вам отказано в доступе."  
        if(row):
            res[row["tp"]] = row["row"]
        else:
            return "Ошибочные логин и пароль."
        sb = self.__getRow(data)      
        if(sb):
            sb.bot_id = res["bot_id"]
            sb.employees = res["employees"]
            sb.students = res["students"]
        else:
            sb = SunBot(**res)   
        try:
            sb.save()
        except:
            return "Ошибка записи в базу данных сервера." 
        return "Ваша регистрация:\n{}".format(row["row"].getFullName())

 
    def __delete(self, data):
        sb = self.__getRow(data)
        if(sb):
            sb.delete()
            return "Ваша регистрация отменена."
        return ""
    
    def __now(self, data):          #TODO
        sb = self.__getRow(data)
        if(sb):
            return "Сегодня: {}\nСейчас: {}.".format(Extra().getStringData(), Extra().getStringTime())
        return ""
        
    def __help(self, data):
        res = "Доступные команды бота:"
        for k, el in self.__activity.items():
            if(el[1]):
                res += "\n/{} - {}".format(k, el[1])
        return res
    

        
    def __today(self, data):
        return self.__getSchedule(data, date.today(), "Сегодня")
        
        
    def __tomorrow(self, data):
        dt = timedelta(days=1)
        return self.__getSchedule(data, date.today()+dt, "Завтра")
        
    def __date(self, data):
        dt = None
        if(len(data["args"]) == 1):
            try:
                dt = Extra().getDate(data["args"][0])
            except:
                pass
        if(dt == None):
            return "Аргумент команды - дата в формате ДД.ММ.ГГГГ."
        return self.__getSchedule(data, dt)
    
    def __getSchedule(self, data, dt, q=""):
        row = self.__getRow(data)        
        if(row):
            str_dt = (q if q else Extra().getStringData(dt))
            sb = row.getPerson()            
            row = Persons().getEvent(sb[1], sb[0], (dt, dt), "my")
            if(len(row) == 0):
                return "{} у вас нет занятий".format(str_dt)            
            row = row[str(dt.day)]
            res = "Ваше расписание на {}:".format(str_dt.lower())
            if(sb[0] == "employees"):
                row = list(map(lambda s: [s[0], s[2], s[1]], row))
            else:
                row = list(map(lambda s: [s[0], s[2], s[3]], row))
            for el in row:
                res += "\n<b>\u2713 {}</b> {} <i>{}</i>".format(*el)
            return res
        return ""
    

        
        
    def __application(self, dt):
        data = Persons().controlData(dt["args"])
        if(not data):
            err = [
            ["Фамилия", "кириллицей"],
            ["Имя", "кирилицей"],
            ["Отчество", "кирилицей, необязательно"],
            ["Дата рождения", "в формате ДД.ММ.ГГГГ"],
            ["Пол", "М или Ж"],            
            ["Телефон", "в формате +X-XXX-XXX-XX-XX"],
            "Эл. почта"]
            return self.__getPromp(*err)             
        data["person"] = dt["command"]
        temp = Generate().generatePassword(8)       
        data["login"] = Generate().encodeInfo(*temp)
        data["bot_id"] = int(dt["id"])  
        try:
            temp = ApplicationBot.objects.get(bot_id=data["bot_id"])                
            if(temp.activ):
                return "Вы уже зарегистрировались.\nЖдите ответа." 
            return "Вы заблокированы."
        except:
            pass     
        try:
            ApplicationBot.objects.create(**data)
        except:
            Extra().paint(data)
            return "Ошибка записи в базу данных сервера."     
        return "Ваша заявка зарегистрирована.\nЖдите ответа."
      
    def __check(self, dt):
        rows = ApplicationBot.objects.filter(activ=True, action__gt=0) 
        keys = ["_state", "department_id", "group_id", "action", "person", "bot_id"]
        res = {}
        for el in rows:
            res[el.bot_id] = el.getMessage() 
            if(el.action == 1):
                el.activ = False
                el.save()
            else:
                if(el.action == 3):
                    temp = el.__dict__.copy()
                    for q in keys:
                        del temp[q]
                    if(el.person == "employee"):
                        db = Employees
                        temp["department"] = el.department
                        temp["status"]= Status_Employees.objects.get(index="employee")
                    else:
                        db = Students
                        temp["group"] = el.group
                    psw = []
                    while(True):
                        psw = Generate().generatePassword(8)                     
                        temp["login"] = Generate().encodeInfo(*psw)
                        try:
                            db.objects.get(login=temp["login"])
                        except:
                            break         
                    db.objects.create(**temp)
                    res[el.bot_id] += "\nВаш логин: <b>{}</b>\nВаш пароль: <b>{}</b>".format(*psw)
                el.delete()
        return json.dumps(res)    
        
        
        