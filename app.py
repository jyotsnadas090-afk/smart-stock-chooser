from flask import Flask, render_template, request, render_template_string
import yfinance as yf
import time
import traceback

app = Flask(__name__)

# List of stocks to show on the home page (example)
STOCKS = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "SBIN.NS","BHARTIARTL.NS","ITC.NS","BAJFINANCE.NS","HINDUNILVR.NS",
    "ASIANPAINT.NS","AXISBANK.NS","MARUTI.NS","LT.NS","SUNPHARMA.NS",
    "TITAN.NS","WIPRO.NS","POWERGRID.NS","NTPC.NS","TECHM.NS"
]

# Simple in-memory cache with TTL (seconds)
CACHE = {}  # { key: (timestamp, value) }
CACHE_TTL = 600  # 10 minutes

def set_cache(key, value):
    CACHE[key] = (time.time(), value)

def get_cache(key):
    item = CACHE.get(key)
    if not item:
        return None
    ts, val = item
    if time.time() - ts > CACHE_TTL:
        # expired
        try:
            del CACHE[key]
        except KeyError:
            pass
        return None
    return val

def fetch_with_retries(symbol, mode="info", retries=3):
    """
    mode: "info" returns fast_info dict (lightweight)
          "history" returns historical DataFrame
    """
    delay = 1.0
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(symbol)
            if mode == "info":
                # use fast_info (lighter) first
                fast = getattr(ticker, "fast_info", None)
                if fast:
                    return fast
                # fallback to info (might be heavier)
                return getattr(ticker, "info", {})
            elif mode == "history":
                # history might be heavier; keep it separate
                hist = ticker.history(period="6mo")
                return hist
        except Exception as e:
            # log and back off
            print(f"Attempt {attempt+1} failed for {symbol} ({mode}): {e}")
            traceback.print_exc()
            time.sleep(delay)
            delay *= 2
    # all retries failed
    return None

def get_stock_info_cached(symbol):
    key = f"info:{symbol}"
    cached = get_cache(key)
    if cached is not None:
        return cached

    info = fetch_with_retries(symbol, mode="info", retries=3)
    if info is None:
        # store a short-lived placeholder to avoid hammering again
        set_cache(key, {})
        return {}
    set_cache(key, info)
    return info

def get_history_cached(symbol):
    key = f"hist:{symbol}"
    cached = get_cache(key)
    if cached is not None:
        return cached

    hist = fetch_with_retries(symbol, mode="history", retries=2)
    if hist is None:
        set_cache(key, None)
        return None
    set_cache(key, hist)
    return hist

# Simple HTML using render_template_string for portability (you can move this to templates later)
HOME_HTML = """
<!doctype html>
<html>
<head><title>Smart Stock Chooser - Senko Getsu</title>
<style>
body{background:#0b0c10;color:#fff;font-family:Segoe UI,Arial;text-align:center}
.table{margin:20px auto;width:92%;border-collapse:collapse}
th,td{padding:10px;border-bottom:1px solid #333}
th{color:#ffd700;background:#121217}
.pos{color:#00ff88}.neg{color:#ff6767}
input{padding:8px;width:260px;border-radius:6px;border:none}
button{padding:8px 12px;border-radius:6px;border:none;background:#ffd700;color:#000}
.card{background:#151520;padding:12px;border-radius:8px;display:inline-block;margin:6px}
</style>
</head>
<body>
<h1>Smart Stock Chooser — Senko Getsu</h1>
<form method="GET"><input name="search" placeholder="Search symbol or name" value="{{ search|default('') }}"><button>Search</button></form>

{% if stocks %}
<table class="table">
<tr><th>Symbol</th><th>Name</th><th>Price</th><th>Market Cap (Cr)</th><th>PE</th><th>Change%</th></tr>
{% for s in stocks %}
<tr>
  <td><a href="/stock/{{ s['symbol'] }}" style="color:#9ad7ff">{{ s['symbol'] }}</a></td>
  <td>{{ s['name'] }}</td>
  <td>{{ s['price'] }}</td>
  <td>{{ s['market_cap'] }}</td>
  <td>{{ s['pe'] }}</td>
  <td class="{{ 'pos' if s['change'] is not none and s['change']>=0 else 'neg' }}">{{ s['change'] if s['change'] is not none else 'N/A' }}</td>
</tr>
{% endfor %}
</table>
{% else %}
<p>No stocks to show.</p>
{% endif %}
<p style="color:#aaa">Data cached for {{ cache_minutes }} minutes to avoid rate limits.</p>
</body>
</html>
"""

DETAIL_HTML = """
<!doctype html>
<html>
<head><title>{{ symbol }} - Smart Stock Chooser</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>body{background:#0b0c10;color:#fff;font-family:Segoe UI,Arial;text-align:center} .box{background:#121217;padding:12px;margin:10px;border-radius:8px;display:inline-block}</style>
</head>
<body>
<h1>{{ info.get('longName') or symbol }}</h1>
<div class="box">
<p>Market Cap: ₹{{ market_cap_cr }} Cr</p>
<p>P/E: {{ pe }}</p>
<p>52W High / Low: {{ week_high }} / {{ week_low }}</p>
<p>Previous Close: {{ prev_close }}</p>
</div>

<div id="chart" style="width:90%;height:400px;margin:auto"></div>

<script>
var chartData = {{ chart_data|safe }};
if (chartData && chartData.x.length>0) {
    var trace = { x: chartData.x, y: chartData.y, type: 'scatter', mode:'lines', line:{color:'#00bfff'} };
    var layout = {template:'plotly_dark', title: symbol + " - 6 month" };
    Plotly.newPlot('chart',[trace],layout);
} else {
    document.getElementById('chart').innerHTML = "<p style='color:#f88'>No chart data available (rate limit or no data).</p>";
}
</script>

<p><a href="/" style="color:#9ad7ff">← Back</a></p>
</body>
</html>
"""

@app.route("/")
def home():
    search = (request.args.get("search") or "").strip()
    stocks_to_show = STOCKS.copy()

    results = []
    for sym in stocks_to_show:
        info = get_stock_info_cached(sym)
        # info may be {} if failed; handle gracefully
        name = info.get("longName") or info.get("shortName") or sym
        price = info.get("last_price") or info.get("last_price") if info else None
        # fast_info often has lastPrice or last_price/last_close variations, try multiple keys:
        price = price or info.get("last_price") or info.get("last_close") or info.get("lastTradePrice") or info.get("price") or None
        # fallback: try history quick get (not recommended repeatedly)
        if price is None:
            try:
                hist = get_history_cached(sym)
                if hist is not None and not hist.empty:
                    price = round(float(hist['Close'].iat[-1]),2)
            except Exception:
                price = None

        market_cap = info.get("market_cap") or info.get("marketCap") or 0
        # normalize market cap to Crores (Cr)
        market_cap_cr = round((market_cap or 0) / 1e7, 2)

        pe = info.get("trailingPE") or info.get("pe") or "N/A"
        change = info.get("regularMarketChangePercent") if info.get("regularMarketChangePercent") is not None else None

        entry = {
            "symbol": sym,
            "name": name,
            "price": price or "N/A",
            "market_cap": market_cap_cr,
            "pe": pe,
            "change": round(change,2) if isinstance(change,(int,float)) else None
        }

        # filter by search if provided
        if search:
            if search.upper() in sym or search.upper() in (name or "").upper():
                results.append(entry)
        else:
            results.append(entry)

    # sort by market cap desc and pick top 20
    results = sorted(results, key=lambda x: x.get("market_cap") or 0, reverse=True)[:20]

    return render_template_string(HOME_HTML, stocks=results, search=search, cache_minutes=CACHE_TTL//60)

@app.route("/stock/<symbol>")
def stock_detail(symbol):
    symbol = symbol.upper()
    info = get_stock_info_cached(symbol) or {}
    hist = get_history_cached(symbol)

    # prepare chart data
    chart_data = {"x": [], "y": []}
    if hist is not None and not getattr(hist, "empty", True):
        # convert index to isoformat strings for JS
        chart_data["x"] = [str(idx.date()) if hasattr(idx, "date") else str(idx) for idx in hist.index]
        chart_data["y"] = [round(float(v),2) for v in hist["Close"].tolist()]

    market_cap = info.get("market_cap") or info.get("marketCap") or 0
    market_cap_cr = round((market_cap or 0) / 1e7, 2)
    pe = info.get("trailingPE") or info.get("pe") or "N/A"
    week_high = info.get("fiftyTwoWeekHigh", "N/A")
    week_low = info.get("fiftyTwoWeekLow", "N/A")
    prev_close = info.get("previousClose", info.get("last_close", "N/A"))

    return render_template_string(DETAIL_HTML,
                                  symbol=symbol,
                                  info=info,
                                  chart_data=chart_data,
                                  market_cap_cr=market_cap_cr,
                                  pe=pe,
                                  week_high=week_high,
                                  week_low=week_low,
                                  prev_close=prev_close)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print("Starting Smart Stock Chooser on 0.0.0.0:%s" % port)
    app.run(host="0.0.0.0", port=port)
