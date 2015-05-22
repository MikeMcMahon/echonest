import json
import os
import datetime
import random
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
import subprocess

from echonest import settings
from echonest.controllers.ingest import process, find_track
from echonest.models import Ingested

from string import ascii_letters


def handle_upload_file(f):
    seed = ascii_letters + "01234567890-_"
    size = f.size / 1024.0 / 1024.0

    if size > 10:
        return None

    f_name = ''.join(seed[random.randrange(0, len(seed) - 1)] for x in range(30))
    file_name = os.path.join(settings.UPLOADS_DIR, f_name)

    with open(os.path.join(settings.UPLOADS_DIR, f_name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_name


@csrf_protect
@never_cache
def login(request):
    return render(
        request,
        'login.html',
        {}
    )


def get_uploaded_files(input_files, extension='.json'):
    uploaded_files = []
    rejected_files = []
    for f in input_files:
        if f.name.endswith(extension):
            file_name = handle_upload_file(f)
            if file_name:
                uploaded_files.append((f, file_name))
            else:
                # TODO - we should have legit reasons
                rejected_files.append(f)
        else:
            rejected_files.append(f)
    return uploaded_files, rejected_files


def process_ingested_json(json_to_parse, rejected_files, success, uploaded_codes):
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


def process_json_uploads(request, input_files):
    uploaded_files, rejected_files = get_uploaded_files(input_files)
    success = []
    uploaded_codes = []

    json_to_parse = []
    for f in uploaded_files:
        with open(f[1], 'rb') as input_json_file:
            try:
                input_json = json.load(input_json_file)
            except:
                rejected_files.append(f[0])
            else:
                json_to_parse = json_to_parse + input_json
        try:
            os.remove(f[1])
        except:
            pass

    process_ingested_json(json_to_parse, rejected_files, success, uploaded_codes)

    return render(request, 'upload.html', {
        'mode': 'json',
        'lawl': 'JSONS',
        'uploaded': uploaded_codes,
        'success': success,
        'rejected': rejected_files,
    })


def process_mp3_uploads(request, input_files):
    uploaded_files, rejected_files = get_uploaded_files(input_files, '.mp3')
    success = []
    uploaded_codes = []

    json_to_parse = []
    for f in uploaded_files:
        try:
            codegen_output = subprocess.Popen(["/data/echoprint-codegen/echoprint-codegen", f[1]], stdout=subprocess.PIPE)
            stdoutdata, stderrdata = codegen_output.communicate()
        except Exception as ex:
            f[0].name += "--subprocess-call--" + str(ex)
            rejected_files.append(f[0])
        else:
            try:
                json_to_parse = json.loads(stdoutdata)
            except Exception as ex:
                f[0].name += "--parsing-the-json--" + str(ex) + "--" + str(stdoutdata) + str(stderrdata)
                rejected_files.append(f[0])

        try:
            os.remove(f[1])
        except:
            pass

    process_ingested_json(json_to_parse, rejected_files, success, uploaded_codes)

    for s in success:
        for uf in uploaded_files:
            if uf[0] == s.filename:
                s.filename = uf[0]

    for rf in range(len(uploaded_codes)):
        for uf in uploaded_files:
            if uf[0] == uploaded_codes[rf]:
                uploaded_codes[rf] = uf[0]

    return render(request, 'upload.html', {
        'mode': 'mp3',
        'lawl': 'em pee threes',
        'uploaded': uploaded_codes,
        'success': success,
        'rejected': rejected_files,
    })

@csrf_protect
@never_cache
def ingester(request):
    if request.method == 'POST':
        ingest_mode = request.POST.get('mode', None)

        input_files = request.FILES.getlist('input_files')

        if ingest_mode == 'json':
            return process_json_uploads(request, input_files)

        if ingest_mode == 'mp3':
            return process_mp3_uploads(request, input_files)

    return render(request, 'upload.html', {
        'uploaded': [],
        'success': [],
        'rejected': [],
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