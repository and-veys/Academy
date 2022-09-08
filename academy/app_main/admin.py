from django.contrib import admin

from .models import Genders 
from .models import Status_Departments, Status_Employees, Status_Aliases
from .models import Students, Groups, Courses
from .models import Employees, Departments 
from .models import Subjects, Course_Subject
from .models import NamesWeekDays, NamesMonths, WeekEnds, LessonTimes, NamesMarks
                  

admin.site.register(Genders)
admin.site.register(Students)
admin.site.register(Groups)
admin.site.register(Courses)
admin.site.register(Employees)
admin.site.register(Departments)
admin.site.register(Status_Departments)
admin.site.register(Status_Employees)
admin.site.register(Status_Aliases)
admin.site.register(Subjects)
admin.site.register(Course_Subject)
admin.site.register(NamesWeekDays)
admin.site.register(NamesMonths)
admin.site.register(WeekEnds)
admin.site.register(LessonTimes)
admin.site.register(NamesMarks)



