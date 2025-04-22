from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Student views
    path('', views.course_list, name='course_list'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    
    # Instructor views
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/become/', views.become_instructor, name='become_instructor'),
    path('instructor/courses/', views.instructor_courses, name='instructor_courses'),
    path('instructor/courses/create/', views.create_course, name='create_course'),
    path('instructor/courses/<slug:course_slug>/edit/', views.edit_course, name='edit_course'),
    path('instructor/courses/<slug:course_slug>/delete/', views.delete_course, name='delete_course'),
    path('instructor/courses/<slug:course_slug>/publish/', views.publish_course, name='publish_course'),
    path('instructor/courses/<slug:course_slug>/unpublish/', views.unpublish_course, name='unpublish_course'),
    path('instructor/courses/<slug:course_slug>/modules/create/', views.create_module, name='create_module'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/delete/', views.delete_module, name='delete_module'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/lessons/create/', views.create_lesson, name='create_lesson'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    
    # Forum views
    path('<slug:course_slug>/forum/', views.forum_thread_list, name='forum_thread_list'),
    path('<slug:course_slug>/forum/create/', views.forum_thread_create, name='forum_thread_create'),
    path('<slug:course_slug>/forum/<int:thread_id>/', views.forum_thread_detail, name='forum_thread_detail'),
    path('<slug:course_slug>/forum/<int:thread_id>/edit/', views.forum_thread_edit, name='forum_thread_edit'),
    path('<slug:course_slug>/forum/<int:thread_id>/delete/', views.forum_thread_delete, name='forum_thread_delete'),
    path('<slug:course_slug>/forum/<int:thread_id>/pin/', views.forum_thread_pin, name='forum_thread_pin'),
    path('<slug:course_slug>/forum/<int:thread_id>/lock/', views.forum_thread_lock, name='forum_thread_lock'),
    path('<slug:course_slug>/forum/<int:thread_id>/reply/<int:reply_id>/edit/', views.forum_reply_edit, name='forum_reply_edit'),
    path('<slug:course_slug>/forum/<int:thread_id>/reply/<int:reply_id>/delete/', views.forum_reply_delete, name='forum_reply_delete'),
    path('<slug:course_slug>/forum/<int:thread_id>/reply/<int:reply_id>/solution/', views.forum_reply_mark_solution, name='forum_reply_mark_solution'),
    
    # Quiz views - Instructor
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/quiz/create/', views.create_quiz, name='create_quiz'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/quiz/edit/', views.edit_quiz, name='edit_quiz'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/quiz/delete/', views.delete_quiz, name='delete_quiz'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/quiz/', views.quiz_detail_instructor, name='quiz_detail_instructor'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/quiz/question/create/', views.create_question, name='create_question'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/quiz/question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('instructor/courses/<slug:course_slug>/modules/<int:module_id>/quiz/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    
    # Quiz views - Student
    path('<slug:course_slug>/modules/<int:module_id>/quiz/', views.quiz_detail_student, name='quiz_detail_student'),
    path('<slug:course_slug>/modules/<int:module_id>/quiz/take/', views.take_quiz, name='take_quiz'),
    path('<slug:course_slug>/modules/<int:module_id>/quiz/results/<int:attempt_id>/', views.quiz_results, name='quiz_results'),
]
