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

def upload_many_4():
    '''多进程，按进程数 并行 下载所有图片
    使用concurrent.futures.ProcessPoolExecutor()
    Executor.map()使用Future而不是返回Future，它返回迭代器，
    迭代器的__next__()方法调用各个Future的result()方法，因此我们得到的是各个Future的结果，而非Future本身

    注意Executor.map()限制了download_one()只能接受一个参数，所以images是字典构成的列表
    '''
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
        images.append(image)

    # with语句将调用executor.__exit__()方法，而这个方法会调用executor.shutdown(wait=True)方法，它会在所有进程都执行完毕前阻塞主进程
    with futures.ProcessPoolExecutor(max_workers=5) as executor:  # 不指定max_workers时，进程池中进程个数默认为os.cpu_count()
        # executor.map()效果类似于内置函数map()，但download_one()函数会在多个进程中并行调用
        # 它的返回值res是一个迭代器<itertools.chain object>，我们后续可以迭代获取各个被调用函数的返回值
        res = executor.map(upload_file, images)  # 传一个序列

    return len(list(res))  # 如果有进程抛出异常，异常会在这里抛出，类似于迭代器中隐式调用next()的效果

if __name__ == '__main__':
    t0 = time.time()
    count = upload_many_4()
    msg = '{} file(s) uploaded in {:.2f} seconds.'
    logger.info(msg.format(count, time.time() - t0))