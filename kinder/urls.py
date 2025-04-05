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
    # games
    path("generate_balloon/", views.generate_balloon, name="generate_balloon"),
    path('start_game/', views.start_game, name='start_game'),
    # path('save_game_progress/', views.save_game_progress, name='save_game_progress'),
    path('end_game/', views.end_game, name='end_game'),
    # puzzle game 
    path("puzzle_game/", views.puzzle_game_page, name="puzzle_game"),
    path("get_images_for_topic/", views.get_images_for_topic, name="get_images_for_topic"),
    path("save_puzzle_game/", views.save_puzzle_game, name="save_puzzle_game"),
    path('get_puzzle_scores/', views.get_puzzle_scores, name='get_puzzle_scores'),
        # memory game 
    path("chimp_memory_game/", views.chimp_memory_game_page, name="chimp_memory_game"),
    path("start_chimp_game/", views.start_chimp_game, name="start_chimp_game"),
    path("check_chimp_game/", views.check_chimp_game, name="check_chimp_game"),
    path("drawing_game/",views.drawing_game_page, name='drawing_game'),
            #URLs for XO game
    path("xo_game/", views.xo_game_page, name="xo_game"),
    path("send_xo_request/", views.send_xo_request, name="send_xo_request"),
    path("accept_xo_request/<int:request_id>/", views.accept_xo_request, name="accept_xo_request"),
    path("get_xo_game_state/", views.get_xo_game_state, name="get_xo_game_state"),
    path("make_xo_move/", views.make_xo_move, name="make_xo_move"),
    path('trigger_toss_coin/', views.trigger_toss_coin, name='trigger_toss_coin'),
    path('get_notifications/', views.get_notifications, name='get_notifications'),
    path('get_toss_result/', views.get_toss_result, name='get_toss_result'),
    path('select_toss_option/', views.select_toss_option, name='select_toss_option'),
    path('get_request_sender/', views.get_request_sender, name='get_request_sender'),
    path('api/game-progress/', views.GameProgressAPI.as_view(), name='game-progress-api'),
    path('api/get-current-student/',views.get_current_student, name='get-current-student'),
    # Number prediction
    path("prediction_game/", views.prediction_game_page, name="prediction_game"),
    path("generate_prediction/", views.generate_prediction, name="generate_prediction"),
    path("generate_third_input/", views.generate_third_input, name="generate_third_input"),
    path("generate_fifth_input/", views.generate_fifth_input, name="generate_fifth_input"),
    path("check_result/", views.check_result, name="check_result"),

    
    
    
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT) 