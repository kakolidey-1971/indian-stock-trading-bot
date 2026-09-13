import os
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv('BROKER', 'dhan')
DHAN_CLIENT_ID = os.getenv('DHAN_CLIENT_ID', '')
DHAN_ACCESS_TOKEN = os.getenv('DHAN_ACCESS_TOKEN', '')
KITE_API_KEY = os.getenv('KITE_API_KEY', '')
KITE_ACCESS_TOKEN = os.getenv('KITE_ACCESS_TOKEN', '')

TRADING_SYMBOL = os.getenv('TRADING_SYMBOL', 'TCS')
TRADING_QUANTITY = int(os.getenv('TRADING_QUANTITY', 1))
RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', 2))

MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
TIMEZONE = "Asia/Kolkata"

STRATEGIES = {
    'ma_crossover': {'short_period': 20, 'long_period': 50, 'enabled': True},
    'rsi': {'period': 14, 'overbought': 70, 'oversold': 30, 'enabled': True},
    'bollinger_bands': {'period': 20, 'std_dev': 2, 'enabled': True},
    'macd': {'fast': 12, 'slow': 26, 'signal': 9, 'enabled': True}
}

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
