import datetime
from django.db import models
from echonest import settings


class Ingested(models.Model):
    filename = models.TextField(max_length=1000)
    code = models.TextField()
    uploaded_on = models.DateField(default=datetime.datetime.now().date())
    last_attempt = models.DateField(default=datetime.datetime.now().date())
    match = models.BooleanField(default=False)
    track_id = models.TextField(max_length=255)

    def solr_url(self):
        return '' if not self.match else settings.REMOTE_SOLR_URL.format(self.track_id)