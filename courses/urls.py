from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
]

