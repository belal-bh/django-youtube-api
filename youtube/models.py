from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel
from .utils.api import YTApi

User = get_user_model()


class YTVideo(TimeStampedModel):
    """Video
    YouTube video API model.
    See: https://developers.google.com/youtube/v3/docs/videos
    """
    class VideoCategory(models.IntegerChoices):
        PEOPLE_AND_BLOG = 22, _('People and Blog')

    class PrivacyStatus(models.TextChoices):
        PRIVATE = 'private', _('Private')
        UNLISTED = 'unlisted', _('Unlisted')
        PUBLIC = 'public', _('Public')

    publish_at_day_after = 15

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, help_text=_("User who uploaded video"))
    video_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True, help_text=_("YouTube video id"))
    title = models.CharField(max_length=100, blank=False, help_text=_(
        "The video's title. The property value has a maximum length of 100 characters "
        "and may contain all valid UTF-8 characters except < and >."))
    description = models.TextField(blank=True, help_text=_(
        "The video's description. The property value has a maximum length of 5000 bytes "
        "and may contain all valid UTF-8 characters except < and >."))
    tags = models.CharField(
        max_length=255, blank=True, help_text=_("Comma seperated tags"))
    category_id = models.SmallIntegerField(choices=VideoCategory.choices,
                                           default=VideoCategory.PEOPLE_AND_BLOG, help_text=_(
                                               "The YouTube video category associated with the video."
                                               "You must set a value for this property if you call the videos.update method "
                                               "and are updating the snippet part of a video resource."))
    privacy_status = models.CharField(max_length=10, choices=PrivacyStatus.choices,
                                      default=PrivacyStatus.PRIVATE, help_text=_("The video's privacy status."))
    publish_at = models.DateTimeField(default=datetime.now() + timedelta(publish_at_day_after), help_text=_(
        "The date and time when the video is scheduled to publish. "
        "It can be set only if the privacy status of the video is private. "
        "The value is specified in ISO 8601 format."))
    embeddable = models.BooleanField(default=True, help_text=_(
        "This value indicates whether the video can be embedded on another website."))
    made_for_kids = models.BooleanField(default=False, help_text=_(
        "This value indicates whether the video is designated as child-directed, and it "
        "contains the current 'made for kids' status of the video."))
    notify_subscribers = models.BooleanField(default=False, help_text=_(
        "The notifySubscribers parameter indicates whether YouTube should send a "
        "notification about the new video to users who subscribe to the video's channel. A "
        "parameter value of True indicates that subscribers will be notified of newly uploaded videos."))

    youtube_url = models.URLField(max_length=255, null=True, blank=True)

    file_on_server = models.FileField(upload_to='youtube/videos', null=True,
                                      help_text=_("Temporary file on server for \
                                              using in `direct upload` from \
                                              your server to youtube"))

    def __str__(self):
        return f"{self.id}:{self.title}"

    def save(self, *args, **kwargs):
        # do_something()
        print("before super save")
        super().save(*args, **kwargs)
        # do_something_else()
        print("after super save")

@receiver(pre_save, sender=YTVideo)
def pre_save_ytvideo_receiver(sender, instance, *args, **kwargs):
    if instance:
        api = YTApi()
        success, response = api.initialize_upload(instance, instance.file_on_server.path)
        print(success, response)
        instance.video_id = response['id']
        print(instance)
        print("pre_save_ytvideo_receiver -> OK")
    else:
        print("pre_save_ytvideo_receiver -> instance was None!")

@receiver(post_save, sender=YTVideo)
def post_save_ytvideo_receiver(sender, instance, created, *args, **kwargs):
    if instance:
        print("post_save_ytvideo_receiver done!")
    else:
        print("post_save_ytvideo_receiver instance is None!")
