from django.db import models
from .extra.extra import Extra
from datetime import timedelta, date

class Genders(models.Model):
    """Таблица полов"""
    name = models.CharField('Пол', max_length = 16, unique=True)
    index = models.CharField('Индекс', max_length = 3, unique=True)
    class Meta: 
        ordering = ['name']  
        verbose_name = "Пол"                     
        verbose_name_plural = "Пол"
        db_table = "amv_genders"        
    def __str__(self):
        return "{} ({})".format(self.name, self.index)

        
class Status_Departments(models.Model):
    """Таблица статуса отдела"""
    name = models.CharField('Статус', max_length = 16, unique=True)
    index = models.CharField('Индекс', max_length = 3, unique=True)
    sort_weight = models.IntegerField('Вес сортировки')
    class Meta: 
        ordering = ['name']  
        verbose_name = "Статус отдела"                     
        verbose_name_plural = "Статусы отделов"
        db_table = "amv_status_departments"        
    def __str__(self):
        return "{} ({})".format(self.name, self.index)
   
class Status_Employees(models.Model):
    """Таблица статуса сотрудника"""
    name = models.CharField('Статус', max_length = 32, unique=True)    
    index = models.CharField('Индекс', max_length = 16, unique=True)
    sort_weight = models.IntegerField('Вес сортировки')
    class Meta: 
        ordering = ['name']  
        verbose_name = "Статус сотрудника"                     
        verbose_name_plural = "Статусы сотрудников"
        db_table = "amv_status_employees"  
    def __str__(self):
        return "{} ({})".format(self.name, self.index)

class Status_Aliases(models.Model):
    """Таблица псевдонимов сотрудников"""
    name = models.CharField('Статус', max_length = 32)
    pl_name = models.CharField('Статусы', max_length = 32)
    status_department = models.ForeignKey(Status_Departments, on_delete=models.CASCADE, verbose_name="Статус отдела")
    status_employee = models.ForeignKey(Status_Employees, on_delete=models.CASCADE, verbose_name="Статус сотрудника")
    
    class Meta: 
        ordering = ['status_department', 'status_employee']  
        verbose_name = "Псевдоним сотрудника"                     
        verbose_name_plural = "Псевдонимы сотрудников"
        db_table = "amv_status_aliases"  
        unique_together = ('status_department', 'status_employee')
    def __str__(self):
        return "{} ({}): {}, {}".format(self.name, self.pl_name, str(self.status_employee), str(self.status_department))
                   
class Departments(models.Model):
    """Таблица факультетов/отделов"""
    name = models.CharField('Наименование', max_length = 64, unique=True)
    status = models.ForeignKey(Status_Departments, on_delete=models.CASCADE, verbose_name="Статус отдела")
    class Meta: 
        ordering = ['name']  
        verbose_name = "Отдел"                     
        verbose_name_plural = "Отделы"
        db_table = "amv_departments"
    def __str__(self):
        return "{} ({})".format(self.name, str(self.status))

class Courses(models.Model):
    """Таблица учебных курсов"""
    name = models.CharField('Наименование', max_length = 64, unique=True) 
    department = models.ForeignKey(Departments, null=True, on_delete=models.CASCADE, verbose_name="Отдел")
    amount_months = models.IntegerField('Количество месяцев')
    class Meta: 
        ordering = ['name']  
        verbose_name = "Курс"                     
        verbose_name_plural = "Курсы"
        db_table = "amv_courses"
    def __str__(self):
        return "{} ({} {}) - {}".format(
                self.name, 
                str(self.amount_months), 
                Extra().getStringAmountMonths(self.amount_months),
                str(self.department)) 

class Subjects(models.Model):
    """Таблица предметов"""
    name = models.CharField('Наименование', max_length = 64, unique=True)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, verbose_name="Отдел")
    amount_lessons = models.IntegerField('Количество занятий')
    class Meta: 
        ordering = ['department']  
        verbose_name = "Предмет"                     
        verbose_name_plural = "Предметы"
        db_table = "amv_subjects"   
    
    def __str__(self):
        return "{} - {} ({} {})".format(
                self.name, 
                str(self.department), 
                self.amount_lessons, 
                Extra().getStringAmountLessons(self.amount_lessons))

class Course_Subject(models.Model):
    """Таблица курсов-предметов"""
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Курс")
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, verbose_name="Предмет")
    class Meta: 
        ordering = ['course']  
        verbose_name = "Курс-Предмет"                     
        verbose_name_plural = "Курсы-Предметы"
        unique_together = ('subject', 'course')
        db_table = "amv_сourse_subject"     
    
    def __str__(self):
        return "{}. Курс: {}".format(str(self.subject), self.course.name)


class Groups(models.Model):
    """Таблица групп студентов"""
    name = models.CharField('Номер группы', max_length = 16, unique=True)    
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Учебный курс")
    started = models.DateField('Дата начала')
    class Meta: 
        ordering = ['name']  
        verbose_name = "Группа"                     
        verbose_name_plural = "Группы"
        db_table = "amv_groups" 
    def __str__(self):
        return '{} "{}" - начало {}'.format(
                self.name,
                str(self.course),
                Extra().getStringData(self.started))
    def save(self, my_generate=False, *args, **kwargs ):
        if(my_generate):
            super(Groups, self).save(*args, **kwargs)
        if(self.pk):
            return
        super(Groups, self).save(*args, **kwargs)
        rows = Course_Subject.objects.filter(course=self.course.id)
        for el in rows:
            for ls in range(el.subject.amount_lessons):
                Schedule.objects.create(group=self, subject=el.subject)  
    def endStudy(self):        
        return self.started + timedelta(self.course.amount_months*30)
        

        
 
class Person(models.Model):
    """Общий класс-родитель для Студентов и Преподавателей"""
    lastname = models.CharField('Фамилия', max_length = 64)
    firstname = models.CharField('Имя', max_length = 64)
    patronymic = models.CharField('Отчество', max_length = 64, default="", null=True, blank=True)  
    birthday = models.DateField('День рождения')
    phone = models.CharField('Телефон', max_length = 16)
    e_mail = models.CharField('Эл. почта', max_length = 64) 
    login = models.CharField('Логин', unique=True, max_length = 128) 
    picture = models.ImageField('Фото', null=True, blank=True, upload_to='persons')  
    gender = models.ForeignKey(Genders, on_delete=models.CASCADE, verbose_name="Пол")
    activ = models.BooleanField('Активный', default = True)
    
    class Meta:        
        abstract = True       
    def getShortName(self):
        pt = (self.patronymic[0:1] + "." if self.patronymic else "")
        return "{} {}.{}".format(self.lastname, self.firstname[0:1], pt)
    def getFullName(self):
        pt = (" " + self.patronymic if self.patronymic else "") 
        return "{} {}{}".format(self.lastname, self.firstname, pt)
    def getInfo(self):
        return {
            "lastname": self.lastname,
            "firstname": self.firstname,
            "patronymic": self.patronymic,
            "birthday": Extra().getStringData(self.birthday),
            "phone": Extra().getStringPhone(self.phone),
            "phoneJS": Extra().getStringPhoneJS(self.phone),
            "e_mail": self.e_mail,
            "picture": (self.picture.url if self.picture else None),
            "gender": self.gender.index,
            "id": str(self.id),
            "name": self.getFullName(),
            "fio": self.getShortName(),
            "OK": self.activ
        }
    def getStringActiv(self):            
        act = ""
        if(not self.activ):
            if(self.gender.index == "F"):
                act += " - не доступна"
            else:
                act += " - не доступен"
        return act
      
class Students(Person):
    """Таблица студентов"""
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, verbose_name="Группа")
    class Meta: 
        ordering = ['lastname', 'firstname', 'patronymic']  
        verbose_name = "Студент"                     
        verbose_name_plural = "Студенты"
        indexes = [models.Index(fields=['login'])]
        db_table = "amv_students"
    def __str__(self):
        return "{} (группа {}){} - id={}".format(self.getShortName(), str(self.group),  self.getStringActiv(), self.id)
    
    def getType(self):
        return "students"
    
    def getPersonalInfo(self):
        res = self.getInfo()
        res["group"] = self.group.name
        res["course"] = self.group.course.name
        res["persons"]= self.getType()
        res["html"] = "work_students.html"
        res["status"] = "Студент"
        return res
       
class Employees(Person):
    """Таблица работников"""
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, verbose_name="Отдел")
    status = models.ForeignKey(Status_Employees, on_delete=models.CASCADE, verbose_name="Должность")
    
    class Meta: 
        ordering = ['lastname', 'firstname', 'patronymic']  
        verbose_name = "Работник"                     
        verbose_name_plural = "Работники"
        indexes = [models.Index(fields=['login'])]
        db_table = "amv_employees"   
    
    def getStatusAlias(self, pl=False):
        try:
            al = Status_Aliases.objects.get(
                    status_department=self.department.status.id,
                    status_employee=self.status.id)
        except:
            return ("Сотрудники" if pl else "Сотрудник")
        return (al.pl_name if pl else al.name)
        
    def __str__(self):           
        return "{} ({}) - {}: {}{} - id={}".format(
            self.getShortName(), 
            str(self.department), 
            str(self.status), 
            self.getStatusAlias(), 
            self.getStringActiv(),
            self.id)
    def getType(self):
        return "employees"
        
    def getPersonalInfo(self):
        res = self.getInfo()
        res["department"] = self.department.name
        res["status"] = self.getStatusAlias()
        res["persons"] = self.getType()
        res["html"] = "work_employees_{}_{}.html".format(self.department.status.index, self.status.index)
        return res
 

class ApplicationBot(Person):
    person = models.CharField('Студент/Сотрудник', max_length = 10)
    action = models.IntegerField('Действие', default=0) #0-зарегистрировано, 1-заблокировано, 2-отказ, 3-принять
    bot_id = models.PositiveBigIntegerField('ID чата', unique=True)
    department = models.ForeignKey(Departments, null=True, on_delete=models.CASCADE, verbose_name="Отдел")
    group = models.ForeignKey(Groups, null=True, on_delete=models.CASCADE, verbose_name="Группа") 
    status = models.ForeignKey(Status_Employees, null=True, on_delete=models.CASCADE, verbose_name="Должность")
    
    class Meta: 
        ordering = ['lastname', 'firstname', 'patronymic']  
        verbose_name = "Заявка"                     
        verbose_name_plural = "Заявки"
        db_table = "amv_applicationbot"   
    
    def getMessage(self):
        temp = self.getFullName() + ",\n"
        if(self.action == 1):
            return temp + "<b>Вас заблокировали!</b>"
        if(self.action == 2):
            return temp + "<b>Вам отказали.</b>"
        if(self.person == "employee"):
            q = Status_Aliases.objects.get(status_department=self.department.status, status_employee=self.status)
        
        
            return temp + 'Вас приняли в отдел:\n<b>{}</b>.\nНа должность:\n<b>"{}"</b>.'.format(self.department.name, q.name)   
 
        return temp + 'Вас зачислили в группу:\n<b>{}</b>.'.format(self.group.name)    
    

 
class SunBot(models.Model):
    """Таблица зарегистрированных чатов"""
    bot_id = models.PositiveBigIntegerField('ID чата', unique=True)
    employees = models.ForeignKey(Employees, null=True, on_delete=models.CASCADE, verbose_name="Сотрудник")
    students = models.ForeignKey(Students, null=True, on_delete=models.CASCADE, verbose_name="Студент")     
    class Meta: 
        ordering = ['bot_id']  
        verbose_name = "Идентификатор чата"                     
        verbose_name_plural = "Идентификаторы чатов"
        indexes = [models.Index(fields=['bot_id'])]
        db_table = "amv_sunbot"      
        
    def getPerson(self):
        return (("employees", self.employees) if self.students == None else ("students", self.students))  
    
class LessonTimes(models.Model):  
    """Таблица времени начала уроков"""
    name = models.CharField('Наменование', max_length = 36)
    time = models.TimeField("Время урока", unique=True)
    class Meta:
        ordering = ['time']  
        verbose_name = "Время начала урока"                     
        verbose_name_plural = "Время начала уроков" 
        db_table = "amv_times_lesson"
    def __str__(self):
        return "{}: {} - {}".format(str(self.id), str(self.time), self.name)

class Schedule(models.Model):
    """Расписание предметов"""
    lesson_date = models.DateField('Дата занятия', null=True)
    lesson_time = models.ForeignKey(LessonTimes, on_delete=models.CASCADE, verbose_name="Время урока", null=True)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, verbose_name="Группа")
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, verbose_name="Предмет")
    professor = models.ForeignKey(Employees, null=True, on_delete=models.PROTECT, verbose_name="Преподаватель")
    class Meta: 
        ordering = ['lesson_date', 'lesson_time']  
        verbose_name = "Расписание"                     
        verbose_name_plural = "Расписания"
        indexes = [models.Index(fields=['lesson_date']), models.Index(fields=['group', 'subject'])]
        db_table = "amv_schedule"      
    
    def setLesson(self, dt, pr):
        self.lesson_date = dt[0]
        self.professor = pr
        self.lesson_time = LessonTimes.objects.get(id=dt[1])
        self.save()
        
    def getStringInfo(self):        
        return [
                Extra().getStringTimeShort(self.lesson_time.time), 
                self.group.name,
                '"{}"'.format(self.subject.name),
                self.getActivProfessor()]
        
    def __str__(self):
        return "{} {} {} {} {}".format(
                Extra().getStringData(self.lesson_date),
                Extra().getStringTimeShort(self.lesson_time.time),
                self.group.name,
                self.subject.name,
                self.professor.getShortName())
        
    def getActivProfessor(self):
        pr = self.isActivProfessor()
        return (pr.getShortName() if pr else "" )
    
    def isActivProfessor(self):      
        if(self.professor != None and self.professor.activ == False and self.lesson_date >= date.today()):
            return None;
        return self.professor   
        
class NamesInfo(models.Model):
    """Общий класс-родитель для стандартных наименований"""
    index = models.IntegerField('Индекс', unique=True)
    name = models.CharField('Полное название', max_length = 24, unique=True)
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
