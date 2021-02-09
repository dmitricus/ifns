import sys

from django.core.management.base import BaseCommand
from django.utils import timezone

from ifns.handlers import IFNSHandler


class Command(BaseCommand):
    def handle(self, *args, **options):
        sys.stdout.write('Start load_ifns command at {}\n'.format(timezone.now().isoformat()))
        handler = IFNSHandler()
        handler.run()
        sys.stdout.write('End load_ifns command at {}\n'.format(timezone.now().isoformat()))
