import datetime
from django.db import models
from echonest import settings


class MatchedTrack(models.Model):
    track_id = models.TextField(max_length=255, unique=True)
    found_on = models.DateField(default=datetime.datetime.now().date())

    def solr_url(self):
                return settings.REMOTE_SOLR_URL.format(self.track_id)


class Ingested(models.Model):
    filename = models.TextField(max_length=1000)
    code = models.TextField()
    uploaded_on = models.DateTimeField(default=datetime.datetime.now())
    last_attempt = models.DateTimeField(default=datetime.datetime.now())
    match = models.BooleanField(default=False)
    tracks = models.ManyToManyField('MatchedTrack', null=True)