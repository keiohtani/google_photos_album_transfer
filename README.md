# Google Photos Album Transfer

## Setup

1. Download the repo
`git clone https://github.com/keiohtani/google_photos_album_transfer.git`

2. Activate Photos Library API in Google Cloud Platform

3. Download API key and move to the root of the project directory

## Create a virtual environment (optional)

- Create a virtual environment

`python -m venv .`

- Start the virtual environment

`source bin/activate`

## Install the dependencies

`pip install -r requirements.txt`

## Start the app

`python main.py`

## Authorize access to the app

1. Your default browser will open up for the first time access. 

2. Login to your Google account you want to transfer photos from. 

3. Click on "advanced" and then "Go to YOUR_APP_NAME (unsafe)".

4. Your default browser will open up again for the access to the second Google account.

5. Login to your Google account you want to transfer photos to. 

6. Click on "advanced" and then "Go to YOUR_APP_NAME (unsafe)".

## Contribution

If you have found a bug that hasn't been reported yet or want to request a new feature, please open a new issue.

## References

- [Google Photos API を使用した画像の自動アップロード](https://qiita.com/inasawa/items/e5362dec4bd45d6900f7)
