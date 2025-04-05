from django.contrib import admin
from .models import Event
from .models import Student,Parent,Homework,Activity,Rank,Staff,GameProgressGroup,PuzzleImage,PuzzleGameRecord,ChimpGameRecord,XOGameRequest,XOGame

admin.site.register(Event)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Homework)
admin.site.register(Activity)
admin.site.register(Rank)
admin.site.register(Staff)
admin.site.register(GameProgressGroup)
admin.site.register(PuzzleImage)
admin.site.register(PuzzleGameRecord)
admin.site.register(ChimpGameRecord)
admin.site.register(XOGameRequest)
admin.site.register(XOGame)
