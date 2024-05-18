import datetime
import os
import logging
import time
import requests
from .config import *
import inspect

# DISCORD_WEBHOOK_URL = config.DISCORD_WEBHOOK_URL


def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)
    logger(message, logging.INFO)


def logger(message, level=logging.DEBUG, _self=None):
    now = datetime.datetime.now()
    log_dir = 'logs'
    log_file = os.path.join(log_dir, 'log_{}.log'.format(now.strftime("%Y-%m-%d")))  # Modified log file name format
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(filename=log_file, level=BASIC_LOG_LEVEL, format='[%(asctime)s] %(levelname)s: %(message)s')
    message = str(message)
    if _self:
        # Get the current method name
        method_name = inspect.currentframe().f_back.f_code.co_name
        # Get the class name
        class_name = _self.__class__.__name__
        # Update the message with the class name and method name
        message = f"{class_name}.{method_name} -- {message}"
        
    print("logger() "+message)
    logging.log(level, message)
    remove_old_log_files()

                
def remove_old_log_files():
    log_dir = 'logs'
    now = time.time()
    days = int(os.environ.get('LOG_DATE'))
    for file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file)
        # Check if the file is a file (not a directory) and if it is older than 7 days
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < now - days * 86400:
            os.remove(file_path)