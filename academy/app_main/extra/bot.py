from ..models import SunBot, Employees, Students
from .extra import Extra
from .persons import Persons
from datetime import date, timedelta

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
                "help": [self.__help, "Справка"]
        }     
    def message(self, dt):         
        data = self.__split(dt) 
        data = self.__activity[data["command"]][0](data)
        if(data):
            return data
        return "Зарегистрируйтесь, пожалуйста.\nКоманда /registration 'логин' 'пароль'"  
        
    def __getRow(self, data):
        try:
            return SunBot.objects.get(bot_id=data["id"])
        except:
            return None
        
    def __split(self, dt):
        temp = list(map(lambda s: s.strip(), dt["command"].split(" ")))    
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
        
    def __registration(self, data):       #/registration Andrey 123456
        if(len(data["args"]) != 2):
            return "Аргументы команды: 'логин' и 'пароль' через пробел."
        login = self.__encodeInfo(*data["args"])
        res = {"bot_id": data["id"], "employees": None, "students": None}
        row = Persons().getPersonFromLogin(login)
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
            res += "\n/{} - {}".format(k, el[1])
        return res
    
    def __encodeInfo(self, lg, pw):
        a = [lg[:5], lg[5:], pw[:3], pw[3:]]
        return a[0]+a[3]+a[2]+a[1]
        
    def __today(self, data):
        return self.__getSchedule(data, date.today(), "Сегодня")
        
        
    def __tomorrow(self, data):
        dt = timedelta(days=1)
        return self.__getSchedule(data, date.today()+dt, "Завтра")
        
    def __date(self, data):
        dt = None
        if(len(data["args"]) == 1):
            try:
                dt = self.__getDate(data["args"][0])
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
                row = list(map(lambda s: [s[0], s[1], ""], row))
            for el in row:
                res += "\n<b>\u2713 {}</b> {} <i>{}</i>".format(*el)
            return res
        return ""
    
    def __getDate(self, dt):
        q = list(map(int, dt.split(".")))
        q.reverse()
        return date(*q)
        