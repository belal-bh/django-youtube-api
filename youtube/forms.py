from django.db.models import fields
from django.forms import ModelForm, models
from .models import YTVideo

class YTVideoForm(ModelForm):
    class Meta:
        model = YTVideo
        fields = '__all__'
