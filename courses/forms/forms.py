from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "short_description",
            "description",
            "price",
            "duration_hours",
            "difficulty",
            "category",
            "instructor",
            "status",
            "is_featured",
        ]
