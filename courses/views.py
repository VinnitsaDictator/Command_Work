from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.models import User

def index(request):
    try:
        from courses.models import Course, Enrollment
        
        popular_courses = Course.objects.filter(
            is_published=True
        ).annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:6]
        
        # Статистика
        total_students = User.objects.filter(enrollments__isnull=False).distinct().count()
        total_courses = Course.objects.filter(is_published=True).count()
        total_instructors = User.objects.filter(courses__isnull=False).distinct().count()
        
        # Обчислюємо відсоток завершення курсів
        completed_enrollments = Enrollment.objects.filter(completed_at__isnull=False).count()
        total_enrollments = Enrollment.objects.count()
        completion_rate = round((completed_enrollments / total_enrollments * 100), 0) if total_enrollments > 0 else 95
        
        context = {
            'popular_courses': popular_courses,
            'total_students': f"{total_students}+" if total_students > 0 else "1000+",
            'total_courses': f"{total_courses}+" if total_courses > 0 else "50+",
            'total_instructors': f"{total_instructors}+" if total_instructors > 0 else "25+",
            'completion_rate': f"{completion_rate}%",
            'stars': range(5), 
        }
        
    except ImportError:
        context = {
            'popular_courses': [],
            'total_students': "1000+",
            'total_courses': "50+",
            'total_instructors': "25+",
            'completion_rate': "95%",
            'stars': range(5),
        }

    return render(request, 'courses/index.html', context)
def about(request):
    return render(request, 'courses/about.html')
def courses(request):
    return render(request, 'courses/Courses.html')

