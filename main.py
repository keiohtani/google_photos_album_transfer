import threading
from downloader import download_images, download_images_by_albums
from queue import Queue
from uploader import upload_images
from time import sleep

if __name__ == '__main__':
    images_queue = Queue()
    # download_thread = threading.Thread(target=download_images, args=(images_queue, ))
    download_thread = threading.Thread(
        target=download_images_by_albums, args=(images_queue, ))
    upload_thread = threading.Thread(
        target=upload_images, args=(images_queue, ))

    download_thread.start()
    upload_thread.start()
