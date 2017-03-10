from django.conf.urls import url

from views.recorder_feed import RecorderFeed
from .views import recorderpreview

urlpatterns = [
    url(r'^preview/(?P<recorder_id>[0-9a-f\-]+)(.jpe?g)?$',
        recorderpreview.preview),
    url(r'^recordings/(?P<recorder_id>[0-9a-f\-]+)\.ics$', RecorderFeed()),
    url(r'^recordings/'
        r'(?P<building>[a-zA-Z0-9]+)[ +_-](?P<room>[a-zA-Z0-9]+)\.ics$',
        RecorderFeed()),
]
