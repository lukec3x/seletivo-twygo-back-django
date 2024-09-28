from django.utils import timezone
from django.test import TestCase
from django.urls import reverse_lazy
from unittest.mock import patch, Mock
import json

from courses.models import Course
from courses.views import CourseViewSet

class CourseViewTestCase(TestCase):

  def setUp(self):
    self.course1 = Course.objects.create(title="Curso 1", description="Descrição do curso 1", ends_at=timezone.now() + timezone.timedelta(days=30))
    self.course2 = Course.objects.create(
      title="Curso 2",
      description="Descrição do curso 2",
      ends_at=timezone.now() + timezone.timedelta(days=20),
      video_urls=[
        {
          "id": "QH2-TGUlwu4",
          "url": "https://www.youtube.com/watch?v=QH2-TGUlwu4",
          "title": "Trailer do curso 2",
          "duration": "0:4:30"
        },
        {
          "id": "QH2-1d3fau4",
          "url": "https://www.youtube.com/watch?v=QH2-TGUlwu4",
          "title": "Trailer do curso 2 pt2",
          "duration": "1:40:30"
        }
      ]
    )
    self.course3 = Course.objects.create(title="Curso 3", description="Descrição do curso 3", ends_at=timezone.now() + timezone.timedelta(days=10))
    self.course4 = Course.objects.create(title="Curso 4", description="Descrição do curso 4", ends_at=timezone.now() - timezone.timedelta(days=10))

  def test_list_courses(self):
    request = self.client.get(reverse_lazy('courses-list'))

    self.assertEqual(request.status_code, 200)
    self.assertEqual(len(request.data.get('results')), 3)
    self.assertEqual(Course.objects.count(), 4)

  def test_create_course_with_valid_data(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'title': 'Curso 5',
      'description': 'Descrição do curso 5',
      'ends_at': timezone.now() + timezone.timedelta(days=5)
    })

    self.assertEqual(request.status_code, 201)
    self.assertEqual(Course.objects.count(), 5)

  def test_create_course_without_title(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'description': 'Descrição do curso 6',
      'ends_at': timezone.now() + timezone.timedelta(days=5)
    })

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.count(), 4)

  def test_create_course_without_description(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'title': 'Curso 6',
      'ends_at': timezone.now() + timezone.timedelta(days=5)
    })

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.count(), 4)

  def test_create_course_without_ends_at(self):
    request = self.client.post(reverse_lazy('courses-list'), data={
      'title': 'Curso 6',
      'description': 'Descrição do curso 6',
    })

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.count(), 4)

  def test_create_video_course(self):
    request = self.client.post(reverse_lazy('courses-create_video', kwargs={'course_id': self.course1.id}), data={
      'title': 'Vídeo 1',
      'url': 'https://www.youtube.com/watch?v=123456789',
      'duration': '0:4:70'
    })

    self.assertEqual(request.status_code, 201)
    self.assertEqual(Course.objects.get(pk=self.course1.id).video_urls[0]['title'], 'Vídeo 1')
    self.assertEqual(len(Course.objects.get(pk=self.course1.id).video_urls), 1)
    self.assertEqual(Course.objects.get(pk=self.course1.id).video_urls[0]['duration'], '0:0:0')

  def test_create_video_course_without_title(self):
    request = self.client.post(reverse_lazy('courses-create_video', kwargs={'course_id': self.course1.id}), data={
      'url': 'https://www.youtube.com/watch?v=123456789',
    })

    self.assertEqual(request.status_code, 400)
    self.assertEqual(len(Course.objects.get(pk=self.course1.id).video_urls), 0)

  def test_create_video_course_without_url(self):
    request = self.client.post(reverse_lazy('courses-create_video', kwargs={'course_id': self.course1.id}), data={
      'title': 'Vídeo 1',
    })

    self.assertEqual(request.status_code, 400)
    self.assertEqual(len(Course.objects.get(pk=self.course1.id).video_urls), 0)

  def test_retrieve_course(self):
    request = self.client.get(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}))

    self.assertEqual(request.status_code, 200)
    self.assertEqual(request.data.get('title'), 'Curso 1')
    self.assertEqual(request.data.get('description'), 'Descrição do curso 1')
    self.assertEqual(request.data.get('ends_at'), self.course1.ends_at.astimezone(timezone.get_default_timezone()).isoformat())

  def test_update_course(self):
    data = json.dumps({
      'title': 'Curso 1 - Atualizado',
      'description': 'Descrição do curso 1 - Atualizado',
      'ends_at': (self.course1.ends_at + timezone.timedelta(days=1)).isoformat()
    })

    request = self.client.put(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 200)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1 - Atualizado')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1 - Atualizado')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at + timezone.timedelta(days=1))

  def test_update_course_without_title(self):
    data = json.dumps({
      'description': 'Descrição do curso 1 - Atualizado',
      'ends_at': (self.course1.ends_at + timezone.timedelta(days=1)).isoformat()
    })

    request = self.client.put(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_update_course_without_description(self):
    data = json.dumps({
      'title': 'Curso 1 - Atualizado',
      'ends_at': (self.course1.ends_at + timezone.timedelta(days=1)).isoformat()
    })
    request = self.client.put(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_update_course_without_ends_at(self):
    data = json.dumps({
      'title': 'Curso 1 - Atualizado',
      'description': 'Descrição do curso 1 - Atualizado',
    })

    request = self.client.put(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_update_course_with_invalid_id(self):
    data = json.dumps({
      'title': 'Curso 1 - Atualizado',
      'description': 'Descrição do curso 1 - Atualizado',
      'ends_at': (self.course1.ends_at + timezone.timedelta(days=1)).isoformat()
    })

    request = self.client.put(reverse_lazy('courses-detail', kwargs={'pk': 0}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 404)
    self.assertNotEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1 - Atualizado')
    self.assertNotEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1 - Atualizado')
    self.assertNotEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at + timezone.timedelta(days=1))


  def test_partial_update_course_with_title(self):
    data = json.dumps({
      'title': 'Curso 1 - Atualizado',
    })

    request = self.client.patch(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 200)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1 - Atualizado')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_partial_update_course_with_description(self):
    data = json.dumps({
      'description': 'Descrição do curso 1 - Atualizado',
    })

    request = self.client.patch(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 200)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1 - Atualizado')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_partial_update_course_with_ends_at(self):
    data = json.dumps({
      'ends_at': (self.course1.ends_at + timezone.timedelta(days=1)).isoformat()
    })

    request = self.client.patch(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 200)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at + timezone.timedelta(days=1))

  def test_partial_update_course_without_fields(self):
    data = json.dumps({})

    request = self.client.patch(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_partial_update_course_with_invalid_date(self):
    data = json.dumps({
      'ends_at': 'invalid date'
    })

    request = self.client.patch(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 400)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_partial_update_course_with_description(self):
    data = json.dumps({
      'description': 'Descrição do curso 1 - Atualizado',
    })

    request = self.client.patch(reverse_lazy('courses-detail', kwargs={'pk': 0}), data=data, content_type='application/json')

    self.assertEqual(request.status_code, 404)
    self.assertEqual(Course.objects.get(pk=self.course1.id).title, 'Curso 1')
    self.assertNotEqual(Course.objects.get(pk=self.course1.id).description, 'Descrição do curso 1 - Atualizado')
    self.assertEqual(Course.objects.get(pk=self.course1.id).ends_at, self.course1.ends_at)

  def test_update_video_course(self):
    data = json.dumps({
      'title': 'Vídeo 2 - Atualizado',
      'url': 'https://www.youtube.com/watch?v=123456789',
    })

    request = self.client.put(
      reverse_lazy('courses-update_video',
                   kwargs={'course_id': str(self.course2.id), 'video_id': self.course2.video_urls[0]['id']}),
                   data=data,
                   content_type='application/json')

    self.assertEqual(request.status_code, 200)
    self.assertEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['title'], 'Vídeo 2 - Atualizado')
    self.assertEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['url'], 'https://www.youtube.com/watch?v=123456789')

  def test_update_video_course_without_title(self):
    data = json.dumps({
      'url': 'https://www.youtube.com/watch?v=123456789',
    })

    request = self.client.put(
      reverse_lazy('courses-update_video',
                   kwargs={'course_id': str(self.course2.id), 'video_id': self.course2.video_urls[0]['id']}),
                   data=data,
                   content_type='application/json')

    self.assertEqual(request.status_code, 400)
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['title'], 'Vídeo 2 - Atualizado')
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['url'], 'https://www.youtube.com/watch?v=123456789')

  def test_update_video_course_without_url(self):
    data = json.dumps({
      'title': 'Vídeo 2 - Atualizado',
    })

    request = self.client.put(
      reverse_lazy('courses-update_video',
                   kwargs={'course_id': str(self.course2.id), 'video_id': self.course2.video_urls[0]['id']}),
                   data=data,
                   content_type='application/json')

    self.assertEqual(request.status_code, 400)
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['title'], 'Vídeo 2 - Atualizado')
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['url'], 'https://www.youtube.com/watch?v=123456789')

  def test_update_video_course_with_invalid_course_id(self):
    data = json.dumps({
      'title': 'Vídeo 2 - Atualizado',
      'url': 'https://www.youtube.com/watch?v=123456789',
    })

    request = self.client.put(
      reverse_lazy('courses-update_video',
                   kwargs={'course_id': 0, 'video_id': self.course2.video_urls[0]['id']}),
                   data=data,
                   content_type='application/json')

    self.assertEqual(request.status_code, 404)
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['title'], 'Vídeo 2 - Atualizado')
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['url'], 'https://www.youtube.com/watch?v=123456789')

  def test_update_video_course_with_invalid_video_id(self):
    data = json.dumps({
      'title': 'Vídeo 2 - Atualizado',
      'url': 'https://www.youtube.com/watch?v=123456789',
    })

    request = self.client.put(
      reverse_lazy('courses-update_video',
                   kwargs={'course_id': str(self.course2.id), 'video_id': 0}),
                   data=data,
                   content_type='application/json')

    self.assertEqual(request.status_code, 404)
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['title'], 'Vídeo 2 - Atualizado')
    self.assertNotEqual(Course.objects.get(pk=self.course2.id).video_urls[0]['url'], 'https://www.youtube.com/watch?v=123456789')

  def test_destroy_course(self):
    request = self.client.delete(reverse_lazy('courses-detail', kwargs={'pk': self.course1.id}))

    self.assertEqual(request.status_code, 204)
    self.assertEqual(len(Course.objects.all()), 3)
    self.assertEqual(len(Course.objects.filter(pk=self.course1.id)), 0)

  def test_destroy_course_with_invalid_id(self):
    request = self.client.delete(reverse_lazy('courses-detail', kwargs={'pk': 0}))

    self.assertEqual(request.status_code, 404)
    self.assertNotEqual(len(Course.objects.all()), 3)
    self.assertNotEqual(len(Course.objects.filter(pk=self.course1.id)), 0)

  def test_destroy_video_course(self):
    request = self.client.delete(
      reverse_lazy('courses-destroy_video',
                   kwargs={'course_id': str(self.course2.id), 'video_id': self.course2.video_urls[0]['id']})
    )

    self.assertEqual(request.status_code, 200)
    self.assertEqual(len(Course.objects.get(pk=self.course2.id).video_urls), 1)

  def test_destroy_video_course_with_invalid_video_id(self):
    request = self.client.delete(
      reverse_lazy('courses-destroy_video',
                   kwargs={'course_id': str(self.course2.id), 'video_id': 0})
    )

    self.assertEqual(request.status_code, 404)
    self.assertEqual(len(Course.objects.get(pk=self.course2.id).video_urls), 2)
  
  def test_destroy_video_course_with_invalid_course_id(self):
    request = self.client.delete(
      reverse_lazy('courses-destroy_video',
                   kwargs={'course_id': 0, 'video_id': self.course2.video_urls[0]['id']})
    )

    self.assertEqual(request.status_code, 404)
    self.assertEqual(len(Course.objects.get(pk=self.course2.id).video_urls), 2)

  def test_export(self):
    request = self.client.get(reverse_lazy('courses-export'))

    self.assertEqual(request.status_code, 200)
    self.assertEqual(request['Content-Type'], 'text/csv')

  @patch('requests.get')
  def test_get_video_duration(self, mock_get):
    mock_response = Mock()
    mock_response.content = '''
    <html>
      <head>
        <meta itemprop="duration" content="PT1H30M10S">
      </head>
    </html>
    '''
    mock_get.return_value = mock_response
    
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    view_set = CourseViewSet()
    duration = view_set._get_video_duration(url)
    
    self.assertEqual(duration, "1:30:10")

  @patch('requests.get')
  def test_get_video_duration_not_found(self, mock_get):
    mock_response = Mock()
    mock_response.content = ''
    mock_get.return_value = mock_response
    
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    view_set = CourseViewSet()
    duration = view_set._get_video_duration(url)
    
    self.assertEqual(duration, "0:0:0")