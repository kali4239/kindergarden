from django.contrib import admin
from .models import Event
from .models import Student,Parent,Homework,Activity,Rank,Staff

admin.site.register(Event)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Homework)
admin.site.register(Activity)
admin.site.register(Rank)
admin.site.register(Staff)