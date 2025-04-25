"""
This script completely resets the database and creates fresh data for high school courses.
WARNING: This will delete your database and all data will be lost!
"""

import os
import django
import shutil
import subprocess
import sys
import getpass
import random
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interacteach.settings')

def confirm_reset():
    """Confirm with the user before proceeding"""
    print("\n" + "="*80)
    print("WARNING: This will DELETE your database and RESET all migrations!")
    print("ALL DATA WILL BE LOST!")
    print("="*80 + "\n")
    
    confirm = input("Are you sure you want to continue? (type 'yes' to confirm): ")
    return confirm.lower() == 'yes'

def delete_database():
    """Delete the SQLite database file"""
    print("\n[Step 1] Deleting database...")
    
    db_file = 'db.sqlite3'
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✓ Deleted {db_file}")
    else:
        print(f"✓ {db_file} not found, skipping")

def delete_migrations():
    """Delete all migration files except __init__.py"""
    print("\n[Step 2] Deleting migration files...")
    
    # List of apps to clean migrations for
    apps = ['core', 'courses', 'instructor']
    
    for app in apps:
        migrations_dir = os.path.join(app, 'migrations')
        
        if not os.path.exists(migrations_dir):
            print(f"✓ No migrations directory found for {app}, skipping")
            continue
        
        # Make sure __init__.py exists
        init_file = os.path.join(migrations_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                pass
            print(f"✓ Created {init_file}")
        
        # Delete all other migration files
        count = 0
        for filename in os.listdir(migrations_dir):
            if filename != '__init__.py' and filename.endswith('.py'):
                file_path = os.path.join(migrations_dir, filename)
                os.remove(file_path)
                count += 1
        
        print(f"✓ Deleted {count} migration files from {app}")

def create_new_migrations():
    """Create new initial migrations for all apps"""
    print("\n[Step 3] Creating new migrations...")
    
    # List of apps to create migrations for
    apps = ['core', 'courses', 'instructor']
    
    for app in apps:
        print(f"Creating migrations for {app}...")
        result = subprocess.run(
            [sys.executable, 'manage.py', 'makemigrations', app],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Successfully created migrations for {app}")
        else:
            print(f"✗ Failed to create migrations for {app}")
            print(f"Error: {result.stderr}")

def apply_migrations():
    """Apply all migrations"""
    print("\n[Step 4] Applying migrations...")
    
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Successfully applied all migrations")
    else:
        print("✗ Failed to apply migrations")
        print(f"Error: {result.stderr}")

def create_superuser():
    """Create a new superuser"""
    print("\n[Step 5] Creating superuser...")
    
    username = input("Enter username (default: admin): ") or "admin"
    email = input("Enter email (default: admin@example.com): ") or "admin@example.com"
    
    # Get password securely
    while True:
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password == password_confirm:
            break
        else:
            print("Passwords don't match. Please try again.")
    
    # Set environment variables for non-interactive createsuperuser
    os.environ['DJANGO_SUPERUSER_USERNAME'] = username
    os.environ['DJANGO_SUPERUSER_EMAIL'] = email
    os.environ['DJANGO_SUPERUSER_PASSWORD'] = password
    
    result = subprocess.run(
        [sys.executable, 'manage.py', 'createsuperuser', '--noinput'],
        capture_output=True,
        text=True
    )
    
    # Clean up environment variables
    del os.environ['DJANGO_SUPERUSER_USERNAME']
    del os.environ['DJANGO_SUPERUSER_EMAIL']
    del os.environ['DJANGO_SUPERUSER_PASSWORD']
    
    if result.returncode == 0:
        print(f"✓ Successfully created superuser: {username}")
    else:
        print("✗ Failed to create superuser")
        print(f"Error: {result.stderr}")

# Now setup Django for model operations
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from courses.models import Course, Module, Lesson, Enrollment, LessonProgress, InstructorProfile, ForumThread, ForumReply

def create_users():
    """Create sample users"""
    print("\n[Step 6] Creating sample users...")
    
    # Create instructor users
    instructors = [
        {'username': 'math_teacher', 'email': 'math@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'physics_teacher', 'email': 'physics@example.com', 'first_name': 'Robert', 'last_name': 'Johnson'},
        {'username': 'chemistry_teacher', 'email': 'chemistry@example.com', 'first_name': 'Emily', 'last_name': 'Davis'},
    ]
    
    # Create student users
    students = [
        {'username': 'student1', 'email': 'student1@example.com', 'first_name': 'Alex', 'last_name': 'Wilson'},
        {'username': 'student2', 'email': 'student2@example.com', 'first_name': 'Emma', 'last_name': 'Taylor'},
        {'username': 'student3', 'email': 'student3@example.com', 'first_name': 'James', 'last_name': 'Miller'},
        {'username': 'student4', 'email': 'student4@example.com', 'first_name': 'Sophia', 'last_name': 'Brown'},
        {'username': 'student5', 'email': 'student5@example.com', 'first_name': 'Noah', 'last_name': 'Anderson'},
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
            
            # Create instructor profile
            InstructorProfile.objects.create(
                user=user,
                bio=f"Experienced high school {instructor['username'].split('_')[0]} teacher with a passion for education.",
                expertise=f"High School {instructor['username'].split('_')[0].title()}",
                website=f"https://www.example.com/{instructor['username']}"
            )
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

def create_highschool_courses(instructors):
    """Create high school courses"""
    print("\n[Step 7] Creating high school courses...")
    
    courses_data = [
        {
            'title': 'High School Algebra and Geometry',
            'description': 'This course covers fundamental concepts of high school algebra and geometry, including equations, inequalities, functions, transformations, and geometric proofs.',
            'instructor': f"{instructors[0].first_name} {instructors[0].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '36 weeks',
            'level': 'high school'
        },
        {
            'title': 'High School Physics: Mechanics and Waves',
            'description': 'This course introduces high school students to the fundamental principles of physics, focusing on mechanics, energy, momentum, and wave phenomena.',
            'instructor': f"{instructors[1].first_name} {instructors[1].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '36 weeks',
            'level': 'high school'
        },
        {
            'title': 'High School Chemistry: Atoms to Reactions',
            'description': 'This comprehensive chemistry course covers atomic structure, periodic trends, chemical bonding, stoichiometry, and chemical reactions for high school students.',
            'instructor': f"{instructors[2].first_name} {instructors[2].last_name}",
            'image': '/static/courses/images/course-placeholder.jpg',
            'duration': '36 weeks',
            'level': 'high school'
        }
    ]
    
    created_courses = []
    
    for i, course_data in enumerate(courses_data):
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults={
                'slug': slugify(course_data['title']),
                'description': course_data['description'],
                'instructor': course_data['instructor'],
                'image': course_data['image'],
                'duration': course_data['duration'],
                'is_published': True
            }
        )
        
        if created:
            print(f"Created course: {course.title}")
        else:
            print(f"Course already exists: {course.title}")
        
        created_courses.append(course)
    
    return created_courses

def create_math_modules_and_lessons(course):
    """Create modules and lessons for math course"""
    print(f"\nCreating modules and lessons for {course.title}...")
    
    math_modules = [
        {
            'title': 'Module 1: Foundations of Algebra',
            'description': 'In this module, we cover the essential foundations of algebra that will be used throughout your high school math journey.',
            'order': 1,
            'lessons': [
                {'title': 'Real Numbers and Properties', 'order': 1},
                {'title': 'Algebraic Expressions', 'order': 2},
                {'title': 'Solving Linear Equations', 'order': 3},
                {'title': 'Applications of Linear Equations', 'order': 4},
                {'title': 'Linear Inequalities', 'order': 5}
            ]
        },
        {
            'title': 'Module 2: Functions and Graphing',
            'description': 'This module explores the concept of functions, their graphs, and how to analyze them.',
            'order': 2,
            'lessons': [
                {'title': 'Introduction to Functions', 'order': 1},
                {'title': 'Linear Functions and Slope', 'order': 2},
                {'title': 'Function Notation and Evaluation', 'order': 3},
                {'title': 'Transformations of Functions', 'order': 4},
                {'title': 'Quadratic Functions', 'order': 5}
            ]
        },
        {
            'title': 'Module 3: Systems of Equations',
            'description': 'This module covers methods for solving systems of linear and nonlinear equations.',
            'order': 3,
            'lessons': [
                {'title': 'Graphical Solutions to Systems', 'order': 1},
                {'title': 'Solving Systems by Substitution', 'order': 2},
                {'title': 'Solving Systems by Elimination', 'order': 3},
                {'title': 'Applications of Systems of Equations', 'order': 4},
                {'title': 'Systems of Linear Inequalities', 'order': 5}
            ]
        },
        {
            'title': 'Module 4: Geometry Fundamentals',
            'description': 'This module introduces the fundamental concepts of geometry and geometric reasoning.',
            'order': 4,
            'lessons': [
                {'title': 'Points, Lines, and Planes', 'order': 1},
                {'title': 'Angles and Triangles', 'order': 2},
                {'title': 'Congruence and Similarity', 'order': 3},
                {'title': 'Quadrilaterals and Polygons', 'order': 4},
                {'title': 'Circle Properties', 'order': 5}
            ]
        },
        {
            'title': 'Module 5: Geometric Measurement',
            'description': 'This module covers techniques for measuring geometric figures and calculating area, perimeter, and volume.',
            'order': 5,
            'lessons': [
                {'title': 'Perimeter and Circumference', 'order': 1},
                {'title': 'Area of Polygons', 'order': 2},
                {'title': 'Area of Circles and Sectors', 'order': 3},
                {'title': 'Surface Area', 'order': 4},
                {'title': 'Volume of Three-Dimensional Figures', 'order': 5}
            ]
        }
    ]
    
    for module_data in math_modules:
        module, created = Module.objects.get_or_create(
            course=course,
            title=module_data['title'],
            defaults={
                'description': module_data['description'],
                'order': module_data['order']
            }
        )
        
        if created:
            print(f"Created module: {module.title}")
        else:
            print(f"Module already exists: {module.title}")
        
        # Create lessons for this module
        for lesson_data in module_data['lessons']:
            lesson, created = Lesson.objects.get_or_create(
                module=module,
                title=lesson_data['title'],
                defaults={
                    'content': get_lesson_content_for_math(module, lesson_data['title']),
                    'order': lesson_data['order']
                }
            )
            
            if created:
                print(f"  Created lesson: {lesson.title}")
            else:
                print(f"  Lesson already exists: {lesson.title}")

def create_physics_modules_and_lessons(course):
    """Create modules and lessons for physics course"""
    print(f"\nCreating modules and lessons for {course.title}...")
    
    physics_modules = [
        {
            'title': 'Module 1: Introduction to Physics',
            'description': 'This module introduces the fundamental concepts and methods of physics.',
            'order': 1,
            'lessons': [
                {'title': 'The Scientific Method in Physics', 'order': 1},
                {'title': 'Units and Measurements', 'order': 2},
                {'title': 'Vectors and Scalars', 'order': 3},
                {'title': 'Dimensional Analysis', 'order': 4},
                {'title': 'Problem-Solving Strategies', 'order': 5}
            ]
        },
        {
            'title': 'Module 2: Kinematics',
            'description': 'This module covers the mathematical description of motion without considering the causes.',
            'order': 2,
            'lessons': [
                {'title': 'Position, Distance, and Displacement', 'order': 1},
                {'title': 'Speed and Velocity', 'order': 2},
                {'title': 'Acceleration', 'order': 3},
                {'title': 'Equations of Motion for Constant Acceleration', 'order': 4},
                {'title': 'Free Fall and Projectile Motion', 'order': 5}
            ]
        },
        {
            'title': 'Module 3: Dynamics',
            'description': 'This module examines the causes of motion and the relationship between force and motion.',
            'order': 3,
            'lessons': [
                {'title': 'Force and Newton\'s First Law', 'order': 1},
                {'title': 'Newton\'s Second Law', 'order': 2},
                {'title': 'Newton\'s Third Law', 'order': 3},
                {'title': 'Types of Forces', 'order': 4},
                {'title': 'Applications of Newton\'s Laws', 'order': 5}
            ]
        },
        {
            'title': 'Module 4: Energy and Work',
            'description': 'This module explores the concepts of energy, work, and their conservation principles.',
            'order': 4,
            'lessons': [
                {'title': 'Work Done by a Constant Force', 'order': 1},
                {'title': 'Kinetic Energy', 'order': 2},
                {'title': 'Potential Energy', 'order': 3},
                {'title': 'Conservation of Energy', 'order': 4},
                {'title': 'Power', 'order': 5}
            ]
        },
        {
            'title': 'Module 5: Waves and Sound',
            'description': 'This module introduces wave phenomena and the specific case of sound waves.',
            'order': 5,
            'lessons': [
                {'title': 'Wave Properties and Classifications', 'order': 1},
                {'title': 'Wave Behavior: Reflection, Refraction, Diffraction', 'order': 2},
                {'title': 'Superposition and Standing Waves', 'order': 3},
                {'title': 'Sound Waves and Their Properties', 'order': 4},
                {'title': 'The Doppler Effect', 'order': 5}
            ]
        }
    ]
    
    for module_data in physics_modules:
        module, created = Module.objects.get_or_create(
            course=course,
            title=module_data['title'],
            defaults={
                'description': module_data['description'],
                'order': module_data['order']
            }
        )
        
        if created:
            print(f"Created module: {module.title}")
        else:
            print(f"Module already exists: {module.title}")
        
        # Create lessons for this module
        for lesson_data in module_data['lessons']:
            lesson, created = Lesson.objects.get_or_create(
                module=module,
                title=lesson_data['title'],
                defaults={
                    'content': get_lesson_content_for_physics(module, lesson_data['title']),
                    'order': lesson_data['order']
                }
            )
            
            if created:
                print(f"  Created lesson: {lesson.title}")
            else:
                print(f"  Lesson already exists: {lesson.title}")

def create_chemistry_modules_and_lessons(course):
    """Create modules and lessons for chemistry course"""
    print(f"\nCreating modules and lessons for {course.title}...")
    
    chemistry_modules = [
        {
            'title': 'Module 1: Matter and Measurement',
            'description': 'This module introduces the basic concepts of matter and the importance of measurement in chemistry.',
            'order': 1,
            'lessons': [
                {'title': 'Classification of Matter', 'order': 1},
                {'title': 'Physical and Chemical Properties', 'order': 2},
                {'title': 'Units of Measurement', 'order': 3},
                {'title': 'Uncertainty in Measurement', 'order': 4},
                {'title': 'Dimensional Analysis and Problem Solving', 'order': 5}
            ]
        },
        {
            'title': 'Module 2: Atomic Structure',
            'description': 'This module explores the structure of atoms and their components.',
            'order': 2,
            'lessons': [
                {'title': 'Development of Atomic Theory', 'order': 1},
                {'title': 'The Modern Atomic Model', 'order': 2},
                {'title': 'Isotopes and Atomic Mass', 'order': 3},
                {'title': 'Electron Configuration', 'order': 4},
                {'title': 'Periodic Trends', 'order': 5}
            ]
        },
        {
            'title': 'Module 3: Chemical Bonding',
            'description': 'This module examines how atoms combine to form compounds through chemical bonds.',
            'order': 3,
            'lessons': [
                {'title': 'Ionic Bonding', 'order': 1},
                {'title': 'Covalent Bonding', 'order': 2},
                {'title': 'Lewis Structures', 'order': 3},
                {'title': 'Molecular Geometry and VSEPR Theory', 'order': 4},
                {'title': 'Polarity and Intermolecular Forces', 'order': 5}
            ]
        },
        {
            'title': 'Module 4: Chemical Reactions',
            'description': 'This module covers the different types of chemical reactions and how to write balanced chemical equations.',
            'order': 4,
            'lessons': [
                {'title': 'Writing Chemical Equations', 'order': 1},
                {'title': 'Types of Chemical Reactions', 'order': 2},
                {'title': 'Balancing Chemical Equations', 'order': 3},
                {'title': 'Predicting Products of Chemical Reactions', 'order': 4},
                {'title': 'Oxidation-Reduction Reactions', 'order': 5}
            ]
        },
        {
            'title': 'Module 5: Stoichiometry',
            'description': 'This module explores the quantitative relationships in chemical reactions.',
            'order': 5,
            'lessons': [
                {'title': 'The Mole Concept', 'order': 1},
                {'title': 'Molar Mass', 'order': 2},
                {'title': 'Percent Composition', 'order': 3},
                {'title': 'Empirical and Molecular Formulas', 'order': 4},
                {'title': 'Stoichiometric Calculations', 'order': 5}
            ]
        }
    ]
    
    for module_data in chemistry_modules:
        module, created = Module.objects.get_or_create(
            course=course,
            title=module_data['title'],
            defaults={
                'description': module_data['description'],
                'order': module_data['order']
            }
        )
        
        if created:
            print(f"Created module: {module.title}")
        else:
            print(f"Module already exists: {module.title}")
        
        # Create lessons for this module
        for lesson_data in module_data['lessons']:
            lesson, created = Lesson.objects.get_or_create(
                module=module,
                title=lesson_data['title'],
                defaults={
                    'content': get_lesson_content_for_chemistry(module, lesson_data['title']),
                    'order': lesson_data['order']
                }
            )
            
            if created:
                print(f"  Created lesson: {lesson.title}")
            else:
                print(f"  Lesson already exists: {lesson.title}")

def get_lesson_content_for_math(module, lesson_title):
    """Generate lesson content for math lessons"""
    content = f"""
# {lesson_title}

## Learning Objectives

By the end of this lesson, you will be able to:
- Understand the key concepts related to {lesson_title.lower()}
- Apply these concepts to solve mathematical problems
- Connect these concepts to real-world applications

## Main Content

### Introduction to {lesson_title}

In high school algebra and geometry, {lesson_title.lower()} plays a crucial role in developing your mathematical reasoning skills. This lesson will provide a clear explanation of the concepts, along with examples and practice problems.

### Key Concepts

**Definition:** {get_math_definition(lesson_title)}

**Properties:** 
- Property 1: Example of a key property related to this concept
- Property 2: Another important property to understand
- Property 3: A final critical property to master

### Examples

**Example 1:**
Given a problem involving {lesson_title.lower()}, we can solve it by applying the following steps:
1. Step one
2. Step two
3. Step three

**Example 2:**
Here's another example that demonstrates a different aspect of {lesson_title.lower()}:
1. Step one
2. Step two
3. Step three

### Applications

{lesson_title} has many real-world applications, including:
1. Application in engineering
2. Application in finance
3. Application in computer science

## Practice Problems

1. Problem 1: A basic problem to test understanding
2. Problem 2: A more challenging problem
3. Problem 3: An advanced problem that combines multiple concepts

## Summary

In this lesson, we covered the fundamental concepts of {lesson_title.lower()}, including its definition, properties, and applications. Remember that practice is essential for mastering these concepts, so work through the practice problems and don't hesitate to ask questions if you're struggling.

## Next Steps

In our next lesson, we'll build on these concepts as we explore {get_math_next_topic(lesson_title)}.
"""
    return content

def get_lesson_content_for_physics(module, lesson_title):
    """Generate lesson content for physics lessons"""
    content = f"""
# {lesson_title}

## Learning Objectives

By the end of this lesson, you will be able to:
- Explain the core principles related to {lesson_title.lower()}
- Solve problems using the equations and concepts presented
- Apply these physics concepts to real-world scenarios

## Main Content

### Introduction to {lesson_title}

In the study of physics, {lesson_title.lower()} is a fundamental concept that helps us understand how the physical world works. This lesson will break down the key ideas and provide you with the tools to apply these concepts.

### Key Concepts

**Definition:** {get_physics_definition(lesson_title)}

**Relevant Equations:**
- Equation 1: $E = mc^2$ (example equation)
- Equation 2: $F = ma$ (example equation)
- Equation 3: $v = d/t$ (example equation)

### Demonstrations and Examples

**Example 1:**
A basic problem involving {lesson_title.lower()} can be solved as follows:
1. Given information
2. Step-by-step solution process
3. Final answer with units

**Example 2:**
A more complex scenario demonstrating {lesson_title.lower()}:
1. Problem setup
2. Application of relevant equations
3. Solution with analysis

### Real-World Applications

{lesson_title} appears in many aspects of our daily lives:
1. Application in transportation
2. Application in sports
3. Application in technology

## Laboratory Activity

In this virtual lab experiment, we will:
1. Set up a simulation to demonstrate {lesson_title.lower()}
2. Collect data and make observations
3. Analyze results and draw conclusions

## Practice Problems

1. Problem 1: Basic application of concepts
2. Problem 2: Intermediate problem requiring multiple steps
3. Problem 3: Challenge problem combining multiple physics principles

## Summary

In this lesson, we explored {lesson_title.lower()}, covering its theoretical foundations, mathematical representations, and practical applications. These concepts are building blocks for understanding more advanced physics topics.

## Next Steps

In our next lesson, we'll examine {get_physics_next_topic(lesson_title)}, which builds upon the principles we've learned today.
"""
    return content

def get_lesson_content_for_chemistry(module, lesson_title):
    """Generate lesson content for chemistry lessons"""
    content = f"""
# {lesson_title}

## Learning Objectives

By the end of this lesson, you will be able to:
- Define and explain the key concepts related to {lesson_title.lower()}
- Apply chemical principles to solve relevant problems
- Connect these chemistry concepts to everyday phenomena

## Main Content

### Introduction to {lesson_title}

Chemistry helps us understand the composition, properties, and transformations of matter. In this lesson, we'll explore {lesson_title.lower()}, which is essential for building your understanding of chemical principles.

### Key Concepts

**Definition:** {get_chemistry_definition(lesson_title)}

**Important Points:**
- Key point 1: Fundamental aspect of this topic
- Key point 2: Critical information to understand
- Key point 3: How this connects to broader chemistry principles

### Chemical Principles and Reactions

**Principle 1:**
The first important principle related to {lesson_title.lower()} can be demonstrated through:
1. Explanation of the principle
2. Example reaction or process
3. Visual representation (refer to diagram)

**Principle 2:**
Another important aspect of {lesson_title.lower()}:
1. Theoretical background
2. Practical implications
3. Common misconceptions

### Laboratory Application

In a chemistry lab, we might investigate {lesson_title.lower()} by:
1. Setting up an experiment
2. Making observations
3. Collecting and analyzing data
4. Drawing conclusions

### Real-World Applications

{lesson_title} has significant applications in:
1. Industrial processes
2. Environmental science
3. Biological systems
4. Everyday products

## Practice Problems

1. Problem 1: Basic concept application
2. Problem 2: Chemical calculations
3. Problem 3: Analysis of chemical reactions

## Summary

In this lesson, we explored the fundamentals of {lesson_title.lower()}, including its definition, principles, and applications. Understanding these concepts is crucial for building your knowledge of chemistry and seeing how chemical processes shape our world.

## Next Steps

Our next lesson will cover {get_chemistry_next_topic(lesson_title)}, which builds on today's concepts and expands our understanding of chemical systems.
"""
    return content

def get_math_definition(topic):
    """Generate a definition for math topics"""
    definitions = {
        'Real Numbers and Properties': 'Real numbers include all rational and irrational numbers on the number line. They have properties such as closure, commutativity, associativity, and distributivity.',
        'Algebraic Expressions': 'Algebraic expressions are mathematical phrases that can include variables, numbers, and operations like addition, subtraction, multiplication, and division.',
        'Solving Linear Equations': 'A linear equation is an equation where each term is either a constant or the product of a constant and a single variable raised to the power of 1.',
        'Applications of Linear Equations': 'Linear equations can be used to model and solve real-world problems involving unknown quantities with linear relationships.',
        'Linear Inequalities': 'Linear inequalities are mathematical statements that compare expressions using inequality symbols (<, >, ≤, ≥) rather than equality.',
    }
    return definitions.get(topic, 'A fundamental concept in high school mathematics that builds problem-solving skills.')

def get_physics_definition(topic):
    """Generate a definition for physics topics"""
    definitions = {
        'The Scientific Method in Physics': 'The scientific method is a systematic approach to investigating phenomena, acquiring new knowledge, and correcting previous findings through observation, measurement, and experimentation.',
        'Units and Measurements': 'Units and measurements form the foundation of physics by providing standard ways to quantify physical quantities and ensure consistency across observations.',
        'Vectors and Scalars': 'Vectors are quantities with both magnitude and direction, while scalars are quantities with only magnitude.',
        'Position, Distance, and Displacement': 'Position describes location, distance is the total path length traveled, and displacement is the straight-line distance and direction from initial to final position.',
        'Speed and Velocity': 'Speed is the rate of change of distance, while velocity is the rate of change of displacement (a vector quantity with both magnitude and direction).',
        'Force and Newton\'s First Law': 'Force is a push or pull that can cause an object to accelerate, and Newton\'s First Law states that an object at rest stays at rest, and an object in motion stays in motion at constant velocity, unless acted upon by an external force.',
    }
    return definitions.get(topic, 'A fundamental concept in physics that explains how the physical world operates.')

def get_chemistry_definition(topic):
    """Generate a definition for chemistry topics"""
    definitions = {
        'Classification of Matter': 'Matter can be classified as pure substances (elements and compounds) or mixtures (homogeneous and heterogeneous), based on composition.',
        'Physical and Chemical Properties': 'Physical properties can be observed without changing the substance\'s composition, while chemical properties describe how a substance can change into different substances.',
        'Atomic Structure': 'Atoms consist of a nucleus (containing protons and neutrons) surrounded by electrons in specific energy levels.',
        'Electron Configuration': 'Electron configuration describes the arrangement of electrons in an atom\'s orbitals, following the Aufbau principle, Pauli exclusion principle, and Hund\'s rule.',
        'Ionic Bonding': 'Ionic bonding occurs when electrons are transferred from one atom to another, resulting in positively and negatively charged ions that attract each other.',
        'The Mole Concept': 'The mole is the SI unit for amount of substance, representing 6.022 × 10²³ (Avogadro\'s number) particles.',
    }
    return definitions.get(topic, 'A fundamental concept in chemistry that helps explain the composition, structure, and changes of matter.')

def get_math_next_topic(current_topic):
    """Get the next topic for math lessons"""
    next_topics = {
        'Real Numbers and Properties': 'Algebraic Expressions',
        'Algebraic Expressions': 'Solving Linear Equations',
        'Solving Linear Equations': 'Applications of Linear Equations',
        'Linear Inequalities': 'Introduction to Functions',
        'Introduction to Functions': 'Linear Functions and Slope',
        'Quadratic Functions': 'Graphical Solutions to Systems',
    }
    return next_topics.get(current_topic, 'more advanced algebraic concepts')

def get_physics_next_topic(current_topic):
    """Get the next topic for physics lessons"""
    next_topics = {
        'The Scientific Method in Physics': 'Units and Measurements',
        'Units and Measurements': 'Vectors and Scalars',
        'Vectors and Scalars': 'Position, Distance, and Displacement',
        'Position, Distance, and Displacement': 'Speed and Velocity',
        'Acceleration': 'Free Fall and Projectile Motion',
        'Force and Newton\'s First Law': 'Newton\'s Second Law',
    }
    return next_topics.get(current_topic, 'more complex physics principles')

def get_chemistry_next_topic(current_topic):
    """Get the next topic for chemistry lessons"""
    next_topics = {
        'Classification of Matter': 'Physical and Chemical Properties',
        'Physical and Chemical Properties': 'Units of Measurement',
        'Development of Atomic Theory': 'The Modern Atomic Model',
        'The Modern Atomic Model': 'Isotopes and Atomic Mass',
        'Ionic Bonding': 'Covalent Bonding',
        'The Mole Concept': 'Molar Mass',
    }
    return next_topics.get(current_topic, 'more advanced chemistry concepts')

def create_enrollments(students, courses):
    """Create enrollments for students"""
    print("\n[Step 8] Creating enrollments...")
    
    for student in students:
        # Enroll each student in 1-3 random courses
        num_enrollments = random.randint(1, 3)
        selected_courses = random.sample(list(courses), min(num_enrollments, len(courses)))
        
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
            
            # Complete 10-60% of lessons
            completion_percentage = random.uniform(0.1, 0.6)
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

def create_forum_content(courses, students, instructors):
    """Create forum threads and replies"""
    print("\n[Step 9] Creating forum content...")
    
    for course in courses:
        # Create 2-4 threads per course
        num_threads = random.randint(2, 4)
        
        for i in range(1, num_threads + 1):
            # Random user for the thread (either student or instructor)
            if random.random() < 0.7:  # 70% chance it's a student
                thread_creator = random.choice(students)
            else:
                thread_creator = random.choice(instructors)
            
            thread_title = f"Question about {get_random_topic(course)}"
            
            thread, created = ForumThread.objects.get_or_create(
                course=course,
                user=thread_creator,
                title=thread_title,
                defaults={
                    'content': f"Hello everyone, I have a question about {get_random_topic(course)}. Can someone explain how this works or provide some examples?",
                    'is_pinned': random.random() < 0.2,  # 20% chance it's pinned
                    'is_locked': random.random() < 0.1    # 10% chance it's locked
                }
            )
            
            if created:
                print(f"Created forum thread: {thread_title} in {course.title}")
            else:
                print(f"Forum thread already exists: {thread_title} in {course.title}")
            
            # Create 1-5 replies per thread
            num_replies = random.randint(1, 5)
            
            for j in range(1, num_replies + 1):
                # Random user for the reply (either student or instructor)
                if random.random() < 0.6:  # 60% chance it's a student
                    reply_creator = random.choice([s for s in students if s != thread_creator])
                else:
                    reply_creator = random.choice(instructors)
                
                reply, created = ForumReply.objects.get_or_create(
                    thread=thread,
                    user=reply_creator,
                    content=f"Here's my response to your question about {get_random_topic(course)}. I think the key point to understand is...",
                    defaults={
                        'is_solution': reply_creator in instructors and random.random() < 0.7  # 70% chance instructor reply is marked as solution
                    }
                )
                
                if created:
                    print(f"  Created forum reply by {reply_creator.username}")
                else:
                    print(f"  Forum reply already exists by {reply_creator.username}")

def get_random_topic(course):
    """Get a random topic based on the course"""
    if 'Math' in course.title or 'Algebra' in course.title:
        topics = ['quadratic equations', 'linear functions', 'geometric proofs', 'exponents', 'factoring polynomials', 
                 'trigonometric functions', 'coordinate geometry', 'logarithms', 'conic sections']
    elif 'Physics' in course.title:
        topics = ['Newton\'s laws', 'projectile motion', 'conservation of energy', 'momentum', 'circular motion', 
                 'wave interference', 'electric fields', 'magnetic fields', 'optics']
    elif 'Chemistry' in course.title:
        topics = ['atomic structure', 'chemical bonding', 'stoichiometry', 'gas laws', 'periodic trends', 
                 'acid-base reactions', 'redox reactions', 'thermochemistry', 'organic compounds']
    else:
        topics = ['this concept', 'the homework', 'the latest assignment', 'the final project', 'exam preparation']
    
    return random.choice(topics)

def main():
    print("="*80)
    print("HIGH SCHOOL COURSE DATA RESET AND CREATION TOOL".center(80))
    print("="*80)
    
    if not confirm_reset():
        print("\nOperation cancelled.")
        return
    
    # Reset database and migrations
    delete_database()
    delete_migrations()
    create_new_migrations()
    apply_migrations()
    create_superuser()
    
    # Create new high school data
    instructors, students = create_users()
    courses = create_highschool_courses(instructors)
    
    # Create modules and lessons for each course type
    create_math_modules_and_lessons(courses[0])  # Math course
    create_physics_modules_and_lessons(courses[1])  # Physics course
    create_chemistry_modules_and_lessons(courses[2])  # Chemistry course
    
    # Create enrollments and forum content
    create_enrollments(students, courses)
    create_forum_content(courses, students, instructors)
    
    print("\n" + "="*80)
    print("HIGH SCHOOL DATA CREATION COMPLETE!".center(80))
    print("="*80)
    print("\nYou can now run 'python manage.py runserver' to start your application.")
    print("\nSample user credentials:")
    print("  Admin: username='admin', password=<the one you entered>")
    print("  Instructors: username='math_teacher', 'physics_teacher', 'chemistry_teacher', password='password123'")
    print("  Students: username='student1', 'student2', 'student3', etc., password='password123'")

if __name__ == "__main__":
    main()