from django.urls import path
from . import views
from . import admin_views

app_name = "courses"

urlpatterns = [
    path("", views.courses, name="course_list"),  
    path("<slug:slug>/", views.course_detail, name="course_detail"),
]
