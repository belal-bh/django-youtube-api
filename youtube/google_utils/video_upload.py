import datetime
from Google import Create_Service
from googleapiclient.http import MediaFileUpload
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


# CLIENT_SECRET_FILE = BASE_DIR /  '.secret/client_secret_django_youtube_api_app.json'
CLIENT_SECRET_FILE = BASE_DIR /  '.secret/desktop_client_1.json'

print('BASE_DIR:', BASE_DIR)
print('CLIENT_SECRET_FILE:', CLIENT_SECRET_FILE)
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

upload_date_time = datetime.datetime(2021, 7, 12, 22, 30, 0).isoformat() + '.000Z'

request_body = {
    'snippet': {
        'categoryI': 19,
        'title': 'Upload Testing',
        'description': 'Hello World Description',
        'tags': ['Travel', 'video test', 'Travel Tips']
    },
    'status': {
        'privacyStatus': 'private',
        'publishAt': upload_date_time,
        'selfDeclaredMadeForKids': False, 
    },
    'notifySubscribers': False
}

mediaFile = MediaFileUpload('video.mp4')

response_upload = service.videos().insert(
    part='snippet,status',
    body=request_body,
    media_body=mediaFile
).execute()


service.thumbnails().set(
    videoId=response_upload.get('id'),
    media_body=MediaFileUpload('thumbnail.png')
).execute()

