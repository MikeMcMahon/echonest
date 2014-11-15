import json
import os
import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from echonest import settings
from echonest.controllers.ingest import process, find_track
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
    rejected_files = []
    uploaded_codes = []
    success = []

    if request.method == 'POST':
        uploaded_files = []
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
                try:
                    input_json = json.load(input_json_file)
                except:
                    rejected_files.append(f[0])
                else:
                    json_to_parse = json_to_parse + input_json

        for f in json_to_parse:
            ingested = Ingested()

            if 'metadata' not in f or 'filename' not in f['metadata'] or 'code' not in f:
                rejected_files.append({'name': 'failed to process json file, missing required fields'})
                continue

            ingested.filename = f['metadata']['filename']
            ingested.code = f['code']
            ingested.save()
            track_id = process(ingested)

            if track_id is not None:
                if type(track_id) is list:
                    for t_id in track_id:
                        track = find_track(t_id)
                        ingested.tracks.add(track)
                else:
                    track = find_track(track_id)
                    ingested.tracks.add(track)
                ingested.match = True
                success.append(ingested)
            else:
                uploaded_codes.append(ingested)

            ingested.save()

    return render(request, 'upload.html', {
        'uploaded': uploaded_codes,
        'success': success,
        'rejected': rejected_files,
    })


@never_cache
@csrf_protect
def song_listing(request, reason):
    match = True
    title = 'Matched Track Information'
    order_by = 'uploaded_on'
    if reason == 'unmatched':
        match = False
        title = 'Unmatched Track Information'
        order_by = 'last_attempt'

    sort_order_by = request.GET.get('sort')
    sort_direction = request.GET.get('dir', 'desc')
    if sort_direction == 'asc':
        direction = ''
    else:
        direction = '-'

    order_by = order_by if sort_order_by is None or sort_order_by == '' else sort_order_by
    order_by = order_by.lstrip().rstrip()
    ingested = Ingested.objects.filter(match=match).order_by(direction + order_by)

    paginator = Paginator(ingested, 100)

    page = request.GET.get('page')
    try:
        songs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        songs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        songs = paginator.page(paginator.num_pages)

    return render(request, 'songlisting.html', {
        'title': title,
        'order_by': order_by[1:] if order_by[0:1] == '-' else order_by,
        'sort_direction': sort_direction,
        'songs': songs
    })


@never_cache
@csrf_protect
def retry(request, ingested_id):
    """
    Attempts to retry a song unless we've already done this before, then just give me what we have...
    :param request:
    :param ingested_id:
    :return:
    """
    ingested = Ingested.objects.filter(id=ingested_id)
    if len(ingested) != 1:
        return HttpResponse(json.dumps({'status': 'too many or too few matching songs'}))
    else:
        ingested = ingested[0]

    if ingested.match:
        return HttpResponse(json.dumps({
            'track_id': [t.track_id for t in ingested.tracks],
            'last_attempt': ingested.last_attempt,
            'status': 'success',
        }))

    track_id = process(ingested)

    if track_id is not None:
        track = find_track(track_id)
        ingested.tracks.add(track)
        ingested.match = True

    ingested.last_attempt = datetime.datetime.now()
    ingested.save()

    return HttpResponse(json.dumps({
        'track_id': [track_id],
        'last_attempt': ingested.last_attempt.strftime('%b. %d, %Y'),
        'status': 'success' if track_id is not None else 'failed',
        }))