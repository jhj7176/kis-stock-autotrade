import datetime
import os
import logging
import time, sys
import requests
from .config import *
import inspect

def send_message(msg, level=logging.INFO):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    logger(message, level)


def logger(message, level=logging.DEBUG, _self=None):
    now = datetime.datetime.now()
    log_dir = 'logs'
    log_file = os.path.join(log_dir, 'log_{}.log'.format(now.strftime("%Y-%m-%d")))  # Modified log file name format
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(filename=log_file, level=BASIC_LOG_LEVEL, format='[%(asctime)s] %(levelname)s: %(message)s')
    message = str(message)
    if _self:
        method_name = inspect.currentframe().f_back.f_code.co_name
        class_name = _self.__class__.__name__
        message = f"{class_name}.{method_name} -- {message}"
        
    logging.log(level, message)
    stdout_logger(message)
    remove_old_log_files()

                
def remove_old_log_files():
    log_dir = 'logs'
    now = time.time()
    days = int(os.environ.get('LOG_DATE'))
    for file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file)
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < now - days * 86400:
            os.remove(file_path)
        
        
def stdout_logger(message):
    if STDOUT_LOGGER_USE_YN != "Y":
        return
    sys.stdout.write(message + '\n')
    sys.stdout.flush()