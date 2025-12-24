
from googleapiclient.discovery import build
from google.oauth2 import service_account

#=============================================================================#

SCOPES               = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'
FOLDER_ID            = '1gD5xuXfOmZyNXgeQjfc-5p2SsTMrBZf4'

#=============================================================================#

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=creds)

#=============================================================================#

def get_doc_url(target_filename):

    query = f"'{FOLDER_ID}' in parents and name = '{target_filename}.pdf' and trashed = false"

    results = service.files().list(
        q=query,
        fields="files(id, name, webViewLink)"
    ).execute()

    doc_info = results.get('files', [])

    return doc_info

#=============================================================================#

if __name__ == '__main__':

    doc_info = get_doc_url('AS901')

    print(doc_info)

    if not doc_info:
        print('找不到該檔案。')
    else:
        for info in doc_info:
            print(f"檔名: {info['name']}")
            print(f"分享連結: {info['webViewLink']}")