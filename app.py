
from flask import Flask, render_template_string, request
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

app = Flask(__name__)

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial; background-color: #111; color: #eee; text-align: center; }
        a { color: #00bfff; text-decoration: none; }
        .stock-list { margin: 30px auto; width: 80%; display: flex; flex-wrap: wrap; justify-content: center; }
        .stock-item { background: #222; border-radius: 10px; padding: 15px; margin: 10px; width: 200px; transition: 0.3s; }
        .stock-item:hover { background: #333; transform: scale(1.05); }
        input { padding: 10px; width: 300px; border-radius: 5px; border: none; margin: 20px; }
        button { padding: 10px; border: none; border-radius: 5px; background: #00bfff; color: white; cursor: pointer; }
        .chart-container { width: 90%; margin: auto; }
    </style>
</head>
<body>
    <h1>📈 Indian Stock Dashboard</h1>

    <form method="GET" action="/">
        <input type="text" name="search" placeholder="Search stock symbol (e.g., RELIANCE.NS)">
        <button type="submit">Search</button>
    </form>

    {% if stocks %}
        <div class="stock-list">
            {% for s in stocks %}
                <div class="stock-item">
                    <a href="/stock/{{ s.symbol }}">
                        <h3>{{ s.name }}</h3>
                        <p>💰 {{ s.symbol }}</p>
                        <p>Market Cap: ₹{{ "{:,}".format(s.market_cap) }}</p>
                    </a>
                </div>
            {% endfor %}
        </div>
    {% elif stock %}
        <h2>{{ stock.info['longName'] }} ({{ stock.info['symbol'] }})</h2>
        <p>💰 Market Cap: ₹{{ "{:,}".format(stock.info.get('marketCap', 0)//10000000) }} Cr</p>
        <p>📊 P/E Ratio: {{ stock.info.get('trailingPE', 'N/A') }}</p>
        <p>📈 52W High: {{ stock.info.get('fiftyTwoWeekHigh', 'N/A') }}</p>
        <p>📉 52W Low: {{ stock.info.get('fiftyTwoWeekLow', 'N/A') }}</p>
        <p>🧾 Previous Close: {{ stock.info.get('previousClose', 'N/A') }}</p>
        <p>📆 Open: {{ stock.info.get('open', 'N/A') }}</p>
        <div class="chart-container" id="chart"></div>

        <script>
            var chartData = {{ chart_data | safe }};
            Plotly.newPlot('chart', chartData.data, chartData.layout);
        </script>

        <p><a href="/">← Back to Home</a></p>
    {% else %}
        <p>No results found.</p>
    {% endif %}
</body>
</html>
"""

# --- MAIN ROUTES ---

@app.route("/")
def home():
    search = request.args.get("search")
    if search:
        try:
            stock = yf.Ticker(search)
            return render_template_string(HTML_TEMPLATE, stock=stock, chart_data={})
        except Exception:
            return render_template_string(HTML_TEMPLATE, stocks=None, stock=None)
    else:
        # Example Indian stocks list
        symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
                   "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "BAJFINANCE.NS", "HINDUNILVR.NS", 
                   "ASIANPAINT.NS", "AXISBANK.NS", "MARUTI.NS", "LT.NS", "SUNPHARMA.NS",
                   "DMART.NS", "TITAN.NS", "WIPRO.NS", "POWERGRID.NS", "NTPC.NS"]

        stocks = []
        for sym in symbols:
            data = yf.Ticker(sym)
            info = data.info
            stocks.append({
                "symbol": sym,
                "name": info.get("shortName", sym),
                "market_cap": info.get("marketCap", 0)//10000000
            })

        stocks = sorted(stocks, key=lambda x: x["market_cap"], reverse=True)
        return render_template_string(HTML_TEMPLATE, stocks=stocks, stock=None)

@app.route("/stock/<symbol>")
def stock_detail(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="6mo")

    if hist.empty:
        return render_template_string(HTML_TEMPLATE, stock=stock, chart_data={})

    # Create Plotly chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        mode="lines",
        name="Close Price",
        line=dict(color="#00bfff")
    ))

    fig.update_layout(
        title=f"{symbol} - Last 6 Months",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    chart_data = {"data": fig.to_plotly_json()["data"], "layout": fig.to_plotly_json()["layout"]}

    return render_template_string(HTML_TEMPLATE, stock=stock, chart_data=chart_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
