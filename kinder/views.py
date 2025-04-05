import json
import random
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import admin
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import calendar
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Event
from .forms import EventForm, StudentForm, HomeworkForm, ParentForm, ActivityForm,TeachingStaffLoginForm,NonTeachingStaffLoginForm
from django.contrib import messages
from .forms import StudentLoginForm,ParentLoginForm
from .models import Student,Parent,Homework,Activity,Rank,Staff,Attendance
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Student, GameProgressGroup,PuzzleImage,PuzzleGameRecord,ChimpGameRecord,XOGameRequest,XOGame,PredictionGameRecord
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GameProgressGroupSerializer
from .serializers import PuzzleGameRecordSerializer, ChimpGameRecordSerializer, XOGameSerializer
import requests
import logging


def home(request):
    context ={}
    return render(request, "index.html", context)

def calendar_view(request):
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    month = request.GET.get('month')
    year = request.GET.get('year')

    if month and year:
        current_month = int(month)
        current_year = int(year)
    else:
        current_year = datetime.now().year
        current_month = datetime.now().month

    current_day = datetime.now().day
    current_date = datetime.now()
    
    current_month_name = datetime(current_year, current_month, 1).strftime('%B')
    calendar.setfirstweekday(calendar.SUNDAY) 
    month_calendar = calendar.monthcalendar(current_year, current_month)

    events = Event.objects.filter(event_date__year=current_year, event_date__month=current_month)
    
    events_by_day = {}
    for event in events:
        event_day = event.event_date.day
        events_by_day[event_day] = {
            'id': event.id,
            'title': event.title,
            'status': 'completed' if event.is_completed else 'upcoming',
            'details': event.details,
        }
        
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1

    next_month = current_month + 1 if current_month < 12 else 1
    next_year = current_year if current_month < 12 else current_year + 1

    # events_by_day_json = json.dumps(events_by_day)  

    return render(request, 'calendar.html', {
        'month_calendar': month_calendar,
        'current_year': current_year,
        'current_month': current_month,
        'events_by_day': events_by_day, 
        'current_month_name': current_month_name,
        'current_day': current_day,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'current_date': current_date,
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})


def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            password = form.cleaned_data['password']
        
            try:
                student = Student.objects.get(student_id=student_id)
                if student.password == password:  
                    request.session['student_id'] = student_id  # Store student_id in session
                    request.session.save() 
                    print(f"Student ID {student_id} stored in session") 
                    return redirect('student_dashboard', student_id=student_id)
                else:
                    form.add_error(None, "Invalid password")
            except Student.DoesNotExist:
                form.add_error(None, "Student ID not found")
    else:
        form = StudentLoginForm()
    
    return render(request, 'student_login.html', {'form': form})


def student_dashboard(request, student_id):
    # if 'student_id' in request.session:
    #     print(f"Student ID in session (dashboard): {request.session['student_id']}")  # Debug statement
    # else:
    #     print("Student ID not found in session (dashboard)") 
    if 'student_id' not in request.session:
        messages.error(request, "Session expired or not found. Please log in again.")
        return redirect('student_login') 

    # student = get_object_or_404(Student, student_id=student_id)
    student = get_object_or_404(Student, student_id=request.session['student_id'])
    homeworks = Homework.objects.filter(student=student, assigned_by__isnull=True)
    assignments = Homework.objects.filter(student=student, assigned_by__isnull=False)
    
    events = Event.objects.all()
    activities = student.activities.all().order_by('-created_at')
    attendance_records = student.attendance_records.all().order_by('-date') 
    attendance_percentage = student.attendance_percentage 
    
    return render(request, 'student_dashboard.html', {
        'student': student,
        'homeworks': homeworks,
        'assignments': assignments, 
        'events': events,
        'activities': activities,
        'attendance_records': attendance_records,
        'attendance_percentage': attendance_percentage,  
    })

def parent_login(request):
    if request.method == 'POST':
        form = ParentLoginForm(request.POST)
        if form.is_valid():
            parent_id = form.cleaned_data['parent_id']
            password = form.cleaned_data['password']
        
            try:
                parent = Parent.objects.get(parent_id=parent_id)
                if parent.password == password:  
                    return redirect('parent_dashboard', parent_id=parent_id)
                else:
                    form.add_error(None, "Invalid password")
            except Parent.DoesNotExist:
                form.add_error(None, "Parent ID not found")
    else:
        form = ParentLoginForm()
    return render(request, 'parent_login.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                error_message = "You are not an admin."
        else:
            error_message = "Invalid credentials. Please check your username and pa ssword."
        
        return render(request, 'admin_login.html', {'error': error_message})
    
    return render(request, 'admin_login.html')

def get_grade(score):
    """Function to calculate grade based on score."""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B+'
    elif score >= 60:
        return 'B'
    elif score >= 50:
        return 'C'
    else:
        return 'F'

def parent_dashboard(request, parent_id):
    parent = Parent.objects.get(parent_id=parent_id)
    homeworks = Homework.objects.filter(student=parent.student)
    student = parent.student 
    total_students = Student.objects.count() 
    child_rank = Rank.objects.get(student=student).rank
    child_rank_percentage = ((total_students - child_rank) / total_students) * 100
    
    # Fetch all students' ranks and scores
    all_students_rank = Rank.objects.order_by('rank').values('student__name', 'rank', 'score')

    all_students_rank_with_grades = [
        {**student, 'grade': get_grade(student['score'])}  
        for student in all_students_rank
    ]
    
    context = {
        'parent': parent,
        'homeworks': homeworks,
        'child_rank': child_rank,
        'child_rank_percentage': child_rank_percentage,
        'all_students_rank': all_students_rank_with_grades,
        'total_students': total_students,
    }
    
    return render(request, 'parent_dashboard.html', context)

def update_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        # Update name and bio
        student.name = request.POST.get('name')
        student.bio = request.POST.get('bio')
        
        # Update profile picture if a new one is uploaded
        if 'profile_picture' in request.FILES:
            student.profile_picture = request.FILES['profile_picture']
        
        student.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('student_dashboard', student_id=student_id)
    
    messages.error(request, 'Invalid request method.')
    return redirect('student_dashboard', student_id=student_id)

# @login_required
# def add_event(request):
#     if not request.user.is_staff:
#         return redirect('calendar')  
    
#     if request.method == 'POST':
#         form = EventForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('calendar')
#     else:
#         form = EventForm()
    
#     return render(request, 'add_event.html', {'form': form})

# @login_required
# def add_student(request):
#     if not request.user.is_staff:
#         return redirect('calendar')  
    
#     if request.method == 'POST':
#         form = StudentForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Student added successfully!')
#             return redirect('admin_dashboard')
#     else:
#         form = StudentForm()
    
#     return render(request, 'add_student.html', {'form': form})

# @login_required
# def add_parent(request):
#     if not request.user.is_staff:
#         return redirect('calendar')  
    
#     if request.method == 'POST':
#         form = ParentForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Parent added successfully!')
#             return redirect('admin_dashboard')
#     else:
#         form = ParentForm()
    
#     return render(request, 'add_parent.html', {'form': form})

# @login_required
# def add_homework(request):
#     if not request.user.is_staff:
#         return redirect('calendar')  
    
#     if request.method == 'POST':
#         form = HomeworkForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Homework added successfully!')
#             return redirect('admin_dashboard')
#     else:
#         form = HomeworkForm()
    
#     return render(request, 'add_homework.html', {'form': form})

# @login_required
# def add_event(request):
#     if not request.user.is_staff:
#         return redirect('calendar')  
    
#     if request.method == 'POST':
#         form = EventForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Event added successfully!')
#             return redirect('admin_dashboard')
#     else:
#         form = EventForm()
    
#     return render(request, 'add_event.html', {'form': form})

def submit_activity(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')  # Get the uploaded file
        
        if title and description:
            activity = Activity.objects.create(
                student=student,
                title=title,
                description=description,
                file=file,  # Save the file
                status='pending'
            )
            
            send_mail(
                'New Activity Submission',
                f'New activity submitted by {student.name}:\n\n{title}\n{description}',
                settings.EMAIL_HOST_USER,
                ['admin@example.com'],
                fail_silently=True,
            )
            
            messages.success(request, 'Activity submitted successfully!')
            return redirect('student_dashboard', student_id=student_id)
        else:
            messages.error(request, 'Please fill in all required fields')
    
    return redirect('student_dashboard', student_id=student_id)


def admin_dashboard(request):
    if not request.user.is_authenticated:
        if 'staff_id' in request.session:
            del request.session['staff_id']
        if 'active_section' in request.session:
            del request.session['active_section'] 
    
    student_form = StudentForm()
    parent_form = ParentForm()
    homework_form = HomeworkForm()
    event_form = EventForm()
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'student':
            student_form = StudentForm(request.POST, request.FILES)
            if student_form.is_valid():
                student_form.save()
                messages.success(request, 'Student added successfully!')
                return redirect('admin_dashboard')

        elif form_type == 'parent':
            parent_form = ParentForm(request.POST)
            if parent_form.is_valid():
                parent_form.save()
                messages.success(request, 'Parent added successfully!')
                return redirect('admin_dashboard')

        elif form_type == 'homework':
            homework_form = HomeworkForm(request.POST)
            if homework_form.is_valid():
                homework_form.save()
                messages.success(request, 'Homework added successfully!')
                return redirect('admin_dashboard')

        elif form_type == 'event':
            event_form = EventForm(request.POST, request.FILES)
            if event_form.is_valid():
                event_form.save()
                messages.success(request, 'Event added successfully!')
                return redirect('admin_dashboard')

        elif form_type == 'teaching_login':
            form = TeachingStaffLoginForm(request.POST)
            if form.is_valid():
                staff_id = form.cleaned_data['staff_id']
                password = form.cleaned_data['password']
                try:
                    staff = Staff.objects.get(staff_id=staff_id, staff_type='teaching')
                    if staff.password == password:
                        request.session['staff_id'] = staff_id
                        request.session['active_section'] = 'teaching' 
                        messages.success(request, 'Teaching staff login successful!')
                        return redirect('teacher_dashboard')
                    else:
                        messages.error(request, 'Please enter the correct login credentials.')
                except Staff.DoesNotExist:
                    messages.error(request, 'Please enter the correct login credentials.')

        elif form_type == 'non_teaching_login':
            form = NonTeachingStaffLoginForm(request.POST)
            if form.is_valid():
                staff_id = form.cleaned_data['staff_id']
                password = form.cleaned_data['password']
                try:
                    staff = Staff.objects.get(staff_id=staff_id, staff_type='non-teaching')
                    if staff.password == password:
                        request.session['staff_id'] = staff_id
                        request.session['active_section'] = 'non-teaching'  
                        messages.success(request, 'Non-teaching staff login successful!')
                        return redirect('non_teaching_dashboard')
                    else:
                        messages.error(request, 'Please enter the correct login credentials.')
                except Staff.DoesNotExist:
                     messages.error(request, 'Please enter the correct login credentials.')
            
    activities = Activity.objects.filter(status='pending')
    pending_activities = Activity.objects.filter(status='pending')
    pending_activities_count = pending_activities.count()
    
    current_staff = None
    if 'staff_id' in request.session:
        current_staff = Staff.objects.get(staff_id=request.session['staff_id'])

    active_section = request.session.get('active_section', 'home')
    
    return render(request, 'admin_dashboard.html', {
        'student_form': student_form,
        'parent_form': parent_form,
        'homework_form': homework_form,
        'event_form': event_form,
        'activities': activities,
        'pending_activities': pending_activities,
        'pending_activities_count': pending_activities_count,
        'current_staff': current_staff,
        'active_section': active_section,  
    })
    
@login_required
def update_activity_status(request, activity_id):
    if not request.user.is_staff:
        return redirect('calendar')  
    
    activity = get_object_or_404(Activity, id=activity_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        admin_comment = request.POST.get('admin_comment')
        
        activity.status = status
        activity.admin_comment = admin_comment
        activity.save()
        
        messages.success(request, 'Activity status updated successfully!')
        return redirect('admin_dashboard')
    
    messages.error(request, 'Invalid request method.')
    return redirect('admin_dashboard')

def logout_view(request):
    if 'staff_id' in request.session:
        del request.session['staff_id']
    if 'active_section' in request.session:
        del request.session['active_section']
    logout(request)
    return redirect('calendar')

def teacher_dashboard(request):
    if 'staff_id' not in request.session:
        return redirect('admin_dashboard')
    
    staff_id = request.session['staff_id']
    try:
        teacher = Staff.objects.get(staff_id=staff_id, staff_type='teaching')
    except Staff.DoesNotExist:
        if 'staff_id' in request.session:
            del request.session['staff_id']
        messages.error(request, 'Teacher not found. Please log in again.')
        return redirect('admin_dashboard')
    students = Student.objects.all().select_related('user')
    assignments = Homework.objects.filter(assigned_by=teacher)
    
    show_modal = False 
    
    for student in students:
        
        student.total_days = student.attendance_records.count()
        student.present_days = student.attendance_records.filter(status='present').count()
        student.absent_days = student.attendance_records.filter(status='absent').count()
        
        student.attendance_percentage_value = (student.present_days / student.total_days * 100) if student.total_days > 0 else 0

        student.total_assignments = student.homework_set.count()
        student.completed_assignments = student.homework_set.filter(status='completed').count()
        student.pending_assignments = student.homework_set.filter(status='pending').count()
        
        student.total_activities = student.activities.count()
        student.approved_activities = student.activities.filter(status='approved').count()
        student.pending_activities = student.activities.filter(status='pending').count()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'update_attendance':
            date = datetime.today().date()
            for student in students:
                status = request.POST.get(f'status_{student.student_id}')
                if status in ['present', 'absent']:
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        date=date,
                        defaults={'status': status}
                    )
                    if not created:
                        messages.warning(request, f'Attendance for {student.name} on {date} is already recorded.')
                    else:
                        messages.success(request, f'Attendance for {student.name} on {date} updated successfully!')
                        
                        messages.success(request, 'Attendance updated successfully!')
            show_modal = True  
        
        elif form_type == 'assign_homework':
            student_id = request.POST.get('student')
            title = request.POST.get('title')
            details = request.POST.get('details')
            due_date = request.POST.get('due_date')
            
            try:
                student = Student.objects.get(student_id=student_id)
                Homework.objects.create(
                    title=title,
                    details=details,
                    due_date=due_date,
                    student=student,
                    assigned_by=teacher
                )
                messages.success(request, 'Homework assigned successfully!')
                show_modal = True 
            except Student.DoesNotExist:
                messages.error(request, 'Student not found!')
    
    return render(request, 'teacher_dashboard.html', {
        'teacher': teacher,
        'students': students,
        'assignments': assignments,
        'show_modal': show_modal,  
        'messages': messages.get_messages(request),
    })
    
def non_teaching_dashboard(request):
    if 'staff_id' not in request.session:
        return redirect('admin_dashboard')
    
    staff_id = request.session['staff_id']
    staff = Staff.objects.get(staff_id=staff_id)
    
    events = Event.objects.all()
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'add_event':
            event_form = EventForm(request.POST, request.FILES)
            if event_form.is_valid():
                event_form.save()
                messages.success(request, 'Event added successfully!')
                return redirect('non_teaching_dashboard')
    
    event_form = EventForm()
    
    return render(request, 'non_teaching_dashboard.html', {
        'staff': staff,
        'events': events,
        'event_form': event_form,
    })

def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Homework, id=assignment_id)
    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.details = request.POST.get('details')
        assignment.due_date = request.POST.get('due_date')
        student_id = request.POST.get('student')
        assignment.student = Student.objects.get(id=student_id)
        assignment.save()
        messages.success(request, 'Assignment updated successfully!')
    return redirect('teacher_dashboard')

def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Homework, id=assignment_id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
    return redirect('teacher_dashboard')

# def revoke_assignment(request, assignment_id):
#     assignment = get_object_or_404(Homework, id=assignment_id)
#     if request.method == 'POST':
#         assignment.revoked = True
#         assignment.save()
#         messages.success(request, 'Assignment revoked successfully!')
#     return redirect('teacher_dashboard')

def assign_homework(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        details = request.POST.get('details')
        due_date = request.POST.get('due_date')
        student_id = request.POST.get('student')
        
        try:
            student = Student.objects.get(id=student_id)

            if 'staff_id' in request.session:
                staff_id = request.session['staff_id']
                teacher = Staff.objects.get(staff_id=staff_id)
            else:
                messages.error(request, 'You are not logged in as a teacher.')
                return redirect('teacher_dashboard')
            
            Homework.objects.create(
                title=title,
                details=details,
                due_date=due_date,
                student=student,
                assigned_by=teacher 
            )
            messages.success(request, 'Homework assigned successfully!')
        except Student.DoesNotExist:
            messages.error(request, 'Student not found!')
        except Staff.DoesNotExist:
            messages.error(request, 'Teacher not found!')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        
        return redirect('teacher_dashboard')
    
    return redirect('teacher_dashboard')


# Balloon game 

def generate_balloon(request):
    x_position = random.randint(0, 1000)
    y_position = 600 

    balloon_data = {
        "x": x_position,
        "y": y_position
    }
    return JsonResponse(balloon_data)


def start_game(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        print(f"Student ID in session: {student_id}") 
        student = get_object_or_404(Student, student_id=student_id)
        return JsonResponse({'message': 'Game Started'})
    else:
        # print("Student ID not found in session")
        return JsonResponse({'error': 'User not logged in'}, status=400)



# def save_game_progress(request):
#     if 'student_id' in request.session:
#         student_id = request.session['student_id']
#         student = get_object_or_404(Student, student_id=student_id)
        
#         if request.method == "POST":    
#             try:
#                 data = json.loads(request.body)  
#                 level = data.get('level_completed')
#                 time_taken = data.get('time_taken')
                
#                 # Add the game attempt to the student's game_attempts
#                 attempt = {
#                     "level_completed": level,
#                     "time_taken": time_taken,
#                     "game_end_time": timezone.now().isoformat()
#                 }
                
#                 if not student.game_attempts:
#                     student.game_attempts = []
                
#                 student.game_attempts.append(attempt)
                
#                 # Update the best rank
#                 if student.game_attempts:
#                     sorted_attempts = sorted(student.game_attempts, key=lambda x: (-x['level_completed'], x['time_taken']))
#                     student.best_rank = sorted_attempts[0]['level_completed']
                
#                 student.save()
                
#                 return JsonResponse({'message': 'Game progress saved successfully.', 'best_rank': student.best_rank})

#             except Student.DoesNotExist:
#                 return JsonResponse({'error': 'Student not found'}, status=404)
#     return JsonResponse({'error': 'User not logged in'}, status=400)



def end_game(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        student = get_object_or_404(Student, student_id=student_id)

        try:
            data = json.loads(request.body)
            level_completed = int(data.get('level_completed'))
            time_taken = float(data.get('time_taken'))

            # Get or create the GameProgressGroup for the student
            game_group, created = GameProgressGroup.objects.get_or_create(student_name=student.name)

            # Update game attempts and best rank
            attempt = {
                "level_completed": level_completed,
                "time_taken": time_taken,
                "game_end_time": timezone.now().isoformat()
            }

            game_group.game_attempts.append(attempt)

            # Sort and get the best rank
            sorted_attempts = sorted(game_group.game_attempts, key=lambda x: (-x['level_completed'], x['time_taken']))
            game_group.best_rank = sorted_attempts[0]['level_completed']

            game_group.save()

            return JsonResponse({'message': 'Game progress saved successfully.', 'best_rank': game_group.best_rank})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'User not logged in'}, status=400)


def add_game_attempt_and_update_rank(game_group, level_completed, time_taken):
    attempt = {
        "level_completed": level_completed,
        "time_taken": time_taken,
        "game_end_time": timezone.now().isoformat()
    }
    game_group.game_attempts.append(attempt)
    
    
    if game_group.game_attempts:
        sorted_attempts = sorted(game_group.game_attempts, key=lambda x: (-x['level_completed'], x['time_taken']))
        game_group.best_rank = sorted_attempts[0]['level_completed']

    game_group.save()



# puzzle game 
def puzzle_game_page(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
    
    # Fetch all topics for the buttons
    topics = PuzzleImage.objects.values_list('topic', flat=True).distinct()
    return render(request, 'puzzle_game.html', {'topics': topics})

def get_images_for_topic(request):
    if request.method == 'GET':
        topic = request.GET.get('topic')
        images = PuzzleImage.objects.filter(topic=topic).values('id', 'image')
        return JsonResponse(list(images), safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
def save_puzzle_game(request):
    if request.method == 'POST' and 'student_id' in request.session:
        try:
            data = json.loads(request.body)
            student_id = request.session['student_id']
            topic = data.get('topic')
            level = data.get('level')
            time_taken = data.get('time_taken')

            # Validate required fields
            if not topic or level is None or time_taken is None:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            student = get_object_or_404(Student, student_id=student_id)
            student_name = student.name

            # Prepare data for the API
            game_data = {
                "student_name": student_name,
                "topic": topic,
                "level": level,
                "time_taken": time_taken
            }

            # Send data to the API
            api_url = "/api/game-progress/"  # Replace with your actual API endpoint
            response = requests.post(api_url, json=game_data, headers={
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}"
            })

            if response.status_code == 201:
                return JsonResponse({'message': 'Puzzle game record saved successfully via API'})
            else:
                return JsonResponse({'error': 'Failed to save record via API'}, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except requests.RequestException as e:
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_puzzle_scores(request):
    # if 'fullname' not in request.session:
    #     return JsonResponse({'error': 'Not authenticated'}, status=401)
    if 'student_id' in request.session:
        student_id = request.session['student_id']

        student = get_object_or_404(Student, student_id=student_id)
        student_name  = student.name
    
    records = PuzzleGameRecord.objects.all().order_by('-completed_at')
    records_data = [
        {
            "username": record.student_name ,
            "topic": record.topic,
            "level": record.level,
            "time_taken": record.time_taken,
            # "date": record.completed_at.strftime("%Y-%m-%d %H:%M")
            "date": record.completed_at.strftime("%d-%m-%Y -- %H:%M")
        }
        for record in records
    ]
    return JsonResponse({'records': records_data})

# memory game 
def chimp_memory_game_page(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
    return render(request, 'memory_game.html')

@csrf_exempt
def start_chimp_game(request):
    if request.method == 'POST' and 'student_id' in request.session:
        numbers = list(range(1, 6))
        random.shuffle(numbers)
        return JsonResponse({'numbers': numbers})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def check_chimp_game(request):
    if request.method == 'POST' and 'student_id' in request.session:
        try:
            data = json.loads(request.body)
            selected_order = data.get('selected_order')
            student_id = request.session['student_id']
            student = get_object_or_404(Student, student_id=student_id)
            student_name = student.name

            # Prepare data for the API
            game_data = {
                "student_name": student_name,
                "selected_order": selected_order 
            }

           
            api_url = "/api/game-progress/" 
            response = requests.post(api_url, json=game_data, headers={
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}"
            })

            if response.status_code == 201:
                if selected_order == list(range(1, 6)):
                    return JsonResponse({'result': 'win'})
                else:
                    return JsonResponse({'result': 'lose'})
            else:
                return JsonResponse({'error': 'Failed to save record via API'}, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except requests.RequestException as e:
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def drawing_game_page(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
    return render(request,'drawing_game.html')


# xo game 

def xo_game_page(request):
    context = {}
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        student = get_object_or_404(Student, student_id=student_id)
        student_name = student.name
        context['username'] = student_name
        context['rows'] = [0, 1, 2]
        context = {
            'student': student,
            'users': Student.objects.exclude(student_id=student_id),
            'pending_requests': XOGameRequest.objects.filter(receiver=student, status="pending"),
            'rows': [0, 1, 2],
        }

        # Create active game 
        active_game = XOGame.objects.filter(
            (models.Q(player_x=student) | models.Q(player_o=student)) &
            models.Q(winner__isnull=True)
        ).order_by('-id').first()  # Get the most recent active game

        if active_game:
            context['game'] = active_game

        # Get all students except the current one
        students = Student.objects.exclude(student_id=student_id)
        context['users'] = students

        # Filter the requests which status is pending
        pending_requests = XOGameRequest.objects.filter(receiver=student, status="pending")
        context['pending_requests'] = pending_requests  

    return render(request, "xo_game.html", context)

def send_xo_request(request):
    if 'student_id' in request.session and request.method == "POST":
        sender_id = request.session['student_id']
        # print(f"Student ID in session: {student_id}") 
        sender = get_object_or_404(Student, student_id=sender_id)
        receiver_id = request.POST.get('receiver')
        receiver = get_object_or_404(Student, student_id=receiver_id)

        if sender != receiver:
            XOGameRequest.objects.create(sender=sender, receiver=receiver)
            return JsonResponse({'message': 'Request sent successfully.'})
        else:
            return JsonResponse({'error': 'Cannot send request to yourself.'}, status=400)
    return JsonResponse({'error': 'User not logged in.'}, status=400)


def accept_xo_request(request, request_id):
    if 'student_id' in request.session:
        try:
            xo_request = XOGameRequest.objects.get(id=request_id)
            receiver_id = request.session['student_id']
            receiver = get_object_or_404(Student, student_id=receiver_id)

            if xo_request.receiver == receiver:
                xo_request.status = "accepted"
                xo_request.save()

                # Enable toss for both sender and receiver
                cache.set(f"enable_toss_{xo_request.sender.student_id}", True, timeout=60)
                cache.set(f"enable_toss_{xo_request.receiver.student_id}", True, timeout=60)

                # Notify both sender and receiver to open the modal
                cache.set(f"notification_{xo_request.sender.student_id}", "Toss selection has started. Choose Head or Tail.", timeout=60)
                cache.set(f"notification_{xo_request.receiver.student_id}", "Toss selection has started. Choose Head or Tail.", timeout=60)

                # Store toss options in cache for both players
                toss_options = {"sender": None, "receiver": None}
                cache.set(f"toss_options_{xo_request.sender.student_id}", toss_options, timeout=60)
                cache.set(f"toss_options_{xo_request.receiver.student_id}", toss_options, timeout=60)

                print(f"Setting notification for sender: {xo_request.sender.student_id}")
                print(f"Setting notification for receiver: {xo_request.receiver.student_id}")

                return JsonResponse({
                    'message': 'Request accepted. Wait for start toss.',
                    'game_id': xo_request.id,
                })

            return JsonResponse({'error': 'Unauthorized.'}, status=403)

        except XOGameRequest.DoesNotExist:
            return JsonResponse({'error': 'Request not found.'}, status=404)

    return JsonResponse({'error': 'User not logged in.'}, status=400)


def get_xo_game_state(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        student = get_object_or_404(Student, student_id=student_id)
        game = XOGame.objects.filter(
            models.Q(player_x=student) | models.Q(player_o=student)).order_by('-id').first()  

        if game:
            winner_username = None
            if game.winner:
                winner_username = game.player_x.name if game.winner == "X" else game.player_o.name

            return JsonResponse({
                'board_state': game.board_state,
                'current_turn': game.current_turn,
                'player_x': game.player_x.name,
                'player_o': game.player_o.name,
                'winner': game.winner,
                'winner_username': winner_username,
                'game_id': game.id,
                'toss_result': game.toss_result 
            })
        return JsonResponse({'error': 'No active game found.'}, status=404)
    return JsonResponse({'error': 'User not logged in.'}, status=400)


@csrf_exempt
def make_xo_move(request):
    if 'student_id' in request.session and request.method == "POST":
        try:
            student_id = request.session['student_id']
            student = get_object_or_404(Student, student_id=student_id)
            row = int(request.POST.get('row'))
            col = int(request.POST.get('col'))
            game_id = request.POST.get('game_id')
            try:
                game = XOGame.objects.get(id=game_id)
            except XOGame.DoesNotExist:
                return JsonResponse({'error': 'Game not found.'}, status=404)

            # Fetch the game state
            # game = XOGame.objects.get(id=game_id)
            if student not in [game.player_x, game.player_o]:
                return JsonResponse({'error': 'Not a game participant.'}, status=403)

            player_symbol = "X" if student == game.player_x else "O"

            if game.current_turn != player_symbol:
                return JsonResponse({'error': 'Not your turn.'}, status=400)

            if game.board_state[row][col] != "":
                return JsonResponse({'error': 'Cell already occupied.'}, status=400)


            
            new_board = game.board_state
            new_board[row][col] = player_symbol
            game.board_state = new_board
            game.current_turn = "O" if player_symbol == "X" else "X"
            game.save()

            
            winner = check_winner(game.board_state)
            if winner:
                game.winner = winner
                game.save()
                winner_username = game.player_x.name if winner == "X" else game.player_o.name

            # Prepare data for the API
            game_data = {
                "game_id": game_id,
                "row": row,
                "col": col,
                "player_symbol": player_symbol,
                "student_id": student_id,
            }

            # Send data to the API
            api_url = "/api/game-progress/"  
            response = requests.post(api_url, json=game_data, headers={
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}"
            })

            if response.status_code == 201:
                return JsonResponse({
                    'message': 'Move successful',
                    'game_id': game_id,
                    'board_state': game.board_state,
                    'current_turn': game.current_turn,
                    'winner': winner,
                    'winner_username': winner_username,
                })
            else:
                return JsonResponse({'error': 'Failed to save move via API'}, status=response.status_code)

        except XOGame.DoesNotExist:
            return JsonResponse({'error': 'Game not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except requests.RequestException as e:
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request.'}, status=400)

def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != "":
            return row[0]
   
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != "":
            return board[0][col]
   
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "":
        return board[0][2]
    
    if all(cell != "" for row in board for cell in row):
        return "draw" 
    return None


def trigger_toss_coin(request):
    if 'student_id' in request.session and request.method == "POST":
        request_id = request.POST.get('request_id')
        try:
            xo_request = XOGameRequest.objects.get(id=request_id)
            sender = xo_request.sender
            receiver = xo_request.receiver

            toss_options_sender = cache.get(f"toss_options_{sender.student_id}")
            toss_options_receiver = cache.get(f"toss_options_{receiver.student_id}")

            # Randomly assign X and O
            toss_result = random.choice(["head", "tail"])
            if toss_result == "head":
                player_x = sender
                player_o = receiver
            else:
                player_x = receiver
                player_o = sender

            # Create the game with the assigned players
            game = XOGame.objects.create(
                player_x=player_x,
                player_o=player_o,
                board_state=[["", "", ""], ["", "", ""], ["", "", ""]],
                current_turn="X",
                toss_result={
                    "toss_winner": player_x.name,
                    "player_x": player_x.name,
                    "player_o": player_o.name,
                    "sender": sender.name,
                    "receiver": receiver.name,
                }
            )

            # Store the toss result in cache for both players
            toss_result = {
                "player_x": player_x.name,
                "player_o": player_o.name,
                "player_x_id": player_x.student_id,
                "player_o_id": player_o.student_id,
                "sender": sender.name,
                "receiver": receiver.name,
            }
            cache.set(f"toss_result_{sender.student_id}", toss_result, timeout=60)
            cache.set(f"toss_result_{receiver.student_id}", toss_result, timeout=60)

            return JsonResponse({
                'toss_result': toss_result,
                'message': 'Toss completed. Result displayed to both players.'
            })

        except XOGameRequest.DoesNotExist:
            return JsonResponse({'error': 'Game request not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request.'}, status=400)



def get_notifications(request):
    student_id = request.session.get("student_id")
    notification = cache.get(f"notification_{student_id}")
  

    if notification:
        cache.delete(f"notification_{student_id}")  

    return JsonResponse({"notification": notification if notification else None})

def get_toss_result(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        toss_result = cache.get(f"toss_result_{student_id}")
        if toss_result:
            return JsonResponse({"toss_result": toss_result})
        return JsonResponse({"toss_result": None})
    return JsonResponse({'error': 'User not logged in.'}, status=400)

def select_toss_option(request):
    if 'student_id' in request.session and request.method == "POST":
        student_id = request.session['student_id']
        selected_option = request.POST.get('selection')
        request_id = request.POST.get('request_id')

        try:
            xo_request = XOGameRequest.objects.get(id=request_id)
            sender = xo_request.sender
            receiver = xo_request.receiver

            toss_options_sender = cache.get(f"toss_options_{sender.student_id}", {"sender": None, "receiver": None})
            toss_options_receiver = cache.get(f"toss_options_{receiver.student_id}", {"sender": None, "receiver": None})

            if selected_option in toss_options_sender.values() or selected_option in toss_options_receiver.values():
                return JsonResponse({'error': 'This option is already selected. Please choose another one.'}, status=400)

            if student_id == sender.student_id:
                toss_options_sender["sender"] = selected_option
            elif student_id == receiver.student_id:
                toss_options_receiver["receiver"] = selected_option

            cache.set(f"toss_options_{sender.student_id}", toss_options_sender, timeout=60)
            cache.set(f"toss_options_{receiver.student_id}", toss_options_receiver, timeout=60)

            if toss_options_sender["sender"] and toss_options_receiver["receiver"]:
                if toss_options_sender["sender"] != toss_options_receiver["receiver"]:
                    cache.set(f"notification_{sender.student_id}", "Both players have selected their options. Please perform the toss.", timeout=60)
                else:
                    return JsonResponse({'error': 'Both players selected the same option. Please choose different options.'}, status=400)

            return JsonResponse({'message': 'Toss option selected successfully.'})

        except XOGameRequest.DoesNotExist:
            return JsonResponse({'error': 'Game request not found.'}, status=404)

    return JsonResponse({'error': 'Invalid request.'}, status=400)

def get_request_sender(request, request_id):
    try:
        xo_request = XOGameRequest.objects.get(id=request_id)
        return JsonResponse({'sender': xo_request.sender.name})
    except XOGameRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found.'}, status=404)




@login_required
def get_current_student(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        student = get_object_or_404(Student, student_id=student_id)
        return JsonResponse({'name': student.name})
    return JsonResponse({'error': 'Student not found'}, status=404)


# class GameProgressAPI(APIView):
#     def post(self, request, *args, **kwargs):
#         if 'topic' in request.data:  # PuzzleGameRecord data
#             serializer = PuzzleGameRecordSerializer(data=request.data)
#         elif 'selected_order' in request.data:  # ChimpGameRecord data
#             serializer = ChimpGameRecordSerializer(data=request.data)
#         elif 'game_id' in request.data:  # XOGame data
#             serializer = XOGameSerializer(data=request.data)
#         else:  # GameProgressGroup data
#             serializer = GameProgressGroupSerializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#             print(serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator(csrf_exempt, name='dispatch')
# class GameProgressAPI(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = json.loads(request.body)

#             # Handle PuzzleGameRecord data
#             if 'topic' in data:
#                 serializer = PuzzleGameRecordSerializer(data=data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#             # Handle ChimpGameRecord data
#             elif 'selected_order' in data:
#                 serializer = ChimpGameRecordSerializer(data=data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#             # Handle XOGame data
#             elif 'game_id' in data:
#                 game_id = data.get('game_id')
#                 row = data.get('row')
#                 col = data.get('col')
#                 student_id = data.get('student_id')

#                 # Validate the data
#                 if not all([game_id, row is not None, col is not None, student_id]):
#                     return Response({'error': 'Missing required fields for XO game.'}, status=status.HTTP_400_BAD_REQUEST)

#                 # Fetch the game and student
#                 game = XOGame.objects.get(id=game_id)
#                 student = Student.objects.get(student_id=student_id)

#                 # Check if the student is a participant in the game
#                 if student not in [game.player_x, game.player_o]:
#                     return Response({'error': 'Not a game participant.'}, status=status.HTTP_403_FORBIDDEN)


#                 player_symbol = "X" if student == game.player_x else "O"

#                 # Check if it's the player's turn
#                 if game.current_turn != player_symbol:
#                     return Response({'error': 'Not your turn.'}, status=status.HTTP_400_BAD_REQUEST)

#                 if game.board_state[row][col] != "":
#                     return Response({'error': 'Cell already occupied.'}, status=status.HTTP_400_BAD_REQUEST)

#                 # Update the game state
#                 new_board = game.board_state
#                 new_board[row][col] = player_symbol
#                 game.board_state = new_board
#                 game.current_turn = "O" if player_symbol == "X" else "X"

#                 # Check for a winner
#                 winner = self.check_winner(game.board_state)
#                 if winner:
#                     game.winner = winner
#                     game.save()
#                     winner_username = game.player_x.name if winner == "X" else game.player_o.name
#                 else:
#                     game.save()

#                 # Return the updated game state
#                 return Response({
#                     'message': 'Move successful',
#                     'game_id': game_id,
#                     'board_state': game.board_state,
#                     'current_turn': game.current_turn,
#                     'winner': winner,
#                     'winner_username': winner_username if winner else None,
#                 }, status=status.HTTP_200_OK)

#             # Handle GameProgressGroup data
#             else:
#                 serializer = GameProgressGroupSerializer(data=data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except XOGame.DoesNotExist:
#             return Response({'error': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class GameProgressAPI(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            logger.debug(f"Incoming request data: {data}")

            # Handle XOGame data
            if 'game_id' in data:
                game_id = data.get('game_id')
                row = data.get('row')
                col = data.get('col')
                student_id = data.get('student_id')

                # Validate the data
                if not all([game_id, row is not None, col is not None, student_id]):
                    logger.error("Missing required fields for XO game.")
                    return Response({'error': 'Missing required fields for XO game.'}, status=status.HTTP_400_BAD_REQUEST)

                # Fetch the game and student
                try:
                    game = XOGame.objects.get(id=game_id)
                    student = Student.objects.get(student_id=student_id)
                except XOGame.DoesNotExist:
                    logger.error("Game not found.")
                    return Response({'error': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)
                except Student.DoesNotExist:
                    logger.error("Student not found.")
                    return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

                # Check if the student is a participant
                if student not in [game.player_x, game.player_o]:
                    logger.error("Student is not a game participant.")
                    return Response({'error': 'Not a game participant.'}, status=status.HTTP_403_FORBIDDEN)

                # Determine player symbol (X/O)
                player_symbol = "X" if student == game.player_x else "O"

                # Check if it's the player's turn
                if game.current_turn != player_symbol:
                    logger.error("Not the player's turn.")
                    return Response({'error': 'Not your turn.'}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the cell is occupied
                if game.board_state[row][col] != "":
                    logger.error("Cell is already occupied.")
                    return Response({'error': 'Cell already occupied.'}, status=status.HTTP_400_BAD_REQUEST)

                # Update the board state
                new_board = game.board_state
                new_board[row][col] = player_symbol
                game.board_state = new_board
                game.current_turn = "O" if player_symbol == "X" else "X"

                # Check for a winner
                winner = self.check_winner(game.board_state)
                if winner:
                    game.winner = winner
                    game.save()
                    winner_username = game.player_x.name if winner == "X" else game.player_o.name
                else:
                    game.save()

                # Return the updated game state
                return Response({
                    'message': 'Move successful',
                    'game_id': game_id,
                    'board_state': game.board_state,
                    'current_turn': game.current_turn,
                    'winner': winner,
                    'winner_username': winner_username if winner else None,
                }, status=status.HTTP_200_OK)

            # Handle other game types 
            elif 'topic' in data:
                serializer = PuzzleGameRecordSerializer(data=data)
            elif 'selected_order' in data:
                serializer = ChimpGameRecordSerializer(data=data)
            else:
                serializer = GameProgressGroupSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def check_winner(self, board):
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] and row[0] != "":
                return row[0]

        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] and board[0][col] != "":
                return board[0][col]

        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "":
            return board[0][2]

        # Check for a draw
        if all(cell != "" for row in board for cell in row):
            return "draw"

        return None


# prediction game 

def prediction_game_page(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        student = get_object_or_404(Student, student_id=student_id)
        return render(request, 'prediction_game.html', {'student': student})
    return redirect('student_login')

@csrf_exempt
def generate_prediction(request):
    if request.method == 'POST' and 'student_id' in request.session:
        try:
            data = json.loads(request.body)
            user_input = data.get('userInput', '')

            print(f"User Input Received: {user_input}")
            
            # Validate input: must be exactly 5 digits
            if not user_input.isdigit() or len(user_input) != 5:
                return JsonResponse({'error': 'Please enter exactly 5 digits (0-9).'}, status=400)

           

            # Generate prediction
            first_four_digits = user_input[:4]  # First 4 digits
            last_digit = str(int(user_input[-1]) - 2)  # Last digit minus 2
            prediction = f"2{first_four_digits}{last_digit}"

            return JsonResponse({
                'message': 'Prediction generated successfully.',
                'prediction': prediction
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request.'}, status=400)

@csrf_exempt
def generate_third_input(request):
    if request.method == 'POST' and 'student_id' in request.session:
        try:
            data = json.loads(request.body)
            second_input = data.get('secondInput')

            # Generate third input
            third_input = ''.join([str(9 - int(digit)) for digit in second_input])

            return JsonResponse({
                'message': 'Third input generated successfully.',
                'third_input': third_input
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request.'}, status=400)

@csrf_exempt
def generate_fifth_input(request):
    if request.method == 'POST' and 'student_id' in request.session:
        try:
            data = json.loads(request.body)
            fourth_input = data.get('fourthInput')

            # Generate fifth input
            fifth_input = ''.join([str(9 - int(digit)) for digit in fourth_input])

            return JsonResponse({
                'message': 'Fifth input generated successfully.',
                'fifth_input': fifth_input
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request.'}, status=400)

@csrf_exempt
def check_result(request):
    if request.method == 'POST' and 'student_id' in request.session:
        try:
            data = json.loads(request.body)
            student_id = request.session['student_id']
            student = get_object_or_404(Student, student_id=student_id)
            student_name = student.name

            user_input = data.get('userInput')
            second_input = data.get('secondInput')
            third_input = data.get('thirdInput')
            fourth_input = data.get('fourthInput')
            fifth_input = data.get('fifthInput')
            prediction = data.get('prediction')


            # Calculate the total
            total = int(user_input) + int(second_input) + int(third_input) + int(fourth_input) + int(fifth_input)

            # Check if the total matches the prediction
            result = "Correct" if str(total) == prediction else "Incorrect"

            # Save the game record
            PredictionGameRecord.objects.create(
                student_name=student_name,
                user_input=user_input,
                prediction=prediction,
                second_input=second_input,
                third_input=third_input,
                fourth_input=fourth_input,
                fifth_input=fifth_input,
                result=result
            )

            return JsonResponse({
                'message': 'Result checked successfully.',
                'total': total,
                'prediction': prediction,
                'result': result
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request.'}, status=400)