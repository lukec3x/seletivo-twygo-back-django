from django.db import models
from django.utils import timezone


class CourseManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted_at__isnull=True)

class Course(models.Model):
  title = models.CharField(max_length=255)
  description = models.TextField()
  ends_at = models.DateTimeField()
  deleted_at = models.DateTimeField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  video_urls = models.JSONField(default=list, blank=True)
  total_duration = models.CharField(max_length=255, default="0:0:0")

  objects = CourseManager()

  def delete(self, *args, **kwargs):
    self.deleted_at = timezone.now()
    self.save()

  def restore(self, *args, **kwargs):
    self.deleted_at = None
    self.save()

  class Meta:
    # Filtros globais para não trazer registros excluídos por padrão
    constraints = [
      models.UniqueConstraint(fields=['title'], condition=models.Q(deleted_at__isnull=True), name='unique_title_if_not_deleted')
    ]

  def is_deleted(self):
    return self.deleted_at is not None