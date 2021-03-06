# -*- coding: utf-8 -*-
from __future__ import print_function
import pickle
import os.path
import io
import sys
import glob
import const
import datetime
import filetype

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_NAME = const.FOLDER_NAME
os.chdir('files')

dt_now = datetime.datetime.now()

log = open("log.txt", "a")
log.write(dt_now.strftime('%Y-%m-%d %H:%M:%S') + "\t" + const.PC_NAME + "\n")
log.close()

files = glob.glob("./*")

def main():
    # OAuth
    drive = None
    creds = None
    if os.path.exists('../token.pickle'):
        with open('../token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists('../client_secret.json'):
            flow = InstalledAppFlow.from_client_secrets_file(
                '../client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('../token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    if creds and creds.valid:
        drive = build('drive', 'v3', credentials=creds)
    if not drive: print('Drive auth failed.')

    # Folfer list
    folders = None
    if drive: 
        results = drive.files().list(
            pageSize=100, 
            fields='nextPageToken, files(id, name)',
            q='name="' + FOLDER_NAME + '" and mimeType="application/vnd.google-apps.folder"'
            ).execute()
        folders = results.get('files', [])
        if not folders: print('No folders found.')

    # get drive files 
    folder = folders[0]
    query = '"' + folder['id'] + '" in parents'
    results = drive.files().list(
        pageSize=100, 
        fields='nextPageToken, files(id, name)',
        q=query
        ).execute()
    drive_files = results.get('files', [])

    # file upload
    folder_id = folders[0]["id"] # ?????????????????????????????????
    drive_files_name = list(map(lambda it : it["name"], drive_files))
    for file in files:
      print(file)
      file_metadata = {
          'name': file.replace('./', '').replace('.\\', ''),
          'parents': [folder_id]
      }

      media = MediaFileUpload(
          file, 
          mimetype= filetype.FILETYPE[file.split(".")[2]] if file.split(".")[2] in filetype.FILETYPE else "text/plain", 
          resumable=True
      )

      if file_metadata["name"] in drive_files_name:
        file = drive.files().update(
          fileId = drive_files[drive_files_name.index(file_metadata["name"])]["id"],
          media_body=media
        ).execute()
        continue

      file = drive.files().create(
          body=file_metadata, media_body=media, fields='id'
      ).execute()

if __name__ == '__main__':
    main()
    print("upload files")