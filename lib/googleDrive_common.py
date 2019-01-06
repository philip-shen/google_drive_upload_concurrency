#2019/01/06 Intial modlue related google drive
#
####################################################
import glob, os
import sys, time
from pydrive.auth import GoogleAuth
from logger import logger

'''
#Google Drive Authentication
#
#Automating pydrive verification process
#https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process/24542604#24542604
'''
def GDriveAuth(str_dir_client_credentials):
    print('Google Authentication Started')
    #Google Drive authentication
    gauth = GoogleAuth()
    #gauth.LocalWebserverAuth()# Creates local webserver and auto handles authentication.
    #gauth.CommandLineAuth() #透過授權碼認證

    # Try to load saved client credentials
    gauth.LoadCredentialsFile(str_dir_client_credentials)
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
        print('Google Authentication Save current credentials.')
        # Save the current credentials to a file
        gauth.SaveCredentialsFile('client_secrets.json')
    elif gauth.access_token_expired:
        print('Google Authentication Refresh current credentials.')
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
        
    print('Google Authentication Completed!') 
    return gauth

'''
# from https://github.com/ITCoders/SyncIt/blob/master/src/drive_sync.py
# """ function of getting id of a given filename """
'''
def id_of_title(drive,title, parent_directory_id):

    foldered_list = drive.ListFile({
        'q': "'{}' in parents and trashed=false".format(parent_directory_id)
    }).GetList()

    #print(foldered_list)
    for file in foldered_list:
        #print(file)
        if file['title'] == title:
            return file['id']
    return None

'''
#""" function for creating a folder and upload into that """
'''
def upload_folder_1(drive,str_source_location,parent_id):
    
    folder_name = os.path.split(str_source_location)[1]
    id_of_folder = id_of_title(drive,folder_name, parent_id)
        
    if id_of_folder is None:
        new_folder = drive.CreateFile({
            'title': folder_name,
            'parents': [{'kind': 'drive#fileLink', 'id': parent_id}],
            'mimeType': 'application/vnd.google-apps.folder'
        })
        new_folder.Upload()
        id_of_folder = new_folder['id']

'''
# """ get all jpg filname under specific folder under folder log """
'''
def get_path_filename(str_localdir):
    #list_filename = []
    #for f in os.listdir(str_localdir):
    #    list_filename.append(f)
    #return list_filename
    return [os.path.join(str_localdir,filename) for filename in os.listdir(str_localdir)]

'''
# """ function for uploading source location to designated id """
'''
def upload_file_1(drive, no_path_filename, path_filename, folder_id):
    t0 = time.time()

    filename = os.path.split(path_filename)[1]
    path = os.path.split(path_filename)[0]
    file_id = id_of_title(drive,filename, folder_id)

    if file_id is not None:
        file_drive = drive.CreateFile({'id': file_id})
        drive_file_size = file_drive['fileSize']
        local_file_size = os.path.getsize(path_filename)

        if drive_file_size != str(local_file_size):
            #logger.info('Downloading No.{} [{}]'.format(image['linkno'], image['link']))
            logger.info('Updating No.{} exisiting {} to of Google Drive folder:{}.'.format(
                                        no_path_filename,filename,os.path.split(path)[1]) )
            file_drive.SetContentFile(path_filename)
            file_drive.Upload()
    else:
        new_file = drive.CreateFile({
            'title': filename,
            'parents': [{
                'kind': 'drive#fileLink',
                'id': folder_id
            }]
        })
        
        #print('Uploading new {} to of Google Drive folder:{}.'.format(path_filename,os.path.split(path)[1]) )
        logger.info('Uploading No.{} new {} to of Google Drive folder:{}.'.format(
                                no_path_filename,filename,os.path.split(path)[1]) )
        new_file.SetContentFile(path_filename)
        new_file.Upload()

    t1 = time.time()
    logger.info('Task No.{} [{}] runs {:.2f} seconds.'.format(no_path_filename, filename, t1 - t0))