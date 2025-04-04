from courses.models import InstructorProfile

def instructor_status(request):
    """
    Add instructor status to the template context for all templates
    """
    context = {
        'is_instructor': False
    }
    
    if request.user.is_authenticated:
        try:
            instructor_profile = InstructorProfile.objects.get(user=request.user)
            context['is_instructor'] = True
            context['instructor_profile'] = instructor_profile
        except InstructorProfile.DoesNotExist:
            pass
    
    return context

