from django.core.management import BaseCommand

import os
import shutil
import datetime

import sys
from echonest import settings

sys.path.insert(0, os.path.join(settings.INGESTER_API_DIR, 'API'))
sys.path.insert(0, os.path.join(settings.INGESTER_API_DIR, 'util'))

from fastingest import parse_json_dump
import fp


class Command(BaseCommand):

    def backup(self, files):
        stamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%MZ')

        for f in files:
            dst = os.path.join(settings.INGESTER_BACK_DIR, "{0}-{1}".format(stamp, f))
            src = os.path.join(settings.INGESTER_JSON_DIR, f)
            print "Moving {0} to {1}".format(src,  dst)
            shutil.move(src, dst)

    def handle(self, *args, **options):
        files = os.listdir(settings.INGESTER_JSON_DIR)
        files = [f for f in files if '.json' in f]

        for f in files:
            print "Ingesting file {0}".format(f)
            codes, bigeval = parse_json_dump(os.path.join(settings.INGESTER_JSON_DIR, f))
            fp.ingest(codes, do_commit=False)
            print "Commiting to database!"
            fp.commit()
            self.backup([f])