from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from .models import Course, Category, Enrollment, Review


def index(request):
    """Главная страница с популярными курсами и статистикой"""
    popular_courses = Course.objects.filter(
        is_published=True
    ).annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:6]

    total_students = User.objects.filter(enrollments__isnull=False).distinct().count()
    total_courses = Course.objects.filter(is_published=True).count()
    total_instructors = User.objects.filter(courses__isnull=False).distinct().count()

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
    return render(request, 'courses/index.html', context)


def about(request):
    return render(request, 'courses/about.html')


def contacts(request):
    return render(request, 'courses/contacts.html')


def courses(request):  
    """Список всех курсов"""
    courses = Course.objects.filter(is_published=True)
    return render(request, 'courses/courses.html', {"courses": courses})


def course_detail(request, slug):
    """Детальная страница курса"""
    course = get_object_or_404(Course, slug=slug, is_published=True)

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()

    context = {
        "course": course,
        "is_enrolled": is_enrolled,
    }
    return render(request, "courses/course_detail.html", context)


def course_by_category(request, category_slug):
    """Курсы по категориям"""
    category = get_object_or_404(Category, slug=category_slug)
    courses = Course.objects.filter(category=category, is_published=True)

    context = {
        "category": category,
        "courses": courses,
    }
    return render(request, "courses/course_by_category.html", context)


def enroll_course(request, course_id):
    """Запись пользователя на курс"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)

    if created:
        messages.success(request, f"Вы успешно записались на курс: {course.title}")
    else:
        messages.info(request, f"Вы уже записаны на курс: {course.title}")

    return redirect("courses:course_detail", slug=course.slug)


def add_review(request, course_id):
    """Добавление отзыва"""
    course = get_object_or_404(Course, id=course_id, is_published=True)

    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "")

        Review.objects.update_or_create(
            course=course,
            student=request.user,
            defaults={"rating": rating, "comment": comment}
        )
        messages.success(request, "Ваш отзыв был добавлен/обновлен!")
        return redirect("courses:course_detail", slug=course.slug)

    return render(request, "courses/add_review.html", {"course": course})


def admin_panel(request):
    """Простая админ-панель (доступ только суперюзерам)"""
    if not request.user.is_superuser:
        messages.error(request, "У вас нет доступа к админ-панели.")
        return redirect("courses:index")

    courses = Course.objects.all()
    users = User.objects.all()
    enrollments = Enrollment.objects.all()

    context = {
        "courses": courses,
        "users": users,
        "enrollments": enrollments,
    }
    return render(request, "courses/admin_panel.html", context)


def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
    return redirect('manage_categories')

def privacypolicy(request):
    return render(request, "courses/privacy_policy.html")

def termsofuse(request):
    return render(request, "courses/terms_of_use.html")

def managecategories(request):
    return render(request, "admin-panel/manage_categories.html")

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
    return redirect('manage_categories')