import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPACA_KEY")
SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = os.getenv("BASE_URL")

def place_order(symbol, qty, side="buy"):
    url = f"{BASE_URL}/v2/orders"

    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": SECRET
    }

    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "gtc"
    }

    res = requests.post(url, json=data, headers=headers)

    print("\n📊 TRADE RESPONSE:")
    print(res.json())


if __name__ == "__main__":
    symbol = sys.argv[1]
    qty = int(sys.argv[2])
    place_order(symbol, qty)
