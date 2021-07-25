import errno
import http.client
import os
import pickle
import random
import time
from pathlib import Path

import httplib2
from django.conf import settings
from django.utils.translation import ugettext as _
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


class OperationError(BaseException):
    """
    Raise when an error happens on YTApi class
    """
    pass


class YTApiError(BaseException):
    """
    Raise when a Youtube API related error occurs
    i.e. redirect Youtube errors with this error
    """
    pass


class YTApi:
    """
    YouTube Wrapper API
    see: https://developers.google.com/youtube/v3
    """

    def yt_api_get_authenticated_service():
        """
        Generate authenticated service using setting.YOUTUBE_API_CONFIG credentials.
        """
        # The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
        # the OAuth 2.0 information for this application, including its client_id and
        # client_secret. You can acquire an OAuth 2.0 client ID and client secret from
        # the Google API Console at
        # https://console.developers.google.com/.
        # Please ensure that you have enabled the YouTube Data API for your project.
        # For more information about using OAuth2 to access the YouTube Data API, see:
        #   https://developers.google.com/youtube/v3/guides/authentication
        # For more information about the client_secrets.json file format, see:
        #   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
        YT_SECRET_DIR = settings.BASE_DIR / '.yt_secrets'
        try:
            # relative path from BASE_DIR
            CLIENT_SECRET_FILE = YT_SECRET_DIR / settings.YOUTUBE_API_CONFIG.get(
                'CLIENT_SECRET_FILE')
        except AttributeError:
            raise OperationError(
                "Youtube CLIENT_SECRET_FILE is missing on settings.")

        # This OAuth 2.0 access scope allows an application to upload files to the
        # authenticated user's YouTube channel, but doesn't allow other types of access.
        try:
            API_NAME = settings.YOUTUBE_API_CONFIG.get(
                'API_NAME', 'youtube')
        except AttributeError:
            raise OperationError(
                "Youtube API_NAME is missing on settings.")
        try:
            API_VERSION = settings.YOUTUBE_API_CONFIG.get(
                'API_VERSION', 'v3')
        except AttributeError:
            raise OperationError(
                "Youtube API_VERSION is missing on settings.")
        try:
            SCOPES = settings.YOUTUBE_API_CONFIG.get(
                'SCOPES', ['https://www.googleapis.com/auth/youtube.upload'])
        except AttributeError:
            raise OperationError(
                "Youtube SCOPES is missing on settings.")
        try:
            # client id is not required but will be used for other features like analytics
            CLIENT_ID = settings.YOUTUBE_API_CONFIG.get('CLIENT_ID', None)
        except AttributeError:
            CLIENT_ID = None

        # Check CLIENT_SECRET_FILE is exist or not
        if not Path.exists(CLIENT_SECRET_FILE):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), CLIENT_SECRET_FILE)

        cred = None
        pickle_file = YT_SECRET_DIR / f'token_{API_NAME}_{API_VERSION}.pickle'

        if Path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                cred = pickle.load(token)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                try:
                    cred.refresh(Request())
                except Exception as error:
                    # This should not happen
                    # If this happen we have to consider
                    # it can happen when CLIENT_SECRET_FILE or Access to data api changed
                    # we must have to debug it

                    """
                    # bellow this section we are tring to regenerate cred
                    # with CLIENT_SECRET_FILE and SCOPES
                    # but this will in browser to authenticate the cred
                    # that's not expected for user
                    # so that we are commenting out this section
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            CLIENT_SECRET_FILE, SCOPES)
                        cred = flow.run_local_server()
                    except Exception as error:
                        raise error
                    """

                    # now just raising the YTApiError error
                    raise YTApiError(error)
            else:
                # bellow this section we are tring to regenerate cred
                # with CLIENT_SECRET_FILE and SCOPES
                # but this will in browser to authenticate the cred
                # that's not expected for user
                # so that we should comment out this section
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CLIENT_SECRET_FILE, SCOPES)
                    cred = flow.run_local_server()
                except Exception as error:
                    raise error

            with open(pickle_file, 'wb') as token:
                pickle.dump(cred, token)

        try:
            service = build(API_NAME, API_VERSION, credentials=cred)
            return service
        except Exception as error:
            raise YTApiError(error)

    # yt_service is a shared resource
    yt_service = yt_api_get_authenticated_service()

    def __init__(self):
        # TODO: need some custom check LATER
        self.authenticated = True

    def initialize_upload(self, ytv_instance, media_file):
        """
        Upload video from browser
        Raises:
            YTApiError: on no authentication

        return: success, response
            success: True or False
            response: YTApi.yt_service.videos().insert() response
        """
        # Raise YTApiError if not authenticated
        if not self.authenticated:
            raise YTApiError(_("Authentication is required"))

        # generate
        # See: https://developers.google.com/youtube/v3/docs/videos/insert
        # and https://developers.google.com/youtube/v3/docs/videos#resource
        body = dict(
            snippet=dict(
                title=ytv_instance.title,
                description=ytv_instance.description,
                tags=ytv_instance.tags.split(","),
                categoryId=ytv_instance.category_id
            ),
            status=dict(
                privacyStatus=ytv_instance.privacy_status,
                embeddable=ytv_instance.embeddable,
                publishAt=ytv_instance.publish_at_iso,
                selfDeclaredMadeForKids=ytv_instance.made_for_kids,
            )
        )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = YTApi.yt_service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            # The chunksize parameter specifies the size of each chunk of data, in
            # bytes, that will be uploaded at a time. Set a higher value for
            # reliable connections as fewer chunks lead to faster uploads. Set a lower
            # value for better recovery on less reliable connections.
            #
            # Setting "chunksize" equal to -1 in the code below means that the entire
            # file will be uploaded in a single HTTP request. (If the upload fails,
            # it will still be retried where it left off.) This is usually a best
            # practice, but if you're using Python older than 2.6 or if you're
            # running on App Engine, you should set the chunksize to something like
            # 1024 * 1024 (1 megabyte).
            media_body=MediaFileUpload(
                media_file, chunksize=-1, resumable=True),
            notifySubscribers=ytv_instance.notify_subscribers,
        )

        return self.resumable_upload(insert_request)

    # This method implements an exponential backoff strategy to resume a
    # failed upload.
    def resumable_upload(self, request):
        """
        Upload video chunk by chunk

        return: success, response
            success: True or False
            response: YTApi.yt_service.videos().insert() response
        """
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                status, response = request.next_chunk()
                # print('Uploading file...')
                if response is not None:
                    if 'id' in response:
                        # print('Video id "%s" was successfully uploaded.' %
                        #       response['id'])
                        # print('response:', response)
                        return True, response
                    else:
                        # exit(
                        #     'The upload failed with an unexpected response: %s' % response)
                        return False, response
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                         e.content)
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = 'A retriable error occurred: %s' % e

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit('No longer attempting to retry.')

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print('Sleeping %f seconds and then retrying...' %
                      sleep_seconds)
                time.sleep(sleep_seconds)

    def set_video_thumbnail(self, video_id, thumbnail):
        """
        Upload video thumbnail
        Raises:
            YTApiError: on no authentication

        return:
            response: YTApi.yt_service.thumbnails().set() response
        """
        # Raise YTApiError if not authenticated
        if not self.authenticated:
            raise YTApiError(_("Authentication is required"))

        response_thumbnail = YTApi.yt_service.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail)
        ).execute()

        return response_thumbnail

    def upload_video(self, request_body, media_file):
        """
        Upload video from browser
        Raises:
            YTApiError: on no authentication
        """
        # Raise YTApiError if not authenticated
        if not self.authenticated:
            raise YTApiError(_("Authentication is required"))

        media_file_upload = MediaFileUpload(media_file)

        response_upload = YTApi.yt_service.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media_file_upload
        ).execute()

        return response_upload
