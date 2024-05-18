import logging
import requests
import json
import datetime
import time
from common.config import *
from common.logging import logger, send_message
from common.kis import get_access_token, hashkey, KoreaKis

# SYMBOL_LIST = config['SYMBOL_LIST']

kor_kis = KoreaKis()

# 자동매매 시작
try:
    ACCESS_TOKEN = get_access_token()

    symbol_list = SYMBOL_LIST # 매수 희망 종목 리스트
    # symbol_list = ["005930","035720","000660","069500"] # 매수 희망 종목 리스트
    bought_list = [] # 매수 완료된 종목 리스트
    total_cash = kor_kis.get_balance() # 보유 현금 조회
    stock_dict = kor_kis.get_stock_balance() # 보유 주식 조회
    for sym in stock_dict.keys():
        bought_list.append(sym)
    target_buy_count = 3 # 매수할 종목 수
    buy_percent = 0.33 # 종목당 매수 금액 비율
    buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
    soldout = False

    send_message("===Domestic Automated Trading Program is Starting===")
    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            send_message("It's the weekend, so the program will shut down")
            send_message("===Shutdowned===")
            break
        if t_9 < t_now < t_start and soldout == False: # 잔여 수량 매도
            for sym, qty in stock_dict.items():
                kor_kis.sell(sym, qty)
            soldout == True
            bought_list = []
            stock_dict = kor_kis.get_stock_balance()
        if t_start < t_now < t_sell :  # AM 09:05 ~ PM 03:15 : 매수
            for sym in symbol_list:
                if len(bought_list) < target_buy_count:
                    if sym in bought_list:
                        continue
                    target_price = kor_kis.get_target_price(sym)
                    current_price = kor_kis.get_current_price(sym)
                    if target_price < current_price:
                        buy_qty = 0  # 매수할 수량 초기화
                        buy_qty = int(buy_amount // current_price)
                        if buy_qty > 0:
                            send_message(f"{sym} target price reached ({target_price} < {current_price}), attempting to purchase.")
                            result = kor_kis.buy(sym, buy_qty)
                            if result:
                                soldout = False
                                bought_list.append(sym)
                                kor_kis.get_stock_balance()
                    time.sleep(1)
            time.sleep(1)
            if t_now.minute == 30 and t_now.second <= 5: 
                kor_kis.get_stock_balance()
                time.sleep(5)
        if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
            if soldout == False:
                stock_dict = kor_kis.get_stock_balance()
                for sym, qty in stock_dict.items():
                    kor_kis.sell(sym, qty)
                soldout = True
                bought_list = []
                time.sleep(1)
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            send_message("Domestic Automated Trading Program is Shutting Down.")
            break
except Exception as e:
    send_message(f"[Unexpected Error Occurred] {e}")
    time.sleep(1)