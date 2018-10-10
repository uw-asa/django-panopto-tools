from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from userservice.user import UserService
from authz_group import Group
from panopto_client.remote_recorder import RemoteRecorderManagement
from panopto_client import PanoptoAPIException
import re
import logging
from PIL import Image
import urllib2
import simplejson as json
from panopto_tools.models import PersistentData
import pickle
import datetime


logger = logging.getLogger(__name__)

_api = RemoteRecorderManagement()


@login_required
def preview(request, **kwargs):
    user = UserService().get_original_user()
    if not Group().is_member_of_group(user, settings.PANOPTO_PREVIEW_GROUP):
        return HttpResponseRedirect("/")

    recorder_id = kwargs.get('recorder_id')

    try:
        thumb = get_recorder_thumbnail(recorder_id)
        return HttpResponse(thumb.read(), content_type="image/jpeg")
    except (PanoptoAPIException, IOError) as err:
        logger.exception(err)
        red = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response


def get_api_recorder_details(api, recorder_id):
    if re.match(r'^\d+$', recorder_id):
        recorders = api.getRemoteRecordersByExternalId(recorder_id)
    else:
        recorders = api.getRemoteRecordersById(recorder_id)

    if not (recorders and hasattr(recorders, 'RemoteRecorder')):
        return None

    return recorders.RemoteRecorder


def get_private_recorder_details(recorder_id):
    key = 'RecorderDetails_%s' % recorder_id
    expiration = timezone.now() - datetime.timedelta(hours=1)

    try:
        details = PersistentData.objects.get(name=key)
        if details.timestamp > expiration:
            return json.loads(details.value)
    except PersistentData.DoesNotExist:
        details = PersistentData(name=key)

    url = 'https://%s/Panopto/Api/remoteRecorders/%s' % \
          (settings.PANOPTO_SERVER, recorder_id)

    request = urllib2.Request(url)
    _add_cookies(request)
    result = urllib2.urlopen(request)

    details.value = result.read()
    details.save()

    return json.loads(details.value)


def get_recorder_preview_url(recorder_id):
    key = 'ThumbnailURL_%s' % recorder_id
    expiration = timezone.now() - datetime.timedelta(hours=1)

    try:
        url = PersistentData.objects.get(name=key)
        if url.timestamp > expiration:
            return url.value
    except PersistentData.DoesNotExist:
        url = PersistentData(name=key)

    recorders = get_api_recorder_details(_api, recorder_id)

    if recorders is None:
        raise RecorderException("No Recorder Found")

    for recorder in recorders:
        recorder.PrivateDetails = get_private_recorder_details(recorder.Id)
        for device in recorder.PrivateDetails['Devices']:
            if recorder.PrivateDetails['PrimaryVideoDeviceId'] == \
                    device['DeviceId']:
                url.value = device['VideoPreviewUrl']
                url.save()
                return url.value

    raise RecorderException("Recorder Preview URL Not Found")


def get_recorder_thumbnail(recorder_id):
    url = get_recorder_preview_url(recorder_id)

    request = urllib2.Request(url)
    _add_cookies(request)
    result = urllib2.urlopen(request)

    return result


def _add_cookies(request):
    cookiejar = _api._api.options.transport.cookiejar
    cookiejar.add_cookie_header(request)

    key = 'CookieJar'
    try:
        c = PersistentData.objects.get(name=key)
    except PersistentData.DoesNotExist:
        c = PersistentData(name=key)

    if not request.has_header('Cookie'):
        # try saved cookie
        cookiejar._cookies = pickle.loads(c.value)
        cookiejar.add_cookie_header(request)

    if not request.has_header('Cookie'):
        # make an authenticated request through public api
        _api.listRecorders()
        cookiejar.add_cookie_header(request)

    c.value = pickle.dumps(cookiejar._cookies)
    c.save()
