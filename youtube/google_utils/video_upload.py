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
        'categoryId': 19,
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

'''
# Response data
print(response_upload)
{
    'kind': 'youtube#video', 
    'etag': 'WfLyYwJhzVHW-oOQOCGnavMb2QQ', 
    'id': '7Gq5lkoE2vw', 
    'snippet': {
        'publishedAt': '2021-07-12T17:16:55Z', 
        'channelId': 'UCqlil5nuDW94jq9Py6sA-yw', 
        'title': 'Upload Testing', 
        'description': 'Hello World Description', 
        'thumbnails': {
            'default': {
                'url': 'https://i9.ytimg.com/vi/7Gq5lkoE2vw/default.jpg?sqp=CJTxsYcG&rs=AOn4CLDX4x_VdpNxhQXwDggSTXG-jB8dOw', 
                'width': 120, 
                'height': 90
            }, 
            'medium': {
                'url': 'https://i9.ytimg.com/vi/7Gq5lkoE2vw/mqdefault.jpg?sqp=CJTxsYcG&rs=AOn4CLAUMkuD3m6qGUyhN-3qI3QBvFbBmA', 
                'width': 320, 
                'height': 180
            }, 
            'high': {
                'url': 'https://i9.ytimg.com/vi/7Gq5lkoE2vw/hqdefault.jpg?sqp=CJTxsYcG&rs=AOn4CLDdju-P9__ZjfiqYqQaT7UBrBk3TQ', 
                'width': 480, 
                'height': 360
            }
        }, 
        'channelTitle': 'Albert Jhon', 
        'tags': ['Travel', 'Travel Tips', 'video test'], 
        'categoryId': '22', 
        'liveBroadcastContent': 'none', 
        'localized': {
            'title': 'Upload Testing', 
            'description': 'Hello World Description'
        }
    }, 
    'status': {
        'uploadStatus': 'uploaded', 
        'privacyStatus': 'private', 
        'publishAt': '2021-07-12T22:30:00Z', 
        'license': 'youtube', 
        'embeddable': True, 
        'publicStatsViewable': True, 
        'selfDeclaredMadeForKids': False
    }
}
'''

