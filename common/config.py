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
REDIS_HOST=os.environ.get('REDIS_HOST')
REDIS_PORT=os.environ.get('REDIS_PORT')
BASIC_LOG_LEVEL=os.environ.get('BASIC_LOG_LEVEL')
NATION=os.environ.get('NATION', None)
STDOUT_LOGGER_USE_YN=os.environ.get('STDOUT_LOGGER_USE_YN', 'Y')

_r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def set_cache(_key, _value, ex=None):
    _r.set(_key, _value, ex=ex)

def get_cache(_key):
    _value = _r.get(_key)
    if _value:
        _value = _value.decode('utf-8')
    return _value

# _r.set('KIS_APP_KEY', KIS_APP_KEY, ex=60*60*24)


def config():
    """
    This function loads the configuration from a .env file and returns it as a dictionary.
    """
    config = {
        'KIS_APP_KEY': KIS_APP_KEY,
        'KIS_APP_SECRET': KIS_APP_SECRET,
        'ACCESS_TOKEN': ACCESS_TOKEN,
        'CANO': CANO,
        'ACNT_PRDT_CD': ACNT_PRDT_CD,
        'DISCORD_WEBHOOK_URL': DISCORD_WEBHOOK_URL,
        'KIS_API_BASE': KIS_API_BASE,
        'SYMBOL_LIST': SYMBOL_LIST,
        'NASD_SYMBOL_LIST': NASD_SYMBOL_LIST,
        'NYSE_SYMBOL_LIST': NYSE_SYMBOL_LIST,
        'AMEX_SYMBOL_LIST': AMEX_SYMBOL_LIST,
        'REDIS_HOST': REDIS_HOST,
        'REDIS_PORT': REDIS_PORT,
        'BASIC_LOG_LEVEL': BASIC_LOG_LEVEL,
        'NATION': NATION,
        'STDOUT_LOGGER_USE_YN': STDOUT_LOGGER_USE_YN
    }
    # print(config)
    return config