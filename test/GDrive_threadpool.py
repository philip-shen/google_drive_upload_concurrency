#2019/01/06 Intial code
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

class ThreadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            drive, id_folder_candlestick_weekly, no_path_filename, path_filename = self.queue.get()
            upload_file_1(drive, id_folder_candlestick_weekly, no_path_filename, path_filename)
            self.queue.task_done()


def upload_many():
    '''多线程，按线程数 并发（非并行） 上傳所有图片'''
    
    list_path_filename_candlestick_weekly = get_path_filename(path_candlestick_weekly_subfolder)
    #print(list_path_filename_candlestick_weekly)

    # 创建队列
    queue = Queue()

    # 创建多个线程
    for i in range(5):
        worker = ThreadWorker(queue)
        worker.daemon = True  # 如果工作线程在等待更多的任务时阻塞了，主线程也可以正常退出
        worker.start()  # 启动线程

    # 往队列中投放任务
    for no_path_filename, path_filename in enumerate(list_path_filename_candlestick_weekly, 1):  # 链接带序号
        logger.info('Queueing No.{} {}'.format(no_path_filename, path_filename))
        queue.put((drive, id_folder_candlestick_weekly, no_path_filename, path_filename))

    logger.info('Waiting for all subthread done...')
    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    logger.info('All subthread done.')

    return len(list_path_filename_candlestick_weekly)


def upload_many_1():
    '''多线程，按线程数 并发（非并行） 下载所有图片
    使用concurrent.futures.ThreadPoolExecutor()
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

    workers = min(5, len(list_path_filename_candlestick_weekly))  # 保证线程池中的线程不会多于总的下载任务数
    # with语句将调用executor.__exit__()方法，而这个方法会调用executor.shutdown(wait=True)方法，它会在所有进程都执行完毕前阻塞主进程
    with futures.ThreadPoolExecutor(workers) as executor:
        # executor.map()效果类似于内置函数map()，但download_one()函数会在多个线程中并发调用
        # 它的返回值res是一个迭代器<itertools.chain object>，我们后续可以迭代获取各个被调用函数的返回值
        res = executor.map(upload_file, images)  # 传一个序列

    logger.info('All subthread done.')
    return len(list(res))  # 如果有进程抛出异常，异常会在这里抛出，类似于迭代器中隐式调用next()的效果


def upload_many_2():
    '''多线程，按线程数 并发（非并行） 下载所有图片
    使用concurrent.futures.ThreadPoolExecutor()
    Executor.map()中的调用函数如果要接受多个参数，可以给Executor.map()传多个序列
    参考：https://yuanjiang.space/threadpoolexecutor-map-method-with-multiple-parameters
    '''
    list_path_filename_candlestick_weekly = get_path_filename(path_candlestick_weekly_subfolder)
    #print(list_path_filename_candlestick_weekly)

    # fixed variables value，不用每次调用下载图片函数时都传同样的drive, id_folder_candlestick_weekly参数
    upload_file_1_partial = partial(upload_file_1, drive, id_folder_candlestick_weekly)

    # 创建包含所有linkno的序列
    no_path_filename = [i for i in range(len(list_path_filename_candlestick_weekly))]

    workers = min(5, len(list_path_filename_candlestick_weekly))  # 保证线程池中的线程不会多于总的下载任务数
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(upload_file_1_partial, no_path_filename, list_path_filename_candlestick_weekly)  # 给Executor.map()传多个序列

    return len(list(res))


def upload_many_3():
    '''多线程，按线程数 并发（非并行） 下载所有图片
    使用concurrent.futures.ThreadPoolExecutor()
    不使用Executor.map()，而使用Executor.submit()和concurrent.futures.as_completed()
    Executor.submit()方法会返回Future，而Executor.map()是使用Future
    '''
    list_path_filename_candlestick_weekly = get_path_filename(path_candlestick_weekly_subfolder)
    #print(list_path_filename_candlestick_weekly)

    # fixed variables value，不用每次调用下载图片函数时都传同样的drive, id_folder_candlestick_weekly参数
    upload_file_1_partial = partial(upload_file_1, drive, id_folder_candlestick_weekly)

    workers = min(4, len(list_path_filename_candlestick_weekly))  # 保证线程池中的线程不会多于总的下载任务数
    with futures.ThreadPoolExecutor(workers) as executor:
        to_do = []
        # 创建并排定Future
        for no_path_filename, path_filename in enumerate(list_path_filename_candlestick_weekly, 1):  # 链接带序号
            future = executor.submit(upload_file_1_partial, no_path_filename, path_filename)
            to_do.append(future)
            #logger.debug('Scheduled for No.{} {}: {}'.format(no_path_filename, list_path_filename_candlestick_weekly, future))

        results = []
        # 获取Future的结果，futures.as_completed(to_do)的参数是Future列表，返回迭代器，
        # 只有当有Future运行结束后，才产出future
        for future in futures.as_completed(to_do):  # future变量表示已完成的Future对象，所以后续future.result()绝不会阻塞
            res = future.result()
            results.append(res)
            #logger.debug('{} result: {!r}'.format(future, res))

    return len(results)


if __name__ == '__main__':
    t0 = time.time()
    
    #upload each file to Google driver under folder:str_candlestick_filepath
    upload_folder_1(drive, path_candlestick_weekly_subfolder, parent_id)
    
    #count = upload_many()
    #count = upload_many_1()
    count = upload_many_2()
    #count = upload_many_3()
    msg = '{} file(s) upload in {:.2f} seconds.'
    logger.info(msg.format(count, time.time() - t0))
