from flask import Flask, render_template_string
import yfinance as yf
import random

app = Flask(__name__)

@app.route("/")
def home():
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
        "MCDOWELL-N.NS", "MARICO.NS", "COLPAL.NS", "PETRONET.NS", "NMDC.NS",
        "SAIL.NS", "UBL.NS", "BOSCHLTD.NS", "PAGEIND.NS", "TRENT.NS", "LODHA.NS", "GODREJCP.NS"
    ]

    # Pick 20 random stocks each time
    selected_stocks = random.sample(stock_list, 20)

    data = []
    for symbol in selected_stocks:
        try:
            info = yf.Ticker(symbol).info
            data.append({
                "symbol": symbol,
                "name": info.get("shortName", "Unknown"),
                "price": round(info.get("currentPrice", 0), 2),
                "change": round(info.get("regularMarketChangePercent", 0), 2)
            })
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")

    html = """
    <html>
    <head>
        <title>🔥 Indian Stock Advisor 🔥</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #0e0e10; color: white; text-align: center; }
            table { margin: 20px auto; border-collapse: collapse; width: 90%; }
            th, td { padding: 10px; border-bottom: 1px solid #444; }
            th { background: #1f1f23; color: #ffcc00; }
            tr:hover { background: #222; }
            .pos { color: #00ff99; }
            .neg { color: #ff6666; }
            h1 { color: #ffcc00; }
        </style>
    </head>
    <body>
        <h1>🔥 Indian Stock Advisor 🔥</h1>
        <p>Showing 20 top stocks (randomly refreshed every 24 hours)</p>
        <table>
            <tr><th>Symbol</th><th>Name</th><th>Price (₹)</th><th>Change (%)</th></tr>
            {% for s in data %}
            <tr>
                <td>{{ s.symbol }}</td>
                <td>{{ s.name }}</td>
                <td>{{ s.price }}</td>
                <td class="{{ 'pos' if s.change >= 0 else 'neg' }}">{{ s.change }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """

    return render_template_string(html, data=data)

if __name__ == "__main__":
    print("🚀 Starting Flask server... Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=True)

