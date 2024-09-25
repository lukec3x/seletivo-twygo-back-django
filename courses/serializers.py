from rest_framework import serializers

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = ['id', 'title', 'description', 'ends_at']


class CourseRetrieveSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = ['id', 'title', 'description', 'ends_at', 'video_urls', 'total_duration']


# class CourseCreateVideoSerializer(serializers.ModelSerializer):
#   title = serializers.CharField(max_length=255)
#   url = serializers.URLField()
