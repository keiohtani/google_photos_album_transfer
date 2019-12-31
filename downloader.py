from authentication import get_authenticated_service
import json
import urllib.request
import os
import re

ALBUM_PAGE_SIZE = 50
IMAGE_PATH = 'images'

service = get_authenticated_service()

with open('downloader_payload.json') as f:
    payload = json.loads(f.read())


def download_images(images_queue, payload=payload, dir_path=IMAGE_PATH):

    image_id = 10001

    while True:

        media_list = service.mediaItems().search(body=payload).execute()

        if 'mediaItems' not in media_list:  # when no items are found
            break

        for mediaItem in media_list['mediaItems']:
            # the size can be set by adding '=w2048-h1024' at the end of URL
            image_url = mediaItem['baseUrl']

            try:
                # w16383-h16383 will ensure to download an image at the maximum size.
                file_name = '{}.jpg'.format(str(image_id)[1:])
                file_path = os.path.join(dir_path, file_name)
                images_queue.put(file_path)
                urllib.request.urlretrieve(
                    image_url + '=w16383-h16383', file_path)
                image_id += 1

            except urllib.request.HTTPError as err:
                print(err.code, 'error found.')

        if 'nextPageToken' not in media_list:
            break

        print('next page')
        nextPageToken = media_list['nextPageToken']
        print(nextPageToken)
        payload['pageToken'] = nextPageToken

    print('finished downloading pictures')


def download_images_by_albums(images_queue):

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
            download_images(images_queue, payload, dir_path)

        if 'nextPageToken' not in album_list:
            break

        print('next page')
        nextPageToken = album_list['nextPageToken']
        print(nextPageToken)
        pageToken = nextPageToken

    print('finished downloading pictures')
