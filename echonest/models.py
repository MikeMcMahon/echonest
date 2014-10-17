from django.db import models


class Ingested(models.Model):
    ingested_code = models.TextField()
    ingested_on = models.DateField()
    match = models.BooleanField()
    track_id = models.TextField(max_length=255)