from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.shortcuts import render

from .forms import YTVideoForm


@login_required
def upload(request):
    status = 'NONE'
    form = YTVideoForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            success = True
            video = form.save(commit=False)
            video.user = request.user
            try:
                video.save()
                status = 'SUCCESS'
            except Exception as error:
                # print("ERROR:", error)
                status = 'FAILED'
                success = False
            if success:
                form = YTVideoForm()
            else:
                form = YTVideoForm(request.POST or None, request.FILES or None)
                form.add_error('__all__', ValidationError(
                    "Video save failed by unexpected reason! Make sure everything right or try later."))
    context = {
        'form': form,
        'status': status
    }

    return render(request, 'youtube/upload.html', context)
