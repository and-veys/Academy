from datetime import datetime 
        
class Extra:
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        self.__amount_months = ["месяц", "месяца", "месяцев"]
        self.__amount_professors = ["профессор", "профессора", "профессоров"]
        self.__amount_students = ["студент", "студента", "студентов"]
        
    def getStringAmountMonths(self, m):
        return self.__getStringAmount(m, self.__amount_months)
    
    def getStringAmountProfessors(self, m):
        return self.__getStringAmount(m, self.__amount_professors)
    
    def getStringAmountStudents(self, m):
        return self.__getStringAmount(m, self.__amount_students)  
    
    def __getStringAmount(self, m, arr):
        """Добавляет правильные окончания к существительным от их количества"""
        a = m%100
        if(a >= 11 and a <=14):
            return arr[2]
        a = m%10       
        if(a == 0 or (a >= 5 and a <= 9)):
            return arr[2]
        if(a == 1):
            return arr[0]
        return arr[1]  
        
    def getStringData(self, dt=None):
        """Форматный вывод даты""" 
        if(dt == None):
            dt = datetime.now()
        return dt.strftime("%d.%m.%Y")
    
    def getStringTime(self, dt=None):
        """Форматный вывод времени""" 
        if(dt == None):
            dt = datetime.now()
        return dt.strftime("%H:%M:%S")
    
    
    
    def getStringPhone(self, ph):
        return self.__getStringPhone(ph, " (XXX) XXX-XX-XX")
    def getStringPhoneJS(self, ph):
        return self.__getStringPhone(ph, "-XXX-XXX-XX-XX")
    
    def __getStringPhone(self, ph, m):
        """Форматный вывод номера телефона"""
        if(len(ph) < 12):
            return ph
        ind = -10;
        mask = list(m)  
        temp = ph[ind:]
        for i in range(len(mask)): 
            if(mask[i] == "X"):
                mask[i] = temp[0]
                temp = temp[1:]
        return ph[:ind] + "".join(mask)
    
    def getRestDay(self):
        dtN = datetime.now()
        dtT = datetime(dtN.year, dtN.month, dtN.day)   
        return (24*60*60 - (dtN - dtT).seconds)  

