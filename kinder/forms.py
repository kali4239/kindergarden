from django import forms
from .models import Event, Student, Parent, Homework, Activity, Staff


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_date', 'details', 'is_completed', 'image']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'bio', 'profile_picture']  
        widgets = {
            'password': forms.PasswordInput(),
        }

class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['parent_id', 'name', 'email', 'student']  # Removed 'password'
        widgets = {
            'password': forms.PasswordInput(),
        }

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['title', 'details', 'due_date', 'student', 'assigned_by']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class StudentLoginForm(forms.Form):
    student_id = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your Student ID', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'password', 'placeholder': 'Enter your password', 'class': 'form-control'})
    )

class ParentLoginForm(forms.Form):
    parent_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your Parent ID', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'})
    )

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
class TeachingStaffLoginForm(forms.Form):
    staff_id = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your Staff ID', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'})
    )

class NonTeachingStaffLoginForm(forms.Form):
    staff_id = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your Staff ID', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'})
    )
