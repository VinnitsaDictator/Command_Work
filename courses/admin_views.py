from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Count

# Попробуем разные способы импорта моделей
try:
    from courses.models import Course, Category, Enrollment, Lesson
    print("✓ Успешный импорт: from courses.models import ...")
except ImportError as e:
    print(f"✗ Ошибка импорта courses.models: {e}")
    try:
        from .models import Course, Category, Enrollment, Lesson
        print("✓ Успешный импорт: from .models import ...")
    except ImportError as e2:
        print(f"✗ Ошибка импорта .models: {e2}")
        # Попробуем импортировать по одной модели
        try:
            from django.apps import apps
            Course = apps.get_model('courses', 'Course')
            Category = apps.get_model('courses', 'Category')
            Enrollment = apps.get_model('courses', 'Enrollment') 
            Lesson = apps.get_model('courses', 'Lesson')
            print("✓ Успешный импорт через apps.get_model")
        except Exception as e3:
            print(f"✗ Ошибка импорта через apps: {e3}")
            raise

def admin_courses(request):
    """Головна сторінка адмін-панелі курсів"""
    editing_course = None

    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            description = request.POST.get('description', '').strip()
            category_id = request.POST.get('category')
            instructor_id = request.POST.get('instructor') or None
            price = request.POST.get('price', 0)
            difficulty = request.POST.get('difficulty', 'beginner')
            duration_hours = request.POST.get('duration_hours', 0)
            is_published = request.POST.get('is_published') == 'on'

            # Перевіряємо тільки обов'язкові поля
            if not title or not description or not category_id:
                messages.error(request, 'Заповніть обов\'язкові поля: Назва та Опис курсу, Категорія!')
                context = get_admin_context(request.POST, editing_course)
                return render(request, 'courses/admin_courses.html', context)

            course_id = request.POST.get('course_id')
            if course_id:  # Редагування існуючого курсу
                course = get_object_or_404(Course, id=course_id)
                course.title = title
                course.short_description = short_description
                course.description = description
                course.category_id = category_id
                course.instructor_id = instructor_id if instructor_id else None
                course.price = float(price) if price else 0
                course.difficulty = difficulty
                course.duration_hours = int(duration_hours) if duration_hours else 0
                course.is_published = is_published

                # Оновлюємо slug тільки якщо змінилася назва
                if slugify(title) != course.slug:
                    course.slug = generate_unique_slug(title)

                messages.success(request, f'Курс "{title}" успішно оновлено!')
            else:  # Створення нового курсу
                course = Course(
                    title=title,
                    slug=generate_unique_slug(title),
                    short_description=short_description,
                    description=description,
                    category_id=category_id,
                    instructor_id=instructor_id if instructor_id else None,
                    price=float(price) if price else 0,
                    difficulty=difficulty,
                    duration_hours=int(duration_hours) if duration_hours else 0,
                    is_published=is_published
                )
                messages.success(request, f'Курс "{title}" успішно створено!')

            # Обробляємо завантаження зображення
            if 'image' in request.FILES:
                course.image = request.FILES['image']

            course.save()
            return redirect('admin_courses')  # Изменено: убран courses:

        except Exception as e:
            messages.error(request, f'Помилка при збереженні курсу: {str(e)}')
            context = get_admin_context(request.POST, editing_course)
            return render(request, 'courses/admin_courses.html', context)

    # GET запрос - показуємо форму
    context = get_admin_context(editing_course=editing_course)
    
    # Отладочная информация прямо перед рендером
    print("=== ПЕРЕД РЕНДЕРОМ ШАБЛОНА ===")
    print(f"Context keys: {list(context.keys())}")
    print(f"Courses в контексте: {len(context.get('courses', []))}")
    print(f"Type of courses: {type(context.get('courses', []))}")
    if context.get('courses'):
        print(f"Первый курс: {context['courses'][0].title}")
    print("==============================")
    
    return render(request, 'courses/admin_courses.html', context)


def get_admin_context(form_data=None, editing_course=None):
    """Отримує контекст для адмін-панелі"""
    
    print("=== НАЧАЛО get_admin_context ===")
    
    # Получаем все курсы БЕЗ select_related чтобы избежать проблем с NULL
    try:
        courses_list = list(Course.objects.all().order_by('-id'))
        print(f"Получено курсов: {len(courses_list)}")
        
        if courses_list:
            print("Курсы получены успешно:")
            for i, course in enumerate(courses_list[:3]):
                # Безопасная проверка инструктора и категории
                instructor_name = "Не вказано"
                try:
                    if hasattr(course, 'instructor') and course.instructor:
                        instructor_name = course.instructor.username
                except:
                    pass
                
                category_name = "Без категории"
                try:
                    if hasattr(course, 'category') and course.category:
                        category_name = course.category.name
                except:
                    pass
                
                print(f"  {i+1}. ID: {course.id}, Title: '{course.title}', Instructor: {instructor_name}, Category: {category_name}")
    except Exception as e:
        print(f"ОШИБКА при получении курсов: {e}")
        courses_list = []
    
    # Статистика
    published_courses = 0
    for course in courses_list:
        if hasattr(course, 'is_published') and course.is_published:
            published_courses += 1
    
    print(f"Опубликованных курсов: {published_courses}")
    
    # Получаем категории
    try:
        categories = list(Category.objects.all())
        print(f"Категорий: {len(categories)}")
    except Exception as e:
        print(f"Ошибка получения категорий: {e}")
        categories = []
        
    # Получаем преподавателей
    try:
        instructors = list(User.objects.all())
        print(f"Преподавателей: {len(instructors)}")
    except Exception as e:
        print(f"Ошибка получения преподавателей: {e}")
        instructors = []
    
    # Записи студентов
    total_enrollments = 0
    try:
        total_enrollments = Enrollment.objects.count()
    except:
        pass
    
    context = {
        'courses': courses_list,
        'courses_count': len(courses_list),
        'categories': categories,
        'instructors': instructors,
        'form_data': form_data or {},
        'editing_course': editing_course,
        'total_enrollments': total_enrollments,
        'published_courses': published_courses,
    }
    
    print(f"КОНТЕКСТ СОЗДАН:")
    print(f"  courses: {len(context['courses'])} элементов")
    print(f"  courses_count: {context['courses_count']}")
    print(f"  categories: {len(context['categories'])} элементов")
    print("=== КОНЕЦ get_admin_context ===")
    
    return context


def generate_unique_slug(title):
    """Генерує унікальний slug для курсу"""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while Course.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def course_edit(request, course_id):
    """Редагування курсу"""
    course = get_object_or_404(Course, id=course_id)
    
    # Безопасное получение instructor_id
    instructor_id = None
    try:
        if hasattr(course, 'instructor') and course.instructor:
            instructor_id = course.instructor.id
    except:
        instructor_id = None
    
    # Безопасное получение category_id    
    category_id = None
    try:
        if hasattr(course, 'category') and course.category:
            category_id = course.category.id
    except:
        category_id = None
    
    form_data = {
        'course_id': course.id,
        'title': course.title,
        'short_description': getattr(course, 'short_description', ''),
        'description': getattr(course, 'description', ''),
        'category': category_id,
        'instructor': instructor_id,
        'price': getattr(course, 'price', 0),
        'difficulty': getattr(course, 'difficulty', 'beginner'),
        'duration_hours': getattr(course, 'duration_hours', 0),
        'is_published': getattr(course, 'is_published', False),
    }
    
    print(f"=== РЕДАКТИРОВАНИЕ КУРСА {course.id} ===")
    print(f"Title: {course.title}")
    print(f"Instructor ID: {instructor_id}")
    print(f"Category ID: {category_id}")
    print("================================")
    
    context = get_admin_context(form_data)
    context['editing_course'] = course
    return render(request, 'courses/admin_courses.html', context)


def course_delete(request, course_id):
    """Видалення курсу"""
    course = get_object_or_404(Course, id=course_id)
    course_title = course.title
    try:
        course.delete()
        messages.success(request, f'Курс "{course_title}" успішно видалено!')
    except Exception as e:
        messages.error(request, f'Помилка при видаленні курсу: {str(e)}')
    return redirect('admin_courses')  # Изменено: убран courses:


def create_sample_courses(request):
    """Створює приклади курсів для тестування"""
    try:
        # Створюємо категорії якщо їх немає
        programming_cat, _ = Category.objects.get_or_create(
            name='Програмування',
            defaults={'slug': 'programming', 'description': 'Курси з програмування та розробки'}
        )
        design_cat, _ = Category.objects.get_or_create(
            name='Дизайн',
            defaults={'slug': 'design', 'description': 'Курси з графічного та веб-дизайну'}
        )

        # Використовуємо першого доступного користувача як викладача
        instructor = User.objects.first()

        # Приклади курсів
        sample_courses = [
            {
                'title': 'Python для початківців',
                'slug': 'python-for-beginners',
                'short_description': 'Вивчіть основи програмування на Python з нуля',
                'description': 'Повний курс Python для початківців. Освоїте синтаксис, структури даних, функції та створіть перші проекти.',
                'category': programming_cat,
                'instructor': instructor,
                'price': 1200.00,
                'difficulty': 'beginner',
                'duration_hours': 40,
                'is_published': True,
            },
            {
                'title': 'Веб-дизайн з нуля',
                'slug': 'web-design-from-scratch',
                'short_description': 'Створюйте красиві та функціональні веб-сайти',
                'description': 'Навчіться створювати сучасні веб-дизайни. Фотошоп, Figma, принципи UX/UI дизайну.',
                'category': design_cat,
                'instructor': instructor,
                'price': 1800.00,
                'difficulty': 'beginner',
                'duration_hours': 35,
                'is_published': True,
            },
        ]

        created_count = 0
        for course_data in sample_courses:
            if not Course.objects.filter(slug=course_data['slug']).exists():
                Course.objects.create(**course_data)
                created_count += 1

        if created_count > 0:
            messages.success(request, f'Створено {created_count} прикладів курсів!')
        else:
            messages.info(request, 'Всі приклади курсів вже існують')

    except Exception as e:
        messages.error(request, f'Помилка при створенні прикладів: {str(e)}')

    return redirect('admin_courses')  # Изменено: убран courses:


def manage_categories(request):
    """Управління категоріями курсів"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            try:
                # Проверяем, не существует ли уже такая категория
                if Category.objects.filter(name=name).exists():
                    messages.error(request, f'Категорія "{name}" вже існує!')
                else:
                    Category.objects.create(
                        name=name,
                        slug=slugify(name),
                        description=description
                    )
                    messages.success(request, f'Категорію "{name}" створено!')
            except Exception as e:
                messages.error(request, f'Помилка при створенні категорії: {str(e)}')
        else:
            messages.error(request, 'Введіть назву категорії')

    categories = Category.objects.annotate(course_count=Count('courses')).order_by('name')
    return render(request, 'courses/manage_categories.html', {
        'categories': categories,
        'form_data': {}
    })


def edit_category(request, category_id):
    """Редагування категорії"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            try:
                # Проверяем, не существует ли уже такая категория (кроме текущей)
                if Category.objects.filter(name=name).exclude(id=category_id).exists():
                    messages.error(request, f'Категорія "{name}" вже існує!')
                else:
                    category.name = name
                    category.description = description
                    category.slug = slugify(name)
                    category.save()
                    messages.success(request, f'Категорію "{name}" оновлено!')
                    return redirect('manage_categories')
            except Exception as e:
                messages.error(request, f'Помилка при оновленні категорії: {str(e)}')
        else:
            messages.error(request, 'Введіть назву категорії')
    
    categories = Category.objects.annotate(course_count=Count('courses')).order_by('name')
    form_data = {
        'name': category.name,
        'description': category.description
    }
    
    return render(request, 'courses/manage_categories.html', {
        'categories': categories,
        'form_data': form_data,
        'editing_category': category
    })


def delete_category(request, category_id):
    """Видалення категорії"""
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        category_name = category.name
        
        try:
            # Проверяем, есть ли курсы в этой категории
            courses_count = category.courses.count()
            if courses_count > 0:
                messages.error(request, f'Неможливо видалити категорію "{category_name}" - в ній є {courses_count} курсів')
            else:
                category.delete()
                messages.success(request, f'Категорію "{category_name}" успішно видалено!')
        except Exception as e:
            messages.error(request, f'Помилка при видаленні категорії: {str(e)}')
    
    return redirect('manage_categories')


def view_enrollments(request):
    """Перегляд записів студентів на курси"""
    try:
        enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')
    except:
        enrollments = []
    return render(request, 'courses/view_enrollments.html', {'enrollments': enrollments})