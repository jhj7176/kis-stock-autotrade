import time
# import argparse
from datetime import timedelta
import datetime
from trade.KoreaStockAutoTrade import ko_auto_trade
from trade.UsaStockAutoTrade import us_auto_trade
from common.config import *
from common.logging import send_message

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--type", help="type of auto trade: 'kor' or 'usa'")
    # args = parser.parse_args()
    
    if NATION is None:
        send_message(f"Please specify the nation[{NATION}] in the environment")
        return
    
    while True:
        if NATION == 'KOR':
            result = ko_auto_trade()
        elif NATION == 'USA':
            result = us_auto_trade()
        else:
            send_message(f"Invalid nation type. Please specify the nation[{NATION}] in the environment")
            break

        if not result:
            # Calculate the time until the next midnight
            now = datetime.datetime.now()
            midnight = datetime.datetime.combine(now + datetime.timedelta(days=1), datetime.time())
            sleep_time = (midnight - now).total_seconds()

            # Wait until the next midnight
            # send_message(f"Sleeping until midnight ({sleep_time} seconds)")
            formatted_time = str(timedelta(seconds=sleep_time))
            send_message(f"Sleeping until midnight (remaining time: {formatted_time})")
            time.sleep(sleep_time)
        else:
            time.sleep(86400)

if __name__ == "__main__":
    main()