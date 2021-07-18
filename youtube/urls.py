from django.urls import path
from .views import upload

app_name = 'youtube'
urlpatterns = [
    path('upload/', upload, name='upload'),
]