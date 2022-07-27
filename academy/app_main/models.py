from django.db import models
from .extra.extra import Extra

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
             
class Courses(models.Model):
    """Таблица учебных курсов"""
    name = models.CharField('Наименование', max_length = 64, unique=True) 
    amount_months = models.IntegerField('Количество месяцев')
    class Meta: 
        ordering = ['name']  
        verbose_name = "Курс"                     
        verbose_name_plural = "Курсы"
        db_table = "amv_courses"
    def __str__(self):
        return "{} ({} {})".format(
                self.name, 
                str(self.amount_months), 
                Extra().getStringAmountMonths(self.amount_months)) 
        
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



  
class Person(models.Model):
    """Общий класс-родитель для Студентов и Преподавателей"""
    lastname = models.CharField('Фамилия', max_length = 64)
    firstname = models.CharField('Имя', max_length = 64)
    patronymic = models.CharField('Отчество', max_length = 64)  
    birthday = models.DateField('День рождения')
    phone = models.CharField('Телефон', max_length = 16)
    e_mail = models.CharField('Эл. почта', max_length = 64) 
    login = models.CharField('Логин', unique=True, max_length = 128) 
    picture = models.ImageField('Фото', null=True, blank=True, upload_to='persons')  
    gender = models.ForeignKey(Genders, on_delete=models.CASCADE, verbose_name="Пол")
    
    class Meta:        
        abstract = True       
    def getShotName(self):
        pt = ("" if self.patronymic == "" else self.patronymic[0:1] + ".")
        return "{} {}.{}".format(self.lastname, self.firstname[0:1], pt)
    def getFullName(self):
        pt = ("" if self.patronymic == "" else " " + self.patronymic) 
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
            "fio": self.getShotName(),
            "OK": True
        }
      
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
        return "{} (группа {})".format(self.getShotName(), str(self.group))
        
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
        return "{} ({}) - {}: {}".format(self.getShotName(), str(self.department), str(self.status), self.getStatusAlias())
        
    def getPersonalInfo(self):
        res = self.getInfo()
        res["department"] = self.department.name
        res["status"] = self.getStatusAlias()
        res["persons"]= "employees"

        return res

        
class SunBot(models.Model):
    """Таблица зарегистрированных чатов"""
    bot_id = models.IntegerField('ID чата', unique=True)
    employee = models.ForeignKey(Employees, null=True, on_delete=models.CASCADE, verbose_name="Сотрудник")
    student = models.ForeignKey(Students, null=True, on_delete=models.CASCADE, verbose_name="Студент")     
    class Meta: 
        ordering = ['bot_id']  
        verbose_name = "Идентификатор чата"                     
        verbose_name_plural = "Идентификаторы чатов"
        indexes = [models.Index(fields=['bot_id'])]
        db_table = "amv_sunbot"      
        
    def getPerson(self):
        return (self.employee if self.student == None else self.student)        #TODO test bot as student