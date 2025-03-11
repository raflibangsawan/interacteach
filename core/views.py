from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Course

@login_required
def home(request):
    courses = [
        {
            'id': 1,
            'title': 'Introduction to Python',
            'description': 'Learn the basics of Python programming language.',
            'instructor': 'John Doe',
            'image': '/static/images/python-logo.jpg'
        },
        {
            'id': 2,
            'title': 'Web Development with Django',
            'description': 'Build web applications using Django framework.',
            'instructor': 'Jane Smith',
            'image': '/static/images/django-logo.jpg'
        },
        {
            'id': 3,
            'title': 'Data Science Fundamentals',
            'description': 'Introduction to data analysis and visualization.',
            'instructor': 'Alex Johnson',
            'image': '/static/images/course-placeholder.jpg'
        },
        {
            'id': 4,
            'title': 'Machine Learning Basics',
            'description': 'Learn the fundamentals of machine learning algorithms.',
            'instructor': 'Sarah Williams',
            'image': '/static/images/course-placeholder.jpg'
        },
        {
            'id': 5,
            'title': 'iOS App Development',
            'description': 'Create applications for Apple devices using Swift.',
            'instructor': 'Michael Brown',
            'image': '/static/images/course-placeholder.jpg'
        },
        {
            'id': 6,
            'title': 'UX/UI Design Principles',
            'description': 'Learn to create user-friendly and visually appealing interfaces.',
            'instructor': 'Emily Davis',
            'image': '/static/images/course-placeholder.jpg'
        },
    ]
    
    return render(request, 'core/home.html', {'courses': courses})


def logout_view(request):
    logout(request)
    return redirect('login')