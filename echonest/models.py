import datetime
from django.db import models
from echonest import settings


class MatchedTrack(models.Model):
    track_id = models.TextField(max_length=255)
    found_on = models.DateField(default=datetime.datetime.now().date())

    def solr_url(self):
                return '' if not self.match else settings.REMOTE_SOLR_URL.format(self.track_id)

    def ingested(self):
        return Ingested.objects.filter(tracks__id=self.id)


class Ingested(models.Model):
    filename = models.TextField(max_length=1000)
    code = models.TextField()
    uploaded_on = models.DateField(default=datetime.datetime.now().date())
    last_attempt = models.DateField(default=datetime.datetime.now().date())
    match = models.BooleanField(default=False)
    tracks = models.ManyToManyField('MatchedTrack', null=True)