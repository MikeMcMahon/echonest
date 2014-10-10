import os
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from echonest import settings


def handle_upload_file(f):
    with open(os.path.join(settings.UPLOADS_DIR, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@csrf_protect
@never_cache
def ingester(request):
    if request.method == 'POST':
        input_files = request.FILES.getlist('input_file')
        for f in input_files:
            handle_upload_file(f)

    return render(request, 'upload.html', {})