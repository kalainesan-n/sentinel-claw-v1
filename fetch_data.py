import sys
import json
import urllib.request
import xml.etree.ElementTree as ET

def fetch_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        meta = data['chart']['result'][0]['meta']
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c]
        change = ((closes[-1] - closes[-2]) / closes[-2]) * 100 if len(closes) >= 2 else 0
        return {
            'price':      round(meta.get('regularMarketPrice', 0), 2),
            'prev_close': round(meta.get('previousClose', 0), 2),
            'day_high':   round(meta.get('regularMarketDayHigh', 0), 2),
            'day_low':    round(meta.get('regularMarketDayLow', 0), 2),
            'volume':     meta.get('regularMarketVolume', 0),
            'change_pct': round(change, 2),
            '5d_closes':  [round(c,2) for c in closes],
        }
    except Exception as e:
        return {'error': str(e)}

def fetch_news(symbol):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            tree = ET.parse(r)
        items = tree.findall('.//item')[:5]
        headlines = []
        for item in items:
            title = item.findtext('title', '').strip()
            if title:
                headlines.append(title)
        return headlines
    except Exception as e:
        return [f"News fetch error: {str(e)}"]

if __name__ == '__main__':
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'NVDA'
    price  = fetch_price(symbol)
    news   = fetch_news(symbol)
    output = {'symbol': symbol, 'price': price, 'news': news}
    print(json.dumps(output, indent=2))
