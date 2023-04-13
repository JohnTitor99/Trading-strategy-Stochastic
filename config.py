# ----- BOT CONFIG -----

TOKEN = '6122912690:AAF95dCPgUdN27uNXSgrN4Fzmo9IU-WtWLo'
CHAT_ID = 862289283



# ----- BASE CONFIG -----

MARKET = [
    # currencies
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X', 'USDCHF=X', 'NZDUSD=X', 'EURJPY=X',
    'GBPJPY=X', 'EURGBP=X', 'EURCAD=X', 'EURCHF=X',
    # crypto
    'BTC-USD', 'ETH-USD',
    # futures (metals, oil, indices)
    'GC=F', 'SI=F', 'PL=F', 'HG=F', 'BZ=F', 'NQ=F', 'RTY=F', 'ES=F', 'YM=F',
    # stocks
    # 'INTC', 'PFE', 'PYPL', 'MRNA', 'DIS', 'ADBE',
    # 'TSLA', 'MSFT', 'GOOG', 'META', 'AMD', 'F', 'NVDA', 'AMZN', 'BAC', 'GM',
    # 'KO', 'JNJ', 'V', 'BA', 'IBM', 'MA', 'EBAY',
    # 'NFLX', 'ZM', 'PEP', 'COIN', 'DELL',
]

PERIOD = '3mo'
INTERVAL = '1h'

RUNTIME = 2 # check the market every hour in 2 minute



# ----- STOCHASTIC SETTINGS -----

KP = 10 # stochastic period
MP = 3 # stochastic ma period

EMA_21 = 21 # ema 21 for finding up and down trend
EMA_50 = 50 # ema 50 for finding up and down trend