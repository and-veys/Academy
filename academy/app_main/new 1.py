from django.db import models
from .extra.extra import Extra
from datetime import timedelta, date

  

   

                   
       
 

 
 
  

class NamesInfo(models.Model):
    """Общий класс-родитель для стандартных наименований"""
    name = models.CharField('Полное название', max_length = 24, unique=True)
    index = models.IntegerField('Индекс', unique=True)    
    shortName = models.CharField('Короткое название', max_length = 4, unique=True)
    
    class Meta:        
        abstract = True
        
    def __str__(self):
        return "{}: {} ({})".format(str(self.index), str(self.name), str(self.shortName)) 
    
    def getInfo(self):
        return (self.name, self.shortName)

class NamesWeekDays(NamesInfo): 
    """Таблица дней недели"""
    class Meta:
        ordering = ['index']  
        verbose_name = "День недели"                     
        verbose_name_plural = "Дни недели" 
        db_table = "amv_names_weekdays"   
        
        
class NamesMonths(NamesInfo):
    """Таблица месяцев"""
    class Meta:
        ordering = ['index']  
        verbose_name = "Месяц"                     
        verbose_name_plural = "Месяцы" 
        db_table = "amv_names_month"

class WeekEnds(models.Model):
    """Таблица праздничных дней с их переносами"""
    date = models.DateField("Дата", unique=True)
    name = models.CharField('Название', max_length = 64, default="Выходной") 
    delay = models.DateField("Дата", unique=True, null=True, blank=True)
    class Meta:
        ordering = ['date']  
        verbose_name = "Выходной"                     
        verbose_name_plural = "Выходные"
        db_table = "amv_weekends"
        
    def __str__(self):
        return "{} - {}".format(Extra().getStringData(self.date), self.getNameDay())
    
    def getNameDay(self):
        return ("{}, перенос с {}".format(self.name, Extra().getStringData(self.delay)) if self.delay else self.name)
        
class NamesMarks(NamesInfo):
    """Таблица наименований оценок"""
    class Meta:
        ordering = ['index']  
        verbose_name = "Оценка"                     
        verbose_name_plural = "Оценки" 
        db_table = "amv_names_mark"



class Marks(models.Model):
    """Таблица оценок студентов"""
    lesson = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name="Урок")
    student = models.ForeignKey(Students, on_delete=models.CASCADE, verbose_name="Студент")
    mark = models.ForeignKey(NamesMarks, on_delete=models.CASCADE, verbose_name="Оценка")
    class Meta:
        ordering = ['lesson']  
        verbose_name = "Оценка студента"                     
        verbose_name_plural = "Оценки студентов" 
        db_table = "amv_marks"
        indexes = [models.Index(fields=['lesson']), models.Index(fields=['student'])]
