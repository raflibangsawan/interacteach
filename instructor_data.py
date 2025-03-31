"""
This script creates instructor profiles and updates existing courses with instructor data.
"""

import os
import django
import random
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interacteach.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from courses.models import Course, InstructorProfile

def create_instructor_profiles():
    """Create instructor profiles for existing users"""
    print("Creating instructor profiles...")
    
    # Get users who might be instructors (staff users or users with 'instructor' in username)
    potential_instructors = User.objects.filter(
        is_staff=True
    ) | User.objects.filter(
        username__icontains='instructor'
    )
    
    # If no potential instructors found, use the first few users
    if not potential_instructors:
        potential_instructors = User.objects.all()[:3]
    
    instructor_bios = [
        "Experienced educator with over 10 years of teaching experience in computer science and programming.",
        "Passionate about sharing knowledge and helping students achieve their learning goals.",
        "Industry professional with extensive experience in software development and web technologies.",
        "Former university professor with a PhD in Computer Science, specializing in artificial intelligence.",
        "Self-taught developer who loves to break down complex concepts into simple, understandable lessons."
    ]
    
    expertise_areas = [
        "Web Development, JavaScript, React, Node.js",
        "Python Programming, Data Science, Machine Learning",
        "Mobile App Development, React Native, Flutter",
        "Database Design, SQL, NoSQL, Data Modeling",
        "DevOps, Cloud Computing, AWS, Docker"
    ]
    
    websites = [
        "https://example-instructor.com",
        "https://teachingtech.edu",
        "https://codementor.io/profile",
        "https://github.com/instructor",
        "https://linkedin.com/in/instructor"
    ]
    
    profile_images = [
        "/static/courses/images/instructor-1.jpg",
        "/static/courses/images/instructor-2.jpg",
        "/static/courses/images/instructor-3.jpg",
        "/static/courses/images/instructor-4.jpg",
        "/static/courses/images/instructor-placeholder.jpg"
    ]
    
    created_profiles = []
    
    for user in potential_instructors:
        # Skip if profile already exists
        if InstructorProfile.objects.filter(user=user).exists():
            print(f"Instructor profile already exists for {user.username}")
            created_profiles.append(InstructorProfile.objects.get(user=user))
            continue
        
        # Create instructor profile
        profile = InstructorProfile.objects.create(
            user=user,
            bio=random.choice(instructor_bios),
            expertise=random.choice(expertise_areas),
            website=random.choice(websites),
            profile_image=random.choice(profile_images)
        )
        
        print(f"Created instructor profile for {user.username}")
        created_profiles.append(profile)
    
    return created_profiles

def update_courses_with_instructors(instructor_profiles):
    """Update existing courses to link to instructor users"""
    print("\nUpdating courses with instructor data...")
    
    # Get all courses
    courses = Course.objects.all()
    
    if not courses:
        print("No courses found to update")
        return
    
    # Distribute courses among instructors
    for i, course in enumerate(courses):
        instructor = instructor_profiles[i % len(instructor_profiles)]
        
        # Update course with instructor user
        course.instructor_user = instructor.user
        course.instructor = instructor.user.get_full_name() or instructor.user.username
        course.is_published = random.choice([True, False])
        course.save()
        
        print(f"Updated course '{course.title}' with instructor {instructor.user.username}")

def create_new_courses(instructor_profiles):
    """Create some new courses for instructors"""
    print("\nCreating new courses for instructors...")
    
    course_titles = [
        "Advanced JavaScript Techniques",
        "Data Visualization with Python",
        "Building RESTful APIs",
        "Mobile App Development Fundamentals",
        "Cloud Computing Essentials",
        "Database Design Principles",
        "Machine Learning for Beginners",
        "Web Security Best Practices",
        "DevOps and Continuous Integration",
        "Responsive Web Design Masterclass"
    ]
    
    course_descriptions = [
        "Master advanced JavaScript concepts including closures, prototypes, async/await, and modern ES6+ features.",
        "Learn how to create compelling visualizations using Python libraries like Matplotlib, Seaborn, and Plotly.",
        "Design and build robust RESTful APIs using modern frameworks and best practices for web and mobile applications.",
        "Get started with mobile app development using cross-platform technologies to build iOS and Android apps.",
        "Understand cloud computing concepts and learn to deploy applications on major cloud platforms.",
        "Learn the principles of good database design, normalization, and optimization techniques.",
        "An introduction to machine learning concepts, algorithms, and practical applications using Python.",
        "Protect your web applications from common security threats and vulnerabilities.",
        "Implement DevOps practices including CI/CD pipelines, containerization, and infrastructure as code.",
        "Create beautiful, responsive websites that work on all devices using modern CSS techniques."
    ]
    
    durations = [
        "4 weeks",
        "6 weeks",
        "8 weeks",
        "10 weeks",
        "12 weeks"
    ]
    
    images = [
        "/static/courses/images/course-1.jpg",
        "/static/courses/images/course-2.jpg",
        "/static/courses/images/course-3.jpg",
        "/static/courses/images/course-4.jpg",
        "/static/courses/images/course-placeholder.jpg"
    ]
    
    # Create 5-10 new courses
    num_new_courses = random.randint(5, 10)
    
    for i in range(num_new_courses):
        # Select a random instructor
        instructor = random.choice(instructor_profiles)
        
        # Select a random title that hasn't been used yet
        title = course_titles.pop(0) if course_titles else f"New Course {i+1}"
        
        # Create the course
        course = Course.objects.create(
            title=title,
            slug=slugify(title),
            description=course_descriptions.pop(0) if course_descriptions else f"Description for {title}",
            instructor=instructor.user.get_full_name() or instructor.user.username,
            instructor_user=instructor.user,
            image=random.choice(images),
            duration=random.choice(durations),
            is_published=random.choice([True, False])
        )
        
        print(f"Created new course '{course.title}' for instructor {instructor.user.username}")

def main():
    print("="*80)
    print("CREATING INSTRUCTOR DATA FOR INTERACTEACH".center(80))
    print("="*80)
    
    # Create instructor profiles
    instructor_profiles = create_instructor_profiles()
    
    if not instructor_profiles:
        print("No instructor profiles created. Please make sure there are users in the database.")
        return
    
    # Update existing courses with instructor data
    update_courses_with_instructors(instructor_profiles)
    
    # Create new courses for instructors
    create_new_courses(instructor_profiles)
    
    print("\n" + "="*80)
    print("INSTRUCTOR DATA CREATION COMPLETE!".center(80))
    print("="*80)
    print("\nYou can now run 'python manage.py runserver' to start your application.")
    print("\nInstructor accounts:")
    for profile in instructor_profiles:
        print(f"  - {profile.user.username} ({profile.user.email})")

if __name__ == "__main__":
    main()

