from django.utils import timezone
from django.test import TestCase
from django.test import Client
from django.urls import reverse_lazy

from courses.models import Course

class CourseViewTestCase(TestCase):

  def setUp(self):
    self.course1 = Course.objects.create(title="Curso 1", description="Descrição do curso 1", ends_at=timezone.now() + timezone.timedelta(days=30))
    self.course2 = Course.objects.create(title="Curso 2", description="Descrição do curso 2", ends_at=timezone.now() + timezone.timedelta(days=20))
    self.course3 = Course.objects.create(title="Curso 3", description="Descrição do curso 3", ends_at=timezone.now() + timezone.timedelta(days=10))
    self.course4 = Course.objects.create(title="Curso 4", description="Descrição do curso 4", ends_at=timezone.now() - timezone.timedelta(days=10))
    self.client = Client()

  def test_list_courses(self):
    request = self.client.get(reverse_lazy('courses-list'))

    self.assertEqual(request.status_code, 200)
    self.assertEqual(len(request.data.get('results')), 3)

  def test_create_course_with_valid_data(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'title': 'Curso 5',
      'description': 'Descrição do curso 5',
      'ends_at': timezone.now() + timezone.timedelta(days=5)
    })

    self.assertEqual(request.status_code, 201)

  def test_create_course_without_title(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'description': 'Descrição do curso 6',
      'ends_at': timezone.now() + timezone.timedelta(days=5)
    })

    self.assertEqual(request.status_code, 400)

  def test_create_course_without_description(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'title': 'Curso 6',
      'ends_at': timezone.now() + timezone.timedelta(days=5)
    })

    self.assertEqual(request.status_code, 400)

  def test_create_course_without_ends_at(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'title': 'Curso 6',
      'description': 'Descrição do curso 6',
    })

    self.assertEqual(request.status_code, 400)

