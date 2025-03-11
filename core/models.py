from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    image = models.CharField(max_length=200, default='/static/images/course-placeholder.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title