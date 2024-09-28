from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet


router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
  path('', include(router.urls)),
  path('courses/<int:course_id>/create_video/', CourseViewSet.as_view({'post': 'create_video'}), name='courses-create_video'),
  path('courses/<int:course_id>/update_video/<str:video_id>/', CourseViewSet.as_view({'put': 'update_video'}), name='courses-update_video'),
  path('courses/<int:course_id>/destroy_video/<str:video_id>/', CourseViewSet.as_view({'delete': 'destroy_video'}), name='courses-destroy_video'),
  path('report/export/', CourseViewSet.as_view({'get': 'export'}), name='courses-export'),
]