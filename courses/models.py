from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField('Назва категорії', max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField('Опис', blank=True)
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        
    def __str__(self):
        return self.name

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Початковий'),
        ('intermediate', 'Середній'),
        ('advanced', 'Просунутий'),
    ]
    
    title = models.CharField('Назва курсу', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Опис')
    short_description = models.CharField('Короткий опис', max_length=300, blank=True)
    image = models.ImageField('Зображення', upload_to='courses/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2, default=0)
    difficulty = models.CharField('Складність', max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_hours = models.PositiveIntegerField('Тривалість (години)', default=0)
    is_published = models.BooleanField('Опубліковано', default=False)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})
        
    @property
    def rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0
        
    @property
    def total_enrollments(self):
        return self.enrollments.count()

class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'Відео'),
        ('text', 'Текст'),
        ('assignment', 'Завдання'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField('Назва уроку', max_length=200)
    slug = models.SlugField()
    content = models.TextField('Зміст', blank=True)
    video_url = models.URLField('Посилання на відео', blank=True)
    lesson_type = models.CharField('Тип уроку', max_length=20, choices=LESSON_TYPES)
    order = models.PositiveIntegerField('Порядок', default=0)
    duration_minutes = models.PositiveIntegerField('Тривалість (хвилини)', default=0)
    is_free = models.BooleanField('Безкоштовний урок', default=False)
    
    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order']
        unique_together = ['course', 'slug']
        
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField('Дата запису', auto_now_add=True)
    completed_at = models.DateTimeField('Дата завершення', blank=True, null=True)
    progress = models.PositiveIntegerField('Прогрес (%)', default=0, 
                                         validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        verbose_name = 'Запис на курс'
        verbose_name_plural = 'Записи на курси'
        unique_together = ['student', 'course']
        
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField('Оцінка', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('Коментар', blank=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        unique_together = ['course', 'student']
        
    def __str__(self):
        return f"{self.course.title} - {self.rating}/5"
