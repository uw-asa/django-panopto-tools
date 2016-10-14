from django.conf.urls import patterns, url
from views.recorder_feed import RecorderFeed

urlpatterns = patterns(
    '',
    url(r'^preview/(?P<recorder_id>[0-9a-f\-]+)(.jpe?g)?$',
        'panopto_tools.views.recorderpreview.preview'),
    url(r'^recordings/(?P<recorder_id>[0-9a-f\-]+)\.ics$', RecorderFeed()),
    url(r'^recordings/'
        r'(?P<building>[a-zA-Z0-9]+)[ +_-](?P<room>[a-zA-Z0-9]+)\.ics$',
        RecorderFeed()),
)
