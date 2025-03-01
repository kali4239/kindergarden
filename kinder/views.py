import json
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
                    return redirect('student_dashboard', student_id=student_id)
                else:
                    form.add_error(None, "Invalid password")
            except Student.DoesNotExist:
                form.add_error(None, "Student ID not found")
    else:
        form = StudentLoginForm()
    
    return render(request, 'student_login.html', {'form': form})

def student_dashboard(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
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
    return redirect('admin_dashboard')

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




