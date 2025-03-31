from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
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
]

