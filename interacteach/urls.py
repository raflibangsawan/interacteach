from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views

# Customize admin site
admin.site.site_header = "InteracTeach Administration"
admin.site.site_title = "InteracTeach Admin Portal"
admin.site.index_title = "Welcome to InteracTeach Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', core_views.logout_view, name='logout'),
    path('courses/', include('courses.urls')),  # Include courses URLs
    path('register/', core_views.register, name='register')
]

