# google_drive_upload_concurrency
Upload files to Google Drive concurrently.

## Apply Google API service first
Apply Google Sheets API CA refers Reference 01 first.
And then apply Google Drive API CA naming 'client_secrets.json' refers Reference 02 for more detail.

## Usage
Step 1. Place Google Drive API CA under folder 'test'.

Step 2. Files structure On Google Drive.

![alt tag](https://i.imgur.com/S6pWg77.jpg)

Step 3. Make sure folder 'candlestick_weekly_subfolder' in config.ini if it exist under folder 'log' or not.

Step 4. cd test to excute 'python GDrive_threadpool.py' 
![alt tag](https://i.imgur.com/1GY1MIq.jpg)

Step 5. cd test to excute 'python GDrive_processpool.py' 
![alt tag](https://i.imgur.com/ZFnf0cq.jpg)

Step 6. cd test to excute 'python GDrive_sequential.py' 
![alt tag](https://i.imgur.com/CFOP6lv.jpg)

## Environment Configuration
* Windows 10
* Python 3.6
* Refer requirements.txt to pip necessary modules.

## Reference 
* [01 How to get Google Drive CA/Python & Google Drive 專案](https://medium.com/@yysu/%E7%B2%BE%E9%80%9Apython-30-days-day-3-54a0347a574b)
* [02 Google Developers Console Setting/使用Python上傳資料到Google試算表](https://sites.google.com/site/zsgititit/home/python-cheng-shi-she-ji/shi-yongpython-shang-chuan-zi-liao-daogoogle-shi-suan-biao)
* [Sync It](https://github.com/ITCoders/SyncIt/blob/master/src/drive_sync.py)
* [Automating pydrive verification process](https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process/24542604#24542604)
* [asyncio_trial](https://github.com/philip-shen/asyncio_trial)