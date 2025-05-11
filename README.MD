# InteracTeach - Interactive Learning Platform

InteracTeach is a comprehensive learning management system built with Django that allows instructors to create and manage courses, and students to learn through interactive lessons, quizzes, and discussions.

## Features

- Course Management
  - Create and manage courses with modules and lessons
  - Upload course materials and videos
  - Track student progress
  - Course enrollment system

- Interactive Learning
  - Video lessons
  - Interactive quizzes
  - Progress tracking
  - Note-taking functionality

- Discussion Forum
  - Course-specific forums
  - Thread management
  - Reply system
  - Solution marking

- User Management
  - Student and instructor roles
  - Profile management
  - Progress tracking
  - Course completion certificates

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/interacteach.git
   cd interacteach
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the project root:
   ```bash
   # Django Settings
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database Settings
   DATABASE_URL=sqlite:///db.sqlite3

   # Email Settings (Optional)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_USER_PASSWORD=your-app-specific-password
   ```

5. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**
   - Main application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

## Project Structure

```
interacteach/
├── core/                 # Core application
├── courses/             # Courses application
├── static/              # Static files
├── templates/           # HTML templates
├── media/              # User-uploaded files
├── manage.py           # Django management script
├── requirements.txt    # Project dependencies
└── .env               # Environment variables
```

## Creating Your First Course

1. Log in as an instructor
2. Navigate to the instructor dashboard
3. Click "Create New Course"
4. Fill in the course details:
   - Title
   - Description
   - Duration
   - Prerequisites
5. Add modules to your course
6. Create lessons within each module
7. Add quizzes if desired
8. Publish the course

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use meaningful variable and function names
   - Add comments for complex logic

2. **Git Workflow**
   ```bash
   git checkout -b feature/your-feature-name
   # Make your changes
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Framework
- Bootstrap
- Font Awesome
- All contributors and users of the platform
