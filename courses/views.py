from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils.dateparse import parse_duration
from django.shortcuts import get_object_or_404
from django.utils import timezone
from bs4 import BeautifulSoup
import requests
import uuid
import re

from .models import Course
from .serializers import CourseSerializer, CourseRetrieveSerializer


class CourseViewSet(viewsets.ViewSet):

  def get_serializer_class(self):
    if self.action == 'create_video':
      return CourseRetrieveSerializer
    elif self.action == 'retrieve':
      return CourseRetrieveSerializer
    elif self.action == 'update_video':
      return CourseRetrieveSerializer
    elif self.action == 'destroy_video':
      return CourseRetrieveSerializer
    return CourseSerializer

  def list(self, request, *args, **kwargs):
    queryset = Course.objects.filter(ends_at__gte=timezone.now()).order_by('created_at')

    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(queryset, request)

    serializer = self.get_serializer_class()(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

  
  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer_class()(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

  def create_video(self, request, course_id=None, *args, **kwargs):
    if not request.data.get('title') or not request.data.get('url'):
      return Response(status=status.HTTP_400_BAD_REQUEST)

    course = Course.objects.get(pk=course_id)

    video_data = {
      'id': str(uuid.uuid4()),
      'title': request.data.get('title'),
      'url': request.data.get('url'),
      'duration': self._get_video_duration(request.data.get('url'))
    }

    course.video_urls.append(video_data)
    course.total_duration = self._calc_total_duration(course.video_urls)
    course.save()
    serializer = self.get_serializer_class()(course)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


  def retrieve(self, request, pk=None, *args, **kwargs):
    queryset = Course.objects.get(pk=pk)
    serialiser = self.get_serializer_class()(queryset)
    return Response(serialiser.data, status=status.HTTP_200_OK)


  def update(self, request, pk=None, *args, **kwargs):
    course = get_object_or_404(Course, pk=pk)
    serializer = CourseSerializer(course, data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


  def partial_update(self, request, pk=None, *args, **kwargs):
    course = get_object_or_404(Course, pk=pk)
    serializer = CourseSerializer(course, data=request.data, partial=True)

    if not request.data:
      return Response(status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


  def update_video(self, request, course_id=None, video_id=None, *args, **kwargs):
    if not request.data.get('title') or not request.data.get('url'):
      return Response(status=status.HTTP_400_BAD_REQUEST)

    course = get_object_or_404(Course, pk=course_id)
    
    new_video_data = {
      'id': video_id,
      'title': request.data.get('title'),
      'url': request.data.get('url'),
      'duration': self._get_video_duration(request.data.get('url'))
    }

    video_urls_before_update = course.video_urls
    course.video_urls = [v if v['id'] != video_id else new_video_data for v in course.video_urls]
    
    if course.video_urls == video_urls_before_update:
      return Response(status=status.HTTP_404_NOT_FOUND)
    
    course.total_duration = self._calc_total_duration(course.video_urls)
    course.save()

    serializer = self.get_serializer_class()(course)
    return Response(serializer.data, status=status.HTTP_200_OK)


  def destroy(self, request, pk=None, *args, **kwargs):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


  def destroy_video(self, request, course_id=None, video_id=None, *args, **kwargs):
    course = get_object_or_404(Course, pk=course_id)

    video_urls_before_delete = course.video_urls
    course.video_urls = [v for v in course.video_urls if v['id'] != video_id]

    if course.video_urls == video_urls_before_delete:
      return Response(status=status.HTTP_404_NOT_FOUND)

    course.total_duration = self._calc_total_duration(course.video_urls)
    course.save()

    serializer = self.get_serializer_class()(course)
    return Response(serializer.data, status=status.HTTP_200_OK)

  def export(self, request, *args, **kwargs):
    pass


  def _get_video_duration(self, url):
    match = re.search(r'(https?://www\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11}))', url)
    if match:
        page = requests.get(match.group(0))
        soup = BeautifulSoup(page.content, 'html.parser')
        duration_tag = soup.find('meta', {'itemprop': 'duration'})
        if duration_tag:
            duration = parse_duration(duration_tag['content'])
            return str(duration)
    return "0:0:0"


  def _calc_total_duration(self, video_urls):
      hours, minutes, seconds = 0, 0, 0
      for video in video_urls:
          h, m, s = map(int, video['duration'].split(':'))
          seconds += s
          minutes += m + seconds // 60
          hours += h + minutes // 60
          seconds %= 60
          minutes %= 60
      return f'{hours}:{minutes}:{seconds}'