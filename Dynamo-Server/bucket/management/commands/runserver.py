import atexit
import signal
import sys
import delegator
from django.core.management.commands.runserver import BaseRunserverCommand
from bucket.handoff import handler

class Command(BaseRunserverCommand):
    def __init__(self, *args, **kwargs):
        atexit.register(self._exit)
        signal.signal(signal.SIGINT, self._handle_SIGINT)
        super(Command, self).__init__(*args, **kwargs)

    def _exit(self):
        flag = 0
        handler(flag)

    def _handle_SIGINT(self, signal, frame):
        #self._exit()
        sys.exit(0)
