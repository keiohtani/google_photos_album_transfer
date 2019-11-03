from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
API_SERVICE_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRETS_FILE = '.google_photos_client_secrets.json'
TOKEN_FILE = '.google_photos_token.json'
# client_secrets.json の内容は以下の形式
#{
# "installed": {
#    "client_id": ".....",
#    "project_id": ".....",
#    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#    "token_uri": "https://www.googleapis.com/oauth2/v3/token",
#    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#    "client_secret": ".....",
#    "redirect_uris": [
#      "urn:ietf:wg:oauth:2.0:oob",
#      "http://localhost"
#    ]
#  }
#}

def get_authenticated_service():
    """
    Google Account を認証し service object を返す
    初回（TOKEN_FILE が存在しない）はブラウザを起動されるので、認証を行う
    次回以降は TOKEN_FILE に保存された access_token を使用
    access_token の有効期限が切れた場合は refresh_token を使用して access_token の再取得が自動で行われる
    """    
    store = Storage(TOKEN_FILE)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
        creds = tools.run_flow(flow, store)

    return build(API_SERVICE_NAME, API_VERSION, http=creds.authorize(Http()))