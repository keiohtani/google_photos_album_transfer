import os
from time import sleep

def upload_images(images_queue):
    sleep(30)
    while True:
        if not images_queue.empty():
            sleep(10)
            os.remove(images_queue.get())