from django.contrib import admin
from django.urls import path
from courses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('courses/', views.courses, name='courses'),
    path('about/', views.about, name='about'),  # ← обязательно!
    path('contacts/', views.contacts, name='contacts')
]