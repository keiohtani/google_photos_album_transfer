from face_recog import Face_Saver
import authentication
import json
import urllib.request

UNKNOWN_FACE_PATH = 'uncropped_face_images'

def download_people_images():
    
    service = authentication.get_authenticated_service()

    with open('downloader_payload.json') as f:
        payload = json.loads(f.read())

    face_saver = Face_Saver()

    while True:
        media_list = service.mediaItems().search(body=payload).execute()
        if 'mediaItems' not in media_list:  # when no items are found
            break
        for mediaItem in media_list['mediaItems']:
            # the size can be set by adding '=w2048-h1024' at the end of URL
            image_url = mediaItem['baseUrl']
            try:
                urllib.request.urlretrieve(image_url + '=w3000', 'temp.jpg')
            except urllib.request.HTTPError as err:
                print(err.code, 'error found.')
            face_saver.save_face_image('temp.jpg')
        if 'nextPageToken' not in media_list:
            break

        print('next page')
        nextPageToken = media_list['nextPageToken']
        print(nextPageToken)
        payload['pageToken'] = nextPageToken

    face_saver.save_photo_id()
    print('finished downloading pictures')

if __name__ == "__main__":
    download_people_images()
