from django_ical.views import ICalFeed
from icalendar import vCalAddress, vText
from scheduler.views.api.exceptions import MissingParamException, \
    InvalidParamException
from panopto_client import PanoptoAPIException
from panopto_client.remote_recorder import RemoteRecorderManagement
from panopto_client.session import SessionManagement
from panopto_client.user import UserManagement
from scheduler.utils.recorder import get_api_recorder_details, \
    RecorderException
from restclients.r25.spaces import get_spaces
import datetime
import logging


logger = logging.getLogger(__name__)


class RecorderFeed(ICalFeed):
    """
    ical feed from Panopto scheduled recordings
    """
    def __init__(self):
        self._api = RemoteRecorderManagement()
        self._session_api = SessionManagement()
        self._user_api = UserManagement()

        # timeout in hours
        self._space_list_cache_timeout = 1

    product_id = '-//UW-IT CTE//PanoptoScheduledRecordings//EN'
    timezone = 'America/Los_Angeles'
    description = "Panopto Scheduled Recordings"

    def get_object(self, request, *args, **kwargs):
        if 'building' in kwargs and 'room' in kwargs:
            spaces = get_spaces(starts_with=kwargs['building'],
                                ends_with=kwargs['room'])

            return get_api_recorder_details(self._api, spaces[0].space_id)

        elif 'recorder_id' in kwargs:
            return get_api_recorder_details(self._api, kwargs['recorder_id'])

        else:
            return []

    def title(self, recorders):
        return "Scheduled recordings in %s" % \
               (', '.join([recorder.Name for recorder in recorders]))

    def file_name(self, recorders):
        return "%s.ics" % '_'.join(recorders[0].Name.split())

    def items(self, recorders):
        session_ids = []
        for recorder in recorders:
            if recorder.ScheduledRecordings is not None:
                session_ids.append(recorder.ScheduledRecordings.guid)
        sessions = self._session_api.getSessionsById(session_ids)
        return sessions.Session if (sessions and 'Session' in sessions and
                                    len(sessions.Session)) else None

    def item_guid(self, session):
        return session.Id

    def item_title(self, session):
        return session.Name

    def item_description(self, session):
        return session.Description

    def item_link(self, session):
        return session.ViewerUrl

    def item_created(self, session):
        return datetime.datetime.now()

    def item_start_datetime(self, session):
        return session.StartTime

    def item_end_datetime(self, session):
        return session.StartTime + \
               datetime.timedelta(seconds=int(session.Duration))

    def item_organizer(self, session):
        users = self._user_api.getUsers(session.CreatorId)

        organizer = vCalAddress("MAILTO:%s" % users.User[0].Email)
        organizer.params['cn'] = \
            vText("%s %s" % (users.User[0].FirstName, users.User[0].LastName))
        return organizer
