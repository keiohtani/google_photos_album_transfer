# Ref: https://qiita.com/inasawa/items/e5362dec4bd45d6900f7
import os
from time import sleep
from authentication import get_authenticated_service
import requests
import sys


CLIENT_SECRETS_FILE = '.downloader_google_photos_client_secrets.json'
TOKEN_FILE = '.downloader_google_photos_token.json'
API_TRY_MAX = 3

service = get_authenticated_service(CLIENT_SECRETS_FILE, TOKEN_FILE)


def upload_images(images_queue):
    previous_album = ''
    album_id = 0
    sleep(30)
    while True:
        if not images_queue.empty():
            sleep(10)
            image_path = images_queue.get()
            slash_index = image_path.find('/')
            if slash_index == -1:
                raise Exception('Slash is not included in the path')
            current_album = image_path[0:slash_index]
            if previous_album != current_album:
                album_id = create_album(current_album)
            upload_image(image_path, album_id)
            os.remove(image_path)


def upload_image(image_file, album_id):
    """
    画像をアップロードし、アルバムに追加する
    """
    for i in range(API_TRY_MAX):
        try:
            # service object がアップロードに対応していないので、
            # ここでは requests を使用
            with open(str(image_file), 'rb') as image_data:
                url = 'https://photoslibrary.googleapis.com/v1/uploads'
                headers = {
                    'Authorization': "Bearer " + service._http.request.credentials.access_token,
                    'Content-Type': 'application/octet-stream',
                    'X-Goog-Upload-File-Name': image_file.name,
                    'X-Goog-Upload-Protocol': "raw",
                }
                response = requests.post(url, data=image_data, headers=headers)
            # アップロードの応答で upload token が返る
            upload_token = response.content.decode('utf-8')
            break
        except Exception as e:
            print(e)
            if i < (API_TRY_MAX - 1):
                sleep(3)
    else:
        # エラーでリトライアウトした場合は終了
        sys.exit(1)
    new_item = {'albumId': album_id,
                'newMediaItems': [{'simpleMediaItem': {'uploadToken': upload_token}}]}
    response = execute_service_api(
        service.mediaItems().batchCreate(body=new_item),
        'service.mediaItems().batchCreate().execute()')
    status = response['newMediaItemResults'][0]['status']

    return status


def execute_service_api(service_api, service_name):
    # 時々、エラーが発生することがあるのでリトライを行う
    # リトライ実績
    # <HttpError 500 when requesting https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate?alt=json returned "Internal error encountered.">
    # <HttpError 503 when requesting https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate?alt=json returned "The service is currently unavailable.">
    # <HttpError 400 when requesting https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate?alt=json returned "Request must contain a valid upload token.">
    # <HttpError 400 when requesting https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate?alt=json returned "Invalid album ID."
    # <HttpError 500 when requesting https://photoslibrary.googleapis.com/v1/albums?alt=json&pageSize=50&pageToken= returned "Internal error encountered.">
    # <HttpError 503 when requesting https://photoslibrary.googleapis.com/v1/albums?alt=json&pageSize=50&pageToken= returned "The service is currently unavailable.">
    # <HttpError 500 when requesting https://photoslibrary.googleapis.com/v1/albums?alt=json&pageToken=.....&pageSize=50 returned "Internal error encountered.">
    # <HttpError 503 when requesting https://photoslibrary.googleapis.com/v1/albums?alt=json&pageSize=50&pageToken=..... returned "The service is currently unavailable.">
    # リトライアウト実績
    # ERROR:__main__:HTTPSConnectionPool(host='photoslibrary.googleapis.com', port=443): Max retries exceeded with url: /v1/uploads (Caused by SSLError(SSLError("bad handshake: SysCallError(104, 'ECONNRESET')",),))
    # ERROR:__main__:service.mediaItems().batchCreate().execute() retry out
    # ERROR:__main__:service.albums().list().execute() retry out

    for i in range(API_TRY_MAX):
        try:
            response = service_api.execute()
            return response
        except Exception as e:
            print(e)
            if i < (API_TRY_MAX - 1):
                sleep(3)
    else:
        # エラーでリトライアウトした場合は終了
        sys.exit(1)


def create_album(title):
    payload = {'album': {'title': title}}
    result = service.albums().create(body=payload).execute()
    album_id = result.id
    return album_id


def main():
    create_album('test')


if __name__ == '__main__':
    main()
