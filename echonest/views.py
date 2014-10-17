import json
from multiprocessing.pool import Pool
import os
import urllib2
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from echonest import settings
from echonest.models import Ingested


def handle_upload_file(f):
    file_name = os.path.join(settings.UPLOADS_DIR, f.name)
    with open(os.path.join(settings.UPLOADS_DIR, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_name


@csrf_protect
@never_cache
def ingester(request):
    uploaded_files = []
    uploaded_codes = []
    rejected_files = []

    if request.method == 'POST':
        input_files = request.FILES.getlist('input_file')
        for f in input_files:
            if f.name.endswith('.json'):
                file_name = handle_upload_file(f)
                uploaded_files.append((f, file_name))
            else:
                rejected_files.append(f)

        json_to_parse = []
        for f in uploaded_files:
            with open(f[1], 'rb') as input_json_file:
                input_json = json.load(input_json_file)
                json_to_parse = json_to_parse + input_json

        for f in json_to_parse:
            ingested = Ingested()
            ingested.filename = f['metadata']['filename']
            ingested.code = f['code']
            track_id = process(ingested)
            if track_id is not None:
                ingested.match = True
                ingested.track_id = track_id

            ingested.save()
            uploaded_codes.append(ingested)

    return render(request, 'upload.html', {
        'uploaded': uploaded_codes,
        'rejected': rejected_files
    })


def process(ingest):
    json_data = ''
    if settings.REMOTE_ENABLED:
        scraped = urllib2.urlopen(settings.REMOTE_API_URL + ingest.code)
        json_data = json.loads(scraped.read())

    ingest.match = True
    ingest.save()
    return json_data['track_id']