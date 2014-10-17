import os
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from echonest import settings


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
    rejected_files = []

    if request.method == 'POST':
        input_files = request.FILES.getlist('input_file')
        for f in input_files:
            if f.name.endswisth('.json'):
                uploaded_files.append(handle_upload_file(f))
            else:
                rejected_files.append(f)

        for f in uploaded_files:
            pass

    return render(request, 'upload.html', {
        'uploaded': uploaded_files,
        'rejected': rejected_files
    })