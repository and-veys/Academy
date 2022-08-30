from datetime import date
from calendar import monthcalendar
from django.db.models import Q
from ..models import NamesWeekDays, NamesMonths, WeekEnds
from .extra import Extra
import json
class Calendar():
    __inst = None 
    def __new__(cls):
        if(cls.__inst == None): 
            cls.__inst = super().__new__(cls)
        return cls.__inst 

    def getMonthData(self, dt):  
        temp = str(dt)
        if(len(temp) != 6):
            return {}
        y = int(temp[:4])
        m = int(temp[4:])
        if(y < 1900 or y > 2100 or m < 1 or m > 12):
            return {}
        d = monthcalendar(y, m)
        d_range = self.__getMonthRange(y, m, d)
        res = {
            "year": y,
            "month": m,
            "days": d,
            "month_info": NamesMonths.objects.get(index=m).getInfo(), 
            "weeks": list(map(lambda s: str(date(y, m, max(s)).isocalendar().week), d)),
            "daysofweek": list(map(lambda s: s.getInfo(), NamesWeekDays.objects.all().order_by("index"))),
            "weekends": self.__getWeekends(d, d_range),
            "today": self.__getToday(d_range),
            "range": d_range
        }
        return res
        
    def getContent(self, dt):  
        arr = []
        for row in dt["days"]:
            r = []
            for el in row: 
                temp = ""
                cl = ""
                if(el):
                    ind = str(el)
                    temp = {
                        "day": "{}, {}".format(
                                    Extra().getStringData(date(dt["year"], dt["month"], el)),
                                    dt["daysofweek"][len(r)][0]),
                        "weekend": ""}                    
                    cl = ["calendar_date"]
                    if(ind in dt["weekends"]):
                        cl.append("calendar_weekend")
                        temp["weekend"] = dt["weekends"][ind]                        
                    if(el == dt["today"]):
                        cl.append("calendar_today") 
                        temp["day"] = "Сегодня " + temp["day"]; 
                    if(ind in dt["events"]):
                        cl.append("calendar_events") 
                        temp["events"] = dt["events"][ind]           #TODO   
                    temp = json.dumps(temp)  
                    cl = " ".join(cl)
                r.append([str(el), cl, temp])
            arr.append(r)    
                
   
            

        
        #TODO make days-line
        return {
            "year": str(dt["year"]),
            "month": [str(dt["month"]), dt["month_info"][0].upper()],
            "days": zip(dt["weeks"], arr),
            "daysofweek": [""] + list(map(lambda s: s[1].lower(), dt["daysofweek"])),
            "back": dt["back"]}
    
    def __getWeekends(self, d, rg):
        res = {}
        for el in d:
            if(el[5] != 0):
                res[str(el[5])] = "Выходной"
            if(el[6] != 0):   
                res[str(el[6])] = "Выходной"
        dtMin, dtMax = rg  
        rows = WeekEnds.objects.filter(~Q(delay=None) & Q(delay__gte=dtMin) & Q(delay__lte=dtMax))
        for el in rows:
            del res[str(el.delay.day)]           
        rows = WeekEnds.objects.filter(Q(date__gte=dtMin) & Q(date__lte=dtMax))        
        for el in rows:
            res[str(el.date.day)] = el.getNameDay();
        return res;
    
    def __getMonthRange(self, y, m, d):
        dtMin = date(y, m, 1)
        dtMax = date(y, m, max(d[len(d)-1])) 
        return dtMin, dtMax
        
    def __getToday(self, rg):
        dt = date.today()
        dtMin, dtMax = rg
        if(dt >= dtMin and dt <= dtMax):
            return dt.day;
        return 0; 