from authentication import get_authenticated_service
import json
import urllib.request
import os
import re
from queue import Queue

ALBUM_PAGE_SIZE = 50
IMAGE_PATH = 'images'
CLIENT_SECRETS_FILE = '.downloader_google_photos_client_secrets.json'
TOKEN_FILE = '.downloader_google_photos_token.json'

service = get_authenticated_service(CLIENT_SECRETS_FILE, TOKEN_FILE)

with open('downloader_payload.json') as f:
    payload = json.loads(f.read())


def download_images(images_queues, title, payload=payload, dir_path=IMAGE_PATH):

    images_queue = Queue()

    while True:

        media_list = service.mediaItems().search(body=payload).execute()

        if 'mediaItems' not in media_list:  # when no items are found
            break

        for mediaItem in media_list['mediaItems']:
            # the size can be set by adding '=w2048-h1024' at the end of URL
            image_url = mediaItem['baseUrl']

            try:
                # w16383-h16383 will ensure to download an image at the maximum size.
                file_name = mediaItem['filename']
                file_path = os.path.join(dir_path, file_name)
                urllib.request.urlretrieve(
                    image_url + '=w16383-h16383', file_path)
                images_queue.put(file_name)
            except urllib.request.HTTPError as err:
                print(err.code, 'error found.')

        if 'nextPageToken' not in media_list:
            break

        print('next page')
        nextPageToken = media_list['nextPageToken']
        payload['pageToken'] = nextPageToken

    album_object = {'title': title,
                    'dir_path': dir_path, 'queue': images_queue}

    images_queues.put(album_object)

    print('completed downloading an album')


def download_images_by_albums(images_queue):

    print('start downloading')

    pageToken = ''

    while True:
        album_list = service.albums().list(
            pageToken=pageToken, pageSize=ALBUM_PAGE_SIZE).execute()

        if 'albums' not in album_list:  # when no items are found
            break

        for album in album_list['albums']:
            title = album['title']
            album_name = re.sub('(\s|\/)', '_', title)
            dir_path = os.path.join(IMAGE_PATH, album_name)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            album_id = album['id']
            payload['albumId'] = album_id
            payload['pageToken'] = ''
            download_images(images_queue, title, payload, dir_path)

        if 'nextPageToken' not in album_list:
            break

        print('next page')
        nextPageToken = album_list['nextPageToken']
        pageToken = nextPageToken

    print('finished downloading pictures')
