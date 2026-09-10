import os
import shutil
import sys
import time
import schedule
from datetime import datetime

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

def create_zip(path, file_name):
    try:
        shutil.make_archive(f"archive/{file_name}", 'zip', path)
        return True
    except FileNotFoundError as e:
        return False

def google_auth():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)
    return gauth, drive

def upload_backup(drive, path, file_name):
    folderName = 'backups'
    folders = drive.ListFile({'q': "title='" + folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    for folder in folders:
        if folder['title'] == folderName:
            f = drive.CreateFile({'parents': [{'id': folder['id']}], 'title': file_name})
            f.SetContentFile(os.path.join(path, file_name))
            f.Upload()
            f = None
            print("Uploaded", file_name)

def controller():
    path = r"/home/ubuntu/zwift-offline/storage"
    now = datetime.now()
    file_name = "backup " + now.strftime(r"%d/%m/%Y %H:%M:%S").replace('/', '-')

    if not create_zip(path, file_name):
        sys.exit(0)
    auth, drive = google_auth()
    upload_backup(drive, r"/home/ubuntu/gdrive-file-backup/archive", file_name + '.zip')

if __name__ == "__main__":
    schedule.every().day.at("03:00").do(controller)
    while True:
        schedule.run_pending()
        time.sleep(60)
