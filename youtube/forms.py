from django.forms import ModelForm

from .models import YTVideo


class YTVideoForm(ModelForm):
    class Meta:
        model = YTVideo
        # fields = '__all__'
        exclude = ['user', 'video_id', 'youtube_url']

    def save(self, commit=True):
        return super().save(commit=commit)
