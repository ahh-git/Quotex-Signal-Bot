# config.py

APP_NAME = "QUOTEX ANALYZER PRO"
VERSION = "2.4.0 (Stable)"

# Valid Assets (Yahoo Finance Tickers mapped to Binary Options pairs)
ASSETS = {
    "FOREX: EUR/USD": "EURUSD=X",
    "FOREX: GBP/USD": "GBPUSD=X",
    "FOREX: USD/JPY": "JPY=X",
    "FOREX: AUD/CAD": "AUDCAD=X",
    "CRYPTO: BTC/USD": "BTC-USD",
    "CRYPTO: ETH/USD": "ETH-USD",
    "OTC: GOLD": "GC=F"
}

# Strategy Parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
BB_LENGTH = 20
BB_STD = 2.0
