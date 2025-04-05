from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
# from .models import Staff
import json
from django.utils import timezone
from django.utils.timezone import localtime

class Event(models.Model):
    title = models.CharField(max_length=200)
    event_date = models.DateField()
    details = models.TextField()
    is_completed = models.BooleanField(default=False)
    image = models.ImageField(upload_to='event_images/',null=True)

    def __str__(self):
        return self.title
    
    
class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)  
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def attendance_percentage(self):
        total_days = self.attendance_records.count()  
        present_days = self.attendance_records.filter(status='present').count()
        if total_days > 0:
            return round((present_days / total_days) * 100, 2)  
        return 0
    
    
class Parent(models.Model):
    parent_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  
    email = models.EmailField(unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Homework(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    title = models.CharField(max_length=200)
    details = models.TextField()
    due_date = models.DateField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True)
    revoked = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,  
        default='pending'
    )

    def __str__(self):
        return self.title


class Activity(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(
        upload_to='activity_attachments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f"{self.title} - {self.student.name}"
    
class Rank(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    rank = models.IntegerField()
    score = models.FloatField()

class Staff(models.Model):
    STAFF_TYPE_CHOICES = [
        ('teaching', 'Teaching'),
        ('non-teaching', 'Non-Teaching'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    profile_picture = models.ImageField(upload_to='staff_profile_pics/', null=True, blank=True)
    staff_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE_CHOICES)
    designation = models.CharField(max_length=100, blank=True, null=True)  
    department = models.CharField(max_length=100, blank=True, null=True)  

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'date')  

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
    
# games

class GameProgressGroup(models.Model):
    student_name = models.CharField(max_length=255, unique=True)
    game_attempts = models.JSONField(default=list)  
    best_rank = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student_name} - Rank {self.best_rank}"
    

class PuzzleImage(models.Model):
    topic = models.CharField(max_length=50)  
    image = models.ImageField(upload_to='puzzle_images/') 

    def __str__(self):
        return f"{self.topic} - {self.image.name}"


class PuzzleGameRecord(models.Model):
    # username = models.CharField(max_length=255)
    student_name = models.CharField(max_length=255, unique=True)  
    topic = models.CharField(max_length=50)  
    level = models.IntegerField()  
    time_taken = models.FloatField()  
    completed_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.student_name} - {self.topic} - Level {self.level} - `{self.time_taken}s`"


class ChimpGameRecord(models.Model):
    # username = models.CharField(max_length=255)
    student_name = models.CharField(max_length=255, unique=True)  
    completed_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        local_time = localtime(self.completed_at)
        return f"{self.student_name} -  {local_time.strftime('%Y-%m-%d %I:%M:%S %p')}"



class XOGameRequest(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sent_requests')  
    receiver = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='received_requests')  
    status = models.CharField(max_length=20, default="pending") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.name} -> {self.receiver.name} ({self.status})"

class XOGame(models.Model):
    player_x = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='games_as_x')  
    player_o = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='games_as_o')  
    current_turn = models.CharField(max_length=1, default="X")  
    board_state = models.JSONField(default=list)  
    winner = models.CharField(max_length=1, null=True, blank=True) 
    toss_result = models.JSONField(default=dict) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player_x.name} vs {self.player_o.name} ({self.current_turn}'s turn)"

class PredictionGameRecord(models.Model):
    student_name = models.CharField(max_length=255)
    user_input = models.CharField(max_length=5) 
    prediction = models.CharField(max_length=6)  
    second_input = models.CharField(max_length=5) 
    third_input = models.CharField(max_length=5)  
    fourth_input = models.CharField(max_length=5) 
    fifth_input = models.CharField(max_length=5)  
    result = models.CharField(max_length=6)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.prediction} - {self.result}"