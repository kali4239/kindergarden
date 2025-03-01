from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="index"),
    path('calendar/', views.calendar_view, name='calendar'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    # path('add-event/', views.add_event, name='add_event'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('custom-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('custom-admin/add-student/', views.add_student, name='add_student'),
    # path('custom-admin/add-parent/', views.add_parent, name='add_parent'),
    # path('custom-admin/add-homework/', views.add_homework, name='add_homework'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/<str:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('parent/login/', views.parent_login, name='parent_login'),
    path('parent/dashboard/<str:parent_id>/', views.parent_dashboard, name='parent_dashboard'),
    path('update_profile/<str:student_id>/', views.update_profile, name='update_profile'),
    path('student/submit-activity/<str:student_id>/', views.submit_activity, name='submit_activity'),
    path('update-activity-status/<int:activity_id>/', views.update_activity_status, name='update_activity_status'),
    path('update-activity-status/<int:activity_id>/', views.update_activity_status, name='update_activity_status'),
    path('submit-activity/<str:student_id>/', views.submit_activity, name='submit_activity'),
    path('logout/', views.logout_view, name='logout'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('non-teaching/dashboard/', views.non_teaching_dashboard, name='non_teaching_dashboard'),
    path('assignment/assign/', views.assign_homework, name='assign_homework'),
    path('assignment/edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('assignment/delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    # path('assignment/revoke/<int:assignment_id>/', views.revoke_assignment, name='revoke_assignment'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT) 