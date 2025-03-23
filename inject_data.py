import os
import django
import random
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interacteach.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from courses.models import Course, Module, Lesson, Enrollment, LessonProgress

def create_users():
    """Create sample users"""
    print("Creating sample users...")
    
    # Create instructor users
    instructors = [
        {'username': 'john_instructor', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Smith'},
        {'username': 'sarah_instructor', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Johnson'},
        {'username': 'michael_instructor', 'email': 'michael@example.com', 'first_name': 'Michael', 'last_name': 'Brown'},
    ]
    
    # Create student users
    students = [
        {'username': 'student1', 'email': 'student1@example.com', 'first_name': 'Alex', 'last_name': 'Wilson'},
        {'username': 'student2', 'email': 'student2@example.com', 'first_name': 'Emma', 'last_name': 'Davis'},
        {'username': 'student3', 'email': 'student3@example.com', 'first_name': 'James', 'last_name': 'Miller'},
    ]
    
    created_instructors = []
    created_students = []
    
    # Create instructor accounts
    for instructor in instructors:
        user, created = User.objects.get_or_create(
            username=instructor['username'],
            defaults={
                'email': instructor['email'],
                'first_name': instructor['first_name'],
                'last_name': instructor['last_name'],
                'is_staff': True
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created instructor: {user.username}")
        else:
            print(f"Instructor already exists: {user.username}")
        
        created_instructors.append(user)
    
    # Create student accounts
    for student in students:
        user, created = User.objects.get_or_create(
            username=student['username'],
            defaults={
                'email': student['email'],
                'first_name': student['first_name'],
                'last_name': student['last_name']
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created student: {user.username}")
        else:
            print(f"Student already exists: {user.username}")
        
        created_students.append(user)
    
    return created_instructors, created_students

def create_courses(instructors):
    """Create sample courses"""
    print("\nCreating sample courses...")
    
    courses_data = [
        {
            'title': 'Introduction to Python Programming',
            'description': 'Learn the basics of Python programming language. This course covers variables, data types, control structures, functions, and more.',
            'instructor_name': f"{instructors[0].first_name} {instructors[0].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '4 weeks',
            'level': 'beginner'
        },
        {
            'title': 'Web Development with Django',
            'description': 'Build web applications using the Django framework. Learn about models, views, templates, forms, and authentication.',
            'instructor_name': f"{instructors[1].first_name} {instructors[1].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '6 weeks',
            'level': 'intermediate'
        },
        {
            'title': 'Advanced Data Science',
            'description': 'Explore advanced topics in data science including machine learning, neural networks, and data visualization.',
            'instructor_name': f"{instructors[2].first_name} {instructors[2].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '8 weeks',
            'level': 'advanced'
        },
        {
            'title': 'Mobile App Development',
            'description': 'Learn to build mobile applications for iOS and Android using React Native.',
            'instructor_name': f"{instructors[0].first_name} {instructors[0].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '6 weeks',
            'level': 'intermediate'
        },
        {
            'title': 'Introduction to JavaScript',
            'description': 'Learn the fundamentals of JavaScript programming for web development.',
            'instructor_name': f"{instructors[1].first_name} {instructors[1].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '4 weeks',
            'level': 'beginner'
        }
    ]
    
    created_courses = []
    
    for i, course_data in enumerate(courses_data):
        instructor = instructors[i % len(instructors)]
        
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults={
                'slug': slugify(course_data['title']),
                'description': course_data['description'],
                'instructor': course_data['instructor_name'],
                'image': course_data['image'],
                'duration': course_data['duration'],
                'level': course_data['level']
            }
        )
        
        if created:
            print(f"Created course: {course.title}")
        else:
            print(f"Course already exists: {course.title}")
        
        created_courses.append(course)
    
    return created_courses

def create_modules_and_lessons(courses):
    """Create modules and lessons for each course"""
    print("\nCreating modules and lessons...")
    
    for course in courses:
        # Create 3-5 modules per course
        num_modules = random.randint(3, 5)
        
        for i in range(1, num_modules + 1):
            module, created = Module.objects.get_or_create(
                course=course,
                title=f"Module {i}: {get_module_title(course, i)}",
                defaults={
                    'description': f"This module covers important topics related to {course.title}.",
                    'order': i
                }
            )
            
            if created:
                print(f"Created module: {module.title}")
            else:
                print(f"Module already exists: {module.title}")
            
            # Create 3-6 lessons per module
            num_lessons = random.randint(3, 6)
            
            for j in range(1, num_lessons + 1):
                lesson, created = Lesson.objects.get_or_create(
                    module=module,
                    title=f"Lesson {j}: {get_lesson_title(module, j)}",
                    defaults={
                        'content': get_lesson_content(module, j),
                        'order': j
                    }
                )
                
                if created:
                    print(f"  Created lesson: {lesson.title}")
                else:
                    print(f"  Lesson already exists: {lesson.title}")

def get_module_title(course, module_number):
    """Generate a module title based on the course"""
    if course.title.lower().find('python') >= 0:
        modules = ['Getting Started', 'Data Structures', 'Functions and Classes', 'File Handling', 'Advanced Topics']
    elif course.title.lower().find('django') >= 0:
        modules = ['Django Basics', 'Models and Databases', 'Views and Templates', 'Forms and Validation', 'Authentication']
    elif course.title.lower().find('data science') >= 0:
        modules = ['Data Preprocessing', 'Exploratory Analysis', 'Machine Learning Basics', 'Neural Networks', 'Data Visualization']
    elif course.title.lower().find('mobile') >= 0:
        modules = ['React Native Basics', 'Components and Props', 'State Management', 'Navigation', 'API Integration']
    elif course.title.lower().find('javascript') >= 0:
        modules = ['JavaScript Basics', 'DOM Manipulation', 'Events and Listeners', 'Asynchronous JavaScript', 'ES6 Features']
    else:
        modules = ['Introduction', 'Core Concepts', 'Advanced Topics', 'Practical Applications', 'Final Project']
    
    return modules[min(module_number - 1, len(modules) - 1)]

def get_lesson_title(module, lesson_number):
    """Generate a lesson title based on the module"""
    module_name = module.title.lower()
    
    if 'getting started' in module_name or 'introduction' in module_name or 'basics' in module_name:
        lessons = ['Introduction to the Course', 'Setting Up Your Environment', 'Hello World Program', 'Basic Syntax', 'Variables and Data Types', 'Control Structures']
    elif 'data structures' in module_name:
        lessons = ['Lists and Tuples', 'Dictionaries', 'Sets', 'List Comprehensions', 'Working with Collections', 'Advanced Data Structures']
    elif 'functions' in module_name or 'classes' in module_name:
        lessons = ['Defining Functions', 'Parameters and Return Values', 'Lambda Functions', 'Object-Oriented Programming', 'Classes and Objects', 'Inheritance and Polymorphism']
    elif 'models' in module_name or 'databases' in module_name:
        lessons = ['Database Basics', 'Creating Models', 'Migrations', 'Querysets', 'Relationships', 'Advanced Queries']
    elif 'views' in module_name or 'templates' in module_name:
        lessons = ['URL Patterns', 'Function-Based Views', 'Class-Based Views', 'Template Basics', 'Template Inheritance', 'Template Tags and Filters']
    else:
        lessons = ['Lesson Introduction', 'Core Concepts', 'Practical Examples', 'Common Pitfalls', 'Best Practices', 'Summary and Next Steps']
    
    return lessons[min(lesson_number - 1, len(lessons) - 1)]

def get_lesson_content(module, lesson_number):
    """Generate lesson content"""
    return f"""
# {module.title} - Lesson {lesson_number}

Welcome to this lesson! In this lesson, you will learn about important concepts related to {module.title}.

## Learning Objectives

- Understand the key concepts of this lesson
- Apply what you've learned to practical examples
- Solve common problems in this area

## Main Content

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, 
nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.

### Section 1

Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

### Section 2

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Summary

In this lesson, you learned about:

1. Important concept 1
2. Important concept 2
3. Important concept 3

## Next Steps

In the next lesson, we'll build on these concepts and explore more advanced topics.
"""

def create_enrollments(students, courses):
    """Create enrollments for students"""
    print("\nCreating enrollments...")
    
    for student in students:
        # Enroll each student in 2-3 random courses
        num_enrollments = random.randint(2, 3)
        selected_courses = random.sample(courses, min(num_enrollments, len(courses)))
        
        for course in selected_courses:
            enrollment, created = Enrollment.objects.get_or_create(
                user=student,
                course=course,
                defaults={
                    'completed': False
                }
            )
            
            if created:
                print(f"Enrolled {student.username} in {course.title}")
            else:
                print(f"{student.username} is already enrolled in {course.title}")
            
            # Create lesson progress for some lessons
            lessons = Lesson.objects.filter(module__course=course)
            
            # Complete 30-70% of lessons
            completion_percentage = random.uniform(0.3, 0.7)
            lessons_to_complete = random.sample(
                list(lessons), 
                int(len(lessons) * completion_percentage)
            )
            
            for lesson in lessons_to_complete:
                lesson_progress, created = LessonProgress.objects.get_or_create(
                    enrollment=enrollment,
                    lesson=lesson,
                    defaults={
                        'completed': True
                    }
                )
                
                if created:
                    print(f"  Created progress for {lesson.title}")
                else:
                    print(f"  Progress already exists for {lesson.title}")
            
            # Check if all lessons are completed
            if LessonProgress.objects.filter(enrollment=enrollment, completed=True).count() == lessons.count():
                enrollment.completed = True
                enrollment.save()
                print(f"  Marked enrollment as completed for {student.username} in {course.title}")

def main():
    print("="*80)
    print("CREATING SAMPLE DATA FOR INTERACTEACH".center(80))
    print("="*80)
    
    instructors, students = create_users()
    courses = create_courses(instructors)
    create_modules_and_lessons(courses)
    create_enrollments(students, courses)
    
    print("\n" + "="*80)
    print("SAMPLE DATA CREATION COMPLETE!".center(80))
    print("="*80)
    print("\nYou can now run 'python manage.py runserver' to start your application.")
    print("\nSample user credentials:")
    print("  Admin: username='admin', password=<the one you entered>")
    print("  Instructors: username='john_instructor', 'sarah_instructor', 'michael_instructor', password='password123'")
    print("  Students: username='student1', 'student2', 'student3', password='password123'")

if __name__ == "__main__":
    main()

