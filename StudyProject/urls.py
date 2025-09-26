from django.contrib import admin
from django.urls import path, include
from courses import views

from django.contrib import admin
from django.urls import path
from courses import views, admin_views  

urlpatterns = [
    path("admin/", admin.site.urls),            
    path("", views.index, name="index"),       
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),


    path("admin-panel/", admin_views.admin_courses, name="admin_courses"),
    path("admin-panel/edit/<int:course_id>/", admin_views.course_edit, name="course_edit"),
    path("admin-panel/delete/<int:course_id>/", admin_views.course_delete, name="course_delete"),
    path("admin-panel/sample-courses/", admin_views.create_sample_courses, name="create_sample_courses"),
    path("admin-panel/manage-categories/", admin_views.manage_categories, name="manage_categories"),
    path("admin-panel/enrollments/", admin_views.view_enrollments, name="view_enrollments"),



    path("courses/", include("courses.urls")),
]
