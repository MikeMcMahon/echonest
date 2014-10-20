"""
author: Family
date: 10/20/2014
"""
import json
import urllib2
from echonest import settings


def process(ingest):
    json_data = {'track_id': None}
    if settings.REMOTE_ENABLED:
        scraped = urllib2.urlopen(settings.REMOTE_API_URL + ingest.code)
        json_data = json.loads(scraped.read())

    return json_data['track_id']