
import logging
import requests
import json
import time
from .config import *
from .logging import logger, send_message

def get_access_token():
    """토큰 발급"""
    logger("get_access_token -- start", logging.DEBUG)
    token = get_cache('ACCESS_TOKEN')
    if token is not None and token:
        logger("Access token is in cache - "+token, logging.INFO)
        return token
    
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":KIS_APP_KEY, 
    "appsecret":KIS_APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{KIS_API_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    logger("get_access_token -- " + res.text, logging.DEBUG)
    token = res.json()["access_token"]
    expires_in = res.json()["expires_in"]
    set_cache('ACCESS_TOKEN', token, ex=expires_in) # Redis에 토큰 저장
    logger("get_access_token -- end", logging.DEBUG)
    return token

def hashkey(datas):
    """암호화"""
    logger("hashkey -- start", logging.DEBUG)
    PATH = "uapi/hashkey"
    URL = f"{KIS_API_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : KIS_APP_KEY,
    'appSecret' : KIS_APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    logger("hashkey -- "+res.text, logging.DEBUG)
    hashkey = res.json()["HASH"]
    logger("hashkey -- end", logging.DEBUG)
    return hashkey

# 한국 주식
class KoreaKis:
    
    def __init__(self) -> None:
        logger("KoreaKis init", logging.DEBUG)
    
    def get_current_price(_self, code="005930"):
        """현재가 조회"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
                "authorization": f"Bearer {get_access_token()}",
                "appKey":KIS_APP_KEY,
                "appSecret":KIS_APP_SECRET,
                "tr_id":"FHKST01010100"}
        params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd":code,
        }
        res = requests.get(URL, headers=headers, params=params)
        logger(res.text, logging.DEBUG, _self)
        logger("end", logging.DEBUG, _self)
        return int(res.json()['output']['stck_prpr'])

    def get_target_price(_self, code="005930"):
        """변동성 돌파 전략으로 매수 목표가 조회"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {get_access_token()}",
            "appKey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"FHKST01010400"}
        params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd":code,
        "fid_org_adj_prc":"1",
        "fid_period_div_code":"D"
        }
        res = requests.get(URL, headers=headers, params=params)
        logger(res.text, logging.DEBUG, _self)
        stck_oprc = int(res.json()['output'][0]['stck_oprc']) #오늘 시가
        stck_hgpr = int(res.json()['output'][1]['stck_hgpr']) #전일 고가
        stck_lwpr = int(res.json()['output'][1]['stck_lwpr']) #전일 저가
        target_price = stck_oprc + (stck_hgpr - stck_lwpr) * 0.5
        logger("end", logging.DEBUG, _self)
        return target_price

    def get_stock_balance(_self):
        """주식 잔고조회"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appkey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"TTTC8434R",
            "custtype":"P",
        }
        params = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        res = requests.get(URL, headers=headers, params=params)
        logger(res.text, logging.DEBUG, _self)
        stock_list = res.json()['output1']
        evaluation = res.json()['output2']
        stock_dict = {}
        send_message(f"====Stock Holdings====")
        for stock in stock_list:
            if int(stock['hldg_qty']) > 0:
                stock_dict[stock['pdno']] = stock['hldg_qty']
                send_message(f"{stock['prdt_name']}({stock['pdno']}): {stock['hldg_qty']}주")
                time.sleep(0.1)
        send_message(f"Stock Valuation Amount: {evaluation[0]['scts_evlu_amt']}원")
        time.sleep(0.1)
        send_message(f"Total Evaluation Profit/Loss: {evaluation[0]['evlu_pfls_smtl_amt']}원")
        time.sleep(0.1)
        send_message(f"Total Valuation Amount: {evaluation[0]['tot_evlu_amt']}원")
        time.sleep(0.1)
        send_message(f"=================")
        logger("end", logging.DEBUG, _self)
        return stock_dict

    def get_balance(_self):
        """현금 잔고조회"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appkey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"TTTC8908R",
            "custtype":"P",
        }
        params = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO": "005930",
            "ORD_UNPR": "65500",
            "ORD_DVSN": "01",
            "CMA_EVLU_AMT_ICLD_YN": "Y",
            "OVRS_ICLD_YN": "Y"
        }
        res = requests.get(URL, headers=headers, params=params)
        logger((res.json()), logging.DEBUG, _self)
        cash = res.json()['output']['ord_psbl_cash']
        send_message(f"Available Cash Balance for Ordering: {cash}원")
        logger("end", logging.DEBUG, _self)
        return int(cash)

    def buy(_self, code="005930", qty="1"):
        """주식 시장가 매수"""  
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/domestic-stock/v1/trading/order-cash"
        URL = f"{KIS_API_BASE}/{PATH}"
        data = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO": code,
            "ORD_DVSN": "01",
            "ORD_QTY": str(int(qty)),
            "ORD_UNPR": "0",
        }
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appkey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"TTTC0802U",
            "custtype":"P",
            "hashkey" : hashkey(data)
        }
        res = requests.post(URL, headers=headers, data=json.dumps(data))
        logger(res.text, logging.DEBUG, _self)
        if res.json()['rt_cd'] == '0':
            send_message(f"[Purchase successful]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return True
        else:
            send_message(f"[Purchase failed]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return False

    def sell(_self, code="005930", qty="1"):
        """주식 시장가 매도"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/domestic-stock/v1/trading/order-cash"
        URL = f"{KIS_API_BASE}/{PATH}"
        data = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO": code,
            "ORD_DVSN": "01",
            "ORD_QTY": qty,
            "ORD_UNPR": "0",
        }
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appkey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"TTTC0801U",
            "custtype":"P",
            "hashkey" : hashkey(data)
        }
        res = requests.post(URL, headers=headers, data=json.dumps(data))
        logger(res.text, logging.DEBUG, _self)
        if res.json()['rt_cd'] == '0':
            send_message(f"[Purchase Successful]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return True
        else:
            send_message(f"[Purchase failed]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return False


'''USA'''
class UsaKis:
    def __init__(self) -> None:
        logger("UsaKis init", logging.DEBUG)
    
    def get_current_price(_self, market="NAS", code="AAPL"):
        """현재가 조회"""
        PATH = "uapi/overseas-price/v1/quotations/price"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
                "authorization": f"Bearer {get_access_token()}",
                "appKey":KIS_APP_KEY,
                "appSecret":KIS_APP_SECRET,
                "tr_id":"HHDFS00000300"}
        params = {
            "AUTH": "",
            "EXCD":market,
            "SYMB":code,
        }
        res = requests.get(URL, headers=headers, params=params)
        return float(res.json()['output']['last'])

    def get_target_price(_self, market="NAS", code="AAPL"):
        """변동성 돌파 전략으로 매수 목표가 조회"""
        PATH = "uapi/overseas-price/v1/quotations/dailyprice"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {get_access_token()}",
            "appKey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"HHDFS76240000"}
        params = {
            "AUTH":"",
            "EXCD":market,
            "SYMB":code,
            "GUBN":"0",
            "BYMD":"",
            "MODP":"0"
        }
        res = requests.get(URL, headers=headers, params=params)
        stck_oprc = float(res.json()['output2'][0]['open']) #오늘 시가
        stck_hgpr = float(res.json()['output2'][1]['high']) #전일 고가
        stck_lwpr = float(res.json()['output2'][1]['low']) #전일 저가
        target_price = stck_oprc + (stck_hgpr - stck_lwpr) * 0.5
        return target_price

    def get_stock_balance(_self):
        """주식 잔고조회"""
        logger("start", logging.INFO, _self)
        PATH = "uapi/overseas-stock/v1/trading/inquire-balance"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appKey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"JTTT3012R",
            "custtype":"P"
        }
        params = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "OVRS_EXCG_CD": "NASD",
            "TR_CRCY_CD": "USD",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": ""
        }
        res = requests.get(URL, headers=headers, params=params)
        logger(res.text, logging.DEBUG, _self)
        stock_list = res.json()['output1']
        evaluation = res.json()['output2']
        stock_dict = {}
        send_message(f"====Stock Holdings====")
        for stock in stock_list:
            if int(stock['ovrs_cblc_qty']) > 0:
                stock_dict[stock['ovrs_pdno']] = stock['ovrs_cblc_qty']
                send_message(f"{stock['ovrs_item_name']}({stock['ovrs_pdno']}): {stock['ovrs_cblc_qty']}주")
                time.sleep(0.1)
        send_message(f"Stock evaluation amount: ${evaluation['tot_evlu_pfls_amt']}")
        time.sleep(0.1)
        send_message(f"Total Valuation Amount: ${evaluation['ovrs_tot_pfls']}")
        time.sleep(0.1)
        send_message(f"=================")
        logger("end", logging.DEBUG, _self)
        return stock_dict

    def get_balance(_self):
        """현금 잔고조회"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appKey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"TTTC8908R",
            "custtype":"P",
        }
        # print(headers)
        params = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO": "005930",
            "ORD_UNPR": "65500",
            "ORD_DVSN": "01",
            "CMA_EVLU_AMT_ICLD_YN": "Y",
            "OVRS_ICLD_YN": "Y"
        }
        res = requests.get(URL, headers=headers, params=params)
        logger(res.text, logging.DEBUG, _self)
        cash = res.json()['output']['ord_psbl_cash']
        send_message(f"Available cash balance for orders: {cash}원")
        logger("end", logging.DEBUG, _self)
        return int(cash)

    def buy(_self, market="NASD", code="AAPL", qty="1", price="0"):
        """미국 주식 지정가 매수"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/overseas-stock/v1/trading/order"
        URL = f"{KIS_API_BASE}/{PATH}"
        data = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "OVRS_EXCG_CD": market,
            "PDNO": code,
            "ORD_DVSN": "00",
            "ORD_QTY": str(int(qty)),
            "OVRS_ORD_UNPR": f"{round(price,2)}",
            "ORD_SVR_DVSN_CD": "0"
        }
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appKey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"JTTT1002U",
            "custtype":"P",
            "hashkey" : hashkey(data)
        }
        res = requests.post(URL, headers=headers, data=json.dumps(data))
        logger(res.text, logging.DEBUG, _self)
        if res.json()['rt_cd'] == '0':
            send_message(f"[Purchase successful]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return True
        else:
            send_message(f"[Purchase failed]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return False

    def sell(_self, market="NASD", code="AAPL", qty="1", price="0"):
        """미국 주식 지정가 매도"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/overseas-stock/v1/trading/order"
        URL = f"{KIS_API_BASE}/{PATH}"
        data = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "OVRS_EXCG_CD": market,
            "PDNO": code,
            "ORD_DVSN": "00",
            "ORD_QTY": str(int(qty)),
            "OVRS_ORD_UNPR": f"{round(price,2)}",
            "ORD_SVR_DVSN_CD": "0"
        }
        headers = {"Content-Type":"application/json", 
            "authorization":f"Bearer {get_access_token()}",
            "appKey":KIS_APP_KEY,
            "appSecret":KIS_APP_SECRET,
            "tr_id":"JTTT1006U",
            "custtype":"P",
            "hashkey" : hashkey(data)
        }
        res = requests.post(URL, headers=headers, data=json.dumps(data))
        logger(res.text, logging.DEBUG, _self)
        if res.json()['rt_cd'] == '0':
            send_message(f"[Purchase successful]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return True
        else:
            send_message(f"[Purchase failed]{str(res.json())}")
            logger("end", logging.DEBUG, _self)
            return False

    def get_exchange_rate(_self):
        """환율 조회"""
        logger("start", logging.DEBUG, _self)
        PATH = "uapi/overseas-stock/v1/trading/inquire-present-balance"
        URL = f"{KIS_API_BASE}/{PATH}"
        headers = {"Content-Type":"application/json", 
                "authorization": f"Bearer {get_access_token()}",
                "appKey":KIS_APP_KEY,
                "appSecret":KIS_APP_SECRET,
                "tr_id":"CTRP6504R"}
        params = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "OVRS_EXCG_CD": "NASD",
            "WCRC_FRCR_DVSN_CD": "01",
            "NATN_CD": "840",
            "TR_MKET_CD": "01",
            "INQR_DVSN_CD": "00"
        }
        res = requests.get(URL, headers=headers, params=params)
        logger(res.text, logging.DEBUG, _self)
        exchange_rate = 1270.0
        if len(res.json()['output2']) > 0:
            exchange_rate = float(res.json()['output2'][0]['frst_bltn_exrt'])
        logger("end", logging.DEBUG, _self)
        return exchange_rate