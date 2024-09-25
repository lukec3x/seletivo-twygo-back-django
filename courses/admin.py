from django.contrib import admin

from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
  list_display = ('id', 'title', 'description', 'ends_at', 'deleted_at', 'created_at', 'updated_at', 'video_urls', 'total_duration')
  