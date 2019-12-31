# Ref: https://qiita.com/inasawa/items/e5362dec4bd45d6900f7
import os
from time import sleep
from authentication import get_authenticated_service
import requests
import sys


CLIENT_SECRETS_FILE = '.uploader_google_photos_client_secrets.json'
TOKEN_FILE = '.uploader_google_photos_token.json'
API_TRY_MAX = 3

service = get_authenticated_service(CLIENT_SECRETS_FILE, TOKEN_FILE)


def upload_images(images_queues):
    sleep(300)
    print('Start uploading')
    while not images_queues.empty():
        sleep(10)
        album_object = images_queues.get()
        title = album_object['title']
        images_queue = album_object['queue']
        dir_path = album_object['dir_path']
        album_id = create_album(title)
        while not images_queue.empty():
            file_name = images_queue.get()
            image_path = os.path.join(dir_path, file_name)
            upload_image(image_path, dir_path, file_name, album_id)
            os.remove(image_path)
            print('uploaded', image_path)
        print('Completed uploading an album', title)
    print('Completed uploading')


def upload_image(image_file, dir_path, file_name, album_id):
    """
    画像をアップロードし、アルバムに追加する
    """
    for i in range(API_TRY_MAX):
        try:
            # service object がアップロードに対応していないので、
            # ここでは requests を使用
            with open(image_file, 'rb') as image_data:
                url = 'https://photoslibrary.googleapis.com/v1/uploads'
                headers = {
                    'Authorization': "Bearer " + service._http.request.credentials.access_token,
                    'Content-Type': 'application/octet-stream',
                    'X-Goog-Upload-File-Name': file_name,
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
    album_id = result['id']
    return album_id


def main():
    create_album('test')


if __name__ == '__main__':
    main()
