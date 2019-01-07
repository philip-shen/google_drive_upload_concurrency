#2019/01/07 Intial code
####################################################
import time,os,sys
from queue import Queue
from threading import Thread
from functools import partial
from concurrent import futures
from pydrive.drive import GoogleDrive

strabspath=os.path.abspath(__file__)
strdirname=os.path.dirname(strabspath)
# get prvious path name
prevdirname=os.path.split(strdirname)[0]
dirnamelib=os.path.join(prevdirname,"lib")
dirnamelog=os.path.join(prevdirname,"log")
# check log folder if exist or not
if not os.path.isdir(dirnamelog):
    os.mkdir(dirnamelog)

sys.path.append(dirnamelib)
from googleDrive_common import GDriveAuth,id_of_title,upload_folder_1,get_path_filename,upload_file_1,upload_file
from logger import logger
from readConfig import *

configPath=os.path.join(strdirname,"config.ini")
localReadConfig = ReadConfig(configPath)
parent_id = localReadConfig.get_GDrive("parent_id")

str_client_credentials = localReadConfig.get_GDrive("gdriveJSON")
# get Google Drive CA file name that including path
str_dir_client_credentials = os.path.join(strdirname,str_client_credentials)

gauth = GDriveAuth(str_dir_client_credentials)
#Make GoogleDrive instance with Authenticated GoogleAuth instance
drive = GoogleDrive(gauth)

# get folder name thant want to upload under folder log
str_candlestick_weekly_subfolder = localReadConfig.get_SeymourExcel("candlestick_weekly_subfolder")
path_candlestick_weekly_subfolder = os.path.join(dirnamelog,str_candlestick_weekly_subfolder)
id_folder_candlestick_weekly = id_of_title(drive,str_candlestick_weekly_subfolder,parent_id)

def upload_many():
    '''依序下载所有图片，同步阻塞'''
    list_path_filename_candlestick_weekly = get_path_filename(path_candlestick_weekly_subfolder)
    #print(list_path_filename_candlestick_weekly)

    images = []
    for no_path_filename, path_filename in enumerate(list_path_filename_candlestick_weekly, 1):
        image = {
            'drive': drive,
            'no_path_filename': no_path_filename,
            'path_filename': path_filename,
            'folder_id': id_folder_candlestick_weekly
        }
        upload_file(image)
    
    return len(list_path_filename_candlestick_weekly)


if __name__ == '__main__':
    t0 = time.time()
    count = upload_many()
    msg = '{} file(s) downloaded in {:.2f} seconds.'
    logger.info(msg.format(count, time.time() - t0))