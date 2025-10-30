from flask import Flask, render_template, request
import yfinance as yf
import random

app = Flask(__name__)

# --- Stock List (100+ symbols) ---
stock_list = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS",
    "WIPRO.NS", "HCLTECH.NS", "LT.NS", "ASIANPAINT.NS", "ITC.NS", "BHARTIARTL.NS",
    "BAJFINANCE.NS", "ADANIENT.NS", "ADANIPORTS.NS", "KOTAKBANK.NS", "AXISBANK.NS",
    "ULTRACEMCO.NS", "TITAN.NS", "SUNPHARMA.NS", "ONGC.NS", "POWERGRID.NS", "NTPC.NS",
    "MARUTI.NS", "EICHERMOT.NS", "TATAMOTORS.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS",
    "COALINDIA.NS", "GRASIM.NS", "BRITANNIA.NS", "HINDUNILVR.NS", "DRREDDY.NS", "CIPLA.NS",
    "DIVISLAB.NS", "NESTLEIND.NS", "TECHM.NS", "BPCL.NS", "IOC.NS", "TATAPOWER.NS",
    "HDFCLIFE.NS", "SBILIFE.NS", "ICICIPRULI.NS", "INDUSINDBK.NS", "DLF.NS", "M&M.NS",
    "UPL.NS", "HAVELLS.NS", "PIDILITIND.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS",
    "BEL.NS", "RECLTD.NS", "MFSL.NS", "TORNTPHARM.NS", "BIOCON.NS", "PNB.NS", "CANBK.NS",
    "BANKBARODA.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "TVSMOTOR.NS", "ABBOTINDIA.NS",
    "LTIM.NS", "POLYCAB.NS", "IRCTC.NS", "ZYDUSLIFE.NS", "JINDALSTEL.NS", "TATACONSUM.NS",
    "SHREECEM.NS", "HINDALCO.NS", "ADANIGREEN.NS", "ADANITRANS.NS", "INDIGO.NS",
    "MCDOWELL-N.NS", "MARICO.NS", "COLPAL.NS", "PETRONET.NS", "NMDC.NS", "SAIL.NS",
    "UBL.NS", "BOSCHLTD.NS", "PAGEIND.NS", "TRENT.NS", "LODHA.NS", "GODREJCP.NS"
]

# --- Homepage ---
@app.route("/", methods=["GET", "POST"])
def home():
    query = request.form.get("query", "").upper()

    # If search bar used
    if query:
        symbols = [s for s in stock_list if query in s]
    else:
        # Top 20 random or best
        symbols = random.sample(stock_list, 20)

    stocks = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            stocks.append({
                "symbol": symbol,
                "name": info.get("shortName", "Unknown"),
                "price": round(info.get("currentPrice", 0), 2),
                "market_cap": round(info.get("marketCap", 0) / 1e7, 2),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "change": round(info.get("regularMarketChangePercent", 0), 2)
            })
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")

    return render_template("index.html", stocks=stocks, query=query)

if __name__ == "__main__":
    print("🚀 Smart Stock Chooser is running...")
    app.run(host="0.0.0.0", port=5000)
