from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import context

from .forms import YTVideoForm


@login_required
def upload(request):
    status = 'NONE'
    form = YTVideoForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            video = form.save()
            status = f"Upload complete. video id: {video.video_id}"
            form = YTVideoForm()
    context = {
        'form': form,
        'status': status
    }

    return render(request, 'youtube/upload.html', context)
    