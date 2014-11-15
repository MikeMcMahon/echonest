"""
author: Family
date: 10/20/2014
"""
import json
import urllib2
import time
from echonest import settings
from echonest.models import MatchedTrack

import fp


def process(ingest, retry=0):
    json_data = {'track_id': None}
    #if settings.REMOTE_ENABLED:
    try:
        scraped = urllib2.urlopen(settings.REMOTE_API_URL + ingest.code)
    except urllib2.URLError:
        time.sleep(5)
        retry += 1
        if retry <= 3:
            return process(ingest, retry)
    else:
        json_data = json.loads(scraped.read())
    #else:
    #    response = fp.best_match_for_query(ingest.code)
    #    json_data['track_id'] = response.TRID

    return json_data['track_id']


def find_track(track_id):
    """
    Finds or creates the specified track id so that it may be associated with an ingested code
    :param track_id:
    :return:
    """
    tracks = MatchedTrack.objects.filter(track_id=track_id)
    if len(tracks) == 0:
        track = MatchedTrack()
        track.track_id = track_id
        track.save()
    else:
        track = tracks[0]

    return track