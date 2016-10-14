from django.core.management.base import BaseCommand
from panopto_client import PanoptoAPIException
from panopto_client.remote_recorder import RemoteRecorderManagement
from optparse import make_option


class Command(BaseCommand):
    help = "Show the status of Panopto remote recorders"

    option_list = BaseCommand.option_list + (
        make_option('--offline', action='store_true', dest='offline',
                    default=False,
                    help='Show only recorders in an abnormal state'))

    def handle(self, *args, **options):
        self._recorder = RemoteRecorderManagement()

        try:
            recorders = self._recorder.listRecorders()
        except PanoptoAPIException as err:
            self.stdout.write(str(err))

        for recorder in recorders:
            if options['offline']:
                if recorder.State == 'Stopped':
                    continue
                if recorder.State == 'Previewing':
                    continue
                if recorder.State == 'Recording':
                    continue

            self.stdout.write("%s: %s" % (recorder.Name, recorder.State))
