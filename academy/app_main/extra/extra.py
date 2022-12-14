from datetime import datetime, date
from django.shortcuts import render

import functools
from django.db import connection, reset_queries
import time

class Extra:
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
            cls.__inst.__init()
        return cls.__inst 
    def __init(self):
        self.__amount_months = ["месяц", "месяца", "месяцев"]
        self.__amount_professors = ["сотрудник", "сотрудника", "сотрудников"]
        self.__amount_students = ["студент", "студента", "студентов"]
        self.__amount_lessons = ["занятие", "занятия", "занятий"]
        self.__amount_notes = ["запись", "записи", "записей"]
        self.__amount_marks = ["оценка", "оценки", "оценок"]
    
    def getDataObject(self, db, id):        
        try:
            return db.objects.get(id=id)   
        except:
            return None    
        
    def getStringAmountMonths(self, m):
        return self.__getStringAmount(m, self.__amount_months)
    
    def getStringAmountProfessors(self, m):
        return self.__getStringAmount(m, self.__amount_professors)
    
    def getStringAmountStudents(self, m):
        return self.__getStringAmount(m, self.__amount_students)  
    
    def getStringAmountLessons(self, m):
        return self.__getStringAmount(m, self.__amount_lessons)
    
    def getStringAmountNotes(self, m):
        return self.__getStringAmount(m, self.__amount_notes)
    
    def getStringAmountMarks(self, m):
        return self.__getStringAmount(m, self.__amount_marks)
    
    def getStringAmount(self, m, ar):
        return self.__getStringAmount(m, ar)
    
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
    
    def getStringTimeShort(self, dt=None):
        """Форматный вывод времени""" 
        if(dt == None):
            dt = datetime.now()
        return dt.strftime("%H:%M")
    
    
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

    def getRoundString(self, n, k): 
        if(n==None):
            n=0
        return format(round(n, k), ".{}f".format(k))
        
    def paint(self, *arg):
        print("*"*88)
        for el in arg:
            print(el)
        print("*"*88)
        
    def getPath(self, *args):        
        return "/" + "/".join(map(str, args))
    
    def getSession(self, request):
        try:
            return request.session[request.COOKIES["login"]] 
        except:
            return {}

    def render(self, *args):
        res = self.getSession(args[0])
        if(res): 
            res["id"] = str(res["id"])
            if(len(args) == 2):
                return render(*args, {"title_person": res})
            else:
                args[2]["title_person"] = res       
                
        return render(*args) 
        
    def setAnchor(self, bk, *an):
        return "{}#{}".format(bk, "_".join(map(str, an)))
     
    def query_debugger(self, func):    
        """Функция расчета времени и обращений к базе данных. С просторов интернета"""
        @functools.wraps(func)
        def inner_func(*args, **kwargs):
            reset_queries()            
            start_queries = len(connection.queries)
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            end_queries = len(connection.queries)
            print(f"Function : {func.__name__}")
            print(f"Number of Queries : {end_queries - start_queries}")
            print(f"Finished in : {(end - start):.2f}s")
            return result
        return inner_func   
    
    def getDate(self, dt):
        q = list(map(int, dt.split(".")))
        q.reverse()
        return date(*q)   
        