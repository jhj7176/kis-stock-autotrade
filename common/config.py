import os
from dotenv import load_dotenv
import redis

load_dotenv()
KIS_APP_KEY=os.environ.get('KIS_APP_KEY')
KIS_APP_SECRET=os.environ.get('KIS_APP_SECRET')
ACCESS_TOKEN=os.environ.get('ACCESS_TOKEN')
CANO=os.environ.get('CANO')
ACNT_PRDT_CD=os.environ.get('ACNT_PRDT_CD')
DISCORD_WEBHOOK_URL=os.environ.get('DISCORD_WEBHOOK_URL')
KIS_API_BASE=os.environ.get('KIS_API_BASE')
SYMBOL_LIST=os.environ.get('SYMBOL_LIST', [])
NASD_SYMBOL_LIST=os.environ.get('NASD_SYMBOL_LIST', [])
NYSE_SYMBOL_LIST=os.environ.get('NYSE_SYMBOL_LIST', [])
AMEX_SYMBOL_LIST=os.environ.get('AMEX_SYMBOL_LIST', [])

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

BASIC_LOG_LEVEL = os.environ.get('BASIC_LOG_LEVEL')

_r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def set_cache(_key, _value, ex=None):
    _r.set(_key, _value, ex=ex)

def get_cache(_key):
    _value = _r.get(_key).decode('utf-8')
    return _value

# _r.set('KIS_APP_KEY', KIS_APP_KEY, ex=60*60*24)


# def get_config():
#     """
#     This function loads the configuration from a .env file and returns it as a dictionary.
#     """
#     load_dotenv()
#     config = {
#         'KIS_APP_KEY': os.environ.get('KIS_APP_KEY'),
#         'KIS_APP_SECRET': os.environ.get('KIS_APP_SECRET'),
#         'ACCESS_TOKEN': os.environ.get('ACCESS_TOKEN'),
#         'CANO': os.environ.get('CANO'),
#         'ACNT_PRDT_CD': os.environ.get('ACNT_PRDT_CD'),
#         'DISCORD_WEBHOOK_URL': os.environ.get('DISCORD_WEBHOOK_URL'),
#         'KIS_API_BASE': os.environ.get('KIS_API_BASE'),
#         'SYMBOL_LIST': os.environ.get('SYMBOL_LIST', []),
#         'NASD_SYMBOL_LIST': os.environ.get('NASD_SYMBOL_LIST', []),
#         'NYSE_SYMBOL_LIST': os.environ.get('NYSE_SYMBOL_LIST', []),
#         'AMEX_SYMBOL_LIST': os.environ.get('AMEX_SYMBOL_LIST', []),
#     }
#     # print(config)
#     return config