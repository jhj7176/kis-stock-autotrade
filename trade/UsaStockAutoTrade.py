import logging
import requests
import json
import datetime
import time
from pytz import timezone
# from common.config import get_config
from common.config import *
from common.logging import logger, send_message
from common.kis import get_access_token, hashkey, UsaKis

usa_kis = UsaKis()

# config = get_config()

# KIS_APP_KEY = config.KIS_APP_KEY
# KIS_APP_SECRET = config['KIS_APP_SECRET']
# CANO = config['CANO']
# ACNT_PRDT_CD = config['ACNT_PRDT_CD']
# DISCORD_WEBHOOK_URL = config['DISCORD_WEBHOOK_URL']
# KIS_API_BASE = config['KIS_API_BASE']
# NASD_SYMBOL_LIST = config['NASD_SYMBOL_LIST']
# NYSE_SYMBOL_LIST = config['NYSE_SYMBOL_LIST']
# AMEX_SYMBOL_LIST = config['AMEX_SYMBOL_LIST']
# ACCESS_TOKEN = ""

# 자동매매 시작
try:
    ACCESS_TOKEN = get_access_token()
    # nasd_symbol_list = ["AAPL"] # 매수 희망 종목 리스트 (NASD)
    # nyse_symbol_list = ["KO"] # 매수 희망 종목 리스트 (NYSE)
    # amex_symbol_list = ["LIT"] # 매수 희망 종목 리스트 (AMEX)
    nasd_symbol_list = NASD_SYMBOL_LIST
    nyse_symbol_list = NYSE_SYMBOL_LIST
    amex_symbol_list = AMEX_SYMBOL_LIST
    symbol_list = nasd_symbol_list + nyse_symbol_list + amex_symbol_list
    bought_list = [] # 매수 완료된 종목 리스트
    total_cash = usa_kis.get_balance() # 보유 현금 조회
    exchange_rate = usa_kis.get_exchange_rate() # 환율 조회
    stock_dict = usa_kis.get_stock_balance() # 보유 주식 조회
    for sym in stock_dict.keys():
        bought_list.append(sym)
    target_buy_count = 3 # 매수할 종목 수
    buy_percent = 0.33 # 종목당 매수 금액 비율
    buy_amount = total_cash * buy_percent / exchange_rate # 종목별 주문 금액 계산 (달러)
    soldout = False

    send_message("===Domestic Automated Trading Program is Starting===")
    while True:
        t_now = datetime.datetime.now(timezone('America/New_York')) # 뉴욕 기준 현재 시간
        t_9 = t_now.replace(hour=9, minute=30, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=35, second=0, microsecond=0)
        t_sell = t_now.replace(hour=15, minute=45, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=50, second=0,microsecond=0)
        today = t_now.weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            send_message("It's the weekend, so the program will shut down")
            send_message("===Shutdowned===")
            break
        if t_9 < t_now < t_start and soldout == False: # 잔여 수량 매도
            for sym, qty in stock_dict.items():
                market1 = "NASD"
                market2 = "NAS"
                if sym in nyse_symbol_list:
                    market1 = "NYSE"
                    market2 = "NYS"
                if sym in amex_symbol_list:
                    market1 = "AMEX"
                    market2 = "AMS"
                usa_kis.sell(market=market1, code=sym, qty=qty, price=usa_kis.get_current_price(market=market2, code=sym))
            soldout == True
            bought_list = []
            time.sleep(1)
            stock_dict = usa_kis.get_stock_balance()
        if t_start < t_now < t_sell :  # AM 09:35 ~ PM 03:45 : 매수
            for sym in symbol_list:
                if len(bought_list) < target_buy_count:
                    if sym in bought_list:
                        continue
                    market1 = "NASD"
                    market2 = "NAS"
                    if sym in nyse_symbol_list:
                        market1 = "NYSE"
                        market2 = "NYS"
                    if sym in amex_symbol_list:
                        market1 = "AMEX"
                        market2 = "AMS"
                    target_price = usa_kis.get_target_price(market2, sym)
                    current_price = usa_kis.get_current_price(market2, sym)
                    if target_price < current_price:
                        buy_qty = 0  # 매수할 수량 초기화
                        buy_qty = int(buy_amount // current_price)
                        if buy_qty > 0:
                            send_message(f"{sym} target price reached ({target_price} < {current_price}), attempting to purchase.")
                            market = "NASD"
                            if sym in nyse_symbol_list:
                                market = "NYSE"
                            if sym in amex_symbol_list:
                                market = "AMEX"
                            result = usa_kis.buy(market=market1, code=sym, qty=buy_qty, price=usa_kis.get_current_price(market=market2, code=sym))
                            time.sleep(1)
                            if result:
                                soldout = False
                                bought_list.append(sym)
                                usa_kis.get_stock_balance()
                    time.sleep(1)
            time.sleep(1)
            if t_now.minute == 30 and t_now.second <= 5: 
                usa_kis.get_stock_balance()
                time.sleep(5)
        if t_sell < t_now < t_exit:  # PM 03:45 ~ PM 03:50 : 일괄 매도
            if soldout == False:
                stock_dict = usa_kis.get_stock_balance()
                for sym, qty in stock_dict.items():
                    market1 = "NASD"
                    market2 = "NAS"
                    if sym in nyse_symbol_list:
                        market1 = "NYSE"
                        market2 = "NYS"
                    if sym in amex_symbol_list:
                        market1 = "AMEX"
                        market2 = "AMS"
                    usa_kis.sell(market=market1, code=sym, qty=qty, price=usa_kis.get_current_price(market=market2, code=sym))
                soldout = True
                bought_list = []
                time.sleep(1)
        if t_exit < t_now:  # PM 03:50 ~ :프로그램 종료
            send_message("Domestic Automated Trading Program is Shutting Down.")
            break
except Exception as e:
    send_message(f"[Unexpected Error Occurred] {e}")
    time.sleep(1)