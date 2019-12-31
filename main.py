import threading
from downloader import download_images_by_albums
from queue import Queue
from uploader import upload_images

if __name__ == '__main__':
    # Setup image queue
    images_queues = Queue()

    # Start downloader
    download_thread = threading.Thread(
        target=download_images_by_albums, args=(images_queues, ))
    download_thread.start()

    # Start uploader
    upload_thread = threading.Thread(
        target=upload_images, args=(images_queues, ))
    upload_thread.start()
